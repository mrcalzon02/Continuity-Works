import unittest

from structure_capability.minecraft.worldgen import (
    BlockBox,
    ReservationIndex,
    StructureReservation,
    jigsaw_structure,
    random_spread_structure_set,
    structure_protection_profile,
    validate_structure_protection_profile,
)


class WorldgenGeometryValidationTests(unittest.TestCase):
    def test_block_box_rejects_non_integer_coordinates(self):
        invalid_values = (True, False, 1.5, "0", None)
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    BlockBox(value, 0, 0, 1, 1, 1)

    def test_block_box_still_rejects_inverted_bounds(self):
        with self.assertRaises(ValueError):
            BlockBox(2, 0, 0, 1, 1, 1)

    def test_collision_padding_must_be_non_negative_integer(self):
        candidate = BlockBox(0, 0, 0, 1, 1, 1)
        other = BlockBox(3, 0, 0, 4, 1, 1)
        for padding in (-1, True, 1.5, "1"):
            with self.subTest(padding=padding):
                with self.assertRaises(ValueError):
                    candidate.overlaps_volume(other, padding=padding)

    def test_jigsaw_structure_rejects_non_integer_absolute_height(self):
        for absolute_y in (True, 0.5, "0", None):
            with self.subTest(absolute_y=absolute_y):
                with self.assertRaises(ValueError):
                    jigsaw_structure(
                        biome_selector="#test:biomes",
                        start_pool="test:start",
                        absolute_y=absolute_y,
                    )

    def test_jigsaw_structure_enforces_minecraft_distance_codec_range(self):
        for max_distance in (True, 0, -1, 129, 80.0, "80", None):
            with self.subTest(max_distance=max_distance):
                with self.assertRaises(ValueError):
                    jigsaw_structure(
                        biome_selector="#test:biomes",
                        start_pool="test:start",
                        max_distance=max_distance,
                    )

        minimum = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
            max_distance=1,
        )
        maximum = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
            max_distance=128,
        )
        self.assertEqual(1, minimum["max_distance_from_center"])
        self.assertEqual(128, maximum["max_distance_from_center"])

    def test_jigsaw_structure_rejects_invalid_resource_locations(self):
        invalid_calls = (
            {"biome_selector": "", "start_pool": "test:start"},
            {"biome_selector": "#", "start_pool": "test:start"},
            {"biome_selector": "#Test:biomes", "start_pool": "test:start"},
            {"biome_selector": "#test:biomes", "start_pool": ""},
            {"biome_selector": "#test:biomes", "start_pool": "Test:start"},
            {"biome_selector": 42, "start_pool": "test:start"},
        )
        for kwargs in invalid_calls:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    jigsaw_structure(**kwargs)

    def test_jigsaw_structure_rejects_invalid_codec_enums(self):
        invalid_calls = (
            {"step": ""},
            {"step": "surface-structures"},
            {"terrain_adaptation": ""},
            {"terrain_adaptation": "bury_it"},
            {"heightmap": ""},
            {"heightmap": "WORLD_SURFACE_WG"},
        )
        for kwargs in invalid_calls:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    jigsaw_structure(
                        biome_selector="#test:biomes",
                        start_pool="test:start",
                        **kwargs,
                    )

    def test_jigsaw_structure_accepts_known_codec_values(self):
        structure = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
            step="surface_structures",
            terrain_adaptation="bury",
            heightmap="world_surface_wg",
        )
        self.assertEqual("surface_structures", structure["step"])
        self.assertEqual("bury", structure["terrain_adaptation"])
        self.assertEqual("world_surface_wg", structure["project_start_to_heightmap"])

    def test_random_spread_rejects_invalid_structure_id_and_salt(self):
        for structure_id in ("", "Test:site", "test:bad path", 42, None):
            with self.subTest(structure_id=structure_id):
                with self.assertRaises(ValueError):
                    random_spread_structure_set(structure_id, 32, 8, 123)

        invalid_salts = (True, 1.5, "123", None, -(2**31) - 1, 2**31)
        for salt in invalid_salts:
            with self.subTest(salt=salt):
                with self.assertRaises(ValueError):
                    random_spread_structure_set("test:site", 32, 8, salt)

        minimum = random_spread_structure_set("test:site", 32, 8, -(2**31))
        maximum = random_spread_structure_set("test:site", 32, 8, 2**31 - 1)
        self.assertEqual(-(2**31), minimum["placement"]["salt"])
        self.assertEqual(2**31 - 1, maximum["placement"]["salt"])

    def test_reservation_rejects_non_integer_or_below_minimum_radius(self):
        box = BlockBox(0, 0, 0, 1, 1, 1)
        for radius in (True, 499, 500.0, "500"):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    StructureReservation(
                        reservation_id="r1",
                        structure_id="test:site",
                        assembly_id="a1",
                        family_id="f1",
                        box=box,
                        exclusion_radius=radius,
                    )

        reservation = StructureReservation(
            reservation_id="r2",
            structure_id="test:site",
            assembly_id="a2",
            family_id="f2",
            box=box,
            exclusion_radius=500,
        )
        self.assertEqual(500, reservation.exclusion_radius)

    def test_reservation_index_rejects_invalid_self_collision_padding(self):
        index = ReservationIndex()
        reservation = StructureReservation(
            reservation_id="r1",
            structure_id="test:site",
            assembly_id="a1",
            family_id="f1",
            box=BlockBox(0, 0, 0, 1, 1, 1),
        )
        for padding in (-1, True, 1.5, "1"):
            with self.subTest(padding=padding):
                with self.assertRaises(ValueError):
                    index.try_reserve(reservation, self_collision_padding=padding)

    def test_profile_constructor_rejects_invalid_exclusion_radii(self):
        for radius in (True, 499, 500.0, "500"):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    structure_protection_profile(
                        structures=("test:site",),
                        exclusion_radius=radius,
                    )

        for radius in (True, 499, 500.0, "500"):
            with self.subTest(piece_radius=radius):
                with self.assertRaises(ValueError):
                    structure_protection_profile(
                        structures=("test:site",),
                        jigsaw_piece_exclusion_radius=radius,
                    )

    def test_profile_constructor_rejects_malformed_selector_and_control_values(self):
        invalid_calls = (
            {"structures": "test:site"},
            {"structures": ("test:site", "")},
            {"structures": ("test:site", 42)},
            {"structures": ("test:site",), "protect_jigsaw_pieces": 1},
            {"structures": ("test:site",), "protect_jigsaw_pieces": False},
            {"structures": ("test:site",), "priority": True},
            {"structures": ("test:site",), "priority": 1.5},
            {"structures": ("test:site",), "family": ""},
        )
        for kwargs in invalid_calls:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    structure_protection_profile(**kwargs)

    def test_profile_validator_rejects_boolean_and_non_integer_radii(self):
        base = {
            "selectors": {"structures": ["test:site"]},
            "protect_jigsaw_pieces": True,
        }
        for radius in (True, 500.0, "500"):
            with self.subTest(radius=radius):
                findings = validate_structure_protection_profile(
                    {
                        **base,
                        "exclusion_radius": radius,
                        "jigsaw_piece_exclusion_radius": 500,
                    }
                )
                self.assertIn(
                    ("error", "STRUCTURE_EXCLUSION_RADIUS_BELOW_MINIMUM"),
                    findings,
                )

        for radius in (True, 500.0, "500"):
            with self.subTest(piece_radius=radius):
                findings = validate_structure_protection_profile(
                    {
                        **base,
                        "exclusion_radius": 500,
                        "jigsaw_piece_exclusion_radius": radius,
                    }
                )
                self.assertIn(
                    ("error", "JIGSAW_PIECE_EXCLUSION_RADIUS_BELOW_MINIMUM"),
                    findings,
                )

    def test_profile_validator_rejects_malformed_selector_and_control_shape(self):
        valid_base = {
            "selectors": {"structures": ["test:site"]},
            "exclusion_radius": 500,
            "jigsaw_piece_exclusion_radius": 500,
            "protect_jigsaw_pieces": True,
            "priority": 0,
        }
        invalid_selector_profiles = (
            {**valid_base, "selectors": "test:site"},
            {**valid_base, "selectors": {"structures": "test:site"}},
            {**valid_base, "selectors": {"structures": [""]}},
            {**valid_base, "selectors": {"structures": [42]}},
        )
        for profile in invalid_selector_profiles:
            with self.subTest(profile=profile):
                self.assertIn(
                    ("error", "INVALID_PROTECTION_SELECTORS"),
                    validate_structure_protection_profile(profile),
                )

        self.assertIn(
            ("error", "JIGSAW_PIECE_PROTECTION_CANNOT_BE_DISABLED"),
            validate_structure_protection_profile(
                {**valid_base, "protect_jigsaw_pieces": 1}
            ),
        )
        self.assertIn(
            ("error", "INVALID_PROTECTION_PRIORITY"),
            validate_structure_protection_profile({**valid_base, "priority": True}),
        )
        self.assertIn(
            ("error", "INVALID_PROTECTION_FAMILY"),
            validate_structure_protection_profile({**valid_base, "family": ""}),
        )

    def test_valid_geometry_jigsaw_and_profile_remain_accepted(self):
        box = BlockBox(-10, 0, -10, 10, 20, 10)
        structure = jigsaw_structure(
            biome_selector="#test:biomes",
            start_pool="test:start",
            absolute_y=-32,
            max_distance=128,
        )
        profile = structure_protection_profile(
            structures=("test:site",),
            exclusion_radius=500,
            jigsaw_piece_exclusion_radius=500,
            family="test_family",
            priority=1,
        )
        self.assertEqual((-10, 0, -10, 10, 20, 10), box.key)
        self.assertEqual(-32, structure["start_height"]["absolute"])
        self.assertEqual(128, structure["max_distance_from_center"])
        self.assertEqual([], validate_structure_protection_profile(profile))


if __name__ == "__main__":
    unittest.main()
