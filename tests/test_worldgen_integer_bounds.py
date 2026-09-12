import unittest

from structure_capability.minecraft.worldgen import (
    BlockBox,
    JAVA_INT_MAX,
    MAXIMUM_RANDOM_SPREAD_DISTANCE,
    StructureReservation,
    jigsaw_structure,
    random_spread_structure_set,
    structure_protection_profile,
    validate_geospatial_worldgen,
    validate_structure_protection_profile,
)


class WorldgenIntegerBoundsTests(unittest.TestCase):
    def test_random_spread_accepts_codec_maximum(self):
        structure_set = random_spread_structure_set(
            "continuity_works:test",
            MAXIMUM_RANDOM_SPREAD_DISTANCE,
            MAXIMUM_RANDOM_SPREAD_DISTANCE - 1,
            1,
        )
        self.assertEqual(
            structure_set["placement"]["spacing"],
            MAXIMUM_RANDOM_SPREAD_DISTANCE,
        )

    def test_random_spread_rejects_spacing_above_codec_maximum(self):
        with self.assertRaisesRegex(ValueError, "spacing must be <= 4096"):
            random_spread_structure_set(
                "continuity_works:test",
                MAXIMUM_RANDOM_SPREAD_DISTANCE + 1,
                1,
                1,
            )

    def test_random_spread_rejects_separation_above_codec_maximum(self):
        with self.assertRaisesRegex(ValueError, "separation must be <= 4096"):
            random_spread_structure_set(
                "continuity_works:test",
                MAXIMUM_RANDOM_SPREAD_DISTANCE,
                MAXIMUM_RANDOM_SPREAD_DISTANCE + 1,
                1,
            )

    def test_validator_rejects_random_spread_values_above_codec_maximum(self):
        structure = jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="continuity_works:test/start",
        )
        structure_set = {
            "structures": [{"structure": "continuity_works:test", "weight": 1}],
            "placement": {
                "type": "minecraft:random_spread",
                "spacing": MAXIMUM_RANDOM_SPREAD_DISTANCE + 1,
                "separation": 1,
                "salt": 1,
            },
        }
        self.assertIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(structure, structure_set),
        )

    def test_reservation_rejects_exclusion_radius_above_java_int_maximum(self):
        with self.assertRaisesRegex(ValueError, "signed 32-bit Java integer"):
            StructureReservation(
                reservation_id="reservation",
                structure_id="continuity_works:test",
                assembly_id="assembly",
                family_id="family",
                box=BlockBox(0, 0, 0, 9, 9, 9),
                exclusion_radius=JAVA_INT_MAX + 1,
            )

    def test_protection_profile_constructor_rejects_radius_above_java_int_maximum(self):
        with self.assertRaisesRegex(ValueError, "signed 32-bit Java integer"):
            structure_protection_profile(
                structures=["continuity_works:test"],
                exclusion_radius=JAVA_INT_MAX + 1,
            )

    def test_protection_profile_validator_rejects_both_radius_overflows(self):
        profile = structure_protection_profile(structures=["continuity_works:test"])
        profile["exclusion_radius"] = JAVA_INT_MAX + 1
        profile["jigsaw_piece_exclusion_radius"] = JAVA_INT_MAX + 1
        findings = validate_structure_protection_profile(profile)
        self.assertIn(
            ("error", "STRUCTURE_EXCLUSION_RADIUS_ABOVE_MAXIMUM"),
            findings,
        )
        self.assertIn(
            ("error", "JIGSAW_PIECE_EXCLUSION_RADIUS_ABOVE_MAXIMUM"),
            findings,
        )

    def test_default_500_block_exclusion_remains_valid(self):
        reservation = StructureReservation(
            reservation_id="reservation",
            structure_id="continuity_works:test",
            assembly_id="assembly",
            family_id="family",
            box=BlockBox(0, 0, 0, 9, 9, 9),
        )
        self.assertEqual(reservation.exclusion_radius, 500)


if __name__ == "__main__":
    unittest.main()
