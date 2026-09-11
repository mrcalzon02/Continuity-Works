import copy
import unittest

from structure_capability.minecraft.worldgen import (
    jigsaw_structure,
    random_spread_structure_set,
    validate_geospatial_worldgen,
)


class RandomSpreadValidationTests(unittest.TestCase):
    def test_constructor_rejects_non_positive_or_non_integer_spacing(self):
        for spacing in (0, -1, True, 1.5, "32"):
            with self.subTest(spacing=spacing):
                with self.assertRaises(ValueError):
                    random_spread_structure_set("test:site", spacing, 0, 1)

    def test_constructor_rejects_negative_or_non_integer_separation(self):
        for separation in (-1, True, 1.5, "8"):
            with self.subTest(separation=separation):
                with self.assertRaises(ValueError):
                    random_spread_structure_set("test:site", 32, separation, 1)

    def test_constructor_still_requires_separation_below_spacing(self):
        for separation in (32, 33):
            with self.subTest(separation=separation):
                with self.assertRaises(ValueError):
                    random_spread_structure_set("test:site", 32, separation, 1)

    def test_validator_reports_invalid_values_without_throwing(self):
        structure = {"biomes": "#minecraft:is_overworld"}
        invalid_pairs = (
            (0, 0),
            (-1, 0),
            (32, -1),
            (32, 32),
            (True, 0),
            (32, True),
            ("32", 8),
            (32, "8"),
            (None, None),
        )
        for spacing, separation in invalid_pairs:
            with self.subTest(spacing=spacing, separation=separation):
                findings = validate_geospatial_worldgen(
                    structure,
                    {
                        "placement": {
                            "type": "minecraft:random_spread",
                            "spacing": spacing,
                            "separation": separation,
                        }
                    },
                )
                self.assertIn(("error", "INVALID_RANDOM_SPREAD"), findings)

    def test_validator_rejects_persisted_jigsaw_codec_fields(self):
        valid_structure = jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="test:start",
            heightmap="WORLD_SURFACE_WG",
            absolute_y=-16,
            max_distance=128,
        )
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        invalid_cases = (
            ("biomes", "Test:biomes", ("error", "INVALID_BIOME_SELECTOR")),
            ("start_pool", "Test:start", ("error", "INVALID_JIGSAW_START_POOL")),
            ("step", "surface-structures", ("error", "INVALID_GENERATION_STEP")),
            ("terrain_adaptation", "bury_it", ("error", "INVALID_TERRAIN_ADAPTATION")),
            ("max_distance_from_center", 129, ("error", "INVALID_JIGSAW_DISTANCE")),
            ("project_start_to_heightmap", "world_surface_wg", ("error", "INVALID_HEIGHTMAP")),
        )
        for field, value, expected in invalid_cases:
            with self.subTest(field=field, value=value):
                structure = copy.deepcopy(valid_structure)
                structure[field] = value
                self.assertIn(expected, validate_geospatial_worldgen(structure, structure_set))

        for invalid_height in (True, 1.5, "0", None):
            with self.subTest(start_height=invalid_height):
                structure = copy.deepcopy(valid_structure)
                structure["start_height"] = {"absolute": invalid_height}
                self.assertIn(
                    ("error", "INVALID_START_HEIGHT"),
                    validate_geospatial_worldgen(structure, structure_set),
                )

    def test_validator_rejects_persisted_structure_ids_weights_and_salt(self):
        structure = jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="test:start",
        )
        valid_set = random_spread_structure_set("test:site", 32, 8, 123)

        invalid_entries = (
            [],
            "test:site",
            [{"structure": "Test:site", "weight": 1}],
            [{"structure": "test:site", "weight": True}],
            [{"structure": "test:site", "weight": 0}],
        )
        for entries in invalid_entries:
            with self.subTest(entries=entries):
                structure_set = copy.deepcopy(valid_set)
                structure_set["structures"] = entries
                self.assertIn(
                    ("error", "INVALID_STRUCTURE_SET_ENTRIES"),
                    validate_geospatial_worldgen(structure, structure_set),
                )

        for salt in (True, 1.5, "123", None, -(2**31) - 1, 2**31):
            with self.subTest(salt=salt):
                structure_set = copy.deepcopy(valid_set)
                structure_set["placement"]["salt"] = salt
                self.assertIn(
                    ("error", "INVALID_RANDOM_SPREAD"),
                    validate_geospatial_worldgen(structure, structure_set),
                )

    def test_constructor_generated_worldgen_remains_validator_clean(self):
        structure = jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="test:start",
            step="surface_structures",
            terrain_adaptation="bury",
            heightmap="WORLD_SURFACE_WG",
            absolute_y=-16,
            max_distance=128,
        )
        structure_set = random_spread_structure_set("test:site", 32, 8, 123)
        self.assertEqual([], validate_geospatial_worldgen(structure, structure_set))

    def test_valid_random_spread_remains_clean(self):
        structure = {"biomes": "#minecraft:is_overworld"}
        structure_set = random_spread_structure_set("test:site", 32, 8, 1)
        self.assertNotIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(structure, structure_set),
        )


if __name__ == "__main__":
    unittest.main()
