import unittest

from structure_capability.minecraft.worldgen import (
    JAVA_INT_MAX,
    MAXIMUM_JIGSAW_SIZE,
    jigsaw_structure,
    random_spread_structure_set,
    validate_geospatial_worldgen,
)


class WorldgenJigsawCodecValidationTests(unittest.TestCase):
    def setUp(self):
        self.structure_set = random_spread_structure_set(
            "continuity_works:test", 32, 8, 1
        )

    @staticmethod
    def _structure():
        return jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="continuity_works:test/start",
        )

    def test_constructor_shape_passes_validation(self):
        self.assertEqual(
            validate_geospatial_worldgen(self._structure(), self.structure_set),
            [],
        )

    def test_jigsaw_size_accepts_codec_boundaries(self):
        for size in (0, MAXIMUM_JIGSAW_SIZE):
            with self.subTest(size=size):
                structure = self._structure()
                structure["size"] = size
                self.assertNotIn(
                    ("error", "INVALID_JIGSAW_SIZE"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

    def test_jigsaw_size_rejects_out_of_range_and_wrong_type(self):
        for size in (-1, MAXIMUM_JIGSAW_SIZE + 1, True, "1", None):
            with self.subTest(size=size):
                structure = self._structure()
                structure["size"] = size
                self.assertIn(
                    ("error", "INVALID_JIGSAW_SIZE"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

    def test_use_expansion_hack_must_be_boolean(self):
        for value in (True, False):
            with self.subTest(valid=value):
                structure = self._structure()
                structure["use_expansion_hack"] = value
                self.assertNotIn(
                    ("error", "INVALID_JIGSAW_EXPANSION_HACK"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

        for value in (None, 0, 1, "false", []):
            with self.subTest(invalid=value):
                structure = self._structure()
                structure["use_expansion_hack"] = value
                self.assertIn(
                    ("error", "INVALID_JIGSAW_EXPANSION_HACK"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

    def test_spawn_overrides_must_be_mapping(self):
        structure = self._structure()
        structure["spawn_overrides"] = {}
        self.assertNotIn(
            ("error", "INVALID_SPAWN_OVERRIDES"),
            validate_geospatial_worldgen(structure, self.structure_set),
        )

        for value in (None, [], "{}", 0):
            with self.subTest(invalid=value):
                structure = self._structure()
                structure["spawn_overrides"] = value
                self.assertIn(
                    ("error", "INVALID_SPAWN_OVERRIDES"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

    def test_spawn_overrides_accept_codec_shaped_non_empty_entries(self):
        structure = self._structure()
        structure["spawn_overrides"] = {
            "monster": {
                "bounding_box": "piece",
                "spawns": [
                    {
                        "type": "minecraft:blaze",
                        "weight": 10,
                        "minCount": 2,
                        "maxCount": 3,
                    }
                ],
            },
            "ambient": {"bounding_box": "full", "spawns": []},
        }
        self.assertNotIn(
            ("error", "INVALID_SPAWN_OVERRIDES"),
            validate_geospatial_worldgen(structure, self.structure_set),
        )

    def test_spawn_overrides_reject_invalid_category_and_override_shape(self):
        invalid_values = (
            {"boss": {"bounding_box": "full", "spawns": []}},
            {"monster": []},
            {"monster": {"spawns": []}},
            {"monster": {"bounding_box": "full"}},
            {"monster": {"bounding_box": "invalid", "spawns": []}},
            {"monster": {"bounding_box": "full", "spawns": {}}},
        )
        for value in invalid_values:
            with self.subTest(invalid=value):
                structure = self._structure()
                structure["spawn_overrides"] = value
                self.assertIn(
                    ("error", "INVALID_SPAWN_OVERRIDES"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )

    def test_spawn_overrides_reject_invalid_spawner_data(self):
        valid_spawn = {
            "type": "minecraft:pillager",
            "weight": 1,
            "minCount": 1,
            "maxCount": 1,
        }
        invalid_spawns = (
            {**valid_spawn, "type": "Not A Resource Location"},
            {**valid_spawn, "weight": 0},
            {**valid_spawn, "weight": True},
            {**valid_spawn, "weight": JAVA_INT_MAX + 1},
            {**valid_spawn, "minCount": 0},
            {**valid_spawn, "minCount": True},
            {**valid_spawn, "maxCount": JAVA_INT_MAX + 1},
            {**valid_spawn, "minCount": 2, "maxCount": 1},
            {"type": "minecraft:pillager", "weight": 1, "minCount": 1},
        )
        for spawn in invalid_spawns:
            with self.subTest(invalid=spawn):
                structure = self._structure()
                structure["spawn_overrides"] = {
                    "monster": {"bounding_box": "piece", "spawns": [spawn]}
                }
                self.assertIn(
                    ("error", "INVALID_SPAWN_OVERRIDES"),
                    validate_geospatial_worldgen(structure, self.structure_set),
                )


if __name__ == "__main__":
    unittest.main()
