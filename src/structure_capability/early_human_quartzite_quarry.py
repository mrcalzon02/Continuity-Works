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

CATALOG_ID = "E01-011"
STRUCTURE_ID = "continuityworks:e01_011_quartzite_quarry"
FAMILY_ID = "continuityworks:early_human_lithic_source"
START_POOL = "continuityworks:early_human/e01_011_quartzite_quarry"
SCALES = ("small", "medium", "large")
SPACING = 124
SEPARATION = 88
SALT = 101011


class QuartziteQuarryGenerationError(ValueError):
    pass


class QuartziteQuarryGenerator:
    """Deterministic Stage-2/3 implementation for E01-011 Quartzite Quarry."""

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
            "temperate": {"ground": "minecraft:coarse_dirt", "host": "minecraft:stone", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:andesite", "weathered": "minecraft:mossy_cobblestone"},
            "boreal": {"ground": "minecraft:coarse_dirt", "host": "minecraft:tuff", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:stone", "weathered": "minecraft:mossy_cobblestone"},
            "tundra": {"ground": "minecraft:gravel", "host": "minecraft:stone", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:andesite", "weathered": "minecraft:stone"},
            "savanna": {"ground": "minecraft:coarse_dirt", "host": "minecraft:granite", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:granite", "weathered": "minecraft:stone"},
            "arid": {"ground": "minecraft:sand", "host": "minecraft:sandstone", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:stone", "weathered": "minecraft:sandstone"},
            "tropical": {"ground": "minecraft:dirt", "host": "minecraft:stone", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:andesite", "weathered": "minecraft:mossy_cobblestone"},
            "coastal": {"ground": "minecraft:gravel", "host": "minecraft:stone", "source": "minecraft:diorite", "spoil": "minecraft:gravel", "hammer": "minecraft:cobblestone", "weathered": "minecraft:stone"},
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
            raise QuartziteQuarryGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {
            "active", "recent", "repeated", "abandoned", "partially_collapsed",
            "sediment_reworked", "source_depleted", "repurposed",
        }
        if condition not in valid_conditions:
            raise QuartziteQuarryGenerationError(f"invalid condition {condition!r}")

        dimensions = {"small": (23, 8, 19), "medium": (37, 10, 31), "large": (57, 12, 45)}
        face_ranges = {"small": (1, 2), "medium": (2, 4), "large": (4, 7)}
        scar_ranges = {"small": (2, 4), "medium": (5, 10), "large": (10, 18)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)

        source_rng = self._rng(seed, "source_orientation")
        face_rng = self._rng(seed, "face_topology")
        scar_rng = self._rng(seed, "extraction_scars")
        debris_rng = self._rng(seed, "coarse_debris")
        hammer_rng = self._rng(seed, "hammerstones")
        staging_rng = self._rng(seed, "staging")
        haul_rng = self._rng(seed, "haul_routing")
        reduction_rng = self._rng(seed, "primary_reduction")
        chronology_rng = self._rng(seed, "chronology")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2

        strike_angle = source_rng.uniform(-0.35, 0.35)
        strike_dx, strike_dz = math.cos(strike_angle), math.sin(strike_angle)
        outward_x, outward_z = -strike_dz, strike_dx
        if source_rng.random() < 0.5:
            outward_x, outward_z = -outward_x, -outward_z

        face_length = {"small": 13, "medium": 23, "large": 37}[scale]
        source_depth = {"small": 4, "medium": 5, "large": 6}[scale]
        base_y = 1
        face_cells: list[tuple[int, int, int]] = []
        source_columns: set[tuple[int, int]] = set()

        for step in range(-face_length // 2, face_length // 2 + 1):
            bx = int(round(cx + strike_dx * step))
            bz = int(round(cz + strike_dz * step))
            for inward in range(0, source_depth):
                x = int(round(bx - outward_x * inward))
                z = int(round(bz - outward_z * inward))
                if not (2 <= x < width - 2 and 2 <= z < depth - 2):
                    continue
                source_columns.add((x, z))
                local_top = min(height - 2, 3 + int(inward * 0.65) + source_rng.randint(0, 2))
                for y in range(base_y, local_top + 1):
                    blocks[(x, y, z)] = palette["source"] if inward <= 2 else palette["host"]
                    if inward == 0:
                        face_cells.append((x, y, z))
                blocks[(x, 0, z)] = palette["host"]

        face_segments = face_rng.randint(*face_ranges[scale])
        segment_centers: list[tuple[int, int]] = []
        for i in range(face_segments):
            t = (i + 1) / (face_segments + 1)
            step = int(round(-face_length / 2 + t * face_length + face_rng.randint(-2, 2)))
            sx = int(round(cx + strike_dx * step))
            sz = int(round(cz + strike_dz * step))
            segment_centers.append((sx, sz))

        scar_count = scar_rng.randint(*scar_ranges[scale])
        scars: list[list[int]] = []
        scar_footprint: set[tuple[int, int]] = set()
        for _ in range(scar_count):
            sx, sz = scar_rng.choice(segment_centers)
            along = scar_rng.randint(-2, 2)
            inward = scar_rng.randint(0, 2)
            x = int(round(sx + strike_dx * along - outward_x * inward))
            z = int(round(sz + strike_dz * along - outward_z * inward))
            if not (2 <= x < width - 2 and 2 <= z < depth - 2):
                continue
            scar_height = scar_rng.randint(1, 3 if scale != "large" else 4)
            for y in range(1, min(height - 1, scar_height + 1)):
                if (x, y, z) in blocks:
                    blocks.pop((x, y, z), None)
                    scars.append([x, y, z])
            scar_footprint.add((x, z))

        bench_cells: set[tuple[int, int]] = set()
        for sx, sz in segment_centers:
            for along in range(-2, 3):
                for outward in range(1, 4):
                    x = int(round(sx + strike_dx * along + outward_x * outward))
                    z = int(round(sz + strike_dz * along + outward_z * outward))
                    if 1 <= x < width - 1 and 1 <= z < depth - 1:
                        blocks[(x, 0, z)] = palette["ground"]
                        bench_cells.add((x, z))

        debris_cells: set[tuple[int, int]] = set()
        debris_count = {"small": 22, "medium": 52, "large": 105}[scale]
        for _ in range(debris_count):
            sx, sz = debris_rng.choice(segment_centers)
            outward = debris_rng.uniform(2.5, 9.0 if scale == "small" else 13.0 if scale == "medium" else 18.0)
            along = debris_rng.gauss(0.0, 3.0 if scale == "small" else 5.0)
            x = int(round(sx + outward_x * outward + strike_dx * along))
            z = int(round(sz + outward_z * outward + strike_dz * along))
            if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                continue
            if (x, z) in bench_cells:
                continue
            y = 1 if debris_rng.random() < 0.92 else 2
            blocks[(x, y, z)] = palette["source"] if debris_rng.random() < 0.46 else palette["spoil"]
            debris_cells.add((x, z))

        hammerstones: list[list[int]] = []
        for sx, sz in segment_centers:
            for _ in range(hammer_rng.randint(1, 3)):
                x = int(round(sx + outward_x * hammer_rng.uniform(1.0, 3.0) + strike_dx * hammer_rng.uniform(-1.5, 1.5)))
                z = int(round(sz + outward_z * hammer_rng.uniform(1.0, 3.0) + strike_dz * hammer_rng.uniform(-1.5, 1.5)))
                if 1 <= x < width - 1 and 1 <= z < depth - 1:
                    blocks[(x, 1, z)] = palette["hammer"]
                    hammerstones.append([x, 1, z])

        reduction_points: list[list[int]] = []
        if scale in {"medium", "large"}:
            target_clusters = 2 if scale == "medium" else 4
            for _ in range(target_clusters):
                sx, sz = reduction_rng.choice(segment_centers)
                anchor_x = int(round(sx + outward_x * reduction_rng.uniform(4.0, 7.0)))
                anchor_z = int(round(sz + outward_z * reduction_rng.uniform(4.0, 7.0)))
                for _ in range(reduction_rng.randint(3, 7)):
                    x = max(1, min(width - 2, anchor_x + reduction_rng.randint(-2, 2)))
                    z = max(1, min(depth - 2, anchor_z + reduction_rng.randint(-2, 2)))
                    if (x, z) not in bench_cells:
                        blocks[(x, 1, z)] = palette["spoil"] if reduction_rng.random() < 0.65 else palette["source"]
                        reduction_points.append([x, 1, z])

        staging_origin = (
            max(2, min(width - 3, int(round(cx + outward_x * (depth * 0.28) + strike_dx * (width * 0.22))))),
            max(2, min(depth - 3, int(round(cz + outward_z * (depth * 0.28) + strike_dz * (width * 0.22))))),
        )
        staging_points: list[list[int]] = []
        for _ in range({"small": 3, "medium": 7, "large": 12}[scale]):
            x = max(1, min(width - 2, staging_origin[0] + staging_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, staging_origin[1] + staging_rng.randint(-2, 2)))
            blocks[(x, 1, z)] = palette["source"]
            staging_points.append([x, 1, z])

        edge_target = (
            max(1, min(width - 2, int(round(staging_origin[0] + outward_x * max(width, depth) * 0.45)))),
            max(1, min(depth - 2, int(round(staging_origin[1] + outward_z * max(width, depth) * 0.45)))),
        )
        route = self._line(staging_origin, edge_target)
        haul_cells: list[list[int]] = []
        for x, z in route:
            if (x, z) in debris_cells and haul_rng.random() < 0.85:
                continue
            blocks[(x, 0, z)] = palette["ground"]
            haul_cells.append([x, 0, z])

        legacy_face: list[list[int]] = []
        if condition in {"repeated", "source_depleted", "repurposed"}:
            sx, sz = chronology_rng.choice(segment_centers)
            for along in range(-3, 4):
                x = int(round(sx + strike_dx * along))
                z = int(round(sz + strike_dz * along))
                if 1 <= x < width - 1 and 1 <= z < depth - 1:
                    for y in range(1, min(height - 1, 4)):
                        blocks.pop((x, y, z), None)
                        legacy_face.append([x, y, z])

        if condition in {"abandoned", "partially_collapsed", "sediment_reworked", "source_depleted", "repurposed"}:
            if condition == "partially_collapsed":
                for _ in range({"small": 8, "medium": 18, "large": 34}[scale]):
                    sx, sz = condition_rng.choice(segment_centers)
                    x = int(round(sx + outward_x * condition_rng.uniform(1.0, 5.0) + strike_dx * condition_rng.uniform(-3.0, 3.0)))
                    z = int(round(sz + outward_z * condition_rng.uniform(1.0, 5.0) + strike_dz * condition_rng.uniform(-3.0, 3.0)))
                    if 1 <= x < width - 1 and 1 <= z < depth - 1:
                        blocks[(x, 1, z)] = condition_rng.choice((palette["host"], palette["source"], palette["spoil"]))
            elif condition == "sediment_reworked":
                for pos in list(blocks):
                    if pos[1] == 1 and blocks[pos] == palette["spoil"] and condition_rng.random() < 0.22:
                        blocks[pos] = palette["ground"]
            elif condition in {"abandoned", "repurposed"} and biome_family in {"temperate", "boreal", "tropical"}:
                candidates = [p for p in blocks if p[1] == 0]
                condition_rng.shuffle(candidates)
                for x, y, z in candidates[: max(1, len(candidates) // 12)]:
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = palette["weathered"]

        block_list = [
            {"pos": [x, y, z], "block": block}
            for (x, y, z), block in sorted(blocks.items())
            if 0 <= x < width and 0 <= y < height and 0 <= z < depth
        ]

        qualification = {
            "extraction_primary": bool(source_columns and segment_centers and scars),
            "source_outcrop_present": bool(source_columns),
            "working_face_present": bool(segment_centers),
            "extraction_scars_present": bool(scars),
            "natural_bench_present": bool(bench_cells),
            "coarse_apron_present": len(debris_cells) >= 8,
            "hammerstone_zone_present": bool(hammerstones),
            "selected_blank_staging": bool(staging_points),
            "haul_route_present": len(haul_cells) >= 2,
            "primary_reduction_subordinate": len(reduction_points) < len(debris_cells),
            "larger_than_procurement_pit": width >= 23 and depth >= 19,
            "no_later_quarry_infrastructure": True,
            "open_sky_required": True,
        }
        if not all(qualification.values()):
            raise QuartziteQuarryGenerationError(f"E01-011 qualification failed: {qualification}")

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
                "terrain_mode": "surface_quarry_face_blended",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "material_semantics": {"source": "quartzite_role_proxy", "source_block": palette["source"]},
                "face_segment_count": len(segment_centers),
                "face_segments": [[x, 0, z] for x, z in segment_centers],
                "extraction_scar_count": len(scars),
                "coarse_debris_cell_count": len(debris_cells),
                "hammerstone_count": len(hammerstones),
                "primary_reduction_point_count": len(reduction_points),
                "staging_points": staging_points,
                "haul_route": haul_cells,
                "legacy_face": legacy_face,
                "qualification": qualification,
                "compatible_family_policy": "same_parent_reservation_only",
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
            max_distance=96,
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
            "compatible_family_policy": "same_parent_reservation_only",
            "replace_policy": "bounded_additive_non_destructive",
            "validation_findings": findings,
        }
