import unittest

from structure_capability.minecraft.worldgen import (
    jigsaw_structure,
    random_spread_structure_set,
    structure_protection_profile,
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

    def test_profile_builder_rejects_invalid_minecraft_selectors(self):
        invalid_cases = (
            {"structures": ["Test:Uppercase"]},
            {"structures": ["test:bad space"]},
            {"tags": ["#test:tag"]},
            {"tags": ["test:bad tag"]},
            {"namespaces": ["test:path"]},
            {"namespaces": ["test/path"]},
            {"namespaces": ["Uppercase"]},
        )
        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    structure_protection_profile(**kwargs)

    def test_direct_profile_validator_rejects_invalid_minecraft_selectors(self):
        valid = structure_protection_profile(
            structures=["test:site"],
            tags=["test:protected"],
            namespaces=["test", "other_mod"],
        )
        self.assertEqual([], validate_structure_protection_profile(valid))

        invalid_profiles = (
            {**valid, "selectors": {"structures": ["Test:site"]}},
            {**valid, "selectors": {"tags": ["#test:protected"]}},
            {**valid, "selectors": {"namespaces": ["test:path"]}},
            {**valid, "selectors": {"namespaces": ["bad namespace"]}},
        )
        for profile in invalid_profiles:
            with self.subTest(profile=profile):
                self.assertIn(
                    ("error", "INVALID_PROTECTION_SELECTORS"),
                    validate_structure_protection_profile(profile),
                )

    def test_constructor_generated_worldgen_remains_clean(self):
        structure = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
        )
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        self.assertEqual([], validate_geospatial_worldgen(structure, structure_set))


if __name__ == "__main__":
    unittest.main()
