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
