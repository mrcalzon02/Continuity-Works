import unittest

from structure_capability.early_human_butchery_site import (
    ButcherySiteGenerationError,
    ButcherySiteGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class ButcherySiteTests(unittest.TestCase):
    def setUp(self):
        self.generator = ButcherySiteGenerator()

    def test_same_seed_is_deterministic(self):
        first = self.generator.generate(seed=12012, scale="medium")
        second = self.generator.generate(seed=12012, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_topology(self):
        first = self.generator.generate(seed=12012, scale="medium")
        second = self.generator.generate(seed=12013, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_bounded_and_nonempty(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=512, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_processing_identity_qualifies(self):
        result = self.generator.generate(seed=20260902, scale="medium")
        qualification = result["metadata"]["qualification"]
        self.assertTrue(all(qualification.values()))
        self.assertGreaterEqual(len(result["metadata"]["carcass_cells"]), 3)
        self.assertGreaterEqual(len(result["metadata"]["work_positions"]), 1)
        self.assertGreaterEqual(result["metadata"]["discard_cell_count"], 4)
        self.assertGreaterEqual(len(result["metadata"]["staging_points"]), 2)
        self.assertGreaterEqual(len(result["metadata"]["carry_route"]), 2)

    def test_marrow_zone_required_for_medium_and_large(self):
        for scale in ("medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=9912, scale=scale)
                self.assertGreater(len(result["metadata"]["marrow_points"]), 0)

    def test_small_remains_below_large_carcass_scale(self):
        result = self.generator.generate(seed=45, scale="small")
        self.assertEqual(result["size"], [17, 5, 15])
        self.assertTrue(result["metadata"]["qualification"]["below_large_carcass_scale"])

    def test_transport_focused_culture_increases_staging(self):
        baseline = self.generator.generate(seed=700, scale="medium", culture_profile="expedient_field_dressing")
        focused = self.generator.generate(seed=700, scale="medium", culture_profile="transport_focused")
        self.assertGreater(len(focused["metadata"]["staging_points"]), len(baseline["metadata"]["staging_points"]))

    def test_marrow_intensive_culture_increases_marrow_evidence(self):
        baseline = self.generator.generate(seed=701, scale="large", culture_profile="expedient_field_dressing")
        intensive = self.generator.generate(seed=701, scale="large", culture_profile="marrow_intensive")
        self.assertGreater(len(intensive["metadata"]["marrow_points"]), len(baseline["metadata"]["marrow_points"]))

    def test_arid_weathered_variant_has_no_moss(self):
        result = self.generator.generate(seed=813, scale="medium", biome_family="arid", condition="weathered")
        self.assertNotIn("minecraft:moss_carpet", {entry["block"] for entry in result["blocks"]})

    def test_scavenger_reworked_still_qualifies(self):
        result = self.generator.generate(seed=814, scale="medium", condition="scavenger_reworked")
        self.assertTrue(all(result["metadata"]["qualification"].values()))

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ButcherySiteGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(ButcherySiteGenerationError):
            self.generator.generate(seed=1, condition="industrial")
        with self.assertRaises(ButcherySiteGenerationError):
            self.generator.generate(seed=1, culture_profile="metal_butchery")

    def test_worldgen_bundle_is_additive_protected_and_valid(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["family_id"], "continuityworks:early_human_carcass_processing")
        self.assertEqual(bundle["compatible_family_policy"], "same_parent_reservation_only")
        self.assertEqual(bundle["replace_policy"], "bounded_additive_non_destructive")
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
