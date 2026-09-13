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

    def test_reservation_index_rejects_malformed_collection_container(self):
        for reservations in (None, 7, "reservation-a", {"reservation-a": self.reservation()}):
            with self.subTest(reservations=reservations):
                with self.assertRaisesRegex(
                    ValueError,
                    "reservations must be an iterable collection",
                ):
                    ReservationIndex(reservations)

    def test_reservation_index_rejects_non_reservation_seed_member(self):
        valid = self.reservation()
        with self.assertRaisesRegex(
            ValueError,
            "reservations must contain only StructureReservation values",
        ):
            ReservationIndex([valid, object()])

    def test_reservation_index_rejects_seeded_external_exclusion_conflict(self):
        first = self.reservation()
        second = self.reservation(
            reservation_id="reservation-b",
            assembly_id="assembly-b",
            piece_id="piece-b",
            box=BlockBox(509, 0, 0, 518, 9, 9),
        )

        with self.assertRaisesRegex(ValueError, "STRUCTURE_EXCLUSION_CONFLICT"):
            ReservationIndex([first, second])

    def test_reservation_index_rejects_seeded_same_assembly_overlap(self):
        first = self.reservation()
        second = self.reservation(
            reservation_id="reservation-b",
            piece_id="piece-b",
            box=BlockBox(9, 0, 0, 18, 9, 9),
        )

        with self.assertRaisesRegex(ValueError, "SELF_JIGSAW_COLLISION"):
            ReservationIndex([first, second])

    def test_reservation_index_accepts_seeded_exact_minimum_clearance(self):
        first = self.reservation()
        second = self.reservation(
            reservation_id="reservation-b",
            assembly_id="assembly-b",
            piece_id="piece-b",
            box=BlockBox(510, 0, 0, 519, 9, 9),
        )

        self.assertEqual(ReservationIndex([first, second]).snapshot(), (first, second))

    def test_reconcile_assembly_rejects_malformed_collection_without_mutating_index(self):
        reservation = self.reservation()
        for actual_boxes in (None, 7, "box", {"box": reservation.box}):
            with self.subTest(actual_boxes=actual_boxes):
                index = ReservationIndex([reservation])
                with self.assertRaisesRegex(
                    ValueError,
                    "actual_boxes must be an iterable collection",
                ):
                    index.reconcile_assembly("assembly-a", actual_boxes)
                self.assertEqual(index.snapshot(), (reservation,))

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
