import unittest

from structure_capability.early_human_quartzite_quarry import (
    QuartziteQuarryGenerationError,
    QuartziteQuarryGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class QuartziteQuarryTests(unittest.TestCase):
    def setUp(self):
        self.generator = QuartziteQuarryGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=11011, scale="medium")
        second = self.generator.generate(seed=11011, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_quarry(self):
        first = self.generator.generate(seed=11011, scale="medium")
        second = self.generator.generate(seed=11012, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_all_scales_are_nonempty_and_in_bounds(self):
        expected = {"small": [23, 8, 19], "medium": [37, 10, 31], "large": [57, 12, 45]}
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=91, scale=scale)
                self.assertEqual(result["size"], expected[scale])
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < result["size"][i] for i in range(3)))

    def test_quarry_identity_is_extraction_first(self):
        result = self.generator.generate(seed=20260902, scale="large")
        meta = result["metadata"]
        qualification = meta["qualification"]
        self.assertTrue(all(qualification.values()))
        self.assertGreaterEqual(meta["face_segment_count"], 4)
        self.assertGreater(meta["extraction_scar_count"], 0)
        self.assertGreater(meta["coarse_debris_cell_count"], meta["primary_reduction_point_count"])
        self.assertGreater(len(meta["staging_points"]), 0)
        self.assertGreaterEqual(len(meta["haul_route"]), 2)

    def test_quartzite_is_declared_as_semantic_proxy(self):
        result = self.generator.generate(seed=42)
        semantics = result["metadata"]["material_semantics"]
        self.assertEqual(semantics["source"], "quartzite_role_proxy")
        self.assertEqual(semantics["source_block"], "minecraft:diorite")
        blocks = {entry["block"] for entry in result["blocks"]}
        self.assertNotIn("minecraft:quartz_block", blocks)
        self.assertNotIn("minecraft:smooth_quartz", blocks)

    def test_source_depleted_condition_preserves_quarry_identity(self):
        result = self.generator.generate(seed=77, scale="medium", condition="source_depleted")
        self.assertGreater(len(result["metadata"]["legacy_face"]), 0)
        self.assertTrue(all(result["metadata"]["qualification"].values()))

    def test_arid_variant_uses_no_mossy_weathering(self):
        result = self.generator.generate(seed=14, biome_family="arid", condition="abandoned")
        self.assertNotIn("minecraft:mossy_cobblestone", {entry["block"] for entry in result["blocks"]})

    def test_invalid_scale_and_condition_are_rejected(self):
        with self.assertRaises(QuartziteQuarryGenerationError):
            self.generator.generate(seed=1, scale="industrial")
        with self.assertRaises(QuartziteQuarryGenerationError):
            self.generator.generate(seed=1, condition="blasted")

    def test_worldgen_bundle_is_protected_and_additive(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["family_id"], "continuityworks:early_human_lithic_source")
        self.assertEqual(bundle["compatible_family_policy"], "same_parent_reservation_only")
        self.assertEqual(bundle["replace_policy"], "bounded_additive_non_destructive")
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])

    def test_worldgen_placement_contract_is_valid(self):
        bundle = self.generator.worldgen_bundle()
        placement = bundle["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])
        self.assertEqual(bundle["structure"]["step"], "surface_structures")
        self.assertEqual(bundle["structure"]["project_start_to_heightmap"], "WORLD_SURFACE_WG")
        self.assertEqual(bundle["structure"]["start_pool"], bundle["start_pool"])


if __name__ == "__main__":
    unittest.main()
