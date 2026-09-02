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

CATALOG_ID = "E01-015"
STRUCTURE_ID = "continuityworks:e01_015_marrow_processing_ground"
FAMILY_ID = "continuityworks:early_human_carcass_processing"
START_POOL = "continuityworks:early_human/e01_015_marrow_processing_ground"
SCALES = ("small", "medium", "large")
SPACING = 124
SEPARATION = 88
SALT = 101015


class MarrowProcessingGroundGenerationError(ValueError):
    pass


class MarrowProcessingGroundGenerator:
    """Deterministic Stage-2/3 implementation for E01-015."""

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
        culture_profile: str = "immediate_consumption",
    ) -> dict[str, Any]:
        if scale not in SCALES:
            raise MarrowProcessingGroundGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")
        valid_conditions = {
            "active", "recent", "repeated", "abandoned", "weathered",
            "scavenger_reworked", "sediment_reworked", "repurposed",
        }
        if condition not in valid_conditions:
            raise MarrowProcessingGroundGenerationError(f"invalid condition {condition!r}")
        valid_cultures = {
            "immediate_consumption", "distributed_extraction", "intensive_cleaning", "repeated_use",
        }
        if culture_profile not in valid_cultures:
            raise MarrowProcessingGroundGenerationError(f"invalid culture profile {culture_profile!r}")

        dimensions = {"small": (19, 6, 17), "medium": (29, 7, 25), "large": (41, 8, 33)}
        pocket_ranges = {"small": (1, 1), "medium": (2, 3), "large": (3, 5)}
        width, height, depth = dimensions[scale]
        palette = self._palette(biome_family)
        layout_rng = self._rng(seed, "layout")
        pocket_rng = self._rng(seed, "handling_pockets")
        bone_rng = self._rng(seed, "opened_bone")
        staging_rng = self._rng(seed, "staging")
        discard_rng = self._rng(seed, "spent_fragments")
        percussion_rng = self._rng(seed, "light_percussion")
        hearth_rng = self._rng(seed, "hearth")
        condition_rng = self._rng(seed, "condition")

        blocks: dict[tuple[int, int, int], str] = {}
        cx, cz = width // 2, depth // 2
        angle = layout_rng.uniform(0.0, math.pi)
        clean_x, clean_z = math.cos(angle), math.sin(angle)
        dirty_x, dirty_z = -clean_x, -clean_z
        side_x, side_z = -clean_z, clean_x

        pocket_count = pocket_rng.randint(*pocket_ranges[scale])
        if culture_profile == "distributed_extraction":
            pocket_count = pocket_ranges[scale][1]
        elif culture_profile == "immediate_consumption" and scale != "small":
            pocket_count = pocket_ranges[scale][0]

        spacing = {"small": 0, "medium": 6, "large": 7}[scale]
        offsets = [0] if pocket_count == 1 else [int(round((i - (pocket_count - 1) / 2) * spacing)) for i in range(pocket_count)]

        handling_pockets: list[dict[str, Any]] = []
        activity_stances: list[list[int]] = []
        opened_bone_points: list[list[int]] = []
        stain_points: list[list[int]] = []

        for idx, lateral in enumerate(offsets):
            along = pocket_rng.randint(-2, 2)
            px = max(3, min(width - 4, int(round(cx + side_x * lateral + clean_x * along))))
            pz = max(3, min(depth - 4, int(round(cz + side_z * lateral + clean_z * along))))

            local_stain_target = {"small": 6, "medium": 8, "large": 10}[scale]
            if culture_profile == "repeated_use":
                local_stain_target += 5
            local_bone_target = {"small": 7, "medium": 10, "large": 13}[scale]
            if culture_profile == "intensive_cleaning":
                local_bone_target += 3

            local_stains: list[list[int]] = []
            for _ in range(local_stain_target):
                x = max(1, min(width - 2, px + bone_rng.randint(-2, 2)))
                z = max(1, min(depth - 2, pz + bone_rng.randint(-2, 2)))
                blocks[(x, 0, z)] = palette["stain"]
                local_stains.append([x, 0, z])
                stain_points.append([x, 0, z])

            local_bones: list[list[int]] = []
            for _ in range(local_bone_target):
                x = max(1, min(width - 2, px + bone_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, pz + bone_rng.randint(-3, 3)))
                blocks[(x, 1, z)] = palette["bone"] if bone_rng.random() < 0.65 else palette["debris"]
                local_bones.append([x, 1, z])
                opened_bone_points.append([x, 1, z])

            sx = max(2, min(width - 3, int(round(px + clean_x * 2))))
            sz = max(2, min(depth - 3, int(round(pz + clean_z * 2))))
            blocks[(sx, 0, sz)] = palette["ground"]
            blocks.pop((sx, 1, sz), None)
            activity_stances.append([sx, 0, sz])

            handling_pockets.append({
                "index": idx,
                "center": [px, 0, pz],
                "stance": [sx, 0, sz],
                "opened_bone_count": len(local_bones),
                "stain_count": len(local_stains),
            })

        stage_distance = {"small": 6, "medium": 8, "large": 10}[scale]
        staging_center = (
            max(2, min(width - 3, int(round(cx + clean_x * stage_distance)))),
            max(2, min(depth - 3, int(round(cz + clean_z * stage_distance)))),
        )
        staging_count = {"small": 5, "medium": 9, "large": 14}[scale]
        staging_points: list[list[int]] = []
        for _ in range(staging_count):
            x = max(1, min(width - 2, staging_center[0] + staging_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, staging_center[1] + staging_rng.randint(-2, 2)))
            blocks[(x, 1, z)] = palette["bone"]
            staging_points.append([x, 1, z])

        dirty_distance = {"small": 7, "medium": 10, "large": 13}[scale]
        discard_center = (
            max(2, min(width - 3, int(round(cx + dirty_x * dirty_distance)))),
            max(2, min(depth - 3, int(round(cz + dirty_z * dirty_distance)))),
        )
        discard_target = {"small": 12, "medium": 22, "large": 36}[scale]
        if culture_profile == "intensive_cleaning":
            discard_target += 8
        spent_fragment_points: list[list[int]] = []
        for _ in range(discard_target):
            x = max(1, min(width - 2, discard_center[0] + discard_rng.randint(-4, 4)))
            z = max(1, min(depth - 2, discard_center[1] + discard_rng.randint(-4, 4)))
            blocks[(x, 1, z)] = palette["bone"] if discard_rng.random() < 0.35 else palette["debris"]
            spent_fragment_points.append([x, 1, z])

        circulation_paths: list[list[list[int]]] = []
        for pocket in handling_pockets:
            endpoint = (pocket["center"][0], pocket["center"][2])
            path_points: list[list[int]] = []
            line = self._line(staging_center, endpoint)
            for i, (x, z) in enumerate(line):
                blocks[(x, 0, z)] = palette["ground"]
                if i < len(line) - 1:
                    blocks.pop((x, 1, z), None)
                path_points.append([x, 0, z])
            circulation_paths.append(path_points)

        disposal_path: list[list[int]] = []
        nearest_pocket = min(
            handling_pockets,
            key=lambda p: abs(p["center"][0] - discard_center[0]) + abs(p["center"][2] - discard_center[1]),
        )
        for x, z in self._line((nearest_pocket["center"][0], nearest_pocket["center"][2]), discard_center):
            blocks[(x, 0, z)] = palette["ground"]
            disposal_path.append([x, 0, z])

        light_percussion = None
        allow_percussion = culture_profile != "immediate_consumption" and percussion_rng.random() < 0.45
        if allow_percussion:
            target = percussion_rng.choice(handling_pockets)["center"]
            tx = max(2, min(width - 3, target[0] + percussion_rng.choice((-2, 2))))
            tz = max(2, min(depth - 3, target[2] + percussion_rng.choice((-2, 2))))
            blocks[(tx, 1, tz)] = palette["tool"]
            light_percussion = [tx, 1, tz]

        hearth = None
        if condition in {"active", "repeated"} and hearth_rng.random() < 0.22:
            hx = max(2, min(width - 3, staging_center[0] + hearth_rng.randint(-3, 3)))
            hz = max(2, min(depth - 3, staging_center[1] + hearth_rng.randint(-3, 3)))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire" if condition == "active" else "minecraft:cobblestone"
            hearth = [hx, 1, hz]

        if condition == "repeated":
            for _ in range({"small": 8, "medium": 18, "large": 30}[scale]):
                pocket = condition_rng.choice(handling_pockets)
                x = max(1, min(width - 2, pocket["center"][0] + condition_rng.randint(-3, 3)))
                z = max(1, min(depth - 2, pocket["center"][2] + condition_rng.randint(-3, 3)))
                blocks[(x, 0, z)] = palette["stain"]
                if condition_rng.random() < 0.55:
                    blocks[(x, 1, z)] = condition_rng.choice((palette["bone"], palette["debris"]))
        elif condition == "abandoned":
            for point in staging_points[::2]:
                blocks.pop(tuple(point), None)
        elif condition == "weathered":
            for key in list(blocks):
                if key[1] == 1 and condition_rng.random() < 0.15:
                    blocks.pop(key, None)
            if biome_family in {"temperate", "boreal", "tropical"}:
                for stance in activity_stances:
                    if condition_rng.random() < 0.45:
                        blocks[(stance[0], 0, stance[2])] = "minecraft:moss_block"
        elif condition == "scavenger_reworked":
            for _ in range({"small": 5, "medium": 9, "large": 14}[scale]):
                x = condition_rng.choice((1, width - 2)) if condition_rng.random() < 0.5 else condition_rng.randint(1, width - 2)
                z = condition_rng.randint(1, depth - 2) if x in {1, width - 2} else condition_rng.choice((1, depth - 2))
                blocks[(x, 1, z)] = palette["bone"]
        elif condition == "sediment_reworked":
            cover = "minecraft:sand" if biome_family == "arid" else palette["ground"]
            for _ in range({"small": 9, "medium": 17, "large": 28}[scale]):
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
            "handling_pocket_count": len(handling_pockets),
            "activity_stance_count": len(activity_stances),
            "opened_bone_count": len(opened_bone_points),
            "stain_count": len(stain_points),
            "staging_count": len(staging_points),
            "spent_fragment_count": len(spent_fragment_points),
            "circulation_path_count": len(circulation_paths),
            "light_percussion_count": 0 if light_percussion is None else 1,
            "has_dominant_carcass_axis": False,
            "hearth_is_subordinate": hearth is None or len(opened_bone_points) >= 6,
        }
        qualification["passes"] = all((
            qualification["handling_pocket_count"] >= 1,
            qualification["activity_stance_count"] >= qualification["handling_pocket_count"],
            qualification["opened_bone_count"] >= 5,
            qualification["stain_count"] >= 4,
            qualification["staging_count"] >= 3,
            qualification["spent_fragment_count"] >= 6,
            qualification["circulation_path_count"] >= 1,
            qualification["light_percussion_count"] <= 1,
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
                "handling_pockets": handling_pockets,
                "activity_stances": activity_stances,
                "opened_bone_points": opened_bone_points,
                "stain_points": stain_points,
                "staging_points": staging_points,
                "spent_fragment_points": spent_fragment_points,
                "circulation_paths": circulation_paths,
                "disposal_path": disposal_path,
                "light_percussion": light_percussion,
                "hearth": hearth,
                "material_semantics": {
                    "bone_block": "opened_or_spent_heavy_bone_proxy",
                    "stone_family": "light_percussion_or_tool_proxy",
                    "gravel": "spent_fragment_debris_proxy",
                    "stain_blocks": "marrow_grease_or_organic_ground_disturbance_proxy",
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
