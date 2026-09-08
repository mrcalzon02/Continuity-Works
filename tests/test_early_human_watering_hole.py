import unittest

from structure_capability.early_human_watering_hole import (
    WateringHoleCampGenerationError,
    WateringHoleCampGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class WateringHoleCampTests(unittest.TestCase):
    def setUp(self):
        self.generator = WateringHoleCampGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=16016, scale="medium")
        second = self.generator.generate(seed=16016, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=16016, scale="medium")
        second = self.generator.generate(seed=16017, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=75, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_qualification_requires_watering_hole_topology(self):
        result = self.generator.generate(seed=161616, scale="large")
        q = result["metadata"]["qualification"]
        self.assertTrue(q["passes"])
        self.assertGreaterEqual(q["water_cell_count"], 20)
        self.assertLess(q["water_fraction"], 0.32)
        self.assertGreaterEqual(q["terrace_water_setback"], 3)
        self.assertGreaterEqual(q["water_access_lane_length"], 3)
        self.assertGreaterEqual(q["external_approach_lane_length"], 3)
        self.assertFalse(q["engineered_water_control"])
        self.assertFalse(q["has_dominant_carcass_axis"])
        self.assertFalse(q["has_river_linear_harvest_program"])

    def test_arid_variant_reduces_water_footprint_without_moss(self):
        temperate = self.generator.generate(seed=7, scale="large", biome_family="temperate")
        arid = self.generator.generate(seed=7, scale="large", biome_family="arid", condition="weathered")
        self.assertLess(len(arid["metadata"]["water_cells"]), len(temperate["metadata"]["water_cells"]))
        self.assertNotIn("minecraft:moss_block", {b["block"] for b in arid["blocks"]})

    def test_cautious_observation_keeps_camp_set_back_and_adds_spoor(self):
        normal = self.generator.generate(seed=88, scale="medium", culture_profile="short_stay")
        cautious = self.generator.generate(seed=88, scale="medium", culture_profile="cautious_observation")
        self.assertGreaterEqual(
            cautious["metadata"]["qualification"]["terrace_water_setback"],
            normal["metadata"]["qualification"]["terrace_water_setback"],
        )
        self.assertGreater(len(cautious["metadata"]["spoor_points"]), len(normal["metadata"]["spoor_points"]))

    def test_carcass_opportunism_remains_secondary(self):
        result = self.generator.generate(seed=91, scale="large", culture_profile="carcass_opportunism")
        self.assertGreater(len(result["metadata"]["carcass_points"]), 0)
        self.assertFalse(result["metadata"]["qualification"]["has_dominant_carcass_axis"])
        self.assertTrue(result["metadata"]["qualification"]["passes"])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(WateringHoleCampGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(WateringHoleCampGenerationError):
            self.generator.generate(seed=1, condition="engineered_reservoir")
        with self.assertRaises(WateringHoleCampGenerationError):
            self.generator.generate(seed=1, culture_profile="canal_builders")

    def test_worldgen_bundle_is_additive_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["family_id"], "continuityworks:early_human_water_access")
        self.assertEqual(bundle["compatibility"]["mode"], "additive_non_destructive")
        self.assertTrue(bundle["compatibility"]["family_tight_composition_requires_same_parent_reservation"])
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
