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

CATALOG_ID = "E01-010"
STRUCTURE_ID = "continuityworks:e01_010_flint_procurement_pit"
FAMILY_ID = "continuityworks:early_human_lithic_source"
START_POOL = "continuityworks:early_human/e01_010_flint_procurement_pit"
SCALES = ("small", "medium", "large")
SPACING = 116
SEPARATION = 84
SALT = 101010


class FlintProcurementPitGenerationError(ValueError):
    pass


class FlintProcurementPitGenerator:
    """Deterministic Stage-2/3 implementation for E01-010.

    Identity is source-first shallow procurement: exposed lithic source, open-sky
    extraction scars, spoil, rejected/tested material, selected-material staging,
    and safe carry-out. On-site reduction remains deliberately subordinate.
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
            "temperate": {"ground": "minecraft:coarse_dirt", "substrate": "minecraft:stone", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:andesite"},
            "boreal": {"ground": "minecraft:coarse_dirt", "substrate": "minecraft:tuff", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:stone"},
            "tundra": {"ground": "minecraft:gravel", "substrate": "minecraft:stone", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:andesite"},
            "savanna": {"ground": "minecraft:coarse_dirt", "substrate": "minecraft:granite", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:granite"},
            "arid": {"ground": "minecraft:sand", "substrate": "minecraft:sandstone", "source": "minecraft:calcite", "spoil": "minecraft:sand", "reject": "minecraft:sandstone"},
            "tropical": {"ground": "minecraft:dirt", "substrate": "minecraft:stone", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:andesite"},
            "coastal": {"ground": "minecraft:sand", "substrate": "minecraft:stone", "source": "minecraft:calcite", "spoil": "minecraft:gravel", "reject": "minecraft:cobblestone"},
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
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise FlintProcurementPitGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        valid_conditions = {
            "active", "recent", "repeated", "abandoned", "partially_infilled",
            "disturbed", "source_depleted", "repurposed",
        }
        if condition not in valid_conditions:
            raise FlintProcurementPitGenerationError(f"invalid condition {condition!r}")

        dimensions = {"small": (17, 6, 15), "medium": (29, 7, 25), "large": (47, 8, 39)}
        pit_ranges = {"small": (1, 2), "medium": (2, 5), "large": (4, 9)}
        depth_caps = {"small": 2, "medium": 3, "large": 4}
        width, height, depth = dimensions[scale]

        source_rng = self._rng(seed, "source_lenses")
        pit_rng = self._rng(seed, "pit_layout")
        spoil_rng = self._rng(seed, "spoil_projection")
        test_rng = self._rng(seed, "testing")
        staging_rng = self._rng(seed, "selected_material")
        chronology_rng = self._rng(seed, "chronology")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2

        # Local ground is intentionally sparse; no artificial slab or quarry floor.
        for x in range(1, width - 1):
            for z in range(1, depth - 1):
                if source_rng.random() < 0.14:
                    blocks[(x, 0, z)] = palette["ground"]

        # Source lens is established before excavation and remains mostly near surface.
        lens_angle = source_rng.random() * math.tau
        lx, lz = math.cos(lens_angle), math.sin(lens_angle)
        source_cells: list[tuple[int, int]] = []
        source_length = {"small": 8, "medium": 15, "large": 25}[scale]
        for step in range(-source_length // 2, source_length // 2 + 1):
            base_x = int(round(cx + lx * step))
            base_z = int(round(cz + lz * step))
            for lateral in (-1, 0, 1):
                x = int(round(base_x - lz * lateral))
                z = int(round(base_z + lx * lateral))
                if 2 <= x < width - 2 and 2 <= z < depth - 2 and source_rng.random() < 0.82:
                    source_cells.append((x, z))
                    blocks[(x, 0, z)] = palette["source"]

        if not source_cells:
            raise FlintProcurementPitGenerationError("source lens generation failed")

        pit_count = pit_rng.randint(*pit_ranges[scale])
        pit_centers: list[tuple[int, int]] = []
        attempts = 0
        while len(pit_centers) < pit_count and attempts < 400:
            attempts += 1
            px, pz = pit_rng.choice(source_cells)
            if all(math.hypot(px - ox, pz - oz) >= 4 for ox, oz in pit_centers):
                pit_centers.append((px, pz))
        if not pit_centers:
            raise FlintProcurementPitGenerationError("could not place procurement pits")

        pit_records: list[dict[str, Any]] = []
        pit_footprint: set[tuple[int, int]] = set()
        spoil_cells: set[tuple[int, int]] = set()
        rejected_points: list[list[int]] = []

        for index, (px, pz) in enumerate(pit_centers):
            radius = pit_rng.randint(2, 3 if scale != "large" else 4)
            cap = depth_caps[scale]
            local_depth = pit_rng.randint(1, cap)
            excavated: list[list[int]] = []
            source_exposed: list[list[int]] = []

            for x in range(max(1, px - radius), min(width - 1, px + radius + 1)):
                for z in range(max(1, pz - radius), min(depth - 1, pz + radius + 1)):
                    dist = math.hypot(x - px, z - pz)
                    if dist > radius + pit_rng.random() * 0.45:
                        continue
                    cell_depth = max(1, min(local_depth, int(round(local_depth * (1.0 - min(0.75, dist / max(1, radius + 0.5)))) + 0.5)))
                    pit_footprint.add((x, z))
                    blocks[(x, 0, z)] = palette["substrate"]
                    if (x, z) in source_cells or source_rng.random() < 0.35:
                        blocks[(x, 0, z)] = palette["source"]
                        source_exposed.append([x, 0, z])
                    excavated.append([x, -cell_depth, z])

            # Spoil projects laterally/down-gradient from the pit, never uniformly.
            spoil_angle = lens_angle + math.pi / 2 + spoil_rng.uniform(-0.55, 0.55)
            sx, sz = math.cos(spoil_angle), math.sin(spoil_angle)
            for _ in range({"small": 7, "medium": 14, "large": 23}[scale]):
                distance = spoil_rng.uniform(radius + 1.5, radius + 5.0)
                lateral = spoil_rng.gauss(0.0, 1.5)
                x = int(round(px + sx * distance - sz * lateral))
                z = int(round(pz + sz * distance + sx * lateral))
                if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                    continue
                if (x, z) in pit_footprint:
                    continue
                blocks[(x, 1, z)] = palette["spoil"] if spoil_rng.random() < 0.72 else palette["reject"]
                spoil_cells.add((x, z))

            # Tested/rejected material remains sparse versus a true knapping ground.
            local_rejects = test_rng.randint(1, 3 if scale != "large" else 4)
            for _ in range(local_rejects):
                angle = test_rng.random() * math.tau
                dist = test_rng.uniform(radius + 0.5, radius + 2.5)
                x = max(1, min(width - 2, int(round(px + math.cos(angle) * dist))))
                z = max(1, min(depth - 2, int(round(pz + math.sin(angle) * dist))))
                if (x, z) not in pit_footprint:
                    blocks[(x, 1, z)] = palette["reject"]
                    rejected_points.append([x, 1, z])

            pit_records.append({
                "index": index,
                "center": [px, 0, pz],
                "radius": radius,
                "max_depth": local_depth,
                "excavated_cells": excavated,
                "source_exposed": source_exposed,
            })

        # Carry-out direction runs away from the spoil side and ends at selected material staging.
        carry_angle = lens_angle - math.pi / 2
        carry_target = (
            max(2, min(width - 3, int(round(cx + math.cos(carry_angle) * width * 0.36)))),
            max(2, min(depth - 3, int(round(cz + math.sin(carry_angle) * depth * 0.36)))),
        )
        nearest = min(pit_centers, key=lambda p: math.hypot(p[0] - carry_target[0], p[1] - carry_target[1]))
        route = [p for p in self._line(nearest, carry_target) if p not in pit_footprint]
        for x, z in route:
            blocks[(x, 0, z)] = palette["ground"]

        staging_points: list[list[int]] = []
        staging_count = {"small": 2, "medium": 5, "large": 9}[scale]
        for _ in range(staging_count):
            x = max(1, min(width - 2, carry_target[0] + staging_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, carry_target[1] + staging_rng.randint(-2, 2)))
            if (x, z) not in pit_footprint:
                blocks[(x, 1, z)] = palette["source"]
                staging_points.append([x, 1, z])

        legacy_pits: list[list[int]] = []
        if condition in {"repeated", "partially_infilled", "disturbed", "source_depleted", "repurposed"}:
            lp = chronology_rng.choice(pit_centers)
            for _ in range({"small": 3, "medium": 7, "large": 12}[scale]):
                x = max(1, min(width - 2, lp[0] + chronology_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, lp[1] + chronology_rng.randint(-3, 3)))
                if (x, z) in pit_footprint:
                    blocks[(x, 1, z)] = palette["ground"] if chronology_rng.random() < 0.7 else palette["spoil"]
                    legacy_pits.append([x, 1, z])

        if condition in {"abandoned", "partially_infilled", "disturbed", "source_depleted", "repurposed"}:
            candidates = [pos for pos in blocks if pos[1] == 1]
            condition_rng.shuffle(candidates)
            loss = {"abandoned": 0.20, "partially_infilled": 0.12, "disturbed": 0.24, "source_depleted": 0.18, "repurposed": 0.10}[condition]
            for pos in candidates[: int(len(candidates) * loss)]:
                blocks.pop(pos, None)

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
            if y >= 0
        ]

        max_modeled_depth = max(record["max_depth"] for record in pit_records)
        qualification = {
            "procurement_primary": bool(pit_records and source_cells and spoil_cells and staging_points),
            "source_explicit": bool(source_cells),
            "shallow_open_pits": max_modeled_depth <= depth_caps[scale],
            "spoil_related_to_pits": bool(spoil_cells),
            "carry_out_route_present": bool(route),
            "selected_material_staging": bool(staging_points),
            "testing_subordinate": len(rejected_points) < max(8, len(spoil_cells)),
            "no_later_mining_infrastructure": True,
            "open_sky_required": True,
        }
        if not all(qualification.values()):
            raise FlintProcurementPitGenerationError(f"E01-010 qualification failed: {qualification}")

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
                "terrain_mode": "surface_shallow_procurement",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "source_cells": [[x, 0, z] for x, z in source_cells],
                "pits": pit_records,
                "spoil_cells": [[x, 1, z] for x, z in sorted(spoil_cells)],
                "rejected_points": rejected_points,
                "carry_out_route": [[x, 0, z] for x, z in route],
                "selected_material_staging": staging_points,
                "legacy_infill": legacy_pits,
                "qualification": qualification,
                "compatibility_mode": "additive_non_destructive",
                "compatible_family_requires_shared_parent_reservation": True,
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
