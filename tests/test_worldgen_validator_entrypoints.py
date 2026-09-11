import unittest

from structure_capability.minecraft.worldgen import (
    jigsaw_structure,
    random_spread_structure_set,
    validate_geospatial_worldgen,
    validate_structure_protection_profile,
)


class WorldgenValidatorEntrypointTests(unittest.TestCase):
    def test_direct_profile_validator_rejects_non_mapping_shapes(self):
        for profile in (None, True, 1, 1.5, "profile", [], ()):
            with self.subTest(profile=profile):
                self.assertEqual(
                    [("error", "INVALID_PROTECTION_PROFILE_SHAPE")],
                    validate_structure_protection_profile(profile),
                )

    def test_geospatial_validator_rejects_missing_or_unsupported_structure_type(self):
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        for structure in (
            {"biomes": "#test:biomes"},
            {"type": "minecraft:ruined_portal", "biomes": "#test:biomes"},
            {"type": "", "biomes": "#test:biomes"},
        ):
            with self.subTest(structure=structure):
                self.assertIn(
                    ("error", "UNSUPPORTED_STRUCTURE_TYPE"),
                    validate_geospatial_worldgen(structure, structure_set),
                )

    def test_geospatial_validator_delegates_profile_shape_failure(self):
        structure = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
        )
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        findings = validate_geospatial_worldgen(
            structure,
            structure_set,
            protection_profile="not-a-profile",
        )
        self.assertIn(("error", "INVALID_PROTECTION_PROFILE_SHAPE"), findings)

    def test_constructor_generated_worldgen_remains_clean(self):
        structure = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
        )
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        self.assertEqual([], validate_geospatial_worldgen(structure, structure_set))


if __name__ == "__main__":
    unittest.main()
