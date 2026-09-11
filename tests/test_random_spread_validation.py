import unittest

from structure_capability.minecraft.worldgen import (
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

    def test_valid_random_spread_remains_clean(self):
        structure = {"biomes": "#minecraft:is_overworld"}
        structure_set = random_spread_structure_set("test:site", 32, 8, 1)
        self.assertNotIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(structure, structure_set),
        )


if __name__ == "__main__":
    unittest.main()
