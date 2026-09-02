from __future__ import annotations

from hashlib import sha256
import math
import random
from typing import Any

from .minecraft.worldgen import (
    DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
    jigsaw_structure,
    random_spread_structure_set,
    structure_protection_profile,
    validate_geospatial_worldgen,
)

CATALOG_ID = "E01-013"
STRUCTURE_ID = "continuityworks:e01_013_large_carcass_processing_site"
FAMILY_ID = "continuityworks:early_human_carcass_processing"
START_POOL = "continuityworks:early_human/e01_013_large_carcass_processing_site"
SCALES = ("small", "medium", "large")
SPACING = 132
SEPARATION = 96
SALT = 101013


class LargeCarcassProcessingSiteGenerationError(ValueError):
    pass


class LargeCarcassProcessingSiteGenerator:
    """Deterministic Stage-2/3 implementation for E01-013."""

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
        return sha256(payload).hexdigest()

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str]:
        palettes = {
            "temperate": {"ground": "minecraft:coarse_dirt", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "discard": "minecraft:gravel", "stain": "minecraft:red_terracotta", "hide": "minecraft:brown_carpet"},
            "boreal": {"ground": "minecraft:podzol", "bone": "minecraft:bone_block", "tool": "minecraft:stone", "discard": "minecraft:gravel", "stain": "minecraft:coarse_dirt", "hide": "minecraft:brown_carpet"},
            "tundra": {"ground": "minecraft:gravel", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "discard": "minecraft:stone", "stain": "minecraft:coarse_dirt", "hide": "minecraft:light_gray_carpet"},
            "savanna": {"ground": "minecraft:coarse_dirt", "bone": "minecraft:bone_block", "tool": "minecraft:granite", "discard": "minecraft:gravel", "stain": "minecraft:red_terracotta", "hide": "minecraft:brown_carpet"},
            "arid": {"ground": "minecraft:sand", "bone": "minecraft:bone_block", "tool": "minecraft:stone", "discard": "minecraft:gravel", "stain": "minecraft:red_sand", "hide": "minecraft:brown_carpet"},
            "tropical": {"ground": "minecraft:dirt", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "discard": "minecraft:gravel", "stain": "minecraft:rooted_dirt", "hide": "minecraft:brown_carpet"},
            "coastal": {"ground": "minecraft:gravel", "bone": "minecraft:bone_block", "tool": "minecraft:cobblestone", "discard": "minecraft:gravel", "stain": "minecraft:coarse_dirt", "hide": "minecraft:light_gray_carpet"},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _line(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
        x0, z0 = a
        x1, z1 = b
        dx, dz = abs(x1 - x0), abs(z1 - z0)
        sx = 1 if x0 < x1 else -1
        sz = 1 if z0 < z1 else -1
        err = dx - dz
        out: list[tuple[int, int]] = []
        while True:
            out.append((x0, z0))
            if x0 == x1 and z0 == z1:
                break
            e2 = 2 * err
            if e2 > -dz:
                err -= dz
                x0 += sx
            if e2 < dx:
                err += dx
                z0 += sz
        return out

    def generate(
        self,
        *,
        seed: int | str,
        scale: str = "medium",
        biome_family: str = "temperate",
        condition: str = "active",
        culture_profile: str = "cooperative_disarticulation",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise LargeCarcassProcessingSiteGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {"active", "recent", "repeated", "abandoned", "weathered", "scavenger_reworked", "sediment_reworked", "repurposed"}
        if condition not in valid_conditions:
            raise LargeCarcassProcessingSiteGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {"cooperative_disarticulation", "marrow_intensive", "transport_priority", "hide_retention"}
        if culture_profile not in valid_cultures:
            raise LargeCarcassProcessingSiteGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (43, 8, 35), "medium": (57, 9, 47), "large": (73, 10, 61)}
        bay_ranges = {"small": (3, 4), "medium": (4, 6), "large": (6, 9)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "dominant_carcass")
        bay_rng = self._rng(seed, "task_bays")
        heavy_rng = self._rng(seed, "heavy_bone")
        discard_rng = self._rng(seed, "dirty_discard")
        staging_rng = self._rng(seed, "clean_staging")
        route_rng = self._rng(seed, "haul_corridor")
        hide_rng = self._rng(seed, "hide_edge")
        hearth_rng = self._rng(seed, "hearth")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi)
        ax, az = math.cos(angle), math.sin(angle)
        px, pz = -az, ax
        carcass_length = {"small": 15, "medium": 21, "large": 29}[scale]
        carcass_cells: list[list[int]] = []

        for step in range(-(carcass_length // 2), carcass_length // 2 + 1):
            x = int(round(cx + ax * step))
            z = int(round(cz + az * step))
            if 2 <= x < width - 2 and 2 <= z < depth - 2:
                blocks[(x, 0, z)] = palette["stain"]
                blocks[(x, 1, z)] = palette["bone"]
                carcass_cells.append([x, 1, z])
                torso_half_width = 2 if abs(step) <= carcass_length * 0.18 else 1
                for lateral in range(1, torso_half_width + 1):
                    if layout_rng.random() < 0.86:
                        for side in (-1, 1):
                            sx = int(round(x + px * lateral * side))
                            sz = int(round(z + pz * lateral * side))
                            if 2 <= sx < width - 2 and 2 <= sz < depth - 2:
                                blocks[(sx, 1, sz)] = palette["bone"]
                                carcass_cells.append([sx, 1, sz])

        bay_count = bay_rng.randint(*bay_ranges[scale])
        if culture_profile == "cooperative_disarticulation":
            bay_count = bay_ranges[scale][1]
        task_bays: list[dict[str, Any]] = []
        work_positions: list[list[int]] = []
        for i in range(bay_count):
            side = -1 if i % 2 == 0 else 1
            fraction = (i + 1) / (bay_count + 1)
            along = -carcass_length * 0.4 + fraction * carcass_length * 0.8 + bay_rng.uniform(-1.5, 1.5)
            offset = bay_rng.uniform(4.0, 6.0)
            bx = max(2, min(width - 3, int(round(cx + ax * along + px * offset * side))))
            bz = max(2, min(depth - 3, int(round(cz + az * along + pz * offset * side))))
            blocks[(bx, 0, bz)] = palette["ground"]
            blocks[(bx, 1, bz)] = palette["tool"]
            work_positions.append([bx, 1, bz])
            task_bays.append({"index": i, "side": side, "center": [bx, 1, bz], "role": "disarticulation" if i % 3 else "meat_removal"})

        heavy_side = -1
        heavy_center = (
            max(3, min(width - 4, int(round(cx - ax * carcass_length * 0.18 + px * heavy_side * width * 0.24)))),
            max(3, min(depth - 4, int(round(cz - az * carcass_length * 0.18 + pz * heavy_side * depth * 0.24)))),
        )
        heavy_target = {"small": 9, "medium": 16, "large": 26}[scale] + (8 if culture_profile == "marrow_intensive" else 0)
        heavy_bone_points: list[list[int]] = []
        for _ in range(heavy_target):
            x = max(2, min(width - 3, heavy_center[0] + heavy_rng.randint(-3, 3)))
            z = max(2, min(depth - 3, heavy_center[1] + heavy_rng.randint(-3, 3)))
            blocks[(x, 1, z)] = palette["tool"] if heavy_rng.random() < 0.32 else palette["bone"]
            heavy_bone_points.append([x, 1, z])

        discard_cells: set[tuple[int, int]] = set()
        discard_target = {"small": 48, "medium": 82, "large": 130}[scale]
        for _ in range(discard_target):
            bay = discard_rng.choice(task_bays)
            anchor = bay["center"]
            side = int(bay["side"])
            radial_x, radial_z = px * side, pz * side
            distance = discard_rng.uniform(5.0, 13.0 if scale == "small" else 17.0 if scale == "medium" else 22.0)
            along = discard_rng.gauss(0.0, 3.0)
            x = int(round(anchor[0] + radial_x * distance + ax * along))
            z = int(round(anchor[2] + radial_z * distance + az * along))
            if not (2 <= x < width - 2 and 2 <= z < depth - 2):
                continue
            blocks[(x, 1, z)] = palette["bone"] if discard_rng.random() < 0.55 else palette["discard"]
            discard_cells.add((x, z))

        clean_side = 1
        staging_center = (
            max(3, min(width - 4, int(round(cx + ax * carcass_length * 0.1 + px * clean_side * width * 0.31)))),
            max(3, min(depth - 4, int(round(cz + az * carcass_length * 0.1 + pz * clean_side * depth * 0.31)))),
        )
        staging_count = {"small": 5, "medium": 9, "large": 14}[scale] + (5 if culture_profile == "transport_priority" else 0)
        staging_points: list[list[int]] = []
        for _ in range(staging_count):
            x = max(2, min(width - 3, staging_center[0] + staging_rng.randint(-3, 3)))
            z = max(2, min(depth - 3, staging_center[1] + staging_rng.randint(-3, 3)))
            blocks[(x, 1, z)] = palette["bone"]
            staging_points.append([x, 1, z])

        # Route to whichever x or z boundary is nearer, preserving the clean circulation lane.
        edge_candidates = [(1, staging_center[1]), (width - 2, staging_center[1]), (staging_center[0], 1), (staging_center[0], depth - 2)]
        edge = min(edge_candidates, key=lambda p: abs(p[0] - staging_center[0]) + abs(p[1] - staging_center[1]) + route_rng.random() * 0.25)
        haul_corridor: list[list[int]] = []
        for x, z in self._line(staging_center, edge):
            blocks[(x, 0, z)] = palette["ground"]
            if (x, z) in discard_cells:
                blocks.pop((x, 1, z), None)
                discard_cells.discard((x, z))
            haul_corridor.append([x, 0, z])

        hide_center = (
            max(3, min(width - 4, int(round(cx + ax * carcass_length * 0.3 - px * width * 0.29)))),
            max(3, min(depth - 4, int(round(cz + az * carcass_length * 0.3 - pz * depth * 0.29)))),
        )
        hide_count = {"small": 4, "medium": 7, "large": 11}[scale] + (6 if culture_profile == "hide_retention" else 0)
        hide_points: list[list[int]] = []
        for _ in range(hide_count):
            x = max(2, min(width - 3, hide_center[0] + hide_rng.randint(-3, 3)))
            z = max(2, min(depth - 3, hide_center[1] + hide_rng.randint(-3, 3)))
            blocks[(x, 1, z)] = palette["hide"]
            hide_points.append([x, 1, z])

        scavenger_points: list[list[int]] = []
        for _ in range({"small": 4, "medium": 7, "large": 10}[scale]):
            x = condition_rng.choice((2, width - 3)) if condition_rng.random() < 0.5 else condition_rng.randint(2, width - 3)
            z = condition_rng.randint(2, depth - 3) if x in {2, width - 3} else condition_rng.choice((2, depth - 3))
            if condition_rng.random() < 0.55:
                blocks[(x, 1, z)] = palette["bone"]
                scavenger_points.append([x, 1, z])

        hearth = None
        if condition in {"active", "repeated"} and hearth_rng.random() < 0.28:
            hx = max(3, min(width - 4, staging_center[0] + hearth_rng.randint(-4, 4)))
            hz = max(3, min(depth - 4, staging_center[1] + hearth_rng.randint(-4, 4)))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"
            hearth = [hx, 1, hz]

        if condition == "repeated":
            for _ in range({"small": 10, "medium": 20, "large": 34}[scale]):
                anchor = condition_rng.choice(work_positions + heavy_bone_points)
                x = max(2, min(width - 3, anchor[0] + condition_rng.randint(-4, 4)))
                z = max(2, min(depth - 3, anchor[2] + condition_rng.randint(-4, 4)))
                blocks[(x, 1, z)] = palette["bone"] if condition_rng.random() < 0.62 else palette["discard"]
                discard_cells.add((x, z))
        elif condition in {"abandoned", "weathered"}:
            for pos in list(blocks):
                if pos[1] == 1 and blocks[pos] == palette["hide"] and condition_rng.random() < 0.8:
                    blocks.pop(pos, None)
            if condition == "weathered" and biome_family in {"temperate", "boreal", "tropical"}:
                candidates = [p for p in blocks if p[1] == 0 and blocks[p] in {palette["ground"], palette["stain"]}]
                condition_rng.shuffle(candidates)
                for x, _, z in candidates[: max(3, len(candidates) // 12)]:
                    blocks[(x, 1, z)] = "minecraft:moss_carpet"
        elif condition == "scavenger_reworked":
            candidates = [p for p in list(blocks) if p[1] == 1 and blocks[p] == palette["bone"]]
            condition_rng.shuffle(candidates)
            for pos in candidates[: max(3, len(candidates) // 5)]:
                block = blocks.pop(pos)
                x = max(2, min(width - 3, pos[0] + condition_rng.randint(-7, 7)))
                z = max(2, min(depth - 3, pos[2] + condition_rng.randint(-7, 7)))
                blocks[(x, 1, z)] = block
                scavenger_points.append([x, 1, z])
        elif condition == "sediment_reworked":
            for pos in list(blocks):
                if pos[1] == 1 and condition_rng.random() < 0.15:
                    blocks[pos] = palette["ground"]
        elif condition == "repurposed":
            for _ in range(4 if scale == "small" else 7 if scale == "medium" else 10):
                x = max(2, min(width - 3, staging_center[0] + condition_rng.randint(-5, 5)))
                z = max(2, min(depth - 3, staging_center[1] + condition_rng.randint(-5, 5)))
                blocks[(x, 1, z)] = palette["tool"]

        # Re-clear the haul corridor after condition transforms.
        for x, _, z in haul_corridor:
            if (x, z) in discard_cells:
                discard_cells.discard((x, z))
            if (x, 1, z) in blocks and blocks[(x, 1, z)] in {palette["discard"], palette["bone"]}:
                blocks.pop((x, 1, z), None)

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
            if 0 <= x < width and 0 <= y < height and 0 <= z < depth
        ]

        route_xz = {(p[0], p[2]) for p in haul_corridor}
        qualification = {
            "one_dominant_carcass_axis": len(carcass_cells) >= carcass_length,
            "multiple_task_bays": len(task_bays) >= 3,
            "heavy_bone_zone_present": len(heavy_bone_points) >= 6,
            "directional_dirty_discard": len(discard_cells) >= 12,
            "clean_staging_present": len(staging_points) >= 5,
            "haul_corridor_present": len(haul_corridor) >= 2,
            "haul_corridor_clear": all((x, z) not in discard_cells for x, z in route_xz),
            "hide_handling_subordinate": len(hide_points) < len(carcass_cells) + len(task_bays),
            "hearth_subordinate": hearth is None or len(carcass_cells) + len(discard_cells) > 30,
            "exceeds_e01_012_scale_ceiling": width > 39 and depth > 33,
            "no_permanent_architecture": True,
            "cooperative_processing_primary": len(carcass_cells) + len(task_bays) + len(heavy_bone_points) > len(hide_points),
        }
        if not all(qualification.values()):
            raise LargeCarcassProcessingSiteGenerationError(f"E01-013 qualification failed: {qualification}")

        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "culture_profile": culture_profile,
                "seed": str(seed),
                "terrain_mode": "surface_large_carcass_task_landscape_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "material_semantics": {
                    "bone": "large_carcass_or_heavy_bone_role_proxy",
                    "stain": "organic_processing_stain_role_proxy",
                    "hide": "hide_or_offcut_role_proxy",
                    "tool": "stone_tool_hammerstone_or_anvil_role_proxy",
                    "discard": "processing_refuse_role_proxy",
                },
                "carcass_cells": carcass_cells,
                "carcass_axis_length": carcass_length,
                "task_bays": task_bays,
                "work_positions": work_positions,
                "heavy_bone_points": heavy_bone_points,
                "discard_cell_count": len(discard_cells),
                "staging_points": staging_points,
                "haul_corridor": haul_corridor,
                "hide_offcut_points": hide_points,
                "scavenger_points": scavenger_points,
                "hearth": hearth,
                "qualification": qualification,
                "compatible_family_policy": "same_parent_reservation_only",
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
            max_distance=96,
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
            "family_id": FAMILY_ID,
            "structure": structure,
            "structure_set": structure_set,
            "protection_profile": protection,
            "compatible_family_policy": "same_parent_reservation_only",
            "replace_policy": "bounded_additive_non_destructive",
            "validation_findings": findings,
        }
