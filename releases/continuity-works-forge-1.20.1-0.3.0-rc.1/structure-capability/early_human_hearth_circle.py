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

CATALOG_ID = "E01-007"
STRUCTURE_ID = "continuityworks:e01_007_hearth_circle"
FAMILY_ID = "continuityworks:early_human_hearth_site"
START_POOL = "continuityworks:early_human/e01_007_hearth_circle"
SCALES = ("small", "medium", "large")
SPACING = 96
SEPARATION = 64
SALT = 101007


class HearthCircleGenerationError(ValueError):
    pass


class HearthCircleGenerator:
    """Deterministic Stage-2/3 implementation for E01-007 Hearth Circle.

    A single hearth is the spatial and functional origin of the site. Seating,
    work, fuel, discard, and ash chronology are expressed as arcs/rings around
    that origin while vertical clearance remains open to the sky. This module
    intentionally refuses multi-hearth topology; that belongs to E01-008.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str | None]:
        palettes = {
            "temperate": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:cobblestone", "seat": "minecraft:oak_log", "fuel": "minecraft:oak_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": "minecraft:moss_carpet"},
            "boreal": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:cobblestone", "seat": "minecraft:spruce_log", "fuel": "minecraft:spruce_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": "minecraft:moss_carpet"},
            "tundra": {"ground": "minecraft:gravel", "ring": "minecraft:stone", "seat": "minecraft:spruce_log", "fuel": "minecraft:spruce_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": None},
            "savanna": {"ground": "minecraft:coarse_dirt", "ring": "minecraft:granite", "seat": "minecraft:acacia_log", "fuel": "minecraft:acacia_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": None},
            "arid": {"ground": "minecraft:sand", "ring": "minecraft:sandstone", "seat": "minecraft:acacia_log", "fuel": "minecraft:acacia_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": None},
            "tropical": {"ground": "minecraft:dirt", "ring": "minecraft:mossy_cobblestone", "seat": "minecraft:jungle_log", "fuel": "minecraft:jungle_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": "minecraft:moss_carpet"},
            "coastal": {"ground": "minecraft:sand", "ring": "minecraft:cobblestone", "seat": "minecraft:oak_log", "fuel": "minecraft:oak_log", "ash": "minecraft:light_gray_concrete_powder", "bedding": None},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
        return sha256(payload).hexdigest()

    @staticmethod
    def _point(cx: int, cz: int, radius: int, angle: float) -> tuple[int, int]:
        return (int(round(cx + math.cos(angle) * radius)), int(round(cz + math.sin(angle) * radius)))

    def generate(
        self,
        *,
        seed: int | str,
        scale: str = "medium",
        biome_family: str = "temperate",
        condition: str = "active",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise HearthCircleGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {"small": (13, 6, 13), "medium": (19, 7, 19), "large": (27, 8, 27)}
        width, height, depth = dimensions[scale]
        layout_rng = self._rng(seed, "radial_layout")
        fuel_rng = self._rng(seed, "fuel_handling")
        ash_rng = self._rng(seed, "ash_chronology")
        occupation_rng = self._rng(seed, "occupation")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)

        ground = str(palette["ground"])
        ring_material = str(palette["ring"])
        seat_material = str(palette["seat"])
        fuel_material = str(palette["fuel"])
        ash_material = str(palette["ash"])
        bedding = palette["bedding"]

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        hearth_radius = 1
        seat_radius = {"small": 4, "medium": 6, "large": 8}[scale]
        work_radius = seat_radius + 1
        outer_radius = min(width, depth) // 2 - 2

        # Sparse trampled occupation floor; this is an activity site, not a paved plaza.
        for x in range(1, width - 1):
            for z in range(1, depth - 1):
                distance = math.hypot(x - cx, z - cz)
                if distance <= outer_radius and occupation_rng.random() < 0.28:
                    blocks[(x, 0, z)] = ground

        # Exactly one central hearth. A stone ring encodes fire control without creating walls.
        hearth_ring: list[list[int]] = []
        for dx, dz in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            blocks[(cx + dx, 1, cz + dz)] = ring_material
            hearth_ring.append([cx + dx, 1, cz + dz])
        blocks[(cx, 0, cz)] = "minecraft:coal_block"
        if condition in {"active", "recent", "repeated"}:
            blocks[(cx, 1, cz)] = "minecraft:campfire"
        else:
            blocks[(cx, 1, cz)] = ash_material
        hearth = [cx, 1, cz]

        # Seating follows broken arcs rather than a complete artificial circle.
        seating_points: list[list[int]] = []
        seat_count = {"small": 5, "medium": 8, "large": 12}[scale]
        base_rotation = layout_rng.random() * math.tau
        blocked_sector_center = base_rotation + layout_rng.uniform(-0.5, 0.5)
        for i in range(seat_count * 2):
            if len(seating_points) >= seat_count:
                break
            angle = base_rotation + (math.tau * i / (seat_count * 2))
            delta = abs((angle - blocked_sector_center + math.pi) % math.tau - math.pi)
            if delta < 0.52 or layout_rng.random() < 0.18:
                continue
            x, z = self._point(cx, cz, seat_radius + layout_rng.choice((-1, 0, 0, 1)), angle)
            if 1 <= x < width - 1 and 1 <= z < depth - 1:
                blocks[(x, 1, z)] = seat_material
                seating_points.append([x, 1, z])

        # Work arc is concentrated to one side, preserving circulation on the other.
        work_points: list[list[int]] = []
        work_center = base_rotation + math.pi * 0.55
        work_count = {"small": 4, "medium": 7, "large": 10}[scale]
        for _ in range(work_count):
            angle = work_center + occupation_rng.uniform(-0.65, 0.65)
            radius = max(3, work_radius + occupation_rng.choice((-1, 0, 1)))
            x, z = self._point(cx, cz, radius, angle)
            if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = "minecraft:gravel" if occupation_rng.random() < 0.72 else ring_material
                work_points.append([x, 1, z])

        # Fuel is staged opposite the work arc and never inside the fire-control ring.
        fuel_points: list[list[int]] = []
        fuel_center = work_center + math.pi
        for _ in range({"small": 3, "medium": 5, "large": 8}[scale]):
            angle = fuel_center + fuel_rng.uniform(-0.48, 0.48)
            radius = seat_radius + fuel_rng.choice((1, 2))
            x, z = self._point(cx, cz, radius, angle)
            if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = fuel_material
                fuel_points.append([x, 1, z])

        # Ash/charcoal chronology creates a downwind cleaning/discard fan outside the ring.
        prevailing = layout_rng.choice(("north", "south", "east", "west"))
        vector = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[prevailing]
        ash_points: list[list[int]] = []
        ash_layers = {"active": 1, "recent": 2, "repeated": 4, "abandoned": 3, "weathered": 2, "repurposed": 2}.get(condition, 2)
        for layer in range(1, ash_layers + 1):
            distance = 2 + layer
            spread = layer
            for offset in range(-spread, spread + 1):
                if ash_rng.random() < 0.48:
                    continue
                x = cx + vector[0] * distance + (offset if vector[0] == 0 else 0)
                z = cz + vector[1] * distance + (offset if vector[1] == 0 else 0)
                if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                    blocks[(x, 1, z)] = ash_material if ash_rng.random() < 0.72 else "minecraft:coal_block"
                    ash_points.append([x, 1, z])

        # Optional rest pads remain peripheral and non-enclosing.
        rest_points: list[list[int]] = []
        if bedding:
            rest_center = base_rotation - math.pi * 0.55
            for _ in range({"small": 2, "medium": 4, "large": 6}[scale]):
                angle = rest_center + occupation_rng.uniform(-0.45, 0.45)
                x, z = self._point(cx, cz, max(3, outer_radius - 1), angle)
                if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                    blocks[(x, 1, z)] = str(bedding)
                    rest_points.append([x, 1, z])

        # Condition handling degrades occupation traces but preserves the single-hearth read.
        if condition in {"weathered", "abandoned", "repurposed"}:
            degradable = [
                pos for pos, block in blocks.items()
                if pos != (cx, 1, cz) and block in {seat_material, fuel_material, str(bedding)}
            ]
            condition_rng.shuffle(degradable)
            loss = {"weathered": 0.28, "abandoned": 0.42, "repurposed": 0.20}[condition]
            for pos in degradable[: int(len(degradable) * loss)]:
                blocks.pop(pos, None)
            if condition == "repurposed":
                # Later users may add a few stone utility markers without adding a second hearth.
                for _ in range({"small": 2, "medium": 3, "large": 5}[scale]):
                    angle = condition_rng.random() * math.tau
                    x, z = self._point(cx, cz, seat_radius + 1, angle)
                    if 1 <= x < width - 1 and 1 <= z < depth - 1 and (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = ring_material

        block_list = [{"pos": [x, y, z], "block": block} for (x, y, z), block in sorted(blocks.items())]

        # Smoke/open-air gate: no generated blocks may occupy the vertical column above the hearth.
        smoke_column_clear = all((cx, y, cz) not in blocks for y in range(2, height))
        hearth_like = [b for b in block_list if b["block"] == "minecraft:campfire"]
        active_hearth_count = len(hearth_like)
        single_organizing_hearth = active_hearth_count == 1 if condition in {"active", "recent", "repeated"} else active_hearth_count == 0
        radial_activity = len(seating_points) >= 3 and len(work_points) >= 2
        chronology_present = bool(ash_points) and bool(fuel_points)
        no_enclosure = all(entry["pos"][1] <= 1 for entry in block_list)
        qualification = {
            "single_organizing_hearth": single_organizing_hearth,
            "radial_or_semiradial_activity_geometry": radial_activity,
            "fuel_and_ash_chronology_present": chronology_present,
            "open_air_smoke_column_clear": smoke_column_clear,
            "no_shelter_enclosure": no_enclosure,
            "multi_hearth_topology_absent": active_hearth_count <= 1,
        }

        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Hearth Circle",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "surface_terrain_responsive_open_air",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "hearth": hearth,
                "hearth_ring": hearth_ring,
                "seating_points": seating_points,
                "work_points": work_points,
                "fuel_points": fuel_points,
                "ash_points": ash_points,
                "rest_points": rest_points,
                "prevailing_wind": prevailing,
                "smoke_column_clear": smoke_column_clear,
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "archetype_constraint": "single_hearth_organizes_open_air_radial_activity_and_fire_maintenance_chronology",
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
            max_distance=56,
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
                "requires_open_sky_or_smoke_clearance": True,
                "family_co_location_requires_shared_parent_reservation": True,
                "must_not_replace_existing_major_structure": True,
                "single_hearth_site_only": True,
            },
        }
