from __future__ import annotations

from dataclasses import dataclass, replace
from math import hypot
from threading import RLock
from typing import Iterable, Mapping, Sequence
from uuid import uuid4


MINIMUM_STRUCTURE_EXCLUSION_RADIUS = 500
DEFAULT_STRUCTURE_EXCLUSION_RADIUS = MINIMUM_STRUCTURE_EXCLUSION_RADIUS


def jigsaw_structure(*, biome_selector, start_pool, step="surface_structures",
                     terrain_adaptation="bury", heightmap=None, absolute_y=0,
                     max_distance=80):
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
    if heightmap:
        out["project_start_to_heightmap"] = heightmap
    return out


def random_spread_structure_set(structure_id, spacing, separation, salt):
    if separation >= spacing:
        raise ValueError("separation must be lower than spacing")
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
        if self.min_x > self.max_x or self.min_y > self.max_y or self.min_z > self.max_z:
            raise ValueError("invalid block box")

    @property
    def key(self) -> tuple[int, int, int, int, int, int]:
        return (self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)

    def overlaps_volume(self, other: "BlockBox", *, padding: int = 0) -> bool:
        """True only for occupied-volume overlap; face adjacency is allowed."""
        if padding < 0:
            raise ValueError("padding must be non-negative")
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
        if self.exclusion_radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
            raise ValueError(
                f"exclusion radius must be >= {MINIMUM_STRUCTURE_EXCLUSION_RADIUS} blocks"
            )


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
        self._reservations: dict[str, StructureReservation] = {
            reservation.reservation_id: reservation for reservation in reservations
        }

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
        for existing in self._reservations.values():
            if existing.reservation_id == candidate.reservation_id:
                continue
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
        changed = 0
        with self._lock:
            for reservation_id, reservation in list(self._reservations.items()):
                if reservation.assembly_id == assembly_id and reservation.provisional:
                    self._reservations[reservation_id] = replace(reservation, provisional=False)
                    changed += 1
        return changed

    def release_assembly(self, assembly_id: str) -> int:
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
        actual = {box.key for box in actual_boxes}
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
    if not protect_jigsaw_pieces:
        raise ValueError("per-piece jigsaw protection is mandatory")
    if exclusion_radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
        raise ValueError(
            f"exclusion radius must be >= {MINIMUM_STRUCTURE_EXCLUSION_RADIUS} blocks"
        )
    if jigsaw_piece_exclusion_radius is None:
        jigsaw_piece_exclusion_radius = exclusion_radius
    if jigsaw_piece_exclusion_radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
        raise ValueError(
            "jigsaw piece exclusion radius must be >= "
            f"{MINIMUM_STRUCTURE_EXCLUSION_RADIUS} blocks"
        )
    if not structures and not tags and not namespaces:
        raise ValueError("at least one structure, tag, or namespace selector is required")

    selectors: dict[str, list[str]] = {}
    if structures:
        selectors["structures"] = list(structures)
    if tags:
        selectors["tags"] = list(tags)
    if namespaces:
        selectors["namespaces"] = list(namespaces)

    out = {
        "selectors": selectors,
        "exclusion_radius": exclusion_radius,
        "jigsaw_piece_exclusion_radius": jigsaw_piece_exclusion_radius,
        "protect_jigsaw_pieces": bool(protect_jigsaw_pieces),
        "priority": int(priority),
    }
    if family:
        out["family"] = family
    return out


def validate_structure_protection_profile(profile: Mapping) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    selectors = profile.get("selectors") or {}
    if not any(selectors.get(key) for key in ("structures", "tags", "namespaces")):
        findings.append(("error", "NO_PROTECTION_SELECTOR"))
    radius = profile.get("exclusion_radius")
    if not isinstance(radius, int) or radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
        findings.append(("error", "STRUCTURE_EXCLUSION_RADIUS_BELOW_MINIMUM"))
    if profile.get("protect_jigsaw_pieces") is False:
        findings.append(("error", "JIGSAW_PIECE_PROTECTION_CANNOT_BE_DISABLED"))
    piece_radius = profile.get("jigsaw_piece_exclusion_radius", radius)
    if not isinstance(piece_radius, int) or piece_radius < MINIMUM_STRUCTURE_EXCLUSION_RADIUS:
        findings.append(("error", "JIGSAW_PIECE_EXCLUSION_RADIUS_BELOW_MINIMUM"))
    return findings


def validate_geospatial_worldgen(
    structure,
    structure_set,
    *,
    protection_profile: Mapping | None = None,
    require_spawn_protection: bool = False,
):
    findings = []
    biomes = structure.get("biomes")
    if not biomes:
        findings.append(("error", "NO_BIOME_SELECTOR"))
    placement = structure_set.get("placement", {})
    if placement.get("type") == "minecraft:random_spread":
        if placement.get("separation", 0) >= placement.get("spacing", 0):
            findings.append(("error", "INVALID_RANDOM_SPREAD"))

    if protection_profile is not None:
        findings.extend(validate_structure_protection_profile(protection_profile))
    elif require_spawn_protection:
        findings.append(("error", "MISSING_STRUCTURE_SPAWN_PROTECTION"))
    return findings
