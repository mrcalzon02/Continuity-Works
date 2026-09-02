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

CATALOG_ID = "E01-012"
STRUCTURE_ID = "continuityworks:e01_012_butchery_site"
FAMILY_ID = "continuityworks:early_human_carcass_processing"
START_POOL = "continuityworks:early_human/e01_012_butchery_site"
SCALES = ("small", "medium", "large")
SPACING = 120
SEPARATION = 84
SALT = 101012


class ButcherySiteGenerationError(ValueError):
    pass


class ButcherySiteGenerator:
    """Deterministic Stage-2/3 implementation for E01-012 Butchery Site."""

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
        culture_profile: str = "expedient_field_dressing",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise ButcherySiteGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {"active", "recent", "repeated", "abandoned", "weathered", "scavenger_reworked", "sediment_reworked", "repurposed"}
        if condition not in valid_conditions:
            raise ButcherySiteGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {"expedient_field_dressing", "transport_focused", "marrow_intensive", "consumption_biased"}
        if culture_profile not in valid_cultures:
            raise ButcherySiteGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (17, 5, 15), "medium": (27, 6, 23), "large": (39, 7, 33)}
        work_ranges = {"small": (1, 2), "medium": (2, 4), "large": (4, 7)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "carcass_layout")
        work_rng = self._rng(seed, "work_positions")
        discard_rng = self._rng(seed, "discard_fans")
        marrow_rng = self._rng(seed, "marrow_zone")
        staging_rng = self._rng(seed, "transport_staging")
        route_rng = self._rng(seed, "carry_route")
        condition_rng = self._rng(seed, "condition")
        hearth_rng = self._rng(seed, "hearth")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi)
        ax, az = math.cos(angle), math.sin(angle)
        px, pz = -az, ax
        carcass_length = {"small": 5, "medium": 7, "large": 9}[scale]
        carcass_cells: list[list[int]] = []
        for step in range(-(carcass_length // 2), carcass_length // 2 + 1):
            x = int(round(cx + ax * step))
            z = int(round(cz + az * step))
            if 1 <= x < width - 1 and 1 <= z < depth - 1:
                blocks[(x, 0, z)] = palette["stain"]
                blocks[(x, 1, z)] = palette["bone"]
                carcass_cells.append([x, 1, z])
                if abs(step) <= 1 and layout_rng.random() < 0.7:
                    sx = max(1, min(width - 2, x + (1 if px >= 0 else -1)))
                    sz = max(1, min(depth - 2, z + (1 if pz >= 0 else -1)))
                    blocks[(sx, 1, sz)] = palette["bone"]
                    carcass_cells.append([sx, 1, sz])

        work_count = work_rng.randint(*work_ranges[scale])
        work_positions: list[list[int]] = []
        for i in range(work_count):
            side = -1 if i % 2 == 0 else 1
            along = work_rng.uniform(-carcass_length * 0.35, carcass_length * 0.35)
            offset = work_rng.uniform(2.0, 3.8)
            x = int(round(cx + ax * along + px * offset * side))
            z = int(round(cz + az * along + pz * offset * side))
            x = max(1, min(width - 2, x))
            z = max(1, min(depth - 2, z))
            blocks[(x, 0, z)] = palette["ground"]
            blocks[(x, 1, z)] = palette["tool"]
            work_positions.append([x, 1, z])

        discard_cells: set[tuple[int, int]] = set()
        discard_target = {"small": 12, "medium": 28, "large": 52}[scale]
        for _ in range(discard_target):
            anchor = discard_rng.choice(work_positions)
            vx, vz = anchor[0] - cx, anchor[2] - cz
            mag = max(1.0, math.hypot(vx, vz))
            vx, vz = vx / mag, vz / mag
            distance = discard_rng.uniform(2.0, 6.0 if scale == "small" else 8.0 if scale == "medium" else 11.0)
            lateral = discard_rng.gauss(0.0, 1.8)
            x = int(round(anchor[0] + vx * distance - vz * lateral))
            z = int(round(anchor[2] + vz * distance + vx * lateral))
            if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                continue
            blocks[(x, 1, z)] = palette["bone"] if discard_rng.random() < 0.42 else palette["discard"]
            discard_cells.add((x, z))

        marrow_points: list[list[int]] = []
        if scale in {"medium", "large"}:
            marrow_count = 4 if scale == "medium" else 8
            if culture_profile == "marrow_intensive":
                marrow_count += 4
            anchor = work_rng.choice(work_positions)
            for _ in range(marrow_count):
                x = max(1, min(width - 2, anchor[0] + marrow_rng.randint(-2, 2)))
                z = max(1, min(depth - 2, anchor[2] + marrow_rng.randint(-2, 2)))
                blocks[(x, 1, z)] = palette["tool"] if marrow_rng.random() < 0.45 else palette["bone"]
                marrow_points.append([x, 1, z])

        staging_side = 1 if culture_profile == "transport_focused" or staging_rng.random() < 0.5 else -1
        staging_center = (
            max(2, min(width - 3, int(round(cx + ax * (carcass_length * 0.15) + px * staging_side * (width * 0.28))))),
            max(2, min(depth - 3, int(round(cz + az * (carcass_length * 0.15) + pz * staging_side * (depth * 0.28))))),
        )
        staging_points: list[list[int]] = []
        staging_count = {"small": 2, "medium": 4, "large": 7}[scale] + (2 if culture_profile == "transport_focused" else 0)
        for _ in range(staging_count):
            x = max(1, min(width - 2, staging_center[0] + staging_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, staging_center[1] + staging_rng.randint(-2, 2)))
            blocks[(x, 1, z)] = palette["bone"]
            staging_points.append([x, 1, z])

        edge = (
            1 if staging_center[0] < cx else width - 2,
            max(1, min(depth - 2, staging_center[1] + route_rng.randint(-3, 3))),
        )
        carry_route: list[list[int]] = []
        for x, z in self._line(staging_center, edge):
            blocks[(x, 0, z)] = palette["ground"]
            if (x, z) in discard_cells and route_rng.random() < 0.9:
                blocks.pop((x, 1, z), None)
                discard_cells.discard((x, z))
            carry_route.append([x, 0, z])

        hide_points: list[list[int]] = []
        hide_anchor = (
            max(1, min(width - 2, cx - int(round(px * width * 0.32)))),
            max(1, min(depth - 2, cz - int(round(pz * depth * 0.32)))),
        )
        for _ in range({"small": 2, "medium": 4, "large": 6}[scale]):
            x = max(1, min(width - 2, hide_anchor[0] + layout_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, hide_anchor[1] + layout_rng.randint(-2, 2)))
            blocks[(x, 1, z)] = palette["hide"]
            hide_points.append([x, 1, z])

        hearth = None
        hearth_allowed = culture_profile == "consumption_biased" or condition in {"active", "repeated"}
        if hearth_allowed and hearth_rng.random() < (0.55 if culture_profile == "consumption_biased" else 0.22):
            hx = max(2, min(width - 3, staging_center[0] + hearth_rng.randint(-3, 3)))
            hz = max(2, min(depth - 3, staging_center[1] + hearth_rng.randint(-3, 3)))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"
            hearth = [hx, 1, hz]

        if condition == "repeated":
            for _ in range({"small": 5, "medium": 12, "large": 22}[scale]):
                anchor = condition_rng.choice(work_positions)
                x = max(1, min(width - 2, anchor[0] + condition_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, anchor[2] + condition_rng.randint(-3, 3)))
                blocks[(x, 1, z)] = palette["bone"] if condition_rng.random() < 0.5 else palette["discard"]
                discard_cells.add((x, z))
        elif condition in {"abandoned", "weathered"}:
            for pos in list(blocks):
                if pos[1] == 1 and blocks[pos] == palette["hide"] and condition_rng.random() < 0.75:
                    blocks.pop(pos, None)
            if condition == "weathered" and biome_family in {"temperate", "boreal", "tropical"}:
                for _ in range(max(2, len(discard_cells) // 6)):
                    x, z = condition_rng.choice(tuple(discard_cells))
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = "minecraft:moss_carpet"
        elif condition == "scavenger_reworked":
            candidates = [p for p in list(blocks) if p[1] == 1 and blocks[p] == palette["bone"]]
            condition_rng.shuffle(candidates)
            for pos in candidates[: max(1, len(candidates) // 4)]:
                block = blocks.pop(pos)
                x = max(1, min(width - 2, pos[0] + condition_rng.randint(-5, 5)))
                z = max(1, min(depth - 2, pos[2] + condition_rng.randint(-5, 5)))
                blocks[(x, 1, z)] = block
        elif condition == "sediment_reworked":
            for pos in list(blocks):
                if pos[1] == 1 and condition_rng.random() < 0.18:
                    blocks[pos] = palette["ground"]

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
            if 0 <= x < width and 0 <= y < height and 0 <= z < depth
        ]

        qualification = {
            "single_primary_processing_center": len(carcass_cells) >= 3,
            "work_positions_present": len(work_positions) >= 1,
            "directional_discard_present": len(discard_cells) >= 4,
            "transport_staging_present": len(staging_points) >= 2,
            "carry_route_present": len(carry_route) >= 2,
            "circulation_preserved": all(tuple(p[::2]) not in discard_cells for p in carry_route),
            "marrow_zone_required_by_scale": scale == "small" or bool(marrow_points),
            "hearth_subordinate": hearth is None or len(carcass_cells) + len(discard_cells) > 8,
            "below_large_carcass_scale": width <= 39 and depth <= 33,
            "no_permanent_architecture": True,
            "processing_primary": len(carcass_cells) + len(discard_cells) > len(hide_points),
        }
        if not all(qualification.values()):
            raise ButcherySiteGenerationError(f"E01-012 qualification failed: {qualification}")

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
                "terrain_mode": "surface_task_site_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "material_semantics": {
                    "bone": "carcass_or_bone_role_proxy",
                    "stain": "organic_processing_stain_role_proxy",
                    "hide": "hide_or_offcut_role_proxy",
                    "tool": "stone_tool_or_hammerstone_role_proxy",
                },
                "carcass_cells": carcass_cells,
                "work_positions": work_positions,
                "discard_cell_count": len(discard_cells),
                "marrow_points": marrow_points,
                "staging_points": staging_points,
                "carry_route": carry_route,
                "hide_offcut_points": hide_points,
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
            max_distance=80,
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
