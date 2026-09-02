import unittest

from structure_capability.early_human_hearth_circle import (
    HearthCircleGenerationError,
    HearthCircleGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class HearthCircleTests(unittest.TestCase):
    def setUp(self):
        self.generator = HearthCircleGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=7007, scale="medium", condition="repeated")
        second = self.generator.generate(seed=7007, scale="medium", condition="repeated")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=7007, scale="medium")
        second = self.generator.generate(seed=7008, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_all_scales_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=77, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_single_hearth_is_organizing_center(self):
        result = self.generator.generate(seed=20260901, scale="large", condition="active")
        meta = result["metadata"]
        self.assertTrue(meta["qualification_pass"])
        self.assertTrue(meta["qualification"]["single_organizing_hearth"])
        self.assertTrue(meta["qualification"]["multi_hearth_topology_absent"])
        campfires = [b for b in result["blocks"] if b["block"] == "minecraft:campfire"]
        self.assertEqual(len(campfires), 1)
        self.assertEqual(campfires[0]["pos"], meta["hearth"])

    def test_activity_geometry_and_chronology_are_present(self):
        result = self.generator.generate(seed=117, scale="medium", condition="repeated")
        meta = result["metadata"]
        self.assertGreaterEqual(len(meta["seating_points"]), 3)
        self.assertGreaterEqual(len(meta["work_points"]), 2)
        self.assertGreater(len(meta["fuel_points"]), 0)
        self.assertGreater(len(meta["ash_points"]), 0)
        self.assertTrue(meta["qualification"]["radial_or_semiradial_activity_geometry"])
        self.assertTrue(meta["qualification"]["fuel_and_ash_chronology_present"])

    def test_open_air_smoke_column_is_clear(self):
        result = self.generator.generate(seed=701, scale="medium", condition="active")
        meta = result["metadata"]
        hx, _, hz = meta["hearth"]
        above = {
            tuple(entry["pos"])
            for entry in result["blocks"]
            if entry["pos"][0] == hx and entry["pos"][2] == hz and entry["pos"][1] >= 2
        }
        self.assertEqual(above, set())
        self.assertTrue(meta["smoke_column_clear"])
        self.assertTrue(meta["qualification"]["no_shelter_enclosure"])

    def test_repeated_use_has_at_least_as_much_ash_as_active(self):
        active = self.generator.generate(seed=902, scale="large", condition="active")
        repeated = self.generator.generate(seed=902, scale="large", condition="repeated")
        self.assertGreaterEqual(
            len(repeated["metadata"]["ash_points"]),
            len(active["metadata"]["ash_points"]),
        )

    def test_arid_variant_has_no_moss_bedding(self):
        result = self.generator.generate(seed=91, biome_family="arid")
        self.assertNotIn("minecraft:moss_carpet", {entry["block"] for entry in result["blocks"]})

    def test_invalid_scale_rejected(self):
        with self.assertRaises(HearthCircleGenerationError):
            self.generator.generate(seed=1, scale="monumental")

    def test_worldgen_bundle_is_protected_and_valid(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        protection = bundle["protection_profile"]
        self.assertEqual(protection["family"], "continuityworks:early_human_hearth_site")
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertTrue(bundle["placement_contract"]["single_hearth_site_only"])
        self.assertTrue(bundle["placement_contract"]["family_co_location_requires_shared_parent_reservation"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
