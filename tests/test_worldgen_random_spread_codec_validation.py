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

    def _assert_random_spread_valid(self, placement_updates):
        structure_set = self._structure_set()
        structure_set["placement"].update(placement_updates)
        self.assertNotIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(self._structure(), structure_set),
        )

    def _assert_random_spread_invalid(self, placement_updates):
        structure_set = self._structure_set()
        structure_set["placement"].update(placement_updates)
        self.assertIn(
            ("error", "INVALID_RANDOM_SPREAD"),
            validate_geospatial_worldgen(self._structure(), structure_set),
        )

    def test_omitted_optional_fields_preserve_default_valid_shape(self):
        self._assert_random_spread_valid({})

    def test_codec_spread_types_are_accepted(self):
        for spread_type in ("linear", "triangular"):
            with self.subTest(spread_type=spread_type):
                self._assert_random_spread_valid({"spread_type": spread_type})

    def test_invalid_spread_type_fails_closed(self):
        for spread_type in ("uniform", "LINEAR", "", None, 0, True, []):
            with self.subTest(spread_type=spread_type):
                self._assert_random_spread_invalid({"spread_type": spread_type})

    def test_frequency_codec_bounds_are_enforced(self):
        for frequency in (0.0, 0.25, 1.0, 1):
            with self.subTest(frequency=frequency):
                self._assert_random_spread_valid({"frequency": frequency})
        for frequency in (-0.01, 1.01, None, "0.5", True, []):
            with self.subTest(frequency=frequency):
                self._assert_random_spread_invalid({"frequency": frequency})

    def test_frequency_reduction_method_codec_values_are_enforced(self):
        valid_methods = (
            "default",
            "legacy_type_1",
            "legacy_type_2",
            "legacy_type_3",
        )
        for method in valid_methods:
            with self.subTest(method=method):
                self._assert_random_spread_valid(
                    {"frequency_reduction_method": method}
                )
        for method in ("legacy", "DEFAULT", "", None, 0, True, []):
            with self.subTest(method=method):
                self._assert_random_spread_invalid(
                    {"frequency_reduction_method": method}
                )

    def test_exclusion_zone_codec_shape_and_chunk_bounds_are_enforced(self):
        for chunk_count in (1, 10, 16):
            with self.subTest(chunk_count=chunk_count):
                self._assert_random_spread_valid(
                    {
                        "exclusion_zone": {
                            "other_set": "minecraft:villages",
                            "chunk_count": chunk_count,
                        }
                    }
                )

        invalid_zones = (
            None,
            "minecraft:villages",
            [],
            {},
            {"other_set": "minecraft:villages"},
            {"chunk_count": 10},
            {"other_set": "Minecraft:Villages", "chunk_count": 10},
            {"other_set": "minecraft:villages", "chunk_count": 0},
            {"other_set": "minecraft:villages", "chunk_count": 17},
            {"other_set": "minecraft:villages", "chunk_count": True},
        )
        for zone in invalid_zones[1:]:
            with self.subTest(zone=zone):
                self._assert_random_spread_invalid({"exclusion_zone": zone})

        # Explicit null is equivalent to the optional field being absent.
        self._assert_random_spread_valid({"exclusion_zone": None})


if __name__ == "__main__":
    unittest.main()
