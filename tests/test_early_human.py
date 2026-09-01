import unittest

from structure_capability.early_human import (
    EarlyHumanGenerationError,
    EarlyHumanStructureGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class EarlyHumanStructureTests(unittest.TestCase):
    def setUp(self):
        self.generator = EarlyHumanStructureGenerator()

    def test_e01_001_same_seed_is_deterministic(self):
        first = self.generator.generate("E01-001", seed=20260901, scale="medium")
        second = self.generator.generate("E01-001", seed=20260901, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_e01_001_different_seed_changes_structure(self):
        first = self.generator.generate("E01-001", seed=1, scale="medium")
        second = self.generator.generate("E01-001", seed=2, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_e01_001_scales_are_in_bounds_and_nonempty(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate("E01-001", seed=77, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_e01_001_contains_supported_geology_and_hearth(self):
        result = self.generator.generate("E01-001", seed=91, scale="medium", condition="active")
        positions = {tuple(entry["pos"]): entry["block"] for entry in result["blocks"]}
        hearth = tuple(result["metadata"]["hearth"])
        self.assertEqual(positions[hearth], "minecraft:campfire")
        rear_z = result["size"][2] - 1
        rear_support = [
            entry for entry in result["blocks"]
            if entry["pos"][2] == rear_z and entry["pos"][1] >= 1
        ]
        self.assertGreater(len(rear_support), 0)

    def test_e01_001_arid_variant_has_no_moss_bedding(self):
        result = self.generator.generate("E01-001", seed=13, biome_family="arid")
        self.assertNotIn("minecraft:moss_carpet", {entry["block"] for entry in result["blocks"]})

    def test_e01_001_invalid_scale_rejected(self):
        with self.assertRaises(EarlyHumanGenerationError):
            self.generator.generate("E01-001", seed=1, scale="gigantic")

    def test_e01_001_worldgen_bundle_is_protected_and_valid(self):
        bundle = self.generator.worldgen_bundle("E01-001")
        self.assertEqual(bundle["validation_findings"], [])
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(
            protection["jigsaw_piece_exclusion_radius"],
            MINIMUM_STRUCTURE_EXCLUSION_RADIUS,
        )
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(bundle["structure"]["start_pool"], bundle["start_pool"])

    def test_e01_001_worldgen_spacing_is_valid(self):
        bundle = self.generator.worldgen_bundle("E01-001")
        placement = bundle["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])

    def test_e01_002_same_seed_is_deterministic(self):
        first = self.generator.generate("E01-002", seed=22002, scale="medium")
        second = self.generator.generate("E01-002", seed=22002, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_e01_002_different_seed_changes_structure(self):
        first = self.generator.generate("E01-002", seed=22002, scale="medium")
        second = self.generator.generate("E01-002", seed=22003, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_e01_002_scales_are_in_bounds_and_nonempty(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate("E01-002", seed=202, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_e01_002_preserves_threshold_identity(self):
        result = self.generator.generate("E01-002", seed=20260902, scale="medium")
        meta = result["metadata"]
        daylight_start, daylight_end = meta["daylight_band"]
        twilight_start, twilight_end = meta["twilight_band"]
        self.assertEqual(daylight_start, meta["mouth_z"])
        self.assertGreaterEqual(twilight_start, daylight_end)
        self.assertEqual(twilight_end, meta["interior_stop_z"])
        self.assertLessEqual(meta["work_zone_anchor"][2], daylight_end)
        self.assertLessEqual(meta["rest_zone_anchor"][2], meta["interior_stop_z"])
        self.assertLessEqual(meta["hearth"][2], meta["interior_stop_z"])

    def test_e01_002_activity_does_not_extend_beyond_interior_stop(self):
        result = self.generator.generate("E01-002", seed=555, scale="large", condition="active")
        stop = result["metadata"]["interior_stop_z"]
        for key in ("hearth", "work_zone_anchor", "rest_zone_anchor", "cache_anchor"):
            self.assertLessEqual(result["metadata"][key][2], stop)

    def test_e01_002_arid_variant_has_no_moss_bedding(self):
        result = self.generator.generate("E01-002", seed=14, biome_family="arid")
        self.assertNotIn("minecraft:moss_carpet", {entry["block"] for entry in result["blocks"]})

    def test_e01_002_worldgen_bundle_is_protected_and_valid(self):
        bundle = self.generator.worldgen_bundle("E01-002")
        self.assertEqual(bundle["validation_findings"], [])
        protection = bundle["protection_profile"]
        self.assertEqual(protection["family"], "continuityworks:early_human_cave_complex")
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(
            protection["jigsaw_piece_exclusion_radius"],
            MINIMUM_STRUCTURE_EXCLUSION_RADIUS,
        )
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(bundle["structure"]["terrain_adaptation"], "bury")
        self.assertEqual(bundle["structure"]["start_pool"], bundle["start_pool"])

    def test_e01_002_worldgen_spacing_is_valid(self):
        bundle = self.generator.worldgen_bundle("E01-002")
        placement = bundle["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
