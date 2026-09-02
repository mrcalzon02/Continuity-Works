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


CATALOG_ID = "E01-003"
STRUCTURE_ID = "continuityworks:e01_003_deep_cave_refuge"
FAMILY_ID = "continuityworks:early_human_cave_complex"
START_POOL = "continuityworks:early_human/e01_003_deep_cave_refuge"
SCALES = ("small", "medium", "large")
SPACING = 112
SEPARATION = 80
SALT = 101003


class DeepCaveRefugeGenerationError(ValueError):
    pass


class DeepCaveRefugeGenerator:
    """Deterministic Stage-2/3 implementation for E01-003 Deep Cave Refuge.

    Unlike E01-002, qualification depends on a simulated route from a remote
    daylight-loss boundary to a defensible refuge chamber. The physical output
    is a terrain-first cave volume contract, not a freestanding building.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _palette(biome_family: str) -> tuple[str, str, str]:
        palettes = {
            "temperate": ("minecraft:stone", "minecraft:andesite", "minecraft:gravel"),
            "boreal": ("minecraft:stone", "minecraft:tuff", "minecraft:gravel"),
            "tundra": ("minecraft:stone", "minecraft:andesite", "minecraft:gravel"),
            "savanna": ("minecraft:stone", "minecraft:granite", "minecraft:coarse_dirt"),
            "arid": ("minecraft:sandstone", "minecraft:smooth_sandstone", "minecraft:sand"),
            "tropical": ("minecraft:stone", "minecraft:mossy_cobblestone", "minecraft:gravel"),
            "coastal": ("minecraft:stone", "minecraft:tuff", "minecraft:gravel"),
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(
            f"{entry['pos']}:{entry['block']}" for entry in blocks
        ).encode("utf-8")
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
            raise DeepCaveRefugeGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {
            "small": (28, 13, 38),
            "medium": (40, 16, 56),
            "large": (56, 20, 76),
        }
        width, height, depth = dimensions[scale]
        topology = self._rng(seed, "topology")
        route_rng = self._rng(seed, "route")
        refuge_rng = self._rng(seed, "refuge")
        occupation = self._rng(seed, "occupation")
        ventilation_rng = self._rng(seed, "ventilation")
        condition_rng = self._rng(seed, "condition")
        primary, secondary, floor_material = self._palette(biome_family)

        blocks: dict[tuple[int, int, int], str] = {}

        daylight_loss_z = {"small": 5, "medium": 7, "large": 9}[scale]
        refuge_start_z = {"small": 24, "medium": 36, "large": 50}[scale] + topology.randint(-2, 2)
        refuge_start_z = max(daylight_loss_z + 12, min(depth - 12, refuge_start_z))
        refuge_end_z = min(depth - 3, refuge_start_z + {"small": 9, "medium": 13, "large": 17}[scale])

        route_center = width // 2 + route_rng.randint(-2, 2)
        route_width = {"small": 2, "medium": 3, "large": 4}[scale]
        route_points: list[list[int]] = []
        turn_count = 0
        previous_dx = 0

        for z in range(daylight_loss_z, refuge_start_z + 1):
            proposed_dx = route_rng.choice((-1, 0, 0, 0, 1))
            if proposed_dx != 0 and proposed_dx != previous_dx:
                turn_count += 1
            previous_dx = proposed_dx
            route_center = max(route_width + 2, min(width - route_width - 3, route_center + proposed_dx))
            route_points.append([route_center, 1, z])

            local_width = route_width + (1 if route_rng.random() < 0.18 else 0)
            ceiling = min(height - 2, 5 + route_rng.randint(0, 2))
            left = route_center - local_width
            right = route_center + local_width
            for x in range(width):
                if x < left or x > right:
                    for y in range(height):
                        if topology.random() < 0.93 or y <= 1:
                            blocks[(x, y, z)] = primary if topology.random() < 0.86 else secondary
            for x in range(left, right + 1):
                blocks[(x, 0, z)] = floor_material
                for y in range(ceiling, height):
                    blocks[(x, y, z)] = primary if topology.random() < 0.88 else secondary

        chamber_center = max(8, min(width - 9, route_center + refuge_rng.randint(-3, 3)))
        chamber_half = {"small": 6, "medium": 8, "large": 11}[scale]
        chamber_ceiling = min(height - 2, {"small": 8, "medium": 10, "large": 13}[scale])
        for z in range(refuge_start_z, refuge_end_z + 1):
            taper = abs((refuge_start_z + refuge_end_z) // 2 - z) // 4
            left = max(1, chamber_center - chamber_half + taper)
            right = min(width - 2, chamber_center + chamber_half - taper)
            for x in range(width):
                if x < left or x > right:
                    for y in range(height):
                        if topology.random() < 0.95 or y <= 1:
                            blocks[(x, y, z)] = primary if topology.random() < 0.87 else secondary
            for x in range(left, right + 1):
                blocks[(x, 0, z)] = floor_material
                for y in range(chamber_ceiling, height):
                    blocks[(x, y, z)] = primary if topology.random() < 0.9 else secondary

        ventilation_class = ventilation_rng.choice(("restricted", "moderate", "drafted"))
        hearth_allowed = ventilation_class != "restricted"
        refuge_anchor = [chamber_center, 1, (refuge_start_z + refuge_end_z) // 2]
        hearth = [
            max(2, min(width - 3, chamber_center - 2)),
            1,
            min(refuge_end_z - 2, refuge_anchor[2]),
        ]
        if hearth_allowed:
            hx, hy, hz = hearth
            for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                blocks[(hx + dx, hy, hz + dz)] = secondary
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            if condition in {"active", "recent", "repeated"}:
                blocks[(hx, hy, hz)] = "minecraft:campfire"

        rest_anchor = [
            max(3, min(width - 4, chamber_center + 3)),
            1,
            min(refuge_end_z - 2, refuge_anchor[2] + 2),
        ]
        bedding = None if biome_family in {"arid", "tundra"} else "minecraft:moss_carpet"
        if bedding:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if occupation.random() < 0.7:
                        blocks[(rest_anchor[0] + dx, 1, rest_anchor[2] + dz)] = bedding

        cache_anchor = [
            max(2, chamber_center - chamber_half + 2),
            1,
            min(refuge_end_z - 2, refuge_anchor[2] + 1),
        ]
        for dz in range(2):
            blocks[(cache_anchor[0], 1, cache_anchor[2] + dz)] = (
                "minecraft:gravel" if occupation.random() < 0.6 else secondary
            )

        marker_interval = {"small": 5, "medium": 6, "large": 7}[scale]
        wayfinding_markers: list[list[int]] = []
        for index, point in enumerate(route_points):
            if index % marker_interval != 0:
                continue
            x, _, z = point
            marker_x = max(1, x - route_width - 1)
            blocks[(marker_x, 1, z)] = secondary
            if occupation.random() < 0.5 and marker_x + 1 < width:
                blocks[(marker_x + 1, 1, z)] = secondary
            wayfinding_markers.append([marker_x, 1, z])

        if condition in {"abandoned", "collapsed", "flooded", "animal_reoccupied"}:
            count = {"abandoned": 7, "collapsed": 22, "flooded": 18, "animal_reoccupied": 12}[condition]
            for _ in range(count):
                x = condition_rng.randrange(max(1, chamber_center - chamber_half), min(width - 1, chamber_center + chamber_half + 1))
                z = condition_rng.randrange(refuge_start_z, refuge_end_z + 1)
                if condition == "flooded":
                    material = "minecraft:water"
                elif condition == "animal_reoccupied":
                    material = condition_rng.choice(("minecraft:bone_block", "minecraft:gravel", secondary))
                else:
                    material = condition_rng.choice((primary, secondary, floor_material))
                blocks[(x, 1, z)] = material

        route_length = max(0, refuge_start_z - daylight_loss_z)
        route_complexity = turn_count + len(wayfinding_markers)
        qualification = {
            "daylight_lost": True,
            "minimum_route_length": route_length >= {"small": 16, "medium": 24, "large": 34}[scale],
            "route_complexity": route_complexity >= {"small": 4, "medium": 6, "large": 8}[scale],
            "refuge_beyond_threshold": refuge_anchor[2] > daylight_loss_z + 12,
        }

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]
        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Deep Cave Refuge",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "terrain_first_deep_cave_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "daylight_loss_z": daylight_loss_z,
                "refuge_start_z": refuge_start_z,
                "refuge_end_z": refuge_end_z,
                "route_length": route_length,
                "route_turn_count": turn_count,
                "route_complexity": route_complexity,
                "ventilation_class": ventilation_class,
                "hearth_allowed": hearth_allowed,
                "hearth": hearth if hearth_allowed else None,
                "refuge_anchor": refuge_anchor,
                "rest_zone_anchor": rest_anchor,
                "cache_anchor": cache_anchor,
                "wayfinding_markers": wayfinding_markers,
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "archetype_constraint": "refuge_must_be_beyond_daylight_loss_and_route_complexity_thresholds",
                "fingerprint": self._fingerprint(block_list),
            },
        }

    def worldgen_bundle(
        self,
        *,
        biome_selector: str = "#minecraft:is_overworld",
        absolute_y: int = -24,
    ) -> dict[str, Any]:
        structure = jigsaw_structure(
            biome_selector=biome_selector,
            start_pool=START_POOL,
            step="underground_structures",
            terrain_adaptation="bury",
            heightmap=None,
            absolute_y=absolute_y,
            max_distance=128,
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
                "anchor": "subterranean_absolute_y",
                "absolute_y": absolute_y,
                "surface_projection": False,
                "requires_deep_cave_topology": True,
            },
        }
