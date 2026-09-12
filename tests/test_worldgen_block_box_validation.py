import unittest

from structure_capability.minecraft.worldgen import BlockBox


class BlockBoxOperandValidationTests(unittest.TestCase):
    def setUp(self):
        self.box = BlockBox(0, 0, 0, 9, 9, 9)

    def test_overlaps_volume_rejects_non_block_box_operand(self):
        with self.assertRaisesRegex(ValueError, "other must be a BlockBox"):
            self.box.overlaps_volume({"min_x": 0})

    def test_horizontal_gap_rejects_non_block_box_operand(self):
        with self.assertRaisesRegex(ValueError, "other must be a BlockBox"):
            self.box.horizontal_gap(object())

    def test_face_adjacent_boxes_remain_non_overlapping(self):
        adjacent = BlockBox(10, 0, 0, 19, 9, 9)
        self.assertFalse(self.box.overlaps_volume(adjacent))
        self.assertEqual(self.box.horizontal_gap(adjacent), 0.0)

    def test_padding_preserves_existing_collision_semantics(self):
        adjacent = BlockBox(10, 0, 0, 19, 9, 9)
        self.assertTrue(self.box.overlaps_volume(adjacent, padding=1))

    def test_separated_boxes_preserve_horizontal_gap(self):
        separated = BlockBox(510, 0, 0, 519, 9, 9)
        self.assertEqual(self.box.horizontal_gap(separated), 500.0)


if __name__ == "__main__":
    unittest.main()
