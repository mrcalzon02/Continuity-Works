import unittest

from structure_capability.early_human_flint_procurement import (
    FlintProcurementPitGenerationError,
    FlintProcurementPitGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class FlintProcurementPitTests(unittest.TestCase):
    def setUp(self):
        self.generator = FlintProcurementPitGenerator()

    def test_same_seed_is_deterministic(self):
        first = self.generator.generate(seed=101010, scale="medium")
        second = self.generator.generate(seed=101010, scale="medium")
        self.assertEqual(first, second)

    def test_different_seed_changes_fingerprint(self):
        first = self.generator.generate(seed=1, scale="medium")
        second = self.generator.generate(seed=2, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=44, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_procurement_identity_is_complete(self):
        result = self.generator.generate(seed=20260901, scale="large")
        meta = result["metadata"]
        self.assertTrue(all(meta["qualification"].values()))
        self.assertGreater(len(meta["source_cells"]), 0)
        self.assertGreater(len(meta["pits"]), 0)
        self.assertGreater(len(meta["spoil_cells"]), 0)
        self.assertGreater(len(meta["carry_out_route"]), 0)
        self.assertGreater(len(meta["selected_material_staging"]), 0)

    def test_depth_stays_shallow_and_scale_bounded(self):
        caps = {"small": 2, "medium": 3, "large": 4}
        for scale, cap in caps.items():
            result = self.generator.generate(seed=880 + cap, scale=scale)
            self.assertLessEqual(max(p["max_depth"] for p in result["metadata"]["pits"]), cap)

    def test_testing_remains_subordinate_to_procurement(self):
        result = self.generator.generate(seed=71, scale="large")
        meta = result["metadata"]
        self.assertLess(len(meta["rejected_points"]), max(8, len(meta["spoil_cells"])))
        self.assertTrue(meta["qualification"]["testing_subordinate"])

    def test_repeated_condition_records_legacy_infill(self):
        result = self.generator.generate(seed=91, scale="medium", condition="repeated")
        self.assertGreater(len(result["metadata"]["legacy_infill"]), 0)

    def test_arid_palette_avoids_moss_and_wood_infrastructure(self):
        result = self.generator.generate(seed=3, biome_family="arid")
        blocks = {entry["block"] for entry in result["blocks"]}
        self.assertNotIn("minecraft:moss_block", blocks)
        self.assertNotIn("minecraft:oak_planks", blocks)
        self.assertNotIn("minecraft:rail", blocks)

    def test_invalid_scale_and_condition_rejected(self):
        with self.assertRaises(FlintProcurementPitGenerationError):
            self.generator.generate(seed=1, scale="mine")
        with self.assertRaises(FlintProcurementPitGenerationError):
            self.generator.generate(seed=1, condition="industrial")

    def test_worldgen_bundle_is_protected_and_valid(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(protection["family"], "continuityworks:early_human_lithic_source")
        self.assertEqual(bundle["compatibility_mode"], "additive_non_destructive")
        self.assertTrue(bundle["compatible_family_requires_shared_parent_reservation"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
