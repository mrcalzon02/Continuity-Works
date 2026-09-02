from __future__ import annotations

from dataclasses import dataclass
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


class EarlyHumanGenerationError(ValueError):
    pass


@dataclass(frozen=True)
class EarlyHumanArchetype:
    catalog_id: str
    structure_id: str
    name: str
    family_id: str
    scales: tuple[str, ...]
    start_pool: str
    spacing: int
    separation: int
    salt: int
    terrain_adaptation: str = "beard_thin"
    max_distance: int = 80


E01_001 = EarlyHumanArchetype(
    catalog_id="E01-001",
    structure_id="continuityworks:e01_001_rock_overhang_camp",
    name="Rock Overhang Camp",
    family_id="continuityworks:early_human_camp",
    scales=("small", "medium", "large"),
    start_pool="continuityworks:early_human/e01_001_rock_overhang_camp",
    spacing=96,
    separation=64,
    salt=101001,
)

E01_002 = EarlyHumanArchetype(
    catalog_id="E01-002",
    structure_id="continuityworks:e01_002_cave_mouth_occupation",
    name="Cave Mouth Occupation",
    family_id="continuityworks:early_human_cave_complex",
    scales=("small", "medium", "large"),
    start_pool="continuityworks:early_human/e01_002_cave_mouth_occupation",
    spacing=104,
    separation=72,
    salt=101002,
    terrain_adaptation="bury",
    max_distance=96,
)


