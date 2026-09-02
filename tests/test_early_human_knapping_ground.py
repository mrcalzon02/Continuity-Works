import unittest

from structure_capability.early_human_knapping_ground import (
    FAMILY_ID,
    StoneToolKnappingGroundGenerationError,
    StoneToolKnappingGroundGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class StoneToolKnappingGroundTests(unittest.TestCase):
    def setUp(self):
        self.generator = StoneToolKnappingGroundGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=20260909, scale="medium", condition="repeated")
        second = self.generator.generate(seed=20260909, scale="medium", condition="repeated")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=1, scale="medium")
        second = self.generator.generate(seed=2, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_vanilla_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=900 + len(scale), scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_lithic_production_identity_is_explicit(self):
        result = self.generator.generate(seed=91, scale="large", parent_context="INDEPENDENT_WORKSITE")
        meta = result["metadata"]
        self.assertTrue(all(meta["qualification"].values()))
        self.assertGreaterEqual(len(meta["work_positions"]), 4)
        self.assertGreater(len(meta["raw_material"]), 0)
        self.assertGreater(len(meta["hammerstones"]), 0)
        self.assertGreater(len(meta["core_points"]), 0)
        self.assertGreater(len(meta["debris_points"]), 0)
        self.assertIn(meta["provenance"], {"LOCAL_COBBLE", "TRANSPORTED_NODULE", "MIXED_LOCAL_IMPORTED"})

    def test_debris_is_directional_and_work_records_are_not_uniform_scatter(self):
        result = self.generator.generate(seed=90210, scale="medium")
        for record in result["metadata"]["work_records"]:
            self.assertGreater(len(record["debris"]), 0)
            vector = record["facing_vector"]
            self.assertAlmostEqual(vector[0] ** 2 + vector[1] ** 2, 1.0, delta=0.01)

    def test_circulation_avoids_dense_sharp_hazard_cells(self):
        result = self.generator.generate(seed=777, scale="large", condition="repeated")
        hazard = {tuple(p) for p in result["metadata"]["dense_hazard_cells"]}
        circulation = {(p[0], p[2]) for p in result["metadata"]["circulation"]}
        self.assertTrue(circulation)
        self.assertTrue(hazard.isdisjoint(circulation))

    def test_repeated_use_adds_legacy_reduction_lens(self):
        result = self.generator.generate(seed=333, scale="medium", condition="repeated")
        self.assertGreater(len(result["metadata"]["legacy_lens"]), 0)
        self.assertTrue(any(record["stage"] == "MIXED_SEQUENCE" for record in result["metadata"]["work_records"]))

    def test_source_adjacent_provenance_is_local(self):
        result = self.generator.generate(seed=51, parent_context="SOURCE_ADJACENT")
        self.assertIn(result["metadata"]["provenance"], {"LOCAL_COBBLE", "LOCAL_OUTCROP"})

    def test_invalid_scale_and_context_are_rejected(self):
        with self.assertRaises(StoneToolKnappingGroundGenerationError):
            self.generator.generate(seed=1, scale="megastructure")
        with self.assertRaises(StoneToolKnappingGroundGenerationError):
            self.generator.generate(seed=1, parent_context="FACTORY_WORKSHOP")

    def test_worldgen_bundle_is_protected_and_additive(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["family_id"], FAMILY_ID)
        self.assertEqual(bundle["compatibility_mode"], "additive_non_destructive")
        self.assertTrue(bundle["compatible_family_requires_shared_parent_reservation"])
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(bundle["structure"]["start_pool"], bundle["start_pool"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
