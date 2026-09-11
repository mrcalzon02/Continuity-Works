import unittest

from structure_capability.minecraft.worldgen import (
    BlockBox,
    ReservationIndex,
    StructureReservation,
)


class ReservationCollectionValidationTests(unittest.TestCase):
    def reservation(self, **overrides):
        values = {
            "reservation_id": "reservation-a",
            "structure_id": "test:structure",
            "assembly_id": "assembly-a",
            "family_id": "test:family",
            "box": BlockBox(0, 0, 0, 9, 9, 9),
            "piece_id": "piece-a",
            "provisional": True,
        }
        values.update(overrides)
        return StructureReservation(**values)

    def test_reservation_index_rejects_non_reservation_seed_member(self):
        valid = self.reservation()
        with self.assertRaisesRegex(
            ValueError,
            "reservations must contain only StructureReservation values",
        ):
            ReservationIndex([valid, object()])

    def test_reconcile_assembly_rejects_non_block_box_member_without_mutating_index(self):
        reservation = self.reservation()
        index = ReservationIndex([reservation])

        with self.assertRaisesRegex(
            ValueError,
            "actual_boxes must contain only BlockBox values",
        ):
            index.reconcile_assembly("assembly-a", [reservation.box, object()])

        self.assertEqual(index.snapshot(), (reservation,))

    def test_reconcile_assembly_accepts_block_boxes_and_removes_missing_provisional_piece(self):
        keep = self.reservation(reservation_id="keep", box=BlockBox(0, 0, 0, 9, 9, 9))
        remove = self.reservation(
            reservation_id="remove",
            piece_id="piece-b",
            box=BlockBox(10, 0, 0, 19, 9, 9),
        )
        index = ReservationIndex([keep, remove])

        removed = index.reconcile_assembly("assembly-a", [keep.box])

        self.assertEqual(removed, 1)
        self.assertEqual(index.snapshot(), (keep,))


if __name__ == "__main__":
    unittest.main()