class EarlyHumanStructureGenerator:
    """Seeded physical generators for the Continuity Works early-human backlog.

    The output shape matches the project's physical structure contract:
    ``{size, blocks, metadata}``. Terrain-sensitive generators deliberately
    include replace-mode metadata because the final world-placement layer must
    reconcile generated geology with the target terrain instead of treating
    these outputs as freestanding prefab buildings.
    """

    def __init__(self):
        self.archetypes = {
            E01_001.catalog_id: E01_001,
            E01_002.catalog_id: E01_002,
        }

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _stone_palette(biome_family: str) -> tuple[str, str, str]:
        palettes = {
            "temperate": ("minecraft:stone", "minecraft:andesite", "minecraft:cobblestone"),
            "boreal": ("minecraft:stone", "minecraft:tuff", "minecraft:cobblestone"),
            "tundra": ("minecraft:stone", "minecraft:andesite", "minecraft:gravel"),
            "savanna": ("minecraft:stone", "minecraft:granite", "minecraft:coarse_dirt"),
            "arid": ("minecraft:sandstone", "minecraft:smooth_sandstone", "minecraft:sand"),
            "tropical": ("minecraft:stone", "minecraft:mossy_cobblestone", "minecraft:dirt"),
            "coastal": ("minecraft:stone", "minecraft:gravel", "minecraft:sand"),
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(block_list: list[dict[str, Any]]) -> str:
        payload = "\n".join(
            f"{entry['pos']}:{entry['block']}" for entry in block_list
        ).encode("utf-8")
        return sha256(payload).hexdigest()

    def generate(
        self,
        catalog_id: str,
        *,
        seed: int | str,
        scale: str = "medium",
        biome_family: str = "temperate",
        condition: str = "active",
    ) -> dict[str, Any]:
        archetype = self.archetypes.get(catalog_id)
        if archetype is None:
            raise EarlyHumanGenerationError(f"unsupported early-human archetype: {catalog_id}")
        if scale not in archetype.scales:
            raise EarlyHumanGenerationError(f"invalid scale {scale!r} for {catalog_id}")
        if catalog_id == "E01-001":
            return self._rock_overhang_camp(
                archetype, seed=seed, scale=scale, biome_family=biome_family, condition=condition
            )
        if catalog_id == "E01-002":
            return self._cave_mouth_occupation(
                archetype, seed=seed, scale=scale, biome_family=biome_family, condition=condition
            )
        raise EarlyHumanGenerationError(f"generator not implemented: {catalog_id}")

    def _rock_overhang_camp(
        self,
        archetype: EarlyHumanArchetype,
        *,
        seed: int | str,
        scale: str,
        biome_family: str,
        condition: str,
    ) -> dict[str, Any]:
        dimensions = {
            "small": (18, 9, 14),
            "medium": (28, 11, 20),
            "large": (42, 13, 28),
        }
        width, height, depth = dimensions[scale]
        geology = self._rng(seed, "geology")
        occupation = self._rng(seed, "occupation_layout")
        hearth_rng = self._rng(seed, "hearth")
        condition_rng = self._rng(seed, "condition")
        primary, secondary, ground = self._stone_palette(biome_family)

        blocks: dict[tuple[int, int, int], str] = {}
        rear_start = max(2, depth - (6 if scale == "small" else 8 if scale == "medium" else 10))
        for x in range(width):
            edge_noise = geology.randint(-2, 2)
            roof_front = max(3, depth // 4 + edge_noise)
            roof_y = height - 3 + geology.randint(-1, 1)
            for z in range(max(0, roof_front), depth):
                rear_weight = max(0, z - rear_start)
                thickness = 2 + min(3, rear_weight // 3) + geology.randint(0, 1)
                for y in range(max(3, roof_y), min(height, roof_y + thickness)):
                    material = primary if geology.random() < 0.82 else secondary
                    blocks[(x, y, z)] = material

        for x in range(width):
            wall_front = rear_start + geology.randint(-2, 1)
            for z in range(max(0, wall_front), depth):
                local_top = height - geology.randint(0, 2)
                for y in range(0, local_top):
                    if geology.random() < 0.90 or z >= depth - 2:
                        blocks[(x, y, z)] = primary if geology.random() < 0.86 else secondary

        floor_front = max(2, depth // 4)
        floor_back = max(floor_front + 3, rear_start + 1)
        for x in range(1, width - 1):
            for z in range(floor_front, min(depth - 1, floor_back)):
                if occupation.random() < 0.91:
                    blocks[(x, 0, z)] = ground

        for x in range(2, width - 2):
            for z in range(1, floor_front + 1):
                if occupation.random() < 0.28:
                    blocks[(x, 0, z)] = "minecraft:coarse_dirt"

        hearth_x = occupation.randint(max(2, width // 4), min(width - 3, (width * 3) // 4))
        hearth_z = min(floor_back - 1, floor_front + hearth_rng.randint(2, max(2, depth // 5)))
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            blocks[(hearth_x + dx, 1, hearth_z + dz)] = secondary
        blocks[(hearth_x, 0, hearth_z)] = "minecraft:coal_block"
        if condition in {"active", "recent"}:
            blocks[(hearth_x, 1, hearth_z)] = "minecraft:campfire"

        work_x = max(2, hearth_x - width // 5)
        work_z = max(floor_front, hearth_z - 2)
        for _ in range({"small": 5, "medium": 9, "large": 14}[scale]):
            x = max(1, min(width - 2, work_x + occupation.randint(-3, 3)))
            z = max(1, min(depth - 2, work_z + occupation.randint(-2, 2)))
            if (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = "minecraft:gravel" if occupation.random() < 0.55 else secondary

        sleep_x = min(width - 4, max(3, hearth_x + width // 6))
        sleep_z = min(depth - 3, max(hearth_z + 2, floor_back - 2))
        bedding = None if biome_family in {"arid", "tundra"} else "minecraft:moss_carpet"
        if bedding:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if occupation.random() < 0.72:
                        blocks[(sleep_x + dx, 1, sleep_z + dz)] = bedding

        refuse_x = 1 if occupation.random() < 0.5 else width - 2
        for _ in range({"small": 3, "medium": 6, "large": 10}[scale]):
            z = occupation.randint(max(1, floor_front - 1), min(depth - 2, floor_back + 1))
            material = "minecraft:bone_block" if occupation.random() < 0.35 else "minecraft:gravel"
            blocks[(refuse_x, 1, z)] = material

        if condition in {"abandoned", "collapsed", "buried"}:
            additions = {"abandoned": 5, "collapsed": 14, "buried": 22}[condition]
            for _ in range(additions):
                x = condition_rng.randrange(1, width - 1)
                z = condition_rng.randrange(floor_front, depth - 1)
                y = 1 if condition != "collapsed" else condition_rng.choice((1, 2))
                blocks[(x, y, z)] = condition_rng.choice((primary, secondary, ground))

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]
        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": archetype.catalog_id,
                "structure_id": archetype.structure_id,
                "name": archetype.name,
                "family_id": archetype.family_id,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "terrain_first_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "hearth": [hearth_x, 1, hearth_z],
                "work_zone_anchor": [work_x, 1, work_z],
                "sleep_zone_anchor": [sleep_x, 1, sleep_z],
                "fingerprint": self._fingerprint(block_list),
            },
        }

    def _cave_mouth_occupation(
        self,
        archetype: EarlyHumanArchetype,
        *,
        seed: int | str,
        scale: str,
        biome_family: str,
        condition: str,
    ) -> dict[str, Any]:
        dimensions = {
            "small": (22, 11, 24),
            "medium": (34, 14, 36),
            "large": (50, 17, 50),
        }
        width, height, depth = dimensions[scale]
        cave_rng = self._rng(seed, "cave_candidate")
        topology_rng = self._rng(seed, "mouth_topology")
        occupation_rng = self._rng(seed, "occupation_layout")
        hearth_rng = self._rng(seed, "hearth")
        condition_rng = self._rng(seed, "condition")
        primary, secondary, ground = self._stone_palette(biome_family)
        blocks: dict[tuple[int, int, int], str] = {}

        mouth_center = width // 2 + topology_rng.randint(-max(1, width // 12), max(1, width // 12))
        mouth_half_width = {"small": 4, "medium": 7, "large": 10}[scale] + topology_rng.randint(-1, 1)
        mouth_height = {"small": 6, "medium": 8, "large": 10}[scale] + topology_rng.randint(-1, 1)
        mouth_z = max(3, depth // 6)
        chamber_end = {"small": 15, "medium": 24, "large": 34}[scale]
        chamber_end = min(depth - 3, chamber_end + topology_rng.randint(-2, 2))
        interior_stop = min(chamber_end - 2, mouth_z + {"small": 9, "medium": 15, "large": 22}[scale])

        for z in range(mouth_z, chamber_end + 1):
            progress = (z - mouth_z) / max(1, chamber_end - mouth_z)
            local_half = mouth_half_width + int(progress * (2 if scale != "small" else 1))
            left = max(1, mouth_center - local_half + cave_rng.randint(-1, 1))
            right = min(width - 2, mouth_center + local_half + cave_rng.randint(-1, 1))
            local_ceiling = min(height - 2, mouth_height + int(progress * 2) + cave_rng.randint(-1, 1))

            for x in range(width):
                if x < left or x > right:
                    for y in range(0, height):
                        if cave_rng.random() < 0.91 or y <= 1:
                            blocks[(x, y, z)] = primary if cave_rng.random() < 0.86 else secondary
            for x in range(left, right + 1):
                blocks[(x, 0, z)] = ground
                for y in range(local_ceiling, height):
                    blocks[(x, y, z)] = primary if cave_rng.random() < 0.88 else secondary

        # Natural rock around the mouth, leaving a real entrance aperture.
        left_mouth = mouth_center - mouth_half_width
        right_mouth = mouth_center + mouth_half_width
        for z in range(0, mouth_z):
            for x in range(width):
                if x < left_mouth - 1 or x > right_mouth + 1:
                    if cave_rng.random() < 0.58:
                        blocks[(x, 0, z)] = ground
        for x in range(width):
            if x < left_mouth or x > right_mouth:
                for y in range(1, min(height, mouth_height + 3)):
                    if cave_rng.random() < 0.82:
                        blocks[(x, y, mouth_z)] = primary if cave_rng.random() < 0.88 else secondary

        # Approach apron and threshold compaction remain sparse and unengineered.
        for z in range(1, mouth_z + 3):
            for x in range(max(1, left_mouth - 2), min(width - 1, right_mouth + 3)):
                if occupation_rng.random() < 0.34:
                    blocks[(x, 0, z)] = "minecraft:coarse_dirt" if biome_family != "arid" else "minecraft:sand"

        daylight_end = min(interior_stop - 3, mouth_z + max(3, (interior_stop - mouth_z) // 3))
        twilight_end = interior_stop
        work_anchor = [
            max(2, min(width - 3, mouth_center - max(2, mouth_half_width // 2))),
            1,
            min(daylight_end, mouth_z + 3),
        ]
        rest_anchor = [
            max(2, min(width - 3, mouth_center + max(2, mouth_half_width // 3))),
            1,
            max(daylight_end + 2, twilight_end - 3),
        ]

        # Tool-work scatter stays in daylight/partial daylight.
        for _ in range({"small": 6, "medium": 11, "large": 17}[scale]):
            x = max(1, min(width - 2, work_anchor[0] + occupation_rng.randint(-3, 3)))
            z = max(mouth_z, min(daylight_end, work_anchor[2] + occupation_rng.randint(-2, 2)))
            if (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = secondary if occupation_rng.random() < 0.45 else "minecraft:gravel"

        hearth_x = max(2, min(width - 3, mouth_center + hearth_rng.randint(-mouth_half_width // 2, mouth_half_width // 2)))
        hearth_z = max(mouth_z + 2, min(daylight_end + 2, mouth_z + hearth_rng.randint(3, max(4, daylight_end - mouth_z + 1))))
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            blocks[(hearth_x + dx, 1, hearth_z + dz)] = secondary
        blocks[(hearth_x, 0, hearth_z)] = "minecraft:coal_block"
        if condition in {"active", "recent", "repeated"}:
            blocks[(hearth_x, 1, hearth_z)] = "minecraft:campfire"

        bedding = None if biome_family in {"arid", "tundra"} else "minecraft:moss_carpet"
        if bedding:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if occupation_rng.random() < 0.66:
                        blocks[(rest_anchor[0] + dx, 1, rest_anchor[2] + dz)] = bedding

        # Cache alcove hugs a wall but remains before the interior stop-line.
        cache_x = max(2, left_mouth + 1) if occupation_rng.random() < 0.5 else min(width - 3, right_mouth - 1)
        cache_z = max(mouth_z + 3, min(twilight_end - 1, rest_anchor[2]))
        for dz in range(0, 2):
            blocks[(cache_x, 1, cache_z + dz)] = "minecraft:gravel" if occupation_rng.random() < 0.6 else secondary

        # Refuse is biased outside/lateral to the mouth, not deep inside.
        refuse_x = max(1, left_mouth - 2) if occupation_rng.random() < 0.5 else min(width - 2, right_mouth + 2)
        for _ in range({"small": 3, "medium": 6, "large": 9}[scale]):
            z = occupation_rng.randint(max(1, mouth_z - 3), mouth_z + 1)
            blocks[(refuse_x, 1, z)] = "minecraft:bone_block" if occupation_rng.random() < 0.3 else "minecraft:gravel"

        if condition in {"abandoned", "collapsed", "silted", "animal_reoccupied"}:
            additions = {
                "abandoned": 6,
                "collapsed": 16,
                "silted": 22,
                "animal_reoccupied": 10,
            }[condition]
            for _ in range(additions):
                x = condition_rng.randrange(max(1, left_mouth - 1), min(width - 1, right_mouth + 2))
                z = condition_rng.randrange(max(1, mouth_z - 1), max(mouth_z + 1, twilight_end))
                if condition == "silted":
                    material = "minecraft:gravel" if biome_family != "arid" else "minecraft:sand"
                elif condition == "animal_reoccupied":
                    material = condition_rng.choice(("minecraft:bone_block", "minecraft:coarse_dirt", secondary))
                else:
                    material = condition_rng.choice((primary, secondary, ground))
                blocks[(x, 1, z)] = material

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]
        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": archetype.catalog_id,
                "structure_id": archetype.structure_id,
                "name": archetype.name,
                "family_id": archetype.family_id,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "terrain_first_cave_mouth_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "mouth_center_x": mouth_center,
                "mouth_z": mouth_z,
                "mouth_half_width": mouth_half_width,
                "daylight_band": [mouth_z, daylight_end],
                "twilight_band": [daylight_end + 1, twilight_end],
                "interior_stop_z": interior_stop,
                "hearth": [hearth_x, 1, hearth_z],
                "work_zone_anchor": work_anchor,
                "rest_zone_anchor": rest_anchor,
                "cache_anchor": [cache_x, 1, cache_z],
                "occupation_constraint": "primary_activity_must_remain_at_or_before_interior_stop",
                "fingerprint": self._fingerprint(block_list),
            },
        }

    def worldgen_bundle(
        self,
        catalog_id: str,
        *,
        biome_selector: str = "#minecraft:is_overworld",
    ) -> dict[str, Any]:
        archetype = self.archetypes.get(catalog_id)
        if archetype is None:
            raise EarlyHumanGenerationError(f"unsupported early-human archetype: {catalog_id}")

        structure = jigsaw_structure(
            biome_selector=biome_selector,
            start_pool=archetype.start_pool,
            step="surface_structures",
            terrain_adaptation=archetype.terrain_adaptation,
            heightmap="WORLD_SURFACE_WG",
            absolute_y=0,
            max_distance=archetype.max_distance,
        )
        structure_set = random_spread_structure_set(
            archetype.structure_id,
            spacing=archetype.spacing,
            separation=archetype.separation,
            salt=archetype.salt,
        )
        protection = structure_protection_profile(
            structures=[archetype.structure_id],
            family=archetype.family_id,
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
            "catalog_id": catalog_id,
            "structure_id": archetype.structure_id,
            "start_pool": archetype.start_pool,
            "structure": structure,
            "structure_set": structure_set,
            "protection_profile": protection,
            "validation_findings": findings,
        }
