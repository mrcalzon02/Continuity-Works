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

CATALOG_ID = "E01-009"
STRUCTURE_ID = "continuityworks:e01_009_stone_tool_knapping_ground"
FAMILY_ID = "continuityworks:early_human_lithic_production"
START_POOL = "continuityworks:early_human/e01_009_stone_tool_knapping_ground"
SCALES = ("small", "medium", "large")
SPACING = 108
SEPARATION = 76
SALT = 101009


class StoneToolKnappingGroundGenerationError(ValueError):
    pass


class StoneToolKnappingGroundGenerator:
    """Deterministic Stage-2/3 implementation for E01-009.

    The structure is an open, task-specific lithic-production landscape. Spatial
    identity comes from provenance-aware raw material, irregular work positions,
    directional flake fans, hazard-aware circulation, core/hammerstone lifecycle,
    and repeated-use lenses rather than from architectural enclosure.
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
    def _palette(biome_family: str) -> dict[str, str]:
        palettes = {
            "temperate": {"ground": "minecraft:coarse_dirt", "local": "minecraft:andesite", "imported": "minecraft:calcite", "hammer": "minecraft:cobblestone", "discard": "minecraft:gravel"},
            "boreal": {"ground": "minecraft:coarse_dirt", "local": "minecraft:tuff", "imported": "minecraft:calcite", "hammer": "minecraft:cobblestone", "discard": "minecraft:gravel"},
            "tundra": {"ground": "minecraft:gravel", "local": "minecraft:stone", "imported": "minecraft:calcite", "hammer": "minecraft:andesite", "discard": "minecraft:gravel"},
            "savanna": {"ground": "minecraft:coarse_dirt", "local": "minecraft:granite", "imported": "minecraft:calcite", "hammer": "minecraft:cobblestone", "discard": "minecraft:gravel"},
            "arid": {"ground": "minecraft:sand", "local": "minecraft:sandstone", "imported": "minecraft:calcite", "hammer": "minecraft:cobblestone", "discard": "minecraft:gravel"},
            "tropical": {"ground": "minecraft:dirt", "local": "minecraft:andesite", "imported": "minecraft:calcite", "hammer": "minecraft:cobblestone", "discard": "minecraft:gravel"},
            "coastal": {"ground": "minecraft:sand", "local": "minecraft:cobblestone", "imported": "minecraft:calcite", "hammer": "minecraft:andesite", "discard": "minecraft:gravel"},
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
        parent_context: str | None = None,
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise StoneToolKnappingGroundGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {"small": (15, 5, 13), "medium": (27, 5, 23), "large": (45, 6, 37)}
        work_ranges = {"small": (1, 1), "medium": (2, 5), "large": (4, 9)}
        width, height, depth = dimensions[scale]

        context_rng = self._rng(seed, "parent_context")
        provenance_rng = self._rng(seed, "material_provenance")
        work_rng = self._rng(seed, "work_positions")
        stage_rng = self._rng(seed, "reduction_stage")
        debris_rng = self._rng(seed, "debris_projection")
        lifecycle_rng = self._rng(seed, "core_lifecycle")
        chronology_rng = self._rng(seed, "chronology")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)

        contexts = (
            "SOURCE_ADJACENT",
            "CAMP_ATTACHED",
            "KILL_BUTCHERY_ATTACHED",
            "TRAVEL_STOP",
            "INDEPENDENT_WORKSITE",
            "MIXED_PROVENANCE",
        )
        context = parent_context or context_rng.choice(contexts)
        if context not in contexts:
            raise StoneToolKnappingGroundGenerationError(f"invalid parent context {context!r}")

        provenance_choices = {
            "SOURCE_ADJACENT": ("LOCAL_COBBLE", "LOCAL_OUTCROP"),
            "CAMP_ATTACHED": ("TRANSPORTED_NODULE", "TRANSPORTED_CORE", "MIXED_LOCAL_IMPORTED"),
            "KILL_BUTCHERY_ATTACHED": ("TRANSPORTED_CORE", "TRANSPORTED_NODULE"),
            "TRAVEL_STOP": ("TRANSPORTED_CORE", "TRANSPORTED_NODULE"),
            "INDEPENDENT_WORKSITE": ("LOCAL_COBBLE", "TRANSPORTED_NODULE", "MIXED_LOCAL_IMPORTED"),
            "MIXED_PROVENANCE": ("MIXED_LOCAL_IMPORTED",),
        }
        provenance = provenance_rng.choice(provenance_choices[context])
        toolstone = palette["imported"] if provenance.startswith("TRANSPORTED") else palette["local"]

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2

        # Sparse trampled working ground only; no floor slab or building mass.
        for x in range(1, width - 1):
            for z in range(1, depth - 1):
                distance = math.hypot(x - cx, z - cz)
                if distance <= min(width, depth) * 0.42 and work_rng.random() < 0.19:
                    blocks[(x, 0, z)] = palette["ground"]

        work_count = work_rng.randint(*work_ranges[scale])
        min_spacing = {"small": 0, "medium": 5, "large": 6}[scale]
        work_positions: list[tuple[int, int]] = []
        attempts = 0
        while len(work_positions) < work_count and attempts < 300:
            attempts += 1
            x = work_rng.randint(3, width - 4)
            z = work_rng.randint(3, depth - 4)
            if all(math.hypot(x - ox, z - oz) >= min_spacing for ox, oz in work_positions):
                work_positions.append((x, z))
        if not work_positions:
            raise StoneToolKnappingGroundGenerationError("could not place a stable knapping position")

        reduction_profiles = ("TESTING", "PRIMARY_REDUCTION", "SECONDARY_SHAPING", "MAINTENANCE", "MIXED_SEQUENCE")
        work_records: list[dict[str, Any]] = []
        dense_hazard: set[tuple[int, int]] = set()
        debris_points: list[list[int]] = []
        hammerstones: list[list[int]] = []
        core_points: list[list[int]] = []

        # Shared raw-material staging sits up-circulation from work positions.
        staging_x = max(2, min(width - 3, min(x for x, _ in work_positions) - 2))
        staging_z = max(2, min(depth - 3, int(sum(z for _, z in work_positions) / len(work_positions))))
        staging_count = {"small": 3, "medium": 7, "large": 13}[scale]
        raw_material: list[list[int]] = []
        for _ in range(staging_count):
            x = max(1, min(width - 2, staging_x + provenance_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, staging_z + provenance_rng.randint(-2, 2)))
            block = palette["local"]
            if provenance == "MIXED_LOCAL_IMPORTED" and provenance_rng.random() < 0.3:
                block = palette["imported"]
            elif provenance.startswith("TRANSPORTED"):
                block = palette["imported"]
            blocks[(x, 1, z)] = block
            raw_material.append([x, 1, z])

        for idx, (wx, wz) in enumerate(work_positions):
            facing_angle = debris_rng.random() * math.tau
            fx = math.cos(facing_angle)
            fz = math.sin(facing_angle)
            stage = stage_rng.choice(reduction_profiles)
            if scale != "small" and idx == 0 and condition == "repeated":
                stage = "MIXED_SEQUENCE"

            # Natural seat/work marker and hammerstone remain visually minor.
            if work_rng.random() < 0.65:
                blocks[(wx, 1, wz)] = palette["hammer"]
            hammer_angle = facing_angle + math.pi * (0.45 + lifecycle_rng.random() * 0.2)
            hx = max(1, min(width - 2, int(round(wx + math.cos(hammer_angle) * 2))))
            hz = max(1, min(depth - 2, int(round(wz + math.sin(hammer_angle) * 2))))
            blocks[(hx, 1, hz)] = palette["hammer"]
            hammerstones.append([hx, 1, hz])

            core_count = {"TESTING": 1, "PRIMARY_REDUCTION": 2, "SECONDARY_SHAPING": 2, "MAINTENANCE": 1, "MIXED_SEQUENCE": 3}[stage]
            local_cores: list[list[int]] = []
            for _ in range(core_count):
                x = max(1, min(width - 2, wx + lifecycle_rng.randint(-1, 1)))
                z = max(1, min(depth - 2, wz + lifecycle_rng.randint(-1, 1)))
                if (x, 1, z) == (wx, 1, wz):
                    z = min(depth - 2, z + 1)
                blocks[(x, 1, z)] = toolstone
                point = [x, 1, z]
                core_points.append(point)
                local_cores.append(point)

            density = {"TESTING": 6, "PRIMARY_REDUCTION": 16, "SECONDARY_SHAPING": 20, "MAINTENANCE": 5, "MIXED_SEQUENCE": 24}[stage]
            local_debris: list[list[int]] = []
            for _ in range(density):
                distance = debris_rng.uniform(2.0, 6.5 if scale == "large" else 5.0)
                lateral = debris_rng.gauss(0.0, 1.4)
                x = int(round(wx + fx * distance - fz * lateral))
                z = int(round(wz + fz * distance + fx * lateral))
                if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                    continue
                blocks[(x, 1, z)] = palette["discard"] if debris_rng.random() < 0.68 else toolstone
                point = [x, 1, z]
                local_debris.append(point)
                debris_points.append(point)
                if distance <= 4.4:
                    dense_hazard.add((x, z))

            work_records.append({
                "index": idx,
                "position": [wx, 1, wz],
                "stage": stage,
                "facing_vector": [round(fx, 3), round(fz, 3)],
                "cores": local_cores,
                "debris": local_debris,
            })

        # Safe circulation connects staging and all work clusters while biasing away from dense hazard.
        circulation: set[tuple[int, int]] = set()
        anchor = (staging_x, staging_z)
        for target in work_positions:
            for x, z in self._line(anchor, target):
                if (x, z) not in dense_hazard:
                    circulation.add((x, z))
            anchor = target
        for x, z in circulation:
            blocks[(x, 0, z)] = palette["ground"]
            if (x, z) in dense_hazard:
                raise StoneToolKnappingGroundGenerationError("circulation crossed dense sharp-debris field")

        # Repeated-use chronology adds an older reduction lens and displaced discard margin.
        legacy_lens: list[list[int]] = []
        if condition in {"repeated", "partially_buried", "disturbed", "source_depleted"}:
            lx = max(2, min(width - 3, cx + chronology_rng.randint(-width // 5, width // 5)))
            lz = max(2, min(depth - 3, cz + chronology_rng.randint(-depth // 5, depth // 5)))
            for _ in range({"small": 4, "medium": 9, "large": 16}[scale]):
                x = max(1, min(width - 2, lx + chronology_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, lz + chronology_rng.randint(-3, 3)))
                if (x, z) not in circulation:
                    block = palette["discard"] if chronology_rng.random() < 0.8 else toolstone
                    blocks[(x, 1, z)] = block
                    legacy_lens.append([x, 1, z])

        # Weathering/burial removes part of surface evidence without destroying the reduction logic.
        if condition in {"abandoned", "partially_buried", "disturbed", "source_depleted", "repurposed"}:
            candidates = [pos for pos in blocks if pos[1] == 1 and pos not in {(p[0], p[1], p[2]) for p in hammerstones}]
            condition_rng.shuffle(candidates)
            loss = {"abandoned": 0.20, "partially_buried": 0.35, "disturbed": 0.28, "source_depleted": 0.15, "repurposed": 0.12}[condition]
            for pos in candidates[: int(len(candidates) * loss)]:
                blocks.pop(pos, None)

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
        ]

        qualification = {
            "lithic_reduction_primary": bool(work_records and debris_points and raw_material),
            "directional_debris_present": all(record["debris"] for record in work_records),
            "raw_material_relationship_explicit": bool(provenance),
            "hammerstone_present": bool(hammerstones),
            "safe_circulation": all(point not in dense_hazard for point in circulation),
            "no_architectural_dependency": True,
            "technology_ceiling_valid": True,
        }
        if not all(qualification.values()):
            failed = [key for key, value in qualification.items() if not value]
            raise StoneToolKnappingGroundGenerationError(f"qualification failed: {failed}")

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
                "seed": str(seed),
                "parent_context": context,
                "provenance": provenance,
                "raw_material": raw_material,
                "work_positions": [list(p) for p in work_positions],
                "work_records": work_records,
                "hammerstones": hammerstones,
                "core_points": core_points,
                "debris_points": debris_points,
                "dense_hazard_cells": [[x, z] for x, z in sorted(dense_hazard)],
                "circulation": [[x, 0, z] for x, z in sorted(circulation)],
                "legacy_lens": legacy_lens,
                "terrain_mode": "terrain_responsive_open_worksite",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "compatible_family_requires_shared_parent_reservation": True,
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
            "family_id": FAMILY_ID,
            "start_pool": START_POOL,
            "structure": structure,
            "structure_set": structure_set,
            "protection_profile": protection,
            "validation_findings": findings,
            "compatibility_mode": "additive_non_destructive",
            "compatible_family_requires_shared_parent_reservation": True,
        }
