import unittest

from structure_capability.early_human_hide_windbreak import (
    FAMILY_ID,
    HideWindbreakCampGenerationError,
    HideWindbreakCampGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class HideWindbreakCampTests(unittest.TestCase):
    def setUp(self):
        self.generator = HideWindbreakCampGenerator()

    def test_same_seed_is_deterministic(self):
        first = self.generator.generate(seed=6006, scale="medium")
        second = self.generator.generate(seed=6006, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=6006, scale="medium")
        second = self.generator.generate(seed=6007, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_all_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=66, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_archetype_qualification_preserves_hide_windbreak_identity(self):
        result = self.generator.generate(seed=20260901, scale="large", condition="active")
        meta = result["metadata"]
        self.assertTrue(meta["qualification_pass"])
        self.assertTrue(meta["qualification"]["hide_skin_dominant"])
        self.assertTrue(meta["qualification"]["support_and_tension_geometry_present"])
        self.assertTrue(meta["qualification"]["camp_scale_occupation_present"])
        self.assertTrue(meta["qualification"]["perimeter_open"])
        self.assertTrue(meta["qualification"]["brush_screen_not_dominant"])
        self.assertGreaterEqual(meta["hide_coverage_ratio"], 0.55)
        self.assertGreater(len(meta["tension_points"]), 0)

    def test_active_camp_has_hearth_and_occupation_anchors(self):
        result = self.generator.generate(seed=42, condition="active")
        meta = result["metadata"]
        self.assertIsNotNone(meta["hearth"])
        self.assertIsNotNone(meta["rest_zone_anchor"])
        self.assertIsNotNone(meta["work_zone_anchor"])

    def test_arid_variant_has_no_carpet_bedding(self):
        result = self.generator.generate(seed=13, biome_family="arid")
        blocks = {entry["block"] for entry in result["blocks"]}
        self.assertNotIn("minecraft:brown_carpet", blocks)
        self.assertNotIn("minecraft:white_carpet", blocks)

    def test_collapsed_condition_reduces_hide_skin(self):
        active = self.generator.generate(seed=91, scale="medium", condition="active")
        collapsed = self.generator.generate(seed=91, scale="medium", condition="collapsed")
        active_hide = len(active["metadata"]["hide_points"])
        collapsed_blocks = {tuple(e["pos"]): e["block"] for e in collapsed["blocks"]}
        hide_palette = {"minecraft:brown_wool", "minecraft:white_wool", "minecraft:light_gray_wool", "minecraft:orange_wool"}
        collapsed_hide = sum(1 for b in collapsed_blocks.values() if b in hide_palette)
        self.assertLess(collapsed_hide, active_hide)

    def test_invalid_scale_is_rejected(self):
        with self.assertRaises(HideWindbreakCampGenerationError):
            self.generator.generate(seed=1, scale="megastructure")

    def test_worldgen_bundle_is_surface_anchored_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["protection_profile"]["family"], FAMILY_ID)
        self.assertGreaterEqual(bundle["protection_profile"]["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(bundle["protection_profile"]["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(bundle["protection_profile"]["protect_jigsaw_pieces"])
        self.assertEqual(bundle["structure"]["step"], "surface_structures")
        self.assertEqual(bundle["structure"]["project_start_to_heightmap"], "WORLD_SURFACE_WG")
        self.assertEqual(bundle["structure"]["start_pool"], bundle["start_pool"])
        self.assertTrue(bundle["placement_contract"]["family_co_location_requires_shared_parent_reservation"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
