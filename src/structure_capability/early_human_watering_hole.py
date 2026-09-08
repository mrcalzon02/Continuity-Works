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

CATALOG_ID = "E01-016"
STRUCTURE_ID = "continuityworks:e01_016_watering_hole_camp"
FAMILY_ID = "continuityworks:early_human_water_access"
START_POOL = "continuityworks:early_human/e01_016_watering_hole_camp"
SCALES = ("small", "medium", "large")
SPACING = 136
SEPARATION = 100
SALT = 101016


class WateringHoleCampGenerationError(ValueError):
    pass


class WateringHoleCampGenerator:
    """Deterministic Stage-2/3 implementation for E01-016."""

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
            "temperate": {"ground": "minecraft:coarse_dirt", "bank": "minecraft:dirt", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "windbreak": "minecraft:oak_log", "foliage": "minecraft:oak_leaves"},
            "boreal": {"ground": "minecraft:podzol", "bank": "minecraft:coarse_dirt", "tool": "minecraft:stone", "refuse": "minecraft:gravel", "windbreak": "minecraft:spruce_log", "foliage": "minecraft:spruce_leaves"},
            "tundra": {"ground": "minecraft:gravel", "bank": "minecraft:stone", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "windbreak": "minecraft:spruce_log", "foliage": "minecraft:spruce_leaves"},
            "savanna": {"ground": "minecraft:coarse_dirt", "bank": "minecraft:coarse_dirt", "tool": "minecraft:granite", "refuse": "minecraft:gravel", "windbreak": "minecraft:acacia_log", "foliage": "minecraft:acacia_leaves"},
            "arid": {"ground": "minecraft:sand", "bank": "minecraft:red_sand", "tool": "minecraft:stone", "refuse": "minecraft:gravel", "windbreak": "minecraft:dead_bush", "foliage": "minecraft:dead_bush"},
            "tropical": {"ground": "minecraft:rooted_dirt", "bank": "minecraft:dirt", "tool": "minecraft:andesite", "refuse": "minecraft:gravel", "windbreak": "minecraft:jungle_log", "foliage": "minecraft:jungle_leaves"},
            "coastal_transition": {"ground": "minecraft:gravel", "bank": "minecraft:sand", "tool": "minecraft:cobblestone", "refuse": "minecraft:gravel", "windbreak": "minecraft:oak_log", "foliage": "minecraft:oak_leaves"},
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
        culture_profile: str = "short_stay",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise WateringHoleCampGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {"active", "recent", "repeated", "abandoned", "weathered", "flood_reworked", "scavenger_reworked", "repurposed"}
        if condition not in valid_conditions:
            raise WateringHoleCampGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {"cautious_observation", "short_stay", "repeated_return", "carcass_opportunism"}
        if culture_profile not in valid_cultures:
            raise WateringHoleCampGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (31, 8, 27), "medium": (43, 9, 37), "large": (57, 10, 49)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "layout")
        water_rng = self._rng(seed, "water_margin")
        camp_rng = self._rng(seed, "camp_terrace")
        spoor_rng = self._rng(seed, "animal_spoor")
        refuse_rng = self._rng(seed, "refuse")
        shelter_rng = self._rng(seed, "windbreak")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi * 2.0)
        water_x, water_z = math.cos(angle), math.sin(angle)
        dry_x, dry_z = -water_x, -water_z
        side_x, side_z = -water_z, water_x

        water_distance = {"small": 8, "medium": 11, "large": 15}[scale]
        water_center = (
            max(4, min(width - 5, int(round(cx + water_x * water_distance)))),
            max(4, min(depth - 5, int(round(cz + water_z * water_distance)))),
        )
        water_rx = {"small": 5, "medium": 7, "large": 10}[scale]
        water_rz = {"small": 4, "medium": 6, "large": 8}[scale]
        if biome_family == "arid":
            water_rx = max(3, water_rx - 2)
            water_rz = max(3, water_rz - 2)

        water_cells: list[list[int]] = []
        bank_cells: list[list[int]] = []
        for dx in range(-water_rx - 1, water_rx + 2):
            for dz in range(-water_rz - 1, water_rz + 2):
                wobble = water_rng.uniform(-0.18, 0.18)
                norm = (dx / max(1, water_rx)) ** 2 + (dz / max(1, water_rz)) ** 2
                x, z = water_center[0] + dx, water_center[1] + dz
                if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                    continue
                if norm <= 1.0 + wobble:
                    blocks[(x, 0, z)] = "minecraft:water"
                    water_cells.append([x, 0, z])
                elif norm <= 1.42:
                    blocks[(x, 0, z)] = palette["bank"]
                    bank_cells.append([x, 0, z])

        setback = {"small": 6, "medium": 8, "large": 10}[scale]
        if culture_profile == "cautious_observation":
            setback += 3
        terrace_center = (
            max(4, min(width - 5, int(round(water_center[0] + dry_x * (water_rz + setback))))),
            max(4, min(depth - 5, int(round(water_center[1] + dry_z * (water_rz + setback))))),
        )
        terrace_radius = {"small": 4, "medium": 6, "large": 8}[scale]
        terrace_cells: list[list[int]] = []
        for _ in range({"small": 34, "medium": 62, "large": 96}[scale]):
            x = max(2, min(width - 3, terrace_center[0] + camp_rng.randint(-terrace_radius, terrace_radius)))
            z = max(2, min(depth - 3, terrace_center[1] + camp_rng.randint(-terrace_radius, terrace_radius)))
            if math.dist((x, z), terrace_center) <= terrace_radius + camp_rng.uniform(-0.3, 1.0):
                blocks[(x, 0, z)] = palette["ground"]
                terrace_cells.append([x, 0, z])

        water_access = min(water_cells, key=lambda p: abs(p[0] - terrace_center[0]) + abs(p[2] - terrace_center[1]))
        water_access_lane: list[list[int]] = []
        for x, z in self._line(terrace_center, (water_access[0], water_access[2])):
            if [x, 0, z] not in water_cells:
                blocks[(x, 0, z)] = palette["ground"]
            blocks.pop((x, 1, z), None)
            water_access_lane.append([x, 0, z])

        dry_edge_candidates = [(1, terrace_center[1]), (width - 2, terrace_center[1]), (terrace_center[0], 1), (terrace_center[0], depth - 2)]
        dry_edge_candidates.sort(key=lambda p: -((p[0] - water_center[0]) * water_x + (p[1] - water_center[1]) * water_z))
        approach_edge = dry_edge_candidates[0]
        external_approach_lane: list[list[int]] = []
        for x, z in self._line(terrace_center, approach_edge):
            blocks[(x, 0, z)] = palette["ground"]
            blocks.pop((x, 1, z), None)
            external_approach_lane.append([x, 0, z])

        hearth_center = (
            max(3, min(width - 4, int(round(terrace_center[0] + side_x * 2)))),
            max(3, min(depth - 4, int(round(terrace_center[1] + side_z * 2)))),
        )
        blocks[(hearth_center[0], 0, hearth_center[1])] = "minecraft:coal_block"
        blocks[(hearth_center[0], 1, hearth_center[1])] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"
        rest_points: list[list[int]] = []
        for _ in range({"small": 4, "medium": 7, "large": 11}[scale]):
            x = max(2, min(width - 3, hearth_center[0] + camp_rng.randint(-3, 3)))
            z = max(2, min(depth - 3, hearth_center[1] + camp_rng.randint(-3, 3)))
            if (x, z) != hearth_center:
                blocks[(x, 0, z)] = palette["ground"]
                rest_points.append([x, 0, z])

        activity_points: list[list[int]] = []
        activity_count = {"small": 4, "medium": 7, "large": 11}[scale]
        for _ in range(activity_count):
            x = max(2, min(width - 3, terrace_center[0] + camp_rng.randint(-terrace_radius, terrace_radius)))
            z = max(2, min(depth - 3, terrace_center[1] + camp_rng.randint(-terrace_radius, terrace_radius)))
            blocks[(x, 1, z)] = palette["tool"] if camp_rng.random() < 0.45 else "minecraft:bone_block"
            activity_points.append([x, 1, z])

        windbreak_points: list[list[int]] = []
        windbreak_count = {"small": 3, "medium": 5, "large": 7}[scale]
        for i in range(windbreak_count):
            lateral = (i - (windbreak_count - 1) / 2) * 2
            x = max(2, min(width - 3, int(round(terrace_center[0] + dry_x * 3 + side_x * lateral))))
            z = max(2, min(depth - 3, int(round(terrace_center[1] + dry_z * 3 + side_z * lateral))))
            blocks[(x, 1, z)] = palette["windbreak"]
            if biome_family != "arid" and shelter_rng.random() < 0.55:
                blocks[(x, 2, z)] = palette["foliage"]
            windbreak_points.append([x, 1, z])

        refuse_center = (
            max(3, min(width - 4, int(round(terrace_center[0] + dry_x * (terrace_radius + 4) - side_x * 3)))),
            max(3, min(depth - 4, int(round(terrace_center[1] + dry_z * (terrace_radius + 4) - side_z * 3)))),
        )
        refuse_count = {"small": 7, "medium": 14, "large": 22}[scale]
        if culture_profile == "short_stay":
            refuse_count = max(4, refuse_count // 2)
        elif culture_profile == "repeated_return":
            refuse_count += 8
        refuse_points: list[list[int]] = []
        for _ in range(refuse_count):
            x = max(1, min(width - 2, refuse_center[0] + refuse_rng.randint(-4, 4)))
            z = max(1, min(depth - 2, refuse_center[1] + refuse_rng.randint(-4, 4)))
            blocks[(x, 1, z)] = refuse_rng.choice((palette["refuse"], "minecraft:bone_block"))
            refuse_points.append([x, 1, z])

        spoor_center = (
            max(2, min(width - 3, int(round(water_center[0] + side_x * (water_rx + 3))))),
            max(2, min(depth - 3, int(round(water_center[1] + side_z * (water_rz + 3))))),
        )
        spoor_count = {"small": 7, "medium": 12, "large": 18}[scale]
        if culture_profile == "cautious_observation":
            spoor_count += 8
        spoor_points: list[list[int]] = []
        for _ in range(spoor_count):
            x = max(1, min(width - 2, spoor_center[0] + spoor_rng.randint(-5, 5)))
            z = max(1, min(depth - 2, spoor_center[1] + spoor_rng.randint(-5, 5)))
            if [x, 0, z] not in water_cells:
                blocks[(x, 0, z)] = palette["ground"]
                spoor_points.append([x, 0, z])

        carcass_points: list[list[int]] = []
        if culture_profile == "carcass_opportunism" and scale in {"medium", "large"}:
            carcass_center = (
                max(3, min(width - 4, terrace_center[0] - int(round(side_x * (terrace_radius + 3))))),
                max(3, min(depth - 4, terrace_center[1] - int(round(side_z * (terrace_radius + 3))))),
            )
            for _ in range(6 if scale == "medium" else 10):
                x = max(2, min(width - 3, carcass_center[0] + camp_rng.randint(-2, 2)))
                z = max(2, min(depth - 3, carcass_center[1] + camp_rng.randint(-2, 2)))
                blocks[(x, 1, z)] = "minecraft:bone_block"
                carcass_points.append([x, 1, z])

        if condition == "repeated":
            for _ in range({"small": 9, "medium": 18, "large": 30}[scale]):
                x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-terrace_radius - 2, terrace_radius + 2)))
                z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-terrace_radius - 2, terrace_radius + 2)))
                blocks[(x, 0, z)] = palette["ground"]
        elif condition == "abandoned":
            for point in windbreak_points[::2]:
                blocks.pop(tuple(point), None)
        elif condition == "weathered":
            for key in list(blocks):
                if key[1] > 0 and condition_rng.random() < 0.14:
                    blocks.pop(key, None)
            if biome_family in {"temperate", "boreal", "tropical"}:
                for _ in range(5):
                    x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-terrace_radius, terrace_radius)))
                    z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-terrace_radius, terrace_radius)))
                    blocks[(x, 0, z)] = "minecraft:moss_block"
        elif condition == "flood_reworked":
            for _ in range(max(4, len(bank_cells) // 5)):
                point = condition_rng.choice(bank_cells)
                blocks[(point[0], 0, point[2])] = "minecraft:water" if condition_rng.random() < 0.55 else palette["bank"]
        elif condition == "scavenger_reworked":
            for _ in range({"small": 4, "medium": 7, "large": 11}[scale]):
                x = condition_rng.choice((1, width - 2)) if condition_rng.random() < 0.5 else condition_rng.randint(1, width - 2)
                z = condition_rng.randint(1, depth - 2) if x in {1, width - 2} else condition_rng.choice((1, depth - 2))
                blocks[(x, 1, z)] = "minecraft:bone_block"
        elif condition == "repurposed":
            x = max(2, min(width - 3, terrace_center[0] + condition_rng.randint(-3, 3)))
            z = max(2, min(depth - 3, terrace_center[1] + condition_rng.randint(-3, 3)))
            blocks[(x, 1, z)] = palette["tool"]

        # Restore critical circulation after all optional transforms.
        for x, _, z in water_access_lane + external_approach_lane:
            if [x, 0, z] not in water_cells:
                blocks[(x, 0, z)] = palette["ground"]
            blocks.pop((x, 1, z), None)

        block_list = [{"pos": [x, y, z], "block": block} for (x, y, z), block in sorted(blocks.items())]

        water_set = {(p[0], p[2]) for p in water_cells}
        terrace_water_distance = min(abs(terrace_center[0] - x) + abs(terrace_center[1] - z) for x, z in water_set)
        water_fraction = len(water_cells) / float(width * depth)
        qualification = {
            "water_cell_count": len(water_cells),
            "water_fraction": water_fraction,
            "terrace_cell_count": len(terrace_cells),
            "terrace_water_setback": terrace_water_distance,
            "water_access_lane_length": len(water_access_lane),
            "external_approach_lane_length": len(external_approach_lane),
            "rest_point_count": len(rest_points),
            "refuse_point_count": len(refuse_points),
            "spoor_point_count": len(spoor_points),
            "carcass_point_count": len(carcass_points),
            "engineered_water_control": False,
            "has_dominant_carcass_axis": False,
            "has_river_linear_harvest_program": False,
        }
        qualification["passes"] = all((
            qualification["water_cell_count"] >= 20,
            qualification["water_fraction"] < 0.32,
            qualification["terrace_cell_count"] >= 12,
            qualification["terrace_water_setback"] >= 3,
            qualification["water_access_lane_length"] >= 3,
            qualification["external_approach_lane_length"] >= 3,
            qualification["rest_point_count"] >= 2,
            qualification["refuse_point_count"] >= 3,
            qualification["spoor_point_count"] >= 3,
            not qualification["engineered_water_control"],
            not qualification["has_dominant_carcass_axis"],
            not qualification["has_river_linear_harvest_program"],
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
                "terrain_mode": "bounded_freshwater_margin_camp",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "water_center": list(water_center),
                "water_cells": water_cells,
                "bank_cells": bank_cells,
                "terrace_center": list(terrace_center),
                "terrace_cells": terrace_cells,
                "water_access_lane": water_access_lane,
                "external_approach_lane": external_approach_lane,
                "hearth": [hearth_center[0], 1, hearth_center[1]],
                "rest_points": rest_points,
                "activity_points": activity_points,
                "windbreak_points": windbreak_points,
                "refuse_points": refuse_points,
                "spoor_points": spoor_points,
                "carcass_points": carcass_points,
                "material_semantics": {
                    "water": "bounded_natural_freshwater_margin_proxy",
                    "ground_family": "camp_terrace_bank_or_trample_proxy",
                    "stone_family": "simple_tool_or_hearth_ring_proxy",
                    "wood_foliage": "temporary_windbreak_debris_proxy",
                    "bone_gravel": "optional_carcass_or_refuse_proxy",
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
        structure_set = random_spread_structure_set(STRUCTURE_ID, spacing=SPACING, separation=SEPARATION, salt=SALT)
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
            "compatibility": {"mode": "additive_non_destructive", "family_tight_composition_requires_same_parent_reservation": True},
            "validation_findings": findings,
        }
