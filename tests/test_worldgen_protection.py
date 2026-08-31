import unittest

from structure_capability.minecraft.worldgen import (
    BlockBox,
    DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
    MINIMUM_STRUCTURE_EXCLUSION_RADIUS,
    ReservationIndex,
    StructureReservation,
    structure_protection_profile,
    validate_geospatial_worldgen,
    validate_structure_protection_profile,
)


class SpawnProtectionTests(unittest.TestCase):
    def reservation(self, rid, assembly, box, radius=500, family="test:family", provisional=False):
        return StructureReservation(
            reservation_id=rid,
            structure_id="test:structure",
            assembly_id=assembly,
            family_id=family,
            box=box,
            exclusion_radius=radius,
            provisional=provisional,
        )

    def test_minimum_radius_is_500(self):
        self.assertEqual(MINIMUM_STRUCTURE_EXCLUSION_RADIUS, 500)
        self.assertEqual(DEFAULT_STRUCTURE_EXCLUSION_RADIUS, 500)

    def test_radius_below_500_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation("a", "one", BlockBox(0, 0, 0, 1, 1, 1), radius=499)

    def test_exactly_500_blocks_of_clearance_is_allowed(self):
        a = self.reservation("a", "one", BlockBox(0, 0, 0, 9, 9, 9))
        b = self.reservation("b", "two", BlockBox(510, 0, 0, 519, 9, 9))
        index = ReservationIndex([a])
        self.assertIsNone(index.try_reserve(b))

    def test_499_blocks_of_clearance_is_rejected(self):
        a = self.reservation("a", "one", BlockBox(0, 0, 0, 9, 9, 9))
        b = self.reservation("b", "two", BlockBox(509, 0, 0, 518, 9, 9))
        conflict = ReservationIndex([a]).try_reserve(b)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.code, "STRUCTURE_EXCLUSION_CONFLICT")

    def test_uses_actual_footprint_edges_not_structure_centers(self):
        huge = self.reservation("a", "one", BlockBox(-400, 0, -400, 400, 20, 400))
        candidate = self.reservation("b", "two", BlockBox(850, 0, 0, 860, 20, 10))
        conflict = ReservationIndex([huge]).try_reserve(candidate)
        self.assertIsNotNone(conflict)

    def test_larger_existing_radius_wins(self):
        a = self.reservation("a", "one", BlockBox(0, 0, 0, 9, 9, 9), radius=800)
        b = self.reservation("b", "two", BlockBox(610, 0, 0, 619, 9, 9), radius=500)
        self.assertIsNotNone(ReservationIndex([a]).try_reserve(b))

    def test_larger_candidate_radius_wins(self):
        a = self.reservation("a", "one", BlockBox(0, 0, 0, 9, 9, 9), radius=500)
        b = self.reservation("b", "two", BlockBox(610, 0, 0, 619, 9, 9), radius=800)
        self.assertIsNotNone(ReservationIndex([a]).try_reserve(b))

    def test_same_assembly_can_be_close(self):
        a = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=True)
        b = self.reservation("b", "same", BlockBox(10, 0, 0, 19, 9, 9), provisional=True)
        self.assertIsNone(ReservationIndex([a]).try_reserve(b))

    def test_same_assembly_cannot_physically_overlap(self):
        a = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=True)
        b = self.reservation("b", "same", BlockBox(9, 0, 0, 18, 9, 9), provisional=True)
        conflict = ReservationIndex([a]).try_reserve(b)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.code, "SELF_JIGSAW_COLLISION")

    def test_same_family_is_not_enough_for_overlap_exception(self):
        a = self.reservation("a", "assembly-a", BlockBox(0, 0, 0, 9, 9, 9), family="test:village")
        b = self.reservation("b", "assembly-b", BlockBox(10, 0, 0, 19, 9, 9), family="test:village")
        self.assertIsNotNone(ReservationIndex([a]).try_reserve(b))

    def test_vertical_separation_prevents_self_collision(self):
        a = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=True)
        b = self.reservation("b", "same", BlockBox(0, 10, 0, 9, 19, 9), provisional=True)
        self.assertIsNone(ReservationIndex([a]).try_reserve(b))

    def test_external_exclusion_is_horizontal_even_when_vertical_layers_differ(self):
        a = self.reservation("a", "one", BlockBox(0, -60, 0, 9, -40, 9))
        b = self.reservation("b", "two", BlockBox(10, 200, 0, 19, 220, 9))
        self.assertIsNotNone(ReservationIndex([a]).try_reserve(b))

    def test_release_removes_only_provisional_attempt_entries(self):
        committed = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=False)
        provisional = self.reservation("b", "same", BlockBox(10, 0, 0, 19, 9, 9), provisional=True)
        index = ReservationIndex([committed, provisional])
        self.assertEqual(index.release_assembly("same"), 1)
        self.assertEqual([r.reservation_id for r in index.snapshot()], ["a"])

    def test_commit_marks_provisional_entries_committed(self):
        provisional = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=True)
        index = ReservationIndex([provisional])
        self.assertEqual(index.commit_assembly("same"), 1)
        self.assertFalse(index.snapshot()[0].provisional)

    def test_reconcile_drops_speculative_rejected_jigsaw_candidates(self):
        a = self.reservation("a", "same", BlockBox(0, 0, 0, 9, 9, 9), provisional=True)
        b = self.reservation("b", "same", BlockBox(10, 0, 0, 19, 9, 9), provisional=True)
        index = ReservationIndex([a, b])
        self.assertEqual(index.reconcile_assembly("same", [a.box]), 1)
        self.assertEqual([r.reservation_id for r in index.snapshot()], ["a"])

    def test_profile_defaults_jigsaw_radius_to_structure_radius(self):
        profile = structure_protection_profile(structures=["test:site"], exclusion_radius=650)
        self.assertEqual(profile["jigsaw_piece_exclusion_radius"], 650)

    def test_profile_requires_a_selector(self):
        with self.assertRaises(ValueError):
            structure_protection_profile()

    def test_profile_cannot_disable_per_piece_jigsaw_protection(self):
        with self.assertRaises(ValueError):
            structure_protection_profile(structures=["test:site"], protect_jigsaw_pieces=False)

    def test_profile_validator_rejects_disabled_piece_protection(self):
        profile = {
            "selectors": {"structures": ["test:site"]},
            "exclusion_radius": 500,
            "jigsaw_piece_exclusion_radius": 500,
            "protect_jigsaw_pieces": False,
        }
        codes = {code for _, code in validate_structure_protection_profile(profile)}
        self.assertIn("JIGSAW_PIECE_PROTECTION_CANNOT_BE_DISABLED", codes)

    def test_profile_validator_is_fail_closed_on_short_piece_radius(self):
        profile = {
            "selectors": {"structures": ["test:site"]},
            "exclusion_radius": 500,
            "jigsaw_piece_exclusion_radius": 100,
        }
        codes = {code for _, code in validate_structure_protection_profile(profile)}
        self.assertIn("JIGSAW_PIECE_EXCLUSION_RADIUS_BELOW_MINIMUM", codes)

    def test_geospatial_validator_can_require_protection_profile(self):
        structure = {"biomes": "#test:biomes"}
        structure_set = {"placement": {"type": "minecraft:random_spread", "spacing": 32, "separation": 8}}
        codes = {
            code for _, code in validate_geospatial_worldgen(
                structure, structure_set, require_spawn_protection=True
            )
        }
        self.assertIn("MISSING_STRUCTURE_SPAWN_PROTECTION", codes)


if __name__ == "__main__":
    unittest.main()
