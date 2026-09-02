import unittest

from structure_capability.early_human_multi_hearth import (
    MultiHearthGatheringSiteGenerationError,
    MultiHearthGatheringSiteGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class MultiHearthGatheringSiteTests(unittest.TestCase):
    def setUp(self):
        self.generator = MultiHearthGatheringSiteGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=8008, scale="medium", condition="repeated")
        second = self.generator.generate(seed=8008, scale="medium", condition="repeated")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=8008, scale="medium")
        second = self.generator.generate(seed=8009, scale="medium")
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

    def test_multi_center_social_topology_qualifies(self):
        result = self.generator.generate(seed=8008, scale="medium", condition="active")
        meta = result["metadata"]
        self.assertTrue(meta["qualification_pass"])
        self.assertGreaterEqual(meta["current_or_recent_hearth_count"], 2)
        self.assertGreaterEqual(len(meta["hearths"]), 3)
        self.assertTrue(meta["qualification"]["differentiated_hearth_roles"])
        self.assertTrue(meta["qualification"]["shared_circulation_present"])
        self.assertTrue(meta["qualification"]["shared_work_zone_present"])

    def test_site_is_larger_than_single_hearth_circle_envelope(self):
        result = self.generator.generate(seed=117, scale="small")
        self.assertGreaterEqual(result["size"][0], 29)
        self.assertGreaterEqual(result["size"][2], 27)
        self.assertGreaterEqual(len(result["metadata"]["hearths"]), 2)

    def test_smoke_interaction_is_managed(self):
        result = self.generator.generate(seed=20260901, scale="large")
        meta = result["metadata"]
        self.assertEqual(meta["smoke_conflict_count"], 0)
        self.assertTrue(meta["qualification"]["smoke_interaction_managed"])

    def test_arid_variant_has_no_moss_rest_material(self):
        result = self.generator.generate(seed=808, scale="medium", biome_family="arid")
        self.assertNotIn("minecraft:moss_carpet", {entry["block"] for entry in result["blocks"]})

    def test_invalid_scale_rejected(self):
        with self.assertRaises(MultiHearthGatheringSiteGenerationError):
            self.generator.generate(seed=1, scale="monumental")

    def test_worldgen_bundle_is_protected_and_additive(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        protection = bundle["protection_profile"]
        self.assertEqual(protection["family"], "continuityworks:early_human_hearth_site")
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(bundle["placement_contract"]["compatibility_mode"], "additive_non_destructive")
        self.assertEqual(bundle["placement_contract"]["compatible_family_exception"], "same_parent_reservation_or_same_assembly_only")

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
