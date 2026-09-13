import unittest

from structure_capability.minecraft.worldgen import (
    BlockBox,
    ReservationIndex,
    StructureReservation,
)


class ReservationIdentityValidationTests(unittest.TestCase):
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

    def test_blank_reservation_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation(reservation_id="   ")

    def test_invalid_structure_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation(structure_id="Invalid Structure")

    def test_blank_assembly_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation(assembly_id="")

    def test_blank_family_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation(family_id="\t")

    def test_blank_optional_piece_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.reservation(piece_id=" ")

    def test_piece_id_may_be_absent(self):
        reservation = self.reservation(piece_id=None)
        self.assertIsNone(reservation.piece_id)

    def test_reservation_index_rejects_duplicate_seed_ids(self):
        first = self.reservation(reservation_id="duplicate-id")
        second = self.reservation(
            reservation_id="duplicate-id",
            assembly_id="assembly-b",
            box=BlockBox(1000, 0, 0, 1009, 9, 9),
        )
        with self.assertRaises(ValueError):
            ReservationIndex([first, second])

    def test_reservation_index_accepts_committed_seed_state(self):
        committed = self.reservation(provisional=False)

        self.assertEqual(ReservationIndex([committed]).snapshot(), (committed,))

    def test_try_reserve_rejects_duplicate_id_without_replacing_existing(self):
        existing = self.reservation(reservation_id="duplicate-id")
        index = ReservationIndex([existing])
        candidate = self.reservation(
            reservation_id="duplicate-id",
            assembly_id="assembly-b",
            box=BlockBox(1000, 0, 0, 1009, 9, 9),
        )

        conflict = index.try_reserve(candidate)

        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.code, "RESERVATION_ID_CONFLICT")
        self.assertIs(conflict.existing, existing)
        self.assertEqual(index.snapshot(), (existing,))

    def test_duplicate_id_takes_precedence_over_same_assembly_spacing_exemption(self):
        existing = self.reservation(reservation_id="duplicate-id", assembly_id="assembly-a")
        index = ReservationIndex([existing])
        candidate = self.reservation(
            reservation_id="duplicate-id",
            assembly_id="assembly-a",
            box=BlockBox(10, 0, 0, 19, 9, 9),
            piece_id="piece-b",
        )

        conflict = index.conflict_for(candidate)

        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.code, "RESERVATION_ID_CONFLICT")

    def test_conflict_for_rejects_non_reservation_candidate_explicitly(self):
        existing = self.reservation(reservation_id="existing")
        index = ReservationIndex([existing])

        with self.assertRaisesRegex(ValueError, "candidate must be a StructureReservation"):
            index.conflict_for({"reservation_id": "fake"})

        self.assertEqual(index.snapshot(), (existing,))

    def test_try_reserve_rejects_non_reservation_candidate_without_mutation(self):
        existing = self.reservation(reservation_id="existing")
        index = ReservationIndex([existing])

        with self.assertRaisesRegex(ValueError, "candidate must be a StructureReservation"):
            index.try_reserve(object())

        self.assertEqual(index.snapshot(), (existing,))

    def test_try_reserve_rejects_committed_candidate_without_mutation(self):
        existing = self.reservation(reservation_id="existing")
        index = ReservationIndex([existing])
        committed = self.reservation(
            reservation_id="committed-candidate",
            assembly_id="assembly-b",
            box=BlockBox(1000, 0, 0, 1009, 9, 9),
            provisional=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "try_reserve requires a provisional reservation",
        ):
            index.try_reserve(committed)

        self.assertEqual(index.snapshot(), (existing,))

    def test_reserve_piece_rejects_blank_assembly_before_spacing_check(self):
        index = ReservationIndex([
            self.reservation(
                reservation_id="existing",
                assembly_id="assembly-a",
                piece_id=None,
            )
        ])
        with self.assertRaises(ValueError):
            index.reserve_piece(
                structure_id="test:structure",
                assembly_id=" ",
                family_id="test:family",
                box=BlockBox(10, 0, 0, 19, 9, 9),
            )
        self.assertEqual(len(index.snapshot()), 1)

    def test_valid_same_assembly_pieces_retain_close_connection_exemption(self):
        index = ReservationIndex([
            self.reservation(
                reservation_id="existing",
                assembly_id="assembly-a",
                piece_id="piece-a",
            )
        ])
        reserved, conflict = index.reserve_piece(
            structure_id="test:structure",
            assembly_id="assembly-a",
            family_id="test:family",
            box=BlockBox(10, 0, 0, 19, 9, 9),
            piece_id="piece-b",
        )
        self.assertIsNone(conflict)
        self.assertIsNotNone(reserved)

    def test_lifecycle_operations_reject_blank_assembly_identity(self):
        index = ReservationIndex()
        for operation in (
            lambda: index.commit_assembly(" "),
            lambda: index.release_assembly(""),
            lambda: index.reconcile_assembly("\t", []),
        ):
            with self.assertRaises(ValueError):
                operation()


if __name__ == "__main__":
    unittest.main()
