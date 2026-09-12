from __future__ import annotations

from dataclasses import dataclass, replace
from math import hypot
import re
from threading import RLock
from typing import Iterable, Mapping, Sequence
from uuid import uuid4


MINIMUM_STRUCTURE_EXCLUSION_RADIUS = 500
DEFAULT_STRUCTURE_EXCLUSION_RADIUS = MINIMUM_STRUCTURE_EXCLUSION_RADIUS
MAXIMUM_JIGSAW_DISTANCE_FROM_CENTER = 128
MAXIMUM_JIGSAW_SIZE = 20
MAXIMUM_RANDOM_SPREAD_DISTANCE = 4096
JAVA_INT_MIN = -(2**31)
JAVA_INT_MAX = 2**31 - 1
RESOURCE_LOCATION_PATTERN = re.compile(r"^(?:[a-z0-9_.-]+:)?[a-z0-9/._-]+$")
NAMESPACE_PATTERN = re.compile(r"^[a-z0-9_.-]+$")
GENERATION_STEPS = frozenset({
    "raw_generation",
    "lakes",
    "local_modifications",
    "underground_structures",
    "surface_structures",
    "strongholds",
    "underground_ores",
    "underground_decoration",
    "fluid_springs",
    "vegetal_decoration",
    "top_layer_modification",
})
TERRAIN_ADAPTATIONS = frozenset({"none", "bury", "beard_thin", "beard_box", "encapsulate"})
HEIGHTMAP_TYPES = frozenset({
    "WORLD_SURFACE_WG",
    "WORLD_SURFACE",
    "OCEAN_FLOOR_WG",
    "OCEAN_FLOOR",
    "MOTION_BLOCKING",
    "MOTION_BLOCKING_NO_LEAVES",
})
MOB_CATEGORIES = frozenset({
    "monster",
    "creature",
    "ambient",
    "axolotls",
    "underground_water_creature",
    "water_creature",
    "water_ambient",
    "misc",
})
SPAWN_OVERRIDE_BOUNDING_BOX_TYPES = frozenset({"piece", "full"})
RANDOM_SPREAD_TYPES = frozenset({"linear", "triangular"})
FREQUENCY_REDUCTION_METHODS = frozenset({
    "default",
    "legacy_type_1",
    "legacy_type_2",
    "legacy_type_3",
})


