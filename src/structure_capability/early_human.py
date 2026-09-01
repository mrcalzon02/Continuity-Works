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


class EarlyHumanStructureGenerator:
    """Seeded physical generators for the Continuity Works early-human backlog.

    The output shape matches the project's physical structure contract:
    ``{size, blocks, metadata}``.  Terrain-sensitive generators deliberately
    include replace-mode metadata because the final world-placement layer must
    reconcile generated geology with the target terrain instead of treating
    these outputs as freestanding prefab buildings.
    """

    def __init__(self):
        self.archetypes = {E01_001.catalog_id: E01_001}

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

        # Terrain-first cliff/overhang mass.  The roof thickens toward the rear,
        # varies by column, and remains connected to a full rear rock mass.
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

        # Rear support mass prevents a floating canopy and creates natural wall recesses.
        for x in range(width):
            wall_front = rear_start + geology.randint(-2, 1)
            for z in range(max(0, wall_front), depth):
                local_top = height - geology.randint(0, 2)
                for y in range(0, local_top):
                    if geology.random() < 0.90 or z >= depth - 2:
                        blocks[(x, y, z)] = primary if geology.random() < 0.86 else secondary

        # Protected occupation floor: irregular, mostly natural, minimally prepared.
        floor_front = max(2, depth // 4)
        floor_back = max(floor_front + 3, rear_start + 1)
        for x in range(1, width - 1):
            for z in range(floor_front, min(depth - 1, floor_back)):
                if occupation.random() < 0.91:
                    blocks[(x, 0, z)] = ground

        # Approach apron uses sparse compaction rather than a road/path.
        for x in range(2, width - 2):
            for z in range(1, floor_front + 1):
                if occupation.random() < 0.28:
                    blocks[(x, 0, z)] = "minecraft:coarse_dirt"

        # Hearth is offset from center and kept under the protected roof edge.
        hearth_x = occupation.randint(max(2, width // 4), min(width - 3, (width * 3) // 4))
        hearth_z = min(floor_back - 1, floor_front + hearth_rng.randint(2, max(2, depth // 5)))
        hearth_points = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dz in hearth_points:
            blocks[(hearth_x + dx, 1, hearth_z + dz)] = secondary
        blocks[(hearth_x, 0, hearth_z)] = "minecraft:coal_block"
        if condition in {"active", "recent"}:
            blocks[(hearth_x, 1, hearth_z)] = "minecraft:campfire"

        # Work zone: carried toolstone/hammerstone analogue clustered near daylight.
        work_x = max(2, hearth_x - width // 5)
        work_z = max(floor_front, hearth_z - 2)
        for _ in range({"small": 5, "medium": 9, "large": 14}[scale]):
            x = max(1, min(width - 2, work_x + occupation.randint(-3, 3)))
            z = max(1, min(depth - 2, work_z + occupation.randint(-2, 2)))
            if (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = "minecraft:flint" if occupation.random() < 0.55 else secondary

        # Sleeping/rest zone stays toward the quieter protected rear edge.
        sleep_x = min(width - 4, max(3, hearth_x + width // 6))
        sleep_z = min(depth - 3, max(hearth_z + 2, floor_back - 2))
        bedding = "minecraft:moss_block" if biome_family not in {"arid", "tundra"} else "minecraft:hay_block"
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if occupation.random() < 0.72:
                    blocks[(sleep_x + dx, 1, sleep_z + dz)] = bedding

        # Refuse edge deliberately biased toward the exposed lateral/down-gradient side.
        refuse_x = 1 if occupation.random() < 0.5 else width - 2
        for _ in range({"small": 3, "medium": 6, "large": 10}[scale]):
            z = occupation.randint(max(1, floor_front - 1), min(depth - 2, floor_back + 1))
            material = "minecraft:bone_block" if occupation.random() < 0.35 else "minecraft:gravel"
            blocks[(refuse_x, 1, z)] = material

        # Abandoned/collapsed conditions add sediment or fallen roof blocks without
        # replacing the underlying archetype.
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
        fingerprint_input = "\n".join(
            f"{entry['pos']}:{entry['block']}" for entry in block_list
        ).encode("utf-8")

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
                "fingerprint": sha256(fingerprint_input).hexdigest(),
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
            terrain_adaptation="beard_thin",
            heightmap="WORLD_SURFACE_WG",
            absolute_y=0,
            max_distance=80,
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
