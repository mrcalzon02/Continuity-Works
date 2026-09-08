import unittest

from structure_capability.early_human_large_carcass_processing import (
    LargeCarcassProcessingSiteGenerationError,
    LargeCarcassProcessingSiteGenerator,
)


class LargeCarcassProcessingSiteTests(unittest.TestCase):
    def setUp(self):
        self.generator = LargeCarcassProcessingSiteGenerator()

    def test_deterministic_replay_and_seed_variation(self):
        a = self.generator.generate(seed=130013, scale="medium")
        b = self.generator.generate(seed=130013, scale="medium")
        c = self.generator.generate(seed=130014, scale="medium")
        self.assertEqual(a["metadata"]["fingerprint"], b["metadata"]["fingerprint"])
        self.assertNotEqual(a["metadata"]["fingerprint"], c["metadata"]["fingerprint"])

    def test_scale_envelopes_and_large_carcass_identity(self):
        cases = [
            ("small", [43, 8, 35], 3),
            ("medium", [57, 9, 47], 4),
            ("large", [73, 10, 61], 6),
        ]
        for scale, size, minimum_bays in cases:
            with self.subTest(scale=scale):
                site = self.generator.generate(seed=7713, scale=scale)
                metadata = site["metadata"]
                self.assertEqual(site["size"], size)
                self.assertGreaterEqual(len(metadata["task_bays"]), minimum_bays)
                self.assertGreaterEqual(len(metadata["heavy_bone_points"]), 6)
                self.assertGreaterEqual(metadata["carcass_axis_length"], 15)
                self.assertTrue(all(metadata["qualification"].values()))
                self.assertGreater(size[0], 39)
                self.assertGreater(size[2], 33)

    def test_processing_topology_has_dirty_and_clean_sides_with_clear_haul_route(self):
        site = self.generator.generate(seed="megafauna-topology", scale="large")
        metadata = site["metadata"]
        self.assertGreaterEqual(metadata["discard_cell_count"], 12)
        self.assertGreaterEqual(len(metadata["staging_points"]), 5)
        self.assertGreaterEqual(len(metadata["haul_corridor"]), 2)
        self.assertTrue(metadata["qualification"]["directional_dirty_discard"])
        self.assertTrue(metadata["qualification"]["clean_staging_present"])
        self.assertTrue(metadata["qualification"]["haul_corridor_clear"])

    def test_culture_variants_preserve_archetype(self):
        for culture in (
            "cooperative_disarticulation",
            "marrow_intensive",
            "transport_priority",
            "hide_retention",
        ):
            with self.subTest(culture=culture):
                site = self.generator.generate(
                    seed=f"culture-{culture}",
                    scale="medium",
                    culture_profile=culture,
                )
                self.assertEqual(site["metadata"]["culture_profile"], culture)
                self.assertTrue(all(site["metadata"]["qualification"].values()))

    def test_marrow_intensive_variant_increases_heavy_bone_evidence(self):
        baseline = self.generator.generate(
            seed=91,
            scale="medium",
            culture_profile="cooperative_disarticulation",
        )
        marrow = self.generator.generate(
            seed=91,
            scale="medium",
            culture_profile="marrow_intensive",
        )
        self.assertGreater(
            len(marrow["metadata"]["heavy_bone_points"]),
            len(baseline["metadata"]["heavy_bone_points"]),
        )

    def test_transport_priority_increases_staging(self):
        baseline = self.generator.generate(seed=92, scale="medium")
        transport = self.generator.generate(
            seed=92,
            scale="medium",
            culture_profile="transport_priority",
        )
        self.assertGreater(
            len(transport["metadata"]["staging_points"]),
            len(baseline["metadata"]["staging_points"]),
        )

    def test_hide_retention_increases_hide_handling_without_domination(self):
        baseline = self.generator.generate(seed=93, scale="large")
        hide = self.generator.generate(
            seed=93,
            scale="large",
            culture_profile="hide_retention",
        )
        self.assertGreater(
            len(hide["metadata"]["hide_offcut_points"]),
            len(baseline["metadata"]["hide_offcut_points"]),
        )
        self.assertTrue(hide["metadata"]["qualification"]["hide_handling_subordinate"])

    def test_condition_variants_remain_qualified(self):
        for condition in (
            "active",
            "recent",
            "repeated",
            "abandoned",
            "weathered",
            "scavenger_reworked",
            "sediment_reworked",
            "repurposed",
        ):
            with self.subTest(condition=condition):
                site = self.generator.generate(
                    seed=f"condition-{condition}",
                    scale="medium",
                    condition=condition,
                )
                self.assertTrue(all(site["metadata"]["qualification"].values()))

    def test_arid_weathering_does_not_add_moss(self):
        site = self.generator.generate(
            seed="dry-weathering",
            scale="medium",
            biome_family="arid",
            condition="weathered",
        )
        self.assertTrue(
            all(block["block"] != "minecraft:moss_carpet" for block in site["blocks"])
        )

    def test_all_blocks_stay_inside_declared_bounds(self):
        site = self.generator.generate(seed=13013, scale="large")
        width, height, depth = site["size"]
        for block in site["blocks"]:
            x, y, z = block["pos"]
            self.assertTrue(0 <= x < width)
            self.assertTrue(0 <= y < height)
            self.assertTrue(0 <= z < depth)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(LargeCarcassProcessingSiteGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(LargeCarcassProcessingSiteGenerationError):
            self.generator.generate(seed=1, condition="museum")
        with self.assertRaises(LargeCarcassProcessingSiteGenerationError):
            self.generator.generate(seed=1, culture_profile="industrial_butchery")

    def test_worldgen_is_additive_and_protected_at_minimum_radius(self):
        bundle = self.generator.worldgen_bundle()
        protection = bundle["protection_profile"]
        self.assertEqual(
            bundle["structure_id"],
            "continuityworks:e01_013_large_carcass_processing_site",
        )
        self.assertEqual(
            bundle["family_id"],
            "continuityworks:early_human_carcass_processing",
        )
        self.assertEqual(bundle["replace_policy"], "bounded_additive_non_destructive")
        self.assertEqual(
            bundle["compatible_family_policy"],
            "same_parent_reservation_only",
        )
        self.assertGreaterEqual(protection["exclusion_radius"], 500)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], 500)
        self.assertTrue(protection["protect_jigsaw_pieces"])

    def test_worldgen_random_spread_spacing_is_valid(self):
        bundle = self.generator.worldgen_bundle()
        placement = bundle["structure_set"]["placement"]
        self.assertGreater(placement["spacing"], placement["separation"])
        self.assertEqual(bundle["validation_findings"], [])


if __name__ == "__main__":
    unittest.main()