def _require_non_negative_int(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _require_java_int(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not JAVA_INT_MIN <= value <= JAVA_INT_MAX:
        raise ValueError(f"{name} must fit a signed 32-bit Java integer")
    return value


def _require_resource_location(value, *, name: str, allow_tag: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a Minecraft resource location")
    candidate = value
    if allow_tag and candidate.startswith("#"):
        candidate = candidate[1:]
    if not candidate or RESOURCE_LOCATION_PATTERN.fullmatch(candidate) is None:
        raise ValueError(f"{name} must be a valid Minecraft resource location")
    return value


def _require_namespace(value, *, name: str) -> str:
    if not isinstance(value, str) or NAMESPACE_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a valid Minecraft namespace")
    return value


def _require_non_empty_identity(value, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _require_iterable_collection(value, *, name: str):
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
        raise ValueError(f"{name} must be an iterable collection")
    return value


def _require_enum(value, allowed: frozenset[str], *, name: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{name} must be one of: {', '.join(sorted(allowed))}")
    return value


def _require_block_coordinate(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer block coordinate")
    if not JAVA_INT_MIN <= value <= JAVA_INT_MAX:
        raise ValueError(f"{name} must fit a signed 32-bit Java integer")
    return value


def _require_exclusion_radius(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
        raise ValueError(
            f"{name} must be >= {MINIMUM_STRUCTURE_EXCLUSION_RADIUS} blocks"
        )
    if value > JAVA_INT_MAX:
        raise ValueError(f"{name} must fit a signed 32-bit Java integer")
    return value


def _require_jigsaw_distance(value, *, name: str = "max distance from center") -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not 1 <= value <= MAXIMUM_JIGSAW_DISTANCE_FROM_CENTER:
        raise ValueError(
            f"{name} must be between 1 and {MAXIMUM_JIGSAW_DISTANCE_FROM_CENTER} blocks"
        )
    return value


def _require_jigsaw_size(value, *, name: str = "jigsaw size") -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not 0 <= value <= MAXIMUM_JIGSAW_SIZE:
        raise ValueError(f"{name} must be between 0 and {MAXIMUM_JIGSAW_SIZE}")
    return value


def _spawn_overrides_are_valid(value) -> bool:
    if not isinstance(value, Mapping):
        return False
    for category, override in value.items():
        if category not in MOB_CATEGORIES or not isinstance(override, Mapping):
            return False
        if override.get("bounding_box") not in SPAWN_OVERRIDE_BOUNDING_BOX_TYPES:
            return False
        spawns = override.get("spawns")
        if isinstance(spawns, (str, bytes)) or not isinstance(spawns, Sequence):
            return False
        for spawn in spawns:
            if not isinstance(spawn, Mapping):
                return False
            try:
                _require_resource_location(spawn.get("type"), name="spawn entity type")
            except ValueError:
                return False
            for field in ("weight", "minCount", "maxCount"):
                field_value = spawn.get(field)
                if (
                    isinstance(field_value, bool)
                    or not isinstance(field_value, int)
                    or field_value <= 0
                    or field_value > JAVA_INT_MAX
                ):
                    return False
            if spawn["maxCount"] < spawn["minCount"]:
                return False
    return True


def _normalize_selector_values(values, *, name: str, validator=None) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(f"{name} must be a sequence of non-empty strings")
    normalized = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only non-empty strings")
        if validator is not None:
            validator(value, name=f"{name} selector")
        normalized.append(value)
    return normalized


def jigsaw_structure(*, biome_selector, start_pool, step="surface_structures",
                     terrain_adaptation="bury", heightmap=None, absolute_y=0,
                     max_distance=80):
    _require_resource_location(biome_selector, name="biome selector", allow_tag=True)
    _require_resource_location(start_pool, name="start pool")
    _require_enum(step, GENERATION_STEPS, name="generation step")
    _require_enum(terrain_adaptation, TERRAIN_ADAPTATIONS, name="terrain adaptation")
    if heightmap is not None:
        _require_enum(heightmap, HEIGHTMAP_TYPES, name="heightmap")
    _require_block_coordinate(absolute_y, name="absolute y")
    _require_jigsaw_distance(max_distance)
    out = {
        "type": "minecraft:jigsaw",
        "biomes": biome_selector,
        "step": step,
        "spawn_overrides": {},
        "terrain_adaptation": terrain_adaptation,
        "start_pool": start_pool,
        "size": 1,
        "start_height": {"absolute": absolute_y},
        "max_distance_from_center": max_distance,
        "use_expansion_hack": False,
    }
    if heightmap is not None:
        out["project_start_to_heightmap"] = heightmap
    return out


def random_spread_structure_set(structure_id, spacing, separation, salt):
    _require_resource_location(structure_id, name="structure id")
    if isinstance(spacing, bool) or not isinstance(spacing, int) or spacing <= 0:
        raise ValueError("spacing must be a positive integer")
    if spacing > MAXIMUM_RANDOM_SPREAD_DISTANCE:
        raise ValueError(f"spacing must be <= {MAXIMUM_RANDOM_SPREAD_DISTANCE}")
    if isinstance(separation, bool) or not isinstance(separation, int) or separation < 0:
        raise ValueError("separation must be a non-negative integer")
    if separation > MAXIMUM_RANDOM_SPREAD_DISTANCE:
        raise ValueError(f"separation must be <= {MAXIMUM_RANDOM_SPREAD_DISTANCE}")
    if separation >= spacing:
        raise ValueError("separation must be lower than spacing")
    _require_java_int(salt, name="salt")
    return {
        "structures": [{"structure": structure_id, "weight": 1}],
        "placement": {
            "type": "minecraft:random_spread",
            "spacing": spacing,
            "separation": separation,
            "salt": salt,
        },
    }


@dataclass(frozen=True)
class BlockBox:
    """Inclusive Minecraft block bounding box used by the spawn-protection gate."""

    min_x: int
    min_y: int
    min_z: int
    max_x: int
    max_y: int
    max_z: int

    def __post_init__(self):
        for name in ("min_x", "min_y", "min_z", "max_x", "max_y", "max_z"):
            _require_block_coordinate(getattr(self, name), name=name)
        if self.min_x > self.max_x or self.min_y > self.max_y or self.min_z > self.max_z:
            raise ValueError("invalid block box")

    @property
    def key(self) -> tuple[int, int, int, int, int, int]:
        return (self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)

    def overlaps_volume(self, other: "BlockBox", *, padding: int = 0) -> bool:
        """True only for occupied-volume overlap; face adjacency is allowed."""
        if not isinstance(other, BlockBox):
            raise ValueError("other must be a BlockBox")
        _require_non_negative_int(padding, name="padding")
        # Convert inclusive Minecraft boxes to half-open boxes. Padding expands
        # this candidate only; ordinary face adjacency remains legal at padding=0.
        return (
            self.min_x - padding < other.max_x + 1
            and self.max_x + 1 + padding > other.min_x
            and self.min_y - padding < other.max_y + 1
            and self.max_y + 1 + padding > other.min_y
            and self.min_z - padding < other.max_z + 1
            and self.max_z + 1 + padding > other.min_z
        )

    def horizontal_gap(self, other: "BlockBox") -> float:
        """Euclidean edge-to-edge X/Z gap in blocks between half-open footprints."""
        if not isinstance(other, BlockBox):
            raise ValueError("other must be a BlockBox")
        self_x1, self_x2 = self.min_x, self.max_x + 1
        other_x1, other_x2 = other.min_x, other.max_x + 1
        self_z1, self_z2 = self.min_z, self.max_z + 1
        other_z1, other_z2 = other.min_z, other.max_z + 1

        dx = max(0, other_x1 - self_x2, self_x1 - other_x2)
        dz = max(0, other_z1 - self_z2, self_z1 - other_z2)
        return hypot(dx, dz)


@dataclass(frozen=True)
class StructureReservation:
    reservation_id: str
    structure_id: str
    assembly_id: str
    family_id: str
    box: BlockBox
    exclusion_radius: int = DEFAULT_STRUCTURE_EXCLUSION_RADIUS
    piece_id: str | None = None
    provisional: bool = True

    def __post_init__(self):
        _require_non_empty_identity(self.reservation_id, name="reservation id")
        _require_resource_location(self.structure_id, name="structure id")
        _require_non_empty_identity(self.assembly_id, name="assembly id")
        _require_non_empty_identity(self.family_id, name="family id")
        if not isinstance(self.box, BlockBox):
            raise ValueError("box must be a BlockBox")
        if self.piece_id is not None:
            _require_non_empty_identity(self.piece_id, name="piece id")
        if not isinstance(self.provisional, bool):
            raise ValueError("provisional must be a boolean")
        _require_exclusion_radius(self.exclusion_radius, name="exclusion radius")


@dataclass(frozen=True)
class ReservationConflict:
    code: str
    candidate: StructureReservation
    existing: StructureReservation
    horizontal_gap: float
    required_gap: int


class ReservationIndex:
    """Atomic in-memory reservation index shared by structure-generation attempts.

    Same-assembly pieces ignore each other's 500+ block *external* exclusion radius,
    but they are still forbidden from occupying the same block volume. Separate
    assemblies never receive a family-only overlap exemption.
    """

    def __init__(self, reservations: Iterable[StructureReservation] = ()):  # noqa: B006
        self._lock = RLock()
        self._reservations: dict[str, StructureReservation] = {}
        _require_iterable_collection(reservations, name="reservations")
        for reservation in reservations:
            if not isinstance(reservation, StructureReservation):
                raise ValueError("reservations must contain only StructureReservation values")
            if reservation.reservation_id in self._reservations:
                raise ValueError(f"duplicate reservation id: {reservation.reservation_id}")
            self._reservations[reservation.reservation_id] = reservation

    def snapshot(self) -> tuple[StructureReservation, ...]:
        with self._lock:
            return tuple(self._reservations.values())

    def conflict_for(
        self,
        candidate: StructureReservation,
        *,
        self_collision_padding: int = 0,
    ) -> ReservationConflict | None:
        with self._lock:
            return self._conflict_for_unlocked(candidate, self_collision_padding=self_collision_padding)

    def _conflict_for_unlocked(
        self,
        candidate: StructureReservation,
        *,
        self_collision_padding: int,
    ) -> ReservationConflict | None:
        if not isinstance(candidate, StructureReservation):
            raise ValueError("candidate must be a StructureReservation")
        _require_non_negative_int(self_collision_padding, name="self collision padding")
        for existing in self._reservations.values():
            if existing.reservation_id == candidate.reservation_id:
                return ReservationConflict(
                    code="RESERVATION_ID_CONFLICT",
                    candidate=candidate,
                    existing=existing,
                    horizontal_gap=0.0,
                    required_gap=0,
                )
            if existing.assembly_id == candidate.assembly_id:
                if candidate.box.overlaps_volume(existing.box, padding=self_collision_padding):
                    return ReservationConflict(
                        code="SELF_JIGSAW_COLLISION",
                        candidate=candidate,
                        existing=existing,
                        horizontal_gap=0.0,
                        required_gap=0,
                    )
                # Same assembly may connect tightly. Family equality alone never grants
                # this exception: the assembly identity must match.
                continue

            gap = candidate.box.horizontal_gap(existing.box)
            required_gap = max(candidate.exclusion_radius, existing.exclusion_radius)
            if gap < required_gap:
                return ReservationConflict(
                    code="STRUCTURE_EXCLUSION_CONFLICT",
                    candidate=candidate,
                    existing=existing,
                    horizontal_gap=gap,
                    required_gap=required_gap,
                )
        return None

    def try_reserve(
        self,
        reservation: StructureReservation,
        *,
        self_collision_padding: int = 0,
    ) -> ReservationConflict | None:
        """Atomically check and provisionally reserve a structure or jigsaw piece."""
        with self._lock:
            conflict = self._conflict_for_unlocked(
                reservation, self_collision_padding=self_collision_padding
            )
            if conflict is not None:
                return conflict
            self._reservations[reservation.reservation_id] = reservation
            return None

    def reserve_piece(
        self,
        *,
        structure_id: str,
        assembly_id: str,
        family_id: str,
        box: BlockBox,
        exclusion_radius: int = DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
        piece_id: str | None = None,
        self_collision_padding: int = 0,
    ) -> tuple[StructureReservation | None, ReservationConflict | None]:
        reservation = StructureReservation(
            reservation_id=str(uuid4()),
            structure_id=structure_id,
            assembly_id=assembly_id,
            family_id=family_id,
            box=box,
            exclusion_radius=exclusion_radius,
            piece_id=piece_id,
            provisional=True,
        )
        conflict = self.try_reserve(
            reservation, self_collision_padding=self_collision_padding
        )
        if conflict:
            return None, conflict
        return reservation, None

    def commit_assembly(self, assembly_id: str) -> int:
        _require_non_empty_identity(assembly_id, name="assembly id")
        changed = 0
        with self._lock:
            for reservation_id, reservation in list(self._reservations.items()):
                if reservation.assembly_id == assembly_id and reservation.provisional:
                    self._reservations[reservation_id] = replace(reservation, provisional=False)
                    changed += 1
        return changed

    def release_assembly(self, assembly_id: str) -> int:
        _require_non_empty_identity(assembly_id, name="assembly id")
        with self._lock:
            remove = [
                reservation_id
                for reservation_id, reservation in self._reservations.items()
                if reservation.assembly_id == assembly_id and reservation.provisional
            ]
            for reservation_id in remove:
                del self._reservations[reservation_id]
            return len(remove)

    def reconcile_assembly(
        self,
        assembly_id: str,
        actual_boxes: Iterable[BlockBox],
    ) -> int:
        """Drop speculative piece reservations not present in the final StructureStart."""
        _require_non_empty_identity(assembly_id, name="assembly id")
        _require_iterable_collection(actual_boxes, name="actual_boxes")
        actual = set()
        for box in actual_boxes:
            if not isinstance(box, BlockBox):
                raise ValueError("actual_boxes must contain only BlockBox values")
            actual.add(box.key)
        removed = 0
        with self._lock:
            for reservation_id, reservation in list(self._reservations.items()):
                if (
                    reservation.assembly_id == assembly_id
                    and reservation.provisional
                    and reservation.box.key not in actual
                ):
                    del self._reservations[reservation_id]
                    removed += 1
        return removed


def structure_protection_profile(
    *,
    structures: Sequence[str] = (),
    tags: Sequence[str] = (),
    namespaces: Sequence[str] = (),
    family: str | None = None,
    exclusion_radius: int = DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
    jigsaw_piece_exclusion_radius: int | None = None,
    protect_jigsaw_pieces: bool = True,
    priority: int = 0,
) -> dict:
    """Build the sidecar profile consumed by the modular spawn-protection JAR."""
    if protect_jigsaw_pieces is not True:
        raise ValueError("per-piece jigsaw protection must be true")
    _require_exclusion_radius(exclusion_radius, name="exclusion radius")
    if jigsaw_piece_exclusion_radius is None:
        jigsaw_piece_exclusion_radius = exclusion_radius
    _require_exclusion_radius(
        jigsaw_piece_exclusion_radius,
        name="jigsaw piece exclusion radius",
    )
    structure_selectors = _normalize_selector_values(
        structures,
        name="structures",
        validator=_require_resource_location,
    )
    tag_selectors = _normalize_selector_values(
        tags,
        name="tags",
        validator=_require_resource_location,
    )
    namespace_selectors = _normalize_selector_values(
        namespaces,
        name="namespaces",
        validator=_require_namespace,
    )
    if not structure_selectors and not tag_selectors and not namespace_selectors:
        raise ValueError("at least one structure, tag, or namespace selector is required")
    if family is not None and (not isinstance(family, str) or not family.strip()):
        raise ValueError("family must be a non-empty string when provided")
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValueError("priority must be an integer")

    selectors: dict[str, list[str]] = {}
    if structure_selectors:
        selectors["structures"] = structure_selectors
    if tag_selectors:
        selectors["tags"] = tag_selectors
    if namespace_selectors:
        selectors["namespaces"] = namespace_selectors

    out = {
        "selectors": selectors,
        "exclusion_radius": exclusion_radius,
        "jigsaw_piece_exclusion_radius": jigsaw_piece_exclusion_radius,
        "protect_jigsaw_pieces": True,
        "priority": priority,
    }
    if family is not None:
        out["family"] = family
    return out


def validate_structure_protection_profile(profile: Mapping) -> list[tuple[str, str]]:
    if not isinstance(profile, Mapping):
        return [("error", "INVALID_PROTECTION_PROFILE_SHAPE")]

    findings: list[tuple[str, str]] = []
    allowed_profile_keys = {
        "selectors",
        "exclusion_radius",
        "jigsaw_piece_exclusion_radius",
        "protect_jigsaw_pieces",
        "priority",
        "family",
    }
    if any(key not in allowed_profile_keys for key in profile):
        findings.append(("error", "INVALID_PROTECTION_PROFILE_FIELDS"))

    selectors = profile.get("selectors")
    selector_shape_valid = isinstance(selectors, Mapping)
    has_selector = False
    if selector_shape_valid:
        selector_validators = {
            "structures": _require_resource_location,
            "tags": _require_resource_location,
            "namespaces": _require_namespace,
        }
        if any(key not in selector_validators for key in selectors):
            selector_shape_valid = False
        else:
            for key, validator in selector_validators.items():
                values = selectors.get(key)
                if values is None:
                    continue
                try:
                    normalized = _normalize_selector_values(
                        values,
                        name=key,
                        validator=validator,
                    )
                except ValueError:
                    selector_shape_valid = False
                    break
                if normalized:
                    has_selector = True
    if not selector_shape_valid:
        findings.append(("error", "INVALID_PROTECTION_SELECTORS"))
    elif not has_selector:
        findings.append(("error", "NO_PROTECTION_SELECTOR"))

    radius = profile.get("exclusion_radius")
    if (
        isinstance(radius, bool)
        or not isinstance(radius, int)
        or radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS
    ):
        findings.append(("error", "STRUCTURE_EXCLUSION_RADIUS_BELOW_MINIMUM"))
    elif radius > JAVA_INT_MAX:
        findings.append(("error", "STRUCTURE_EXCLUSION_RADIUS_ABOVE_MAXIMUM"))
    if profile.get("protect_jigsaw_pieces") is not True:
        findings.append(("error", "JIGSAW_PIECE_PROTECTION_CANNOT_BE_DISABLED"))
    piece_radius = profile.get("jigsaw_piece_exclusion_radius", radius)
    if (
        isinstance(piece_radius, bool)
        or not isinstance(piece_radius, int)
        or piece_radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS
    ):
        findings.append(("error", "JIGSAW_PIECE_EXCLUSION_RADIUS_BELOW_MINIMUM"))
    elif piece_radius > JAVA_INT_MAX:
        findings.append(("error", "JIGSAW_PIECE_EXCLUSION_RADIUS_ABOVE_MAXIMUM"))
    family = profile.get("family")
    if family is not None and (not isinstance(family, str) or not family.strip()):
        findings.append(("error", "INVALID_PROTECTION_FAMILY"))
    priority = profile.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, int):
        findings.append(("error", "INVALID_PROTECTION_PRIORITY"))
    return findings


def validate_geospatial_worldgen(
    structure,
    structure_set,
    *,
    protection_profile: Mapping | None = None,
    require_spawn_protection: bool = False,
):
    findings = []
    structure_shape_valid = isinstance(structure, Mapping)
    if not structure_shape_valid:
        findings.append(("error", "INVALID_STRUCTURE_SHAPE"))
        structure = {}
    if not isinstance(structure_set, Mapping):
        findings.append(("error", "INVALID_STRUCTURE_SET_SHAPE"))
        structure_set = {}

    biomes = structure.get("biomes")
    if not biomes:
        findings.append(("error", "NO_BIOME_SELECTOR"))
    else:
        try:
            _require_resource_location(biomes, name="biome selector", allow_tag=True)
        except ValueError:
            findings.append(("error", "INVALID_BIOME_SELECTOR"))

    structure_type = structure.get("type")
    if structure_shape_valid and structure_type != "minecraft:jigsaw":
        findings.append(("error", "UNSUPPORTED_STRUCTURE_TYPE"))

    if structure_type == "minecraft:jigsaw":
        try:
            _require_resource_location(structure.get("start_pool"), name="start pool")
        except ValueError:
            findings.append(("error", "INVALID_JIGSAW_START_POOL"))

        try:
            _require_jigsaw_size(structure.get("size"))
        except ValueError:
            findings.append(("error", "INVALID_JIGSAW_SIZE"))

        if not isinstance(structure.get("use_expansion_hack"), bool):
            findings.append(("error", "INVALID_JIGSAW_EXPANSION_HACK"))

        if not _spawn_overrides_are_valid(structure.get("spawn_overrides")):
            findings.append(("error", "INVALID_SPAWN_OVERRIDES"))

        try:
            _require_enum(structure.get("step"), GENERATION_STEPS, name="generation step")
        except ValueError:
            findings.append(("error", "INVALID_GENERATION_STEP"))

        try:
            _require_enum(
                structure.get("terrain_adaptation"),
                TERRAIN_ADAPTATIONS,
                name="terrain adaptation",
            )
        except ValueError:
            findings.append(("error", "INVALID_TERRAIN_ADAPTATION"))

        start_height = structure.get("start_height")
        if not isinstance(start_height, Mapping) or "absolute" not in start_height:
            findings.append(("error", "INVALID_START_HEIGHT"))
        else:
            try:
                _require_block_coordinate(start_height.get("absolute"), name="absolute y")
            except ValueError:
                findings.append(("error", "INVALID_START_HEIGHT"))

        try:
            _require_jigsaw_distance(structure.get("max_distance_from_center"))
        except ValueError:
            findings.append(("error", "INVALID_JIGSAW_DISTANCE"))

        if "project_start_to_heightmap" in structure:
            try:
                _require_enum(
                    structure.get("project_start_to_heightmap"),
                    HEIGHTMAP_TYPES,
                    name="heightmap",
                )
            except ValueError:
                findings.append(("error", "INVALID_HEIGHTMAP"))

    entries = structure_set.get("structures")
    invalid_entries = (
        isinstance(entries, (str, bytes))
        or not isinstance(entries, Sequence)
        or not entries
    )
    if not invalid_entries:
        for entry in entries:
            if not isinstance(entry, Mapping):
                invalid_entries = True
                break
            try:
                _require_resource_location(entry.get("structure"), name="structure id")
            except ValueError:
                invalid_entries = True
                break
            weight = entry.get("weight")
            if (
                isinstance(weight, bool)
                or not isinstance(weight, int)
                or weight <= 0
                or weight > JAVA_INT_MAX
            ):
                invalid_entries = True
                break
    if invalid_entries:
        findings.append(("error", "INVALID_STRUCTURE_SET_ENTRIES"))

    placement = structure_set.get("placement")
    if not isinstance(placement, Mapping):
        findings.append(("error", "INVALID_PLACEMENT_SHAPE"))
    else:
        placement_type = placement.get("type")
        if placement_type != "minecraft:random_spread":
            findings.append(("error", "UNSUPPORTED_PLACEMENT_TYPE"))
        else:
            spacing = placement.get("spacing")
            separation = placement.get("separation")
            salt = placement.get("salt")
            spread_type = placement.get("spread_type", "linear")
            frequency = placement.get("frequency", 1.0)
            frequency_reduction_method = placement.get(
                "frequency_reduction_method", "default"
            )
            exclusion_zone = placement.get("exclusion_zone")
            invalid_spacing = (
                isinstance(spacing, bool)
                or not isinstance(spacing, int)
                or spacing <= 0
                or spacing > MAXIMUM_RANDOM_SPREAD_DISTANCE
            )
            invalid_separation = (
                isinstance(separation, bool)
                or not isinstance(separation, int)
                or separation < 0
                or separation > MAXIMUM_RANDOM_SPREAD_DISTANCE
            )
            invalid_salt = (
                isinstance(salt, bool)
                or not isinstance(salt, int)
                or not JAVA_INT_MIN <= salt <= JAVA_INT_MAX
            )
            invalid_spread_type = (
                not isinstance(spread_type, str)
                or spread_type not in RANDOM_SPREAD_TYPES
            )
            invalid_frequency = (
                isinstance(frequency, bool)
                or not isinstance(frequency, (int, float))
                or not 0.0 <= frequency <= 1.0
            )
            invalid_frequency_reduction_method = (
                not isinstance(frequency_reduction_method, str)
                or frequency_reduction_method not in FREQUENCY_REDUCTION_METHODS
            )
            invalid_exclusion_zone = False
            if exclusion_zone is not None:
                if not isinstance(exclusion_zone, Mapping):
                    invalid_exclusion_zone = True
                else:
                    try:
                        _require_resource_location(
                            exclusion_zone.get("other_set"),
                            name="exclusion zone structure set",
                        )
                    except ValueError:
                        invalid_exclusion_zone = True
                    chunk_count = exclusion_zone.get("chunk_count")
                    if (
                        isinstance(chunk_count, bool)
                        or not isinstance(chunk_count, int)
                        or not 1 <= chunk_count <= 16
                    ):
                        invalid_exclusion_zone = True
            if (
                invalid_spacing
                or invalid_separation
                or invalid_salt
                or invalid_spread_type
                or invalid_frequency
                or invalid_frequency_reduction_method
                or invalid_exclusion_zone
                or (
                    not invalid_spacing
                    and not invalid_separation
                    and separation >= spacing
                )
            ):
                findings.append(("error", "INVALID_RANDOM_SPREAD"))

    if protection_profile is not None:
        findings.extend(validate_structure_protection_profile(protection_profile))
    elif require_spawn_protection:
        findings.append(("error", "MISSING_STRUCTURE_SPAWN_PROTECTION"))
    return findings
