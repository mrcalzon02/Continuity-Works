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

CATALOG_ID = "E01-008"
STRUCTURE_ID = "continuityworks:e01_008_multi_hearth_gathering_site"
FAMILY_ID = "continuityworks:early_human_hearth_site"
START_POOL = "continuityworks:early_human/e01_008_multi_hearth_gathering_site"
SCALES = ("small", "medium", "large")
SPACING = 112
SEPARATION = 80
SALT = 101008


class MultiHearthGatheringSiteGenerationError(ValueError):
    pass


class MultiHearthGatheringSiteGenerator:
    """Deterministic Stage-2/3 implementation for E01-008.

    The site is one coordinated aggregation landscape with several meaningful
    hearth territories, shared circulation, differentiated roles, distributed
    fuel/ash management, and explicit smoke-conflict checks. It is not a loose
    collection of independent E01-007 placements.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
        return sha256(payload).hexdigest()

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str | None]:
        palettes = {
            "temperate": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:cobblestone", "fuel": "minecraft:oak_log", "ash": "minecraft:light_gray_concrete_powder", "rest": "minecraft:moss_carpet"},
            "boreal": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:cobblestone", "fuel": "minecraft:spruce_log", "ash": "minecraft:light_gray_concrete_powder", "rest": "minecraft:moss_carpet"},
            "tundra": {"ground": "minecraft:gravel", "ring": "minecraft:stone", "fuel": "minecraft:spruce_log", "ash": "minecraft:light_gray_concrete_powder", "rest": None},
            "savanna": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:granite", "fuel": "minecraft:acacia_log", "ash": "minecraft:light_gray_concrete_powder", "rest": None},
            "arid": {"ground": "minecraft:sand", "ring": "minecraft:sandstone", "fuel": "minecraft:acacia_log", "ash": "minecraft:light_gray_concrete_powder", "rest": None},
            "tropical": {"ground": "minecraft:dirt", "ring": "minecraft:mossy_cobblestone", "fuel": "minecraft:jungle_log", "ash": "minecraft:light_gray_concrete_powder", "rest": "minecraft:moss_carpet"},
            "coastal": {"ground": "minecraft:sand", "ring": "minecraft:cobblestone", "fuel": "minecraft:oak_log", "ash": "minecraft:light_gray_concrete_powder", "rest": None},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _distance(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def _bresenham(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
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
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise MultiHearthGatheringSiteGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {"small": (29, 7, 27), "medium": (45, 8, 41), "large": (69, 9, 63)}
        hearth_ranges = {"small": (2, 3), "medium": (3, 6), "large": (5, 9)}
        width, height, depth = dimensions[scale]
        layout_rng = self._rng(seed, "hearth_geometry")
        chronology_rng = self._rng(seed, "chronology")
        role_rng = self._rng(seed, "cluster_roles")
        wind_rng = self._rng(seed, "wind_field")
        work_rng = self._rng(seed, "shared_zones")
        fuel_rng = self._rng(seed, "fuel_distribution")
        refuse_rng = self._rng(seed, "refuse")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)
        ground = str(palette["ground"])
        ring = str(palette["ring"])
        fuel = str(palette["fuel"])
        ash = str(palette["ash"])
        rest = palette["rest"]

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        hearth_count = layout_rng.randint(*hearth_ranges[scale])
        min_spacing = {"small": 7, "medium": 9, "large": 10}[scale]
        max_radius_x = width // 2 - 6
        max_radius_z = depth // 2 - 6

        # Irregular clustered hearth placement around a terrain-derived gathering centroid proxy.
        centers: list[tuple[int, int]] = []
        attempts = 0
        while len(centers) < hearth_count and attempts < 400:
            attempts += 1
            angle = layout_rng.random() * math.tau
            radius = layout_rng.uniform(min_spacing * 0.65, min(max_radius_x, max_radius_z))
            x = int(round(cx + math.cos(angle) * radius + layout_rng.uniform(-2.0, 2.0)))
            z = int(round(cz + math.sin(angle) * radius + layout_rng.uniform(-2.0, 2.0)))
            x = max(4, min(width - 5, x))
            z = max(4, min(depth - 5, z))
            if all(self._distance((x, z), old) >= min_spacing for old in centers):
                centers.append((x, z))
        if len(centers) < 2:
            raise MultiHearthGatheringSiteGenerationError("could not place multiple meaningful hearths")

        roles_pool = ["DOMESTIC_SOCIAL", "COOKING_PROCESSING", "WORK_LIGHT", "WARMTH_REFUGE", "SUBGROUP_HEARTH", "HOT_STONE_TASK"]
        chronology_pool = ["ACTIVE_CONTEMPORARY", "RECENT_CONTEMPORARY", "SHIFTED_SAME_EPISODE", "LEGACY_PRIOR_EPISODE"]
        roles: list[str] = []
        chronologies: list[str] = []
        for i in range(len(centers)):
            role = roles_pool[(i + role_rng.randrange(len(roles_pool))) % len(roles_pool)]
            roles.append(role)
            if i < 2:
                chronologies.append("ACTIVE_CONTEMPORARY" if i == 0 else "RECENT_CONTEMPORARY")
            else:
                chronologies.append(chronology_rng.choice(chronology_pool))
        if len(set(roles[:2])) < 2:
            roles[1] = "COOKING_PROCESSING" if roles[0] != "COOKING_PROCESSING" else "SUBGROUP_HEARTH"

        prevailing = wind_rng.choice(("north", "south", "east", "west"))
        wind = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[prevailing]

        # Sparse group-scale trampling, strongest around the centroid and cluster connectors.
        occupation_radius = min(width, depth) // 2 - 3
        for x in range(1, width - 1):
            for z in range(1, depth - 1):
                if math.hypot(x - cx, z - cz) <= occupation_radius and layout_rng.random() < 0.17:
                    blocks[(x, 0, z)] = ground

        hearth_records: list[dict[str, Any]] = []
        active_centers: list[tuple[int, int]] = []
        smoke_corridors: list[list[list[int]]] = []
        for idx, ((hx, hz), role, chronology) in enumerate(zip(centers, roles, chronologies)):
            current = chronology in {"ACTIVE_CONTEMPORARY", "RECENT_CONTEMPORARY", "SHIFTED_SAME_EPISODE"}
            for dx, dz in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                blocks[(hx + dx, 1, hz + dz)] = ring
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            if current and condition in {"active", "recent", "repeated"}:
                blocks[(hx, 1, hz)] = "minecraft:campfire"
                active_centers.append((hx, hz))
            else:
                blocks[(hx, 1, hz)] = ash

            corridor: list[list[int]] = []
            for distance in range(2, 7):
                sx = hx + wind[0] * distance
                sz = hz + wind[1] * distance
                if 0 <= sx < width and 0 <= sz < depth:
                    corridor.append([sx, 1, sz])
            smoke_corridors.append(corridor)
            hearth_records.append({"index": idx, "center": [hx, 1, hz], "role": role, "chronology": chronology, "smoke_corridor": corridor})

        # Shared circulation is one connected graph, not independent circular micro-sites.
        circulation_points: set[tuple[int, int]] = set()
        ordered = sorted(centers, key=lambda p: math.atan2(p[1] - cz, p[0] - cx))
        for a, b in zip(ordered, ordered[1:] + ordered[:1]):
            for x, z in self._bresenham(a, b):
                if all(self._distance((x, z), h) > 2.0 for h in centers):
                    circulation_points.add((x, z))
        # Connect all clusters to the shared center, giving M/L redundant movement routes.
        for center in centers:
            for x, z in self._bresenham(center, (cx, cz)):
                if all(self._distance((x, z), h) > 2.0 for h in centers):
                    circulation_points.add((x, z))
        for x, z in circulation_points:
            if (x, 0, z) not in blocks or work_rng.random() < 0.66:
                blocks[(x, 0, z)] = ground

        # Shared work apron around the centroid differentiates the aggregation from isolated hearth circles.
        shared_work: list[list[int]] = []
        for _ in range({"small": 7, "medium": 13, "large": 22}[scale]):
            x = max(2, min(width - 3, cx + work_rng.randint(-5, 5)))
            z = max(2, min(depth - 3, cz + work_rng.randint(-5, 5)))
            if all(self._distance((x, z), h) > 3.0 for h in centers) and (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = "minecraft:gravel" if work_rng.random() < 0.7 else ring
                shared_work.append([x, 1, z])

        # Fuel is distributed per active/recent cluster and scaled to total hearth demand.
        fuel_points: list[list[int]] = []
        for hx, hz in centers:
            for _ in range({"small": 2, "medium": 3, "large": 4}[scale]):
                angle = fuel_rng.random() * math.tau
                radius = fuel_rng.choice((3, 4))
                x = int(round(hx + math.cos(angle) * radius))
                z = int(round(hz + math.sin(angle) * radius))
                if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                    blocks[(x, 1, z)] = fuel
                    fuel_points.append([x, 1, z])

        # Rest sectors appear around selected domestic/subgroup hearths, avoiding smoke corridors.
        smoke_cells = {(p[0], p[2]) for corridor in smoke_corridors for p in corridor}
        rest_points: list[list[int]] = []
        if rest:
            for (hx, hz), role in zip(centers, roles):
                if role not in {"DOMESTIC_SOCIAL", "WARMTH_REFUGE", "SUBGROUP_HEARTH"}:
                    continue
                for _ in range(3):
                    angle = work_rng.random() * math.tau
                    x = int(round(hx + math.cos(angle) * 4))
                    z = int(round(hz + math.sin(angle) * 4))
                    if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, z) not in smoke_cells and (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = str(rest)
                        rest_points.append([x, 1, z])

        # Peripheral refuse and ash are biased downwind and away from the shared circulation core.
        refuse_points: list[list[int]] = []
        margin_x = cx + wind[0] * (occupation_radius - 2)
        margin_z = cz + wind[1] * (occupation_radius - 2)
        for _ in range({"small": 5, "medium": 9, "large": 15}[scale]):
            x = max(1, min(width - 2, margin_x + refuse_rng.randint(-4, 4)))
            z = max(1, min(depth - 2, margin_z + refuse_rng.randint(-4, 4)))
            if (x, 1, z) not in blocks:
                material = ash if refuse_rng.random() < 0.62 else "minecraft:bone_block"
                blocks[(x, 1, z)] = material
                refuse_points.append([x, 1, z])

        # Condition states alter intensity without erasing the multi-hearth topology.
        if condition in {"weathered", "abandoned", "contracted", "repurposed"}:
            removable = [pos for pos, block in blocks.items() if pos[1] == 1 and block in {fuel, str(rest), "minecraft:gravel"}]
            condition_rng.shuffle(removable)
            loss = {"weathered": 0.25, "abandoned": 0.45, "contracted": 0.35, "repurposed": 0.20}[condition]
            for pos in removable[: int(len(removable) * loss)]:
                blocks.pop(pos, None)

        block_list = [{"pos": [x, y, z], "block": block} for (x, y, z), block in sorted(blocks.items())]

        current_hearths = sum(1 for h in hearth_records if h["chronology"] in {"ACTIVE_CONTEMPORARY", "RECENT_CONTEMPORARY", "SHIFTED_SAME_EPISODE"})
        meaningful_roles = len(set(roles)) >= 2
        pair_distances = [self._distance(a, b) for i, a in enumerate(centers) for b in centers[i + 1:]]
        spacing_valid = bool(pair_distances) and min(pair_distances) >= min_spacing
        shared_circulation = len(circulation_points) >= max(5, len(centers) * 3)
        group_scale = min(width, depth) >= 27 and len(centers) >= 2
        smoke_conflicts = 0
        for i, center in enumerate(centers):
            for j, corridor in enumerate(smoke_corridors):
                if i == j:
                    continue
                if any(self._distance(center, (p[0], p[2])) < 3.0 for p in corridor):
                    smoke_conflicts += 1
        smoke_managed = smoke_conflicts == 0
        no_permanent_fabric = all(entry["pos"][1] <= 1 for entry in block_list)
        qualification = {
            "multiple_current_or_recent_hearths": current_hearths >= 2,
            "differentiated_hearth_roles": meaningful_roles,
            "inter_hearth_spacing_valid": spacing_valid,
            "shared_circulation_present": shared_circulation,
            "group_scale_occupation": group_scale,
            "shared_work_zone_present": len(shared_work) >= 3,
            "fuel_distribution_present": len(fuel_points) >= len(centers),
            "smoke_interaction_managed": smoke_managed,
            "temporary_character_preserved": no_permanent_fabric,
        }

        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Multi-Hearth Gathering Site",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "surface_terrain_responsive_aggregation_landscape",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "gathering_centroid": [cx, 0, cz],
                "hearths": hearth_records,
                "current_or_recent_hearth_count": current_hearths,
                "shared_circulation_points": [[x, 0, z] for x, z in sorted(circulation_points)],
                "shared_work_points": shared_work,
                "fuel_points": fuel_points,
                "rest_points": rest_points,
                "refuse_points": refuse_points,
                "prevailing_wind": prevailing,
                "smoke_conflict_count": smoke_conflicts,
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "compatible_family_policy": "same_parent_reservation_or_same_assembly_only",
                "archetype_constraint": "multiple_meaningful_hearth_territories_share_one_social_circulation_and_work_landscape",
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
            max_distance=128,
        )
        structure_set = random_spread_structure_set(STRUCTURE_ID, SPACING, SEPARATION, SALT)
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
            "family_id": FAMILY_ID,
            "start_pool": START_POOL,
            "structure": structure,
            "structure_set": structure_set,
            "protection_profile": protection,
            "placement_contract": {
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "compatible_family_exception": "same_parent_reservation_or_same_assembly_only",
                "compatibility_mode": "additive_non_destructive",
                "requires_open_smoke_dispersion": True,
            },
            "validation_findings": findings,
        }
