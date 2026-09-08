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

CATALOG_ID = "E01-017"
STRUCTURE_ID = "continuityworks:e01_017_riverbank_foraging_camp"
FAMILY_ID = "continuityworks:early_human_water_access"
START_POOL = "continuityworks:early_human/e01_017_riverbank_foraging_camp"
SCALES = ("small", "medium", "large")
SPACING = 140
SEPARATION = 104
SALT = 101017


class RiverbankForagingCampGenerationError(ValueError):
    pass


class RiverbankForagingCampGenerator:
    """Deterministic Stage-2/3 implementation for E01-017."""

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
            "temperate": {"ground": "minecraft:coarse_dirt", "bank": "minecraft:dirt", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "plant": "minecraft:short_grass", "windbreak": "minecraft:oak_log"},
            "boreal": {"ground": "minecraft:podzol", "bank": "minecraft:coarse_dirt", "tool": "minecraft:stone", "refuse": "minecraft:gravel", "plant": "minecraft:fern", "windbreak": "minecraft:spruce_log"},
            "tundra": {"ground": "minecraft:gravel", "bank": "minecraft:stone", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "plant": "minecraft:short_grass", "windbreak": "minecraft:spruce_log"},
            "savanna": {"ground": "minecraft:coarse_dirt", "bank": "minecraft:dirt", "tool": "minecraft:granite", "refuse": "minecraft:gravel", "plant": "minecraft:short_grass", "windbreak": "minecraft:acacia_log"},
            "arid": {"ground": "minecraft:sand", "bank": "minecraft:red_sand", "tool": "minecraft:stone", "refuse": "minecraft:gravel", "plant": "minecraft:dead_bush", "windbreak": "minecraft:dead_bush"},
            "tropical": {"ground": "minecraft:rooted_dirt", "bank": "minecraft:dirt", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "plant": "minecraft:fern", "windbreak": "minecraft:jungle_log"},
            "coastal_transition": {"ground": "minecraft:gravel", "bank": "minecraft:sand", "tool": "minecraft:cobblestone", "refuse": "minecraft:gravel", "plant": "minecraft:short_grass", "windbreak": "minecraft:oak_log"},
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
        culture_profile: str = "broad_spectrum_foraging",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise RiverbankForagingCampGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {
            "active", "recent", "repeated", "abandoned", "weathered",
            "flood_reworked", "sediment_reworked", "repurposed",
        }
        if condition not in valid_conditions:
            raise RiverbankForagingCampGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {
            "broad_spectrum_foraging", "root_seed_processing",
            "shoreline_gathering", "repeated_return",
        }
        if culture_profile not in valid_cultures:
            raise RiverbankForagingCampGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (29, 8, 25), "medium": (41, 9, 35), "large": (55, 10, 47)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "layout")
        river_rng = self._rng(seed, "river")
        camp_rng = self._rng(seed, "camp")
        forage_rng = self._rng(seed, "forage")
        refuse_rng = self._rng(seed, "refuse")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi)
        axis_x, axis_z = math.cos(angle), math.sin(angle)
        dry_x, dry_z = -axis_z, axis_x
        if layout_rng.random() < 0.5:
            dry_x, dry_z = -dry_x, -dry_z

        river_length = {"small": 23, "medium": 33, "large": 45}[scale]
        river_half_width = {"small": 2, "medium": 3, "large": 4}[scale]
        if biome_family == "arid":
            river_half_width = max(1, river_half_width - 1)
        river_center = (
            max(5, min(width - 6, int(round(cx - dry_x * width * 0.20)))),
            max(5, min(depth - 6, int(round(cz - dry_z * depth * 0.20)))),
        )

        water_cells: set[tuple[int, int]] = set()
        bank_cells: set[tuple[int, int]] = set()
        bank_anchors: list[tuple[int, int]] = []
        for step in range(-(river_length // 2), river_length // 2 + 1):
            meander = math.sin(step * 0.35 + river_rng.uniform(-0.25, 0.25)) * 1.3
            center_x = int(round(river_center[0] + axis_x * step + dry_x * meander))
            center_z = int(round(river_center[1] + axis_z * step + dry_z * meander))
            for lateral in range(-river_half_width - 1, river_half_width + 2):
                x = int(round(center_x + dry_x * lateral))
                z = int(round(center_z + dry_z * lateral))
                if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                    continue
                if abs(lateral) <= river_half_width:
                    blocks[(x, 0, z)] = "minecraft:water"
                    water_cells.add((x, z))
                else:
                    if (x, z) not in water_cells:
                        blocks[(x, 0, z)] = palette["bank"]
                        bank_cells.add((x, z))
                    if lateral > 0:
                        bank_anchors.append((x, z))

        setback = {"small": 5, "medium": 7, "large": 9}[scale]
        terrace_center = (
            max(4, min(width - 5, int(round(river_center[0] + dry_x * (river_half_width + setback))))),
            max(4, min(depth - 5, int(round(river_center[1] + dry_z * (river_half_width + setback))))),
        )
        terrace_radius = {"small": 4, "medium": 6, "large": 8}[scale]
        terrace_cells: set[tuple[int, int]] = set()
        for _ in range({"small": 38, "medium": 68, "large": 108}[scale]):
            along = camp_rng.randint(-terrace_radius, terrace_radius)
            lateral = camp_rng.randint(-max(2, terrace_radius // 2), max(2, terrace_radius // 2))
            x = int(round(terrace_center[0] + axis_x * along + dry_x * lateral))
            z = int(round(terrace_center[1] + axis_z * along + dry_z * lateral))
            if 2 <= x < width - 2 and 2 <= z < depth - 2 and (x, z) not in water_cells:
                blocks[(x, 0, z)] = palette["ground"]
                terrace_cells.add((x, z))

        nearest_water = min(water_cells, key=lambda p: abs(p[0] - terrace_center[0]) + abs(p[1] - terrace_center[1]))
        water_access_lane: list[list[int]] = []
        for x, z in self._line(terrace_center, nearest_water):
            if (x, z) not in water_cells:
                blocks[(x, 0, z)] = palette["ground"]
            blocks.pop((x, 1, z), None)
            water_access_lane.append([x, 0, z])

        return_count = {"small": 2, "medium": 3, "large": 5}[scale]
        if culture_profile == "shoreline_gathering":
            return_count = min(5, return_count + 1)
        sorted_anchors = sorted(
            set(bank_anchors),
            key=lambda p: (p[0] - terrace_center[0]) * axis_x + (p[1] - terrace_center[1]) * axis_z,
        )
        if not sorted_anchors:
            raise RiverbankForagingCampGenerationError("river bank anchors could not be generated")
        anchor_indexes = [int(round(i * (len(sorted_anchors) - 1) / max(1, return_count - 1))) for i in range(return_count)]
        foraging_return_paths: list[list[list[int]]] = []
        for index in anchor_indexes:
            anchor = sorted_anchors[index]
            offset = forage_rng.randint(-2, 2)
            target = (
                max(2, min(width - 3, int(round(terrace_center[0] + axis_x * offset)))),
                max(2, min(depth - 3, int(round(terrace_center[1] + axis_z * offset)))),
            )
            path: list[list[int]] = []
            for x, z in self._line(anchor, target):
                if (x, z) not in water_cells:
                    blocks[(x, 0, z)] = palette["ground"]
                blocks.pop((x, 1, z), None)
                path.append([x, 0, z])
            foraging_return_paths.append(path)

        pocket_ranges = {"small": (1, 2), "medium": (2, 3), "large": (3, 5)}
        pocket_count = forage_rng.randint(*pocket_ranges[scale])
        if culture_profile in {"root_seed_processing", "repeated_return"}:
            pocket_count = pocket_ranges[scale][1]
        processing_pockets: list[dict[str, Any]] = []
        staging_points: list[list[int]] = []
        activity_stances: list[list[int]] = []
        for index in range(pocket_count):
            fraction = (index + 1) / (pocket_count + 1)
            along = int(round(-terrace_radius + fraction * terrace_radius * 2))
            px = max(3, min(width - 4, int(round(terrace_center[0] + axis_x * along))))
            pz = max(3, min(depth - 4, int(round(terrace_center[1] + axis_z * along))))
            local_staging: list[list[int]] = []
            local_tools: list[list[int]] = []
            for _ in range(4 + (2 if culture_profile == "root_seed_processing" else 0)):
                x = max(2, min(width - 3, px + forage_rng.randint(-2, 2)))
                z = max(2, min(depth - 3, pz + forage_rng.randint(-2, 2)))
                if (x, z) in water_cells:
                    continue
                blocks[(x, 0, z)] = palette["ground"]
                if forage_rng.random() < 0.55:
                    blocks[(x, 1, z)] = palette["plant"]
                    local_staging.append([x, 1, z])
                    staging_points.append([x, 1, z])
                else:
                    blocks[(x, 1, z)] = palette["tool"]
                    local_tools.append([x, 1, z])
            sx = max(2, min(width - 3, int(round(px + dry_x * 2))))
            sz = max(2, min(depth - 3, int(round(pz + dry_z * 2))))
            if (sx, sz) not in water_cells:
                blocks[(sx, 0, sz)] = palette["ground"]
                blocks.pop((sx, 1, sz), None)
            activity_stances.append([sx, 0, sz])
            processing_pockets.append({
                "index": index,
                "center": [px, 0, pz],
                "stance": [sx, 0, sz],
                "staging": local_staging,
                "tools": local_tools,
            })

        hearth = (
            max(3, min(width - 4, int(round(terrace_center[0] + dry_x * 2 - axis_x * 2)))),
            max(3, min(depth - 4, int(round(terrace_center[1] + dry_z * 2 - axis_z * 2)))),
        )
        blocks[(hearth[0], 0, hearth[1])] = "minecraft:coal_block"
        blocks[(hearth[0], 1, hearth[1])] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"

        refuse_center = (
            max(3, min(width - 4, int(round(terrace_center[0] + dry_x * (terrace_radius + 4))))),
            max(3, min(depth - 4, int(round(terrace_center[1] + dry_z * (terrace_radius + 4))))),
        )
        refuse_target = {"small": 7, "medium": 13, "large": 21}[scale]
        if culture_profile == "repeated_return":
            refuse_target += 8
        refuse_points: list[list[int]] = []
        for _ in range(refuse_target):
            x = max(1, min(width - 2, refuse_center[0] + refuse_rng.randint(-4, 4)))
            z = max(1, min(depth - 2, refuse_center[1] + refuse_rng.randint(-4, 4)))
            if (x, z) not in water_cells:
                blocks[(x, 1, z)] = refuse_rng.choice((palette["refuse"], "minecraft:bone_block"))
                refuse_points.append([x, 1, z])

        windbreak_points: list[list[int]] = []
        for offset in (-2, 0, 2):
            if camp_rng.random() < 0.68:
                x = max(2, min(width - 3, int(round(terrace_center[0] + dry_x * 4 + axis_x * offset))))
                z = max(2, min(depth - 3, int(round(terrace_center[1] + dry_z * 4 + axis_z * offset))))
                blocks[(x, 1, z)] = palette["windbreak"]
                windbreak_points.append([x, 1, z])

        if condition == "repeated":
            for _ in range({"small": 6, "medium": 12, "large": 20}[scale]):
                x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-terrace_radius, terrace_radius)))
                z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-terrace_radius, terrace_radius)))
                if (x, z) not in water_cells:
                    blocks[(x, 0, z)] = palette["ground"]
        elif condition == "abandoned":
            for point in staging_points[::2]:
                blocks.pop(tuple(point), None)
        elif condition == "weathered":
            for key in list(blocks):
                if key[1] == 1 and condition_rng.random() < 0.14:
                    blocks.pop(key, None)
            if biome_family in {"temperate", "boreal", "tropical"}:
                for _ in range({"small": 3, "medium": 5, "large": 8}[scale]):
                    x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-terrace_radius, terrace_radius)))
                    z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-terrace_radius, terrace_radius)))
                    if (x, z) not in water_cells:
                        blocks[(x, 0, z)] = "minecraft:moss_block"
        elif condition == "flood_reworked":
            for _ in range({"small": 8, "medium": 14, "large": 24}[scale]):
                anchor = condition_rng.choice(sorted_anchors)
                x = max(1, min(width - 2, anchor[0] + condition_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, anchor[1] + condition_rng.randint(-3, 3)))
                if (x, z) not in water_cells:
                    blocks[(x, 0, z)] = palette["bank"]
        elif condition == "sediment_reworked":
            cover = "minecraft:sand" if biome_family in {"arid", "coastal_transition"} else palette["bank"]
            for _ in range({"small": 8, "medium": 14, "large": 22}[scale]):
                x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-terrace_radius, terrace_radius)))
                z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-terrace_radius, terrace_radius)))
                if (x, z) not in water_cells:
                    blocks[(x, 1, z)] = cover
        elif condition == "repurposed":
            rx = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-3, 3)))
            rz = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-3, 3)))
            blocks[(rx, 1, rz)] = palette["tool"]

        # Restore critical paths after all condition transforms.
        for path in [water_access_lane, *foraging_return_paths]:
            for point in path:
                x, z = point[0], point[2]
                if (x, z) not in water_cells:
                    blocks[(x, 0, z)] = palette["ground"]
                blocks.pop((x, 1, z), None)

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]
        axial = [
            (x - river_center[0]) * axis_x + (z - river_center[1]) * axis_z
            for x, z in water_cells
        ]
        lateral = [
            (x - river_center[0]) * dry_x + (z - river_center[1]) * dry_z
            for x, z in water_cells
        ]
        water_major_span = max(axial) - min(axial) + 1.0
        water_minor_span = max(lateral) - min(lateral) + 1.0
        qualification = {
            "water_cell_count": len(water_cells),
            "water_major_span": water_major_span,
            "water_minor_span": water_minor_span,
            "river_is_linear": water_major_span >= max(10.0, water_minor_span * 2.0),
            "terrace_cell_count": len(terrace_cells),
            "water_access_lane_length": len(water_access_lane),
            "return_path_count": len(foraging_return_paths),
            "processing_pocket_count": len(processing_pockets),
            "staging_count": len(staging_points),
            "activity_stance_count": len(activity_stances),
            "refuse_count": len(refuse_points),
            "has_permanent_architecture": False,
            "hearth_is_subordinate": len(processing_pockets) >= 1 and len(foraging_return_paths) >= 2,
        }
        qualification["passes"] = all((
            qualification["river_is_linear"],
            qualification["terrace_cell_count"] >= 8,
            qualification["water_access_lane_length"] >= 2,
            qualification["return_path_count"] >= 2,
            qualification["processing_pocket_count"] >= 1,
            qualification["staging_count"] >= 1,
            qualification["activity_stance_count"] >= qualification["processing_pocket_count"],
            qualification["refuse_count"] >= 3,
            not qualification["has_permanent_architecture"],
            qualification["hearth_is_subordinate"],
        ))

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
                "terrain_mode": "riverbank_surface_task_landscape",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "water_cells": [list(p) for p in sorted(water_cells)],
                "bank_cells": [list(p) for p in sorted(bank_cells)],
                "terrace_center": list(terrace_center),
                "water_access_lane": water_access_lane,
                "foraging_return_paths": foraging_return_paths,
                "processing_pockets": processing_pockets,
                "staging_points": staging_points,
                "activity_stances": activity_stances,
                "refuse_points": refuse_points,
                "windbreak_points": windbreak_points,
                "hearth": [hearth[0], 1, hearth[1]],
                "material_semantics": {
                    "water": "river_margin_proxy",
                    "bank_blocks": "river_bank_and_sediment_proxy",
                    "plant_blocks": "gathered_or_riparian_vegetation_proxy",
                    "stone_family": "expedient_processing_tool_proxy",
                    "bone_or_gravel": "mixed_food_processing_refuse_proxy",
                },
                "qualification": qualification,
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
            "compatibility": {
                "mode": "additive_non_destructive",
                "family_tight_composition_requires_same_parent_reservation": True,
            },
            "validation_findings": findings,
        }
