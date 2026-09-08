import unittest

from structure_capability.early_human_riverbank_foraging import (
    RiverbankForagingCampGenerationError,
    RiverbankForagingCampGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class RiverbankForagingCampTests(unittest.TestCase):
    def setUp(self):
        self.generator = RiverbankForagingCampGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=17017, scale="medium")
        second = self.generator.generate(seed=17017, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=17017, scale="medium")
        second = self.generator.generate(seed=17018, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=71, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_qualification_requires_linear_river_foraging_topology(self):
        result = self.generator.generate(seed=171717, scale="large")
        q = result["metadata"]["qualification"]
        self.assertTrue(q["passes"])
        self.assertTrue(q["river_is_linear"])
        self.assertGreaterEqual(q["return_path_count"], 2)
        self.assertGreaterEqual(q["processing_pocket_count"], 1)
        self.assertGreaterEqual(q["activity_stance_count"], q["processing_pocket_count"])
        self.assertFalse(q["has_permanent_architecture"])
        self.assertTrue(q["hearth_is_subordinate"])

    def test_scale_increases_river_and_foraging_extent(self):
        small = self.generator.generate(seed=44, scale="small", culture_profile="shoreline_gathering")
        large = self.generator.generate(seed=44, scale="large", culture_profile="shoreline_gathering")
        small_q = small["metadata"]["qualification"]
        large_q = large["metadata"]["qualification"]
        self.assertGreater(large_q["water_major_span"], small_q["water_major_span"])
        self.assertGreater(large_q["return_path_count"], small_q["return_path_count"])

    def test_root_seed_processing_maximizes_processing_pockets(self):
        result = self.generator.generate(seed=55, scale="large", culture_profile="root_seed_processing")
        self.assertEqual(result["metadata"]["qualification"]["processing_pocket_count"], 5)
        self.assertTrue(result["metadata"]["qualification"]["passes"])

    def test_arid_variant_remains_linear_and_weathering_has_no_moss(self):
        result = self.generator.generate(seed=8, biome_family="arid", condition="weathered")
        self.assertTrue(result["metadata"]["qualification"]["river_is_linear"])
        self.assertNotIn("minecraft:moss_block", {b["block"] for b in result["blocks"]})

    def test_flood_reworked_preserves_core_qualification(self):
        result = self.generator.generate(seed=91, scale="large", condition="flood_reworked")
        self.assertTrue(result["metadata"]["qualification"]["passes"])
        self.assertGreaterEqual(len(result["metadata"]["water_access_lane"]), 2)

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(RiverbankForagingCampGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(RiverbankForagingCampGenerationError):
            self.generator.generate(seed=1, condition="engineered_canal")
        with self.assertRaises(RiverbankForagingCampGenerationError):
            self.generator.generate(seed=1, culture_profile="agriculture")

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
