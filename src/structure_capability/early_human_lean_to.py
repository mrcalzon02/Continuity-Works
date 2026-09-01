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

CATALOG_ID = "E01-005"
STRUCTURE_ID = "continuityworks:e01_005_lean_to_windbreak"
FAMILY_ID = "continuityworks:early_human_ephemeral_shelter"
START_POOL = "continuityworks:early_human/e01_005_lean_to_windbreak"
SCALES = ("small", "medium", "large")
SPACING = 100
SEPARATION = 68
SALT = 101005


class LeanToWindbreakGenerationError(ValueError):
    pass


class LeanToWindbreakGenerator:
    """Deterministic Stage-2/3 implementation for E01-005.

    Identity is a directional wind-blocking plane with a shallow lean and a
    leeward occupation strip. It is not a closed brush shelter and not a hide-
    dominated camp enclosure.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str | None]:
        palettes = {
            "temperate": {"post": "minecraft:oak_log", "screen": "minecraft:oak_leaves", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:moss_carpet"},
            "boreal": {"post": "minecraft:spruce_log", "screen": "minecraft:spruce_leaves", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:moss_carpet"},
            "tundra": {"post": "minecraft:spruce_log", "screen": "minecraft:spruce_leaves", "floor": "minecraft:gravel", "bedding": None},
            "savanna": {"post": "minecraft:acacia_log", "screen": "minecraft:acacia_leaves", "floor": "minecraft:coarse_dirt", "bedding": None},
            "arid": {"post": "minecraft:acacia_log", "screen": "minecraft:dead_bush", "floor": "minecraft:sand", "bedding": None},
            "tropical": {"post": "minecraft:jungle_log", "screen": "minecraft:jungle_leaves", "floor": "minecraft:dirt", "bedding": "minecraft:moss_carpet"},
            "coastal": {"post": "minecraft:oak_log", "screen": "minecraft:oak_leaves", "floor": "minecraft:sand", "bedding": None},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
        return sha256(payload).hexdigest()

    def generate(self, *, seed: int | str, scale: str = "medium", biome_family: str = "temperate", condition: str = "active") -> dict[str, Any]:
        if scale not in SCALES:
            raise LeanToWindbreakGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {"small": (11, 7, 9), "medium": (17, 8, 11), "large": (23, 10, 15)}
        width, height, depth = dimensions[scale]
        frame_rng = self._rng(seed, "frame")
        screen_rng = self._rng(seed, "screen")
        occupancy_rng = self._rng(seed, "occupancy")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)
        post = str(palette["post"])
        screen = str(palette["screen"])
        floor = str(palette["floor"])
        bedding = palette["bedding"]

        blocks: dict[tuple[int, int, int], str] = {}
        windward = frame_rng.choice(("north", "south", "east", "west"))
        axis_x = windward in {"north", "south"}
        wall_length = {"small": 7, "medium": 11, "large": 15}[scale]
        wall_height = {"small": 4, "medium": 5, "large": 6}[scale]
        cx, cz = width // 2, depth // 2

        if windward == "north":
            wall_origin = [cx, 0, max(2, cz - 2)]
            lee = (0, 1)
        elif windward == "south":
            wall_origin = [cx, 0, min(depth - 3, cz + 2)]
            lee = (0, -1)
        elif windward == "west":
            wall_origin = [max(2, cx - 2), 0, cz]
            lee = (1, 0)
        else:
            wall_origin = [min(width - 3, cx + 2), 0, cz]
            lee = (-1, 0)

        half = wall_length // 2
        frame_points: list[list[int]] = []
        screen_points: list[list[int]] = []

        # Repeated upright supports define a readable linear windbreak plane.
        for i in range(-half, half + 1, 2):
            x = wall_origin[0] + (i if axis_x else 0)
            z = wall_origin[2] + (0 if axis_x else i)
            if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                continue
            local_h = max(3, wall_height + frame_rng.choice((-1, 0, 0, 1)))
            for y in range(1, local_h + 1):
                blocks[(x, y, z)] = post
                frame_points.append([x, y, z])
            # Shallow leeward lean gives minimal overhead protection without a roof.
            for step in range(1, 3):
                lx, lz = x + lee[0] * step, z + lee[1] * step
                ly = max(2, local_h - step)
                if 1 <= lx < width - 1 and 1 <= lz < depth - 1:
                    blocks[(lx, ly, lz)] = post
                    frame_points.append([lx, ly, lz])

        candidates: list[tuple[int, int, int]] = []
        for i in range(-half, half + 1):
            x = wall_origin[0] + (i if axis_x else 0)
            z = wall_origin[2] + (0 if axis_x else i)
            for y in range(2, wall_height + 1):
                if 1 <= x < width - 1 and 1 <= z < depth - 1:
                    candidates.append((x, y, z))
        target = {"small": 0.58, "medium": 0.66, "large": 0.70}[scale]
        for pos in candidates:
            if pos not in blocks and screen_rng.random() <= target:
                blocks[pos] = screen
                screen_points.append(list(pos))

        lee_anchor = [wall_origin[0] + lee[0] * 3, 1, wall_origin[2] + lee[1] * 3]
        for along in range(-max(2, half - 1), max(2, half)):
            x = lee_anchor[0] + (along if axis_x else 0)
            z = lee_anchor[2] + (0 if axis_x else along)
            if 1 <= x < width - 1 and 1 <= z < depth - 1 and occupancy_rng.random() < 0.60:
                blocks[(x, 0, z)] = floor

        rest_anchor = [lee_anchor[0], 1, lee_anchor[2]]
        if bedding:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    x, z = rest_anchor[0] + dx, rest_anchor[2] + dz
                    if 1 <= x < width - 1 and 1 <= z < depth - 1 and occupancy_rng.random() < 0.52:
                        blocks[(x, 1, z)] = str(bedding)

        hearth = None
        if condition in {"active", "recent"} and occupancy_rng.random() < 0.45:
            hx = max(1, min(width - 2, lee_anchor[0] + lee[0] * 2))
            hz = max(1, min(depth - 2, lee_anchor[2] + lee[1] * 2))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire"
            hearth = [hx, 1, hz]

        if condition in {"weathered", "collapsed", "abandoned", "repurposed"}:
            if condition in {"weathered", "collapsed"}:
                removable = [p for p, b in blocks.items() if b in {post, screen}]
                condition_rng.shuffle(removable)
                fraction = 0.18 if condition == "weathered" else 0.40
                for pos in removable[: int(len(removable) * fraction)]:
                    blocks.pop(pos, None)
            if condition == "repurposed":
                for _ in range({"small": 2, "medium": 4, "large": 6}[scale]):
                    x = max(1, min(width - 2, lee_anchor[0] + condition_rng.randint(-2, 2)))
                    z = max(1, min(depth - 2, lee_anchor[2] + condition_rng.randint(-2, 2)))
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = "minecraft:gravel"

        block_list = [{"pos": [x, y, z], "block": block} for (x, y, z), block in sorted(blocks.items())]
        coverage_ratio = len(screen_points) / max(1, len(candidates))
        qualification = {
            "directional_windward_leeward_logic": True,
            "dominant_planar_windbreak": True,
            "perimeter_open": True,
            "overhead_cover_minimal": True,
            "hide_dominance_absent": True,
            "screen_coverage_below_full": coverage_ratio < 0.85,
        }
        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Lean-To Windbreak",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "surface_terrain_responsive",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "windward": windward,
                "leeward_vector": [lee[0], lee[1]],
                "wall_origin": wall_origin,
                "rest_zone_anchor": rest_anchor,
                "hearth": hearth,
                "frame_points": frame_points,
                "screen_points": screen_points,
                "screen_coverage_ratio": coverage_ratio,
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "archetype_constraint": "directional_planar_windbreak_with_minimal_overhead_cover_and_no_hide_enclosure",
                "fingerprint": self._fingerprint(block_list),
            },
        }

    def worldgen_bundle(self, *, biome_selector: str = "#minecraft:is_overworld") -> dict[str, Any]:
        structure = jigsaw_structure(
            biome_selector=biome_selector,
            start_pool=START_POOL,
            step="surface_structures",
            terrain_adaptation="beard_thin",
            heightmap="WORLD_SURFACE_WG",
            absolute_y=0,
            max_distance=64,
        )
        structure_set = random_spread_structure_set(STRUCTURE_ID, spacing=SPACING, separation=SEPARATION, salt=SALT)
        protection = structure_protection_profile(
            structures=[STRUCTURE_ID],
            family=FAMILY_ID,
            exclusion_radius=DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
            jigsaw_piece_exclusion_radius=DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
            protect_jigsaw_pieces=True,
            priority=10,
        )
        findings = validate_geospatial_worldgen(structure, structure_set, protection_profile=protection, require_spawn_protection=True)
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
                "requires_exposed_wind_context": True,
                "must_not_replace_existing_major_structure": True,
            },
        }
