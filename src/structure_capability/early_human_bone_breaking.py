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

CATALOG_ID = "E01-014"
STRUCTURE_ID = "continuityworks:e01_014_bone_breaking_station"
FAMILY_ID = "continuityworks:early_human_carcass_processing"
START_POOL = "continuityworks:early_human/e01_014_bone_breaking_station"
SCALES = ("small", "medium", "large")
SPACING = 120
SEPARATION = 84
SALT = 101014


class BoneBreakingStationGenerationError(ValueError):
    pass


class BoneBreakingStationGenerator:
    """Deterministic Stage-2/3 implementation for E01-014."""

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
            "temperate": {"ground": "minecraft:coarse_dirt", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "debris": "minecraft:gravel", "stain": "minecraft:red_terracotta"},
            "boreal": {"ground": "minecraft:podzol", "bone": "minecraft:bone_block", "tool": "minecraft:stone", "debris": "minecraft:gravel", "stain": "minecraft:coarse_dirt"},
            "tundra": {"ground": "minecraft:gravel", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "debris": "minecraft:stone", "stain": "minecraft:coarse_dirt"},
            "savanna": {"ground": "minecraft:coarse_dirt", "bone": "minecraft:bone_block", "tool": "minecraft:granite", "debris": "minecraft:gravel", "stain": "minecraft:red_terracotta"},
            "arid": {"ground": "minecraft:sand", "bone": "minecraft:bone_block", "tool": "minecraft:stone", "debris": "minecraft:gravel", "stain": "minecraft:red_sand"},
            "tropical": {"ground": "minecraft:dirt", "bone": "minecraft:bone_block", "tool": "minecraft:andesite", "debris": "minecraft:gravel", "stain": "minecraft:rooted_dirt"},
            "coastal": {"ground": "minecraft:gravel", "bone": "minecraft:bone_block", "tool": "minecraft:cobblestone", "debris": "minecraft:gravel", "stain": "minecraft:coarse_dirt"},
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
        culture_profile: str = "marrow_intensive",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise BoneBreakingStationGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {
            "active", "recent", "repeated", "abandoned", "weathered",
            "scavenger_reworked", "sediment_reworked", "repurposed",
        }
        if condition not in valid_conditions:
            raise BoneBreakingStationGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {
            "marrow_intensive", "single_station_reuse", "distributed_percussion",
            "clean_staging_priority",
        }
        if culture_profile not in valid_cultures:
            raise BoneBreakingStationGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (17, 6, 15), "medium": (25, 7, 21), "large": (35, 8, 29)}
        station_ranges = {"small": (1, 1), "medium": (2, 3), "large": (3, 5)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "layout")
        station_rng = self._rng(seed, "impact_stations")
        fracture_rng = self._rng(seed, "fracture_fans")
        staging_rng = self._rng(seed, "staging")
        route_rng = self._rng(seed, "carry_lane")
        hearth_rng = self._rng(seed, "hearth")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi)
        clean_x, clean_z = math.cos(angle), math.sin(angle)
        dirty_x, dirty_z = -clean_x, -clean_z
        side_x, side_z = -clean_z, clean_x

        station_count = station_rng.randint(*station_ranges[scale])
        if culture_profile == "single_station_reuse":
            station_count = 1
        elif culture_profile == "distributed_percussion":
            station_count = station_ranges[scale][1]

        impact_stations: list[list[int]] = []
        operator_stances: list[list[int]] = []
        hammerstone_points: list[list[int]] = []
        fracture_cells: list[list[int]] = []

        separation = {"small": 0, "medium": 5, "large": 7}[scale]
        offsets = [0] if station_count == 1 else [int(round((i - (station_count - 1) / 2) * separation)) for i in range(station_count)]

        for idx, lateral in enumerate(offsets):
            ix = max(3, min(width - 4, int(round(cx + side_x * lateral))))
            iz = max(3, min(depth - 4, int(round(cz + side_z * lateral))))
            blocks[(ix, 0, iz)] = palette["stain"]
            blocks[(ix, 1, iz)] = palette["tool"]
            impact_stations.append([ix, 1, iz])

            sx = max(2, min(width - 3, int(round(ix + clean_x * 2))))
            sz = max(2, min(depth - 3, int(round(iz + clean_z * 2))))
            blocks[(sx, 0, sz)] = palette["ground"]
            operator_stances.append([sx, 0, sz])

            hx = max(2, min(width - 3, int(round(ix + side_x * (2 if idx % 2 == 0 else -2)))))
            hz = max(2, min(depth - 3, int(round(iz + side_z * (2 if idx % 2 == 0 else -2)))))
            blocks[(hx, 1, hz)] = palette["tool"]
            hammerstone_points.append([hx, 1, hz])

            base_target = {"small": 16, "medium": 24, "large": 34}[scale]
            if culture_profile == "marrow_intensive":
                base_target += 10
            if culture_profile == "single_station_reuse":
                base_target += 18
            per_station = max(8, base_target // max(1, station_count))
            for _ in range(per_station):
                distance = fracture_rng.uniform(2.0, 7.0 if scale == "small" else 9.0 if scale == "medium" else 12.0)
                spread = fracture_rng.gauss(0.0, 1.8 if scale != "large" else 2.5)
                x = int(round(ix + dirty_x * distance + side_x * spread))
                z = int(round(iz + dirty_z * distance + side_z * spread))
                if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                    continue
                blocks[(x, 1, z)] = palette["bone"] if fracture_rng.random() < 0.55 else palette["debris"]
                fracture_cells.append([x, 1, z])

        stage_distance = 5 if scale == "small" else 7 if scale == "medium" else 9
        staging_center = (
            max(2, min(width - 3, int(round(cx + clean_x * stage_distance)))),
            max(2, min(depth - 3, int(round(cz + clean_z * stage_distance)))),
        )
        staging_count = {"small": 5, "medium": 9, "large": 14}[scale]
        if culture_profile == "clean_staging_priority":
            staging_count += 6
        staging_points: list[list[int]] = []
        for _ in range(staging_count):
            x = max(1, min(width - 2, staging_center[0] + staging_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, staging_center[1] + staging_rng.randint(-2, 2)))
            blocks[(x, 1, z)] = palette["bone"]
            staging_points.append([x, 1, z])

        marrow_center = (
            max(2, min(width - 3, int(round(cx + clean_x * max(2, stage_distance - 3) + side_x * 2)))),
            max(2, min(depth - 3, int(round(cz + clean_z * max(2, stage_distance - 3) + side_z * 2)))),
        )
        marrow_points: list[list[int]] = []
        for _ in range({"small": 3, "medium": 5, "large": 8}[scale]):
            x = max(1, min(width - 2, marrow_center[0] + staging_rng.randint(-1, 1)))
            z = max(1, min(depth - 2, marrow_center[1] + staging_rng.randint(-1, 1)))
            blocks[(x, 0, z)] = palette["stain"]
            if staging_rng.random() < 0.65:
                blocks[(x, 1, z)] = palette["bone"]
            marrow_points.append([x, 1, z])

        dirty_center = (
            max(2, min(width - 3, int(round(cx + dirty_x * (stage_distance + 2))))),
            max(2, min(depth - 3, int(round(cz + dirty_z * (stage_distance + 2))))),
        )
        discard_points: list[list[int]] = []
        for _ in range({"small": 6, "medium": 12, "large": 18}[scale]):
            x = max(1, min(width - 2, dirty_center[0] + fracture_rng.randint(-3, 3)))
            z = max(1, min(depth - 2, dirty_center[1] + fracture_rng.randint(-3, 3)))
            blocks[(x, 1, z)] = palette["bone"] if fracture_rng.random() < 0.45 else palette["debris"]
            discard_points.append([x, 1, z])

        target_station = impact_stations[0]
        carry_start = staging_center
        carry_end = (target_station[0], target_station[2])
        carry_lane: list[list[int]] = []
        for x, z in self._line(carry_start, carry_end):
            blocks[(x, 0, z)] = palette["ground"]
            if [x, 1, z] in fracture_cells:
                blocks.pop((x, 1, z), None)
            carry_lane.append([x, 0, z])

        hearth = None
        if condition in {"active", "repeated"} and hearth_rng.random() < 0.24:
            hx = max(2, min(width - 3, staging_center[0] + hearth_rng.randint(-3, 3)))
            hz = max(2, min(depth - 3, staging_center[1] + hearth_rng.randint(-3, 3)))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"
            hearth = [hx, 1, hz]

        if condition == "repeated":
            for _ in range({"small": 8, "medium": 16, "large": 28}[scale]):
                anchor = condition_rng.choice(impact_stations)
                x = max(1, min(width - 2, anchor[0] + condition_rng.randint(-4, 4)))
                z = max(1, min(depth - 2, anchor[2] + condition_rng.randint(-4, 4)))
                blocks[(x, 1, z)] = condition_rng.choice((palette["bone"], palette["debris"], palette["stain"]))
        elif condition == "abandoned":
            for point in staging_points[::2]:
                blocks.pop(tuple(point), None)
        elif condition == "weathered":
            for key in list(blocks):
                if key[1] == 1 and condition_rng.random() < 0.16:
                    blocks.pop(key, None)
            if biome_family in {"temperate", "boreal", "tropical"}:
                for stance in operator_stances:
                    if condition_rng.random() < 0.5:
                        blocks[(stance[0], 0, stance[2])] = "minecraft:moss_block"
        elif condition == "scavenger_reworked":
            for _ in range({"small": 4, "medium": 8, "large": 12}[scale]):
                x = condition_rng.choice((1, width - 2)) if condition_rng.random() < 0.5 else condition_rng.randint(1, width - 2)
                z = condition_rng.randint(1, depth - 2) if x in {1, width - 2} else condition_rng.choice((1, depth - 2))
                blocks[(x, 1, z)] = palette["bone"]
        elif condition == "sediment_reworked":
            cover = "minecraft:sand" if biome_family == "arid" else palette["ground"]
            for _ in range({"small": 10, "medium": 18, "large": 30}[scale]):
                x = condition_rng.randint(1, width - 2)
                z = condition_rng.randint(1, depth - 2)
                blocks[(x, 1, z)] = cover
        elif condition == "repurposed":
            rx = max(2, min(width - 3, cx + condition_rng.randint(-3, 3)))
            rz = max(2, min(depth - 3, cz + condition_rng.randint(-3, 3)))
            blocks[(rx, 1, rz)] = palette["tool"]

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]

        qualification = {
            "impact_station_count": len(impact_stations),
            "operator_stance_count": len(operator_stances),
            "fracture_cell_count": len(fracture_cells),
            "staging_count": len(staging_points),
            "marrow_point_count": len(marrow_points),
            "carry_lane_length": len(carry_lane),
            "has_dominant_carcass_axis": False,
            "hearth_is_subordinate": hearth is None or len(fracture_cells) >= 8,
        }
        qualification["passes"] = all((
            qualification["impact_station_count"] >= 1,
            qualification["operator_stance_count"] >= qualification["impact_station_count"],
            qualification["fracture_cell_count"] >= 8,
            qualification["staging_count"] >= 3,
            qualification["marrow_point_count"] >= 2,
            qualification["carry_lane_length"] >= 2,
            not qualification["has_dominant_carcass_axis"],
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
                "terrain_mode": "surface_task_landscape",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "impact_stations": impact_stations,
                "operator_stances": operator_stances,
                "hammerstone_points": hammerstone_points,
                "staging_points": staging_points,
                "marrow_points": marrow_points,
                "fracture_cells": fracture_cells,
                "discard_points": discard_points,
                "carry_lane": carry_lane,
                "hearth": hearth,
                "material_semantics": {
                    "bone_block": "heavy_or_fractured_bone_proxy",
                    "stone_family": "anvil_or_hammerstone_proxy",
                    "gravel": "small_fracture_debris_proxy",
                    "stain_blocks": "processing_ground_disturbance_proxy",
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
