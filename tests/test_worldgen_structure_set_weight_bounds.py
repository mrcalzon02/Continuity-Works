import copy
import unittest

from structure_capability.minecraft.worldgen import (
    JAVA_INT_MAX,
    jigsaw_structure,
    random_spread_structure_set,
    validate_geospatial_worldgen,
)


class StructureSetWeightBoundsTests(unittest.TestCase):
    def setUp(self):
        self.structure = jigsaw_structure(
            biome_selector="#minecraft:is_overworld",
            start_pool="test:start",
        )
        self.structure_set = random_spread_structure_set("test:site", 32, 8, 123)

    def test_java_int_max_weight_remains_valid(self):
        structure_set = copy.deepcopy(self.structure_set)
        structure_set["structures"][0]["weight"] = JAVA_INT_MAX
        self.assertNotIn(
            ("error", "INVALID_STRUCTURE_SET_ENTRIES"),
            validate_geospatial_worldgen(self.structure, structure_set),
        )

    def test_weight_above_java_int_max_fails_closed(self):
        structure_set = copy.deepcopy(self.structure_set)
        structure_set["structures"][0]["weight"] = JAVA_INT_MAX + 1
        self.assertIn(
            ("error", "INVALID_STRUCTURE_SET_ENTRIES"),
            validate_geospatial_worldgen(self.structure, structure_set),
        )


if __name__ == "__main__":
    unittest.main()
