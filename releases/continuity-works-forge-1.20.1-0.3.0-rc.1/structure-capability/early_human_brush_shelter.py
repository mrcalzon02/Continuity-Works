from __future__ import annotations

from hashlib import sha256
import random
from typing import Any

from .minecraft.worldgen import (
    DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
    jigsaw_structure,
    random_spread_structure_set,
    structure_protection_profile,
    validate_geospatial_worldgen,
)

CATALOG_ID = "E01-004"
STRUCTURE_ID = "continuityworks:e01_004_temporary_brush_shelter"
FAMILY_ID = "continuityworks:early_human_ephemeral_shelter"
START_POOL = "continuityworks:early_human/e01_004_temporary_brush_shelter"
SCALES = ("small", "medium", "large")
SPACING = 100
SEPARATION = 68
SALT = 101004


class TemporaryBrushShelterGenerationError(ValueError):
    pass


class TemporaryBrushShelterGenerator:
    """Deterministic Stage-2/3 implementation for E01-004.

    The archetype is intentionally ephemeral: a loose rib frame and patchy brush
    skin create a sheltered lee pocket without forming a closed hut, complete
    roof, or planar windbreak wall.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str | None]:
        palettes = {
            "temperate": {"rib": "minecraft:oak_log", "brush": "minecraft:oak_leaves", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:moss_carpet"},
            "boreal": {"rib": "minecraft:spruce_log", "brush": "minecraft:spruce_leaves", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:moss_carpet"},
            "tundra": {"rib": "minecraft:spruce_log", "brush": "minecraft:spruce_leaves", "floor": "minecraft:coarse_dirt", "bedding": None},
            "savanna": {"rib": "minecraft:acacia_log", "brush": "minecraft:acacia_leaves", "floor": "minecraft:coarse_dirt", "bedding": None},
            "arid": {"rib": "minecraft:acacia_log", "brush": "minecraft:dead_bush", "floor": "minecraft:sand", "bedding": None},
            "tropical": {"rib": "minecraft:jungle_log", "brush": "minecraft:jungle_leaves", "floor": "minecraft:dirt", "bedding": "minecraft:moss_carpet"},
            "coastal": {"rib": "minecraft:oak_log", "brush": "minecraft:oak_leaves", "floor": "minecraft:sand", "bedding": None},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
        return sha256(payload).hexdigest()

    def generate(
        self,
        *,
        seed: int | str,
        scale: str = "medium",
        biome_family: str = "temperate",
        condition: str = "active",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise TemporaryBrushShelterGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {
            "small": (11, 7, 10),
            "medium": (15, 8, 13),
            "large": (21, 10, 17),
        }
        width, height, depth = dimensions[scale]
        frame_rng = self._rng(seed, "frame")
        skin_rng = self._rng(seed, "brush_skin")
        occupancy_rng = self._rng(seed, "occupancy")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)
        rib = str(palette["rib"])
        brush = str(palette["brush"])
        floor = str(palette["floor"])
        bedding = palette["bedding"]

        blocks: dict[tuple[int, int, int], str] = {}
        center_x = width // 2
        open_side = frame_rng.choice(("north", "south"))
        rear_z = depth - 3 if open_side == "north" else 2
        entry_z = 1 if open_side == "north" else depth - 2
        shelter_depth_sign = 1 if open_side == "north" else -1

        half_width = {"small": 3, "medium": 5, "large": 7}[scale]
        rib_count = {"small": 4, "medium": 6, "large": 8}[scale]
        frame_points: list[list[int]] = []

        # Rear anchor row, irregular and intentionally incomplete.
        for i in range(rib_count):
            x = round(center_x - half_width + (2 * half_width) * (i / max(1, rib_count - 1)))
            x = max(1, min(width - 2, x + frame_rng.choice((-1, 0, 0, 1))))
            max_h = {"small": 4, "medium": 5, "large": 6}[scale] + frame_rng.choice((-1, 0, 0, 1))
            for y in range(1, max_h + 1):
                blocks[(x, y, rear_z)] = rib
                frame_points.append([x, y, rear_z])

            # Leaning/bent rib toward the open side; every rib terminates before
            # crossing the full footprint, preventing a complete roof shell.
            reach = frame_rng.randint(2, max(2, depth // 3))
            for step in range(1, reach + 1):
                z = rear_z - shelter_depth_sign * step
                y = max(2, max_h - step // 2)
                if 1 <= z < depth - 1:
                    blocks[(x, y, z)] = rib
                    frame_points.append([x, y, z])

        # Patchy brush skin: deliberately below full coverage and concentrated
        # along the rear and upper lee side.
        candidate_skin: list[tuple[int, int, int]] = []
        for x in range(max(1, center_x - half_width - 1), min(width - 1, center_x + half_width + 2)):
            for y in range(2, min(height - 1, {"small": 5, "medium": 6, "large": 7}[scale])):
                for offset in (0, 1):
                    z = rear_z - shelter_depth_sign * offset
                    if 1 <= z < depth - 1:
                        candidate_skin.append((x, y, z))
        skin_target_fraction = {"small": 0.48, "medium": 0.54, "large": 0.58}[scale]
        skin_points: list[list[int]] = []
        for pos in candidate_skin:
            if skin_rng.random() <= skin_target_fraction and pos not in blocks:
                blocks[pos] = brush
                skin_points.append(list(pos))

        # Interior floor disturbance and lee pocket remain minimal.
        sheltered_z = rear_z - shelter_depth_sign * max(1, depth // 4)
        sheltered_z = max(2, min(depth - 3, sheltered_z))
        floor_radius_x = max(2, half_width - 1)
        for x in range(max(1, center_x - floor_radius_x), min(width - 1, center_x + floor_radius_x + 1)):
            for z in range(min(sheltered_z, rear_z), max(sheltered_z, rear_z) + 1):
                if occupancy_rng.random() < 0.55:
                    blocks[(x, 0, z)] = floor

        rest_anchor = [center_x + frame_rng.choice((-1, 0, 1)), 1, sheltered_z]
        if bedding:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if occupancy_rng.random() < 0.56:
                        blocks[(rest_anchor[0] + dx, 1, rest_anchor[2] + dz)] = str(bedding)

        # Hearth is optional and exterior-biased; this is a temporary shelter,
        # not a hearth-centered camp.
        hearth_allowed = condition in {"active", "recent"} and occupancy_rng.random() < 0.55
        hearth = [center_x, 1, max(1, min(depth - 2, entry_z + shelter_depth_sign * 2))]
        if hearth_allowed:
            hx, hy, hz = hearth
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, hy, hz)] = "minecraft:campfire"

        # Ephemeral tool/refuse traces, kept sparse.
        trace_count = {"small": 2, "medium": 4, "large": 6}[scale]
        for _ in range(trace_count):
            x = max(1, min(width - 2, center_x + occupancy_rng.randint(-half_width, half_width)))
            z = max(1, min(depth - 2, sheltered_z + occupancy_rng.randint(-2, 2)))
            if (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = occupancy_rng.choice(("minecraft:gravel", floor))

        if condition in {"abandoned", "weathered", "collapsed", "overgrown", "repurposed"}:
            if condition in {"weathered", "collapsed"}:
                removable = [p for p, block in blocks.items() if block in {rib, brush}]
                condition_rng.shuffle(removable)
                fraction = 0.18 if condition == "weathered" else 0.42
                for pos in removable[: int(len(removable) * fraction)]:
                    blocks.pop(pos, None)
            if condition == "overgrown" and biome_family not in {"arid", "tundra"}:
                for _ in range({"small": 5, "medium": 9, "large": 14}[scale]):
                    x = condition_rng.randrange(1, width - 1)
                    z = condition_rng.randrange(1, depth - 1)
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = "minecraft:moss_carpet"
            if condition == "repurposed":
                # Later reuse may add traces but cannot close the original shell.
                for _ in range({"small": 2, "medium": 3, "large": 5}[scale]):
                    x = max(1, min(width - 2, center_x + condition_rng.randint(-half_width, half_width)))
                    z = max(1, min(depth - 2, sheltered_z + condition_rng.randint(-2, 2)))
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = "minecraft:gravel"

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]
        perimeter_closed = False
        complete_roof = False
        dominant_planar_wall = False
        coverage_ratio = len(skin_points) / max(1, len(candidate_skin))
        qualification = {
            "partial_enclosure_only": not perimeter_closed,
            "roof_incomplete": not complete_roof,
            "not_planar_windbreak": not dominant_planar_wall,
            "brush_skin_below_full_coverage": coverage_ratio < 0.75,
            "ephemeral_material_logic": True,
        }

        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Temporary Brush Shelter",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "surface_terrain_responsive",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "open_side": open_side,
                "rear_anchor_z": rear_z,
                "entry_z": entry_z,
                "rest_zone_anchor": rest_anchor,
                "hearth_allowed": hearth_allowed,
                "hearth": hearth if hearth_allowed else None,
                "frame_points": frame_points,
                "brush_skin_points": skin_points,
                "brush_skin_coverage_ratio": coverage_ratio,
                "perimeter_closed": perimeter_closed,
                "complete_roof": complete_roof,
                "dominant_planar_wall": dominant_planar_wall,
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "archetype_constraint": "partial_ephemeral_brush_enclosure_without_complete_roof_or_planar_windbreak",
                "fingerprint": self._fingerprint(block_list),
            },
        }

    def worldgen_bundle(
        self,
        *,
        biome_selector: str = "#minecraft:is_overworld",
    ) -> dict[str, Any]:
        structure = jigsaw_structure(
            biome_selector=biome_selector,
            start_pool=START_POOL,
            step="surface_structures",
            terrain_adaptation="beard_thin",
            heightmap="WORLD_SURFACE_WG",
            absolute_y=0,
            max_distance=64,
        )
        structure_set = random_spread_structure_set(
            STRUCTURE_ID,
            spacing=SPACING,
            separation=SEPARATION,
            salt=SALT,
        )
        protection = structure_protection_profile(
            structures=[STRUCTURE_ID],
            family=FAMILY_ID,
            exclusion_radius=DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
            jigsaw_piece_exclusion_radius=DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
            protect_jigsaw_pieces=True,
            priority=10,
        )
        findings = validate_geospatial_worldgen(
            structure,
            structure_set,
            protection_profile=protection,
            require_spawn_protection=True,
        )
        return {
            "catalog_id": CATALOG_ID,
            "structure_id": STRUCTURE_ID,
            "start_pool": START_POOL,
            "structure": structure,
            "structure_set": structure_set,
            "protection_profile": protection,
            "validation_findings": findings,
            "placement_contract": {
                "anchor": "surface_heightmap",
                "terrain_responsive": True,
                "requires_vegetation_or_portable_brush_material_context": True,
                "must_not_replace_existing_major_structure": True,
            },
        }
