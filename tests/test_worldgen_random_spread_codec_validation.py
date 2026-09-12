import unittest

from structure_capability.minecraft.worldgen import (
    jigsaw_structure,
    random_spread_structure_set,
    validate_geospatial_worldgen,
)


class WorldgenRandomSpreadCodecValidationTests(unittest.TestCase):
    @staticmethod
    def _structure():
        return jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="continuity_works:test/start",
        )

    @staticmethod
    def _structure_set():
        return random_spread_structure_set("continuity_works:test", 32, 8, 1)

    def test_omitted_spread_type_preserves_default_valid_shape(self):
        structure_set = self._structure_set()
        self.assertNotIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(self._structure(), structure_set),
        )

    def test_codec_spread_types_are_accepted(self):
        for spread_type in ("linear", "triangular"):
            with self.subTest(spread_type=spread_type):
                structure_set = self._structure_set()
                structure_set["placement"]["spread_type"] = spread_type
                self.assertNotIn(
                    ("error", "INVALID_RANDOM_SPREAD"),
                    validate_geospatial_worldgen(self._structure(), structure_set),
                )

    def test_invalid_spread_type_fails_closed(self):
        for spread_type in ("uniform", "LINEAR", "", None, 0, True, []):
            with self.subTest(spread_type=spread_type):
                structure_set = self._structure_set()
                structure_set["placement"]["spread_type"] = spread_type
                self.assertIn(
                    ("error", "INVALID_RANDOM_SPREAD"),
                    validate_geospatial_worldgen(self._structure(), structure_set),
                )


if __name__ == "__main__":
    unittest.main()
