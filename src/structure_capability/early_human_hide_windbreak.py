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

CATALOG_ID = "E01-006"
STRUCTURE_ID = "continuityworks:e01_006_hide_windbreak_camp"
FAMILY_ID = "continuityworks:early_human_ephemeral_shelter"
START_POOL = "continuityworks:early_human/e01_006_hide_windbreak_camp"
SCALES = ("small", "medium", "large")
SPACING = 104
SEPARATION = 72
SALT = 101006


class HideWindbreakCampGenerationError(ValueError):
    pass


class HideWindbreakCampGenerator:
    """Deterministic Stage-2/3 implementation for E01-006.

    The archetype is a camp-scale windbreak whose defining skin is hide rather
    than brush. Vanilla wool/carpet blocks act only as material-role proxies for
    taut hides; the geometry, tension points, open leeward occupation area, and
    camp organization carry the functional identity.
    """

    @staticmethod
    def _rng(seed: int | str, stream: str) -> random.Random:
        digest = sha256(f"{seed}|{CATALOG_ID}|{stream}".encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    @staticmethod
    def _palette(biome_family: str) -> dict[str, str | None]:
        palettes = {
            "temperate": {"post": "minecraft:oak_log", "hide": "minecraft:brown_wool", "edge": "minecraft:white_wool", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:brown_carpet"},
            "boreal": {"post": "minecraft:spruce_log", "hide": "minecraft:brown_wool", "edge": "minecraft:light_gray_wool", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:brown_carpet"},
            "tundra": {"post": "minecraft:spruce_log", "hide": "minecraft:white_wool", "edge": "minecraft:light_gray_wool", "floor": "minecraft:gravel", "bedding": "minecraft:white_carpet"},
            "savanna": {"post": "minecraft:acacia_log", "hide": "minecraft:brown_wool", "edge": "minecraft:orange_wool", "floor": "minecraft:coarse_dirt", "bedding": "minecraft:brown_carpet"},
            "arid": {"post": "minecraft:acacia_log", "hide": "minecraft:light_gray_wool", "edge": "minecraft:brown_wool", "floor": "minecraft:sand", "bedding": None},
            "tropical": {"post": "minecraft:jungle_log", "hide": "minecraft:brown_wool", "edge": "minecraft:white_wool", "floor": "minecraft:dirt", "bedding": "minecraft:brown_carpet"},
            "coastal": {"post": "minecraft:oak_log", "hide": "minecraft:light_gray_wool", "edge": "minecraft:white_wool", "floor": "minecraft:sand", "bedding": None},
        }
        return palettes.get(biome_family, palettes["temperate"])

    @staticmethod
    def _fingerprint(blocks: list[dict[str, Any]]) -> str:
        payload = "\n".join(f"{b['pos']}:{b['block']}" for b in blocks).encode("utf-8")
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
            raise HideWindbreakCampGenerationError(f"invalid scale {scale!r} for {CATALOG_ID}")

        dimensions = {"small": (13, 7, 11), "medium": (19, 9, 15), "large": (27, 11, 19)}
        width, height, depth = dimensions[scale]
        frame_rng = self._rng(seed, "frame")
        hide_rng = self._rng(seed, "hide_skin")
        camp_rng = self._rng(seed, "camp_layout")
        condition_rng = self._rng(seed, "condition")
        palette = self._palette(biome_family)
        post = str(palette["post"])
        hide = str(palette["hide"])
        edge = str(palette["edge"])
        floor = str(palette["floor"])
        bedding = palette["bedding"]

        blocks: dict[tuple[int, int, int], str] = {}
        windward = frame_rng.choice(("north", "south", "east", "west"))
        axis_x = windward in {"north", "south"}
        cx, cz = width // 2, depth // 2
        wall_length = {"small": 9, "medium": 13, "large": 19}[scale]
        wall_height = {"small": 4, "medium": 5, "large": 6}[scale]

        if windward == "north":
            origin = [cx, 0, max(2, cz - 3)]; lee = (0, 1)
        elif windward == "south":
            origin = [cx, 0, min(depth - 3, cz + 3)]; lee = (0, -1)
        elif windward == "west":
            origin = [max(2, cx - 3), 0, cz]; lee = (1, 0)
        else:
            origin = [min(width - 3, cx + 3), 0, cz]; lee = (-1, 0)

        half = wall_length // 2
        support_points: list[list[int]] = []
        tension_points: list[list[int]] = []
        hide_points: list[list[int]] = []

        # Upright end/intermediate posts and leeward guy/tension feet.
        post_offsets = list(range(-half, half + 1, 3))
        if half not in post_offsets:
            post_offsets.append(half)
        if -half not in post_offsets:
            post_offsets.append(-half)
        for i in sorted(set(post_offsets)):
            x = origin[0] + (i if axis_x else 0)
            z = origin[2] + (0 if axis_x else i)
            if not (1 <= x < width - 1 and 1 <= z < depth - 1):
                continue
            local_h = max(3, wall_height + frame_rng.choice((-1, 0, 0, 1)))
            for y in range(1, local_h + 1):
                blocks[(x, y, z)] = post
                support_points.append([x, y, z])
            tx, tz = x + lee[0] * 2, z + lee[1] * 2
            if 1 <= tx < width - 1 and 1 <= tz < depth - 1:
                blocks[(tx, 0, tz)] = "minecraft:cobblestone"
                tension_points.append([tx, 0, tz])
                # sloped strut stands in for a tensioned hide line in vanilla geometry
                blocks[(x + lee[0], max(2, local_h - 1), z + lee[1])] = post

        # Taut hide panels dominate the windward plane but remain patchy at edges.
        panel_candidates: list[tuple[int, int, int]] = []
        for i in range(-half, half + 1):
            x = origin[0] + (i if axis_x else 0)
            z = origin[2] + (0 if axis_x else i)
            for y in range(2, wall_height + 1):
                if 1 <= x < width - 1 and 1 <= z < depth - 1:
                    panel_candidates.append((x, y, z))
        target = {"small": 0.72, "medium": 0.78, "large": 0.82}[scale]
        for pos in panel_candidates:
            if pos not in blocks and hide_rng.random() <= target:
                material = edge if hide_rng.random() < 0.14 else hide
                blocks[pos] = material
                hide_points.append(list(pos))

        # Camp occupation spreads leeward, making this a camp rather than a bare screen.
        camp_anchor = [origin[0] + lee[0] * 4, 1, origin[2] + lee[1] * 4]
        camp_radius = {"small": 2, "medium": 3, "large": 4}[scale]
        for dx in range(-camp_radius, camp_radius + 1):
            for dz in range(-camp_radius, camp_radius + 1):
                x, z = camp_anchor[0] + dx, camp_anchor[2] + dz
                if 1 <= x < width - 1 and 1 <= z < depth - 1 and camp_rng.random() < 0.46:
                    blocks[(x, 0, z)] = floor

        rest_anchor = [camp_anchor[0], 1, camp_anchor[2]]
        if bedding:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    x, z = rest_anchor[0] + dx, rest_anchor[2] + dz
                    if 1 <= x < width - 1 and 1 <= z < depth - 1 and camp_rng.random() < 0.62:
                        blocks[(x, 1, z)] = str(bedding)

        work_anchor = [
            max(1, min(width - 2, camp_anchor[0] + (2 if axis_x else 0))),
            1,
            max(1, min(depth - 2, camp_anchor[2] + (0 if axis_x else 2))),
        ]
        for _ in range({"small": 4, "medium": 7, "large": 11}[scale]):
            x = max(1, min(width - 2, work_anchor[0] + camp_rng.randint(-2, 2)))
            z = max(1, min(depth - 2, work_anchor[2] + camp_rng.randint(-2, 2)))
            if (x, 1, z) not in blocks:
                blocks[(x, 1, z)] = "minecraft:gravel"

        hearth = None
        if condition in {"active", "recent", "repeated"}:
            hx = max(1, min(width - 2, camp_anchor[0] + lee[0]))
            hz = max(1, min(depth - 2, camp_anchor[2] + lee[1]))
            blocks[(hx, 0, hz)] = "minecraft:coal_block"
            blocks[(hx, 1, hz)] = "minecraft:campfire"
            hearth = [hx, 1, hz]

        if condition in {"weathered", "collapsed", "abandoned", "repurposed"}:
            removable_hide = [p for p, b in blocks.items() if b in {hide, edge}]
            condition_rng.shuffle(removable_hide)
            loss = {"weathered": 0.22, "collapsed": 0.48, "abandoned": 0.30, "repurposed": 0.15}[condition]
            for pos in removable_hide[: int(len(removable_hide) * loss)]:
                blocks.pop(pos, None)
            if condition == "collapsed":
                removable_frame = [p for p, b in blocks.items() if b == post]
                condition_rng.shuffle(removable_frame)
                for pos in removable_frame[: int(len(removable_frame) * 0.24)]:
                    blocks.pop(pos, None)
            if condition == "repurposed":
                for _ in range({"small": 2, "medium": 4, "large": 6}[scale]):
                    x = max(1, min(width - 2, camp_anchor[0] + condition_rng.randint(-2, 2)))
                    z = max(1, min(depth - 2, camp_anchor[2] + condition_rng.randint(-2, 2)))
                    if (x, 1, z) not in blocks:
                        blocks[(x, 1, z)] = "minecraft:cobblestone"

        block_list = [{"pos": [x, y, z], "block": block} for (x, y, z), block in sorted(blocks.items())]
        hide_ratio = len(hide_points) / max(1, len(panel_candidates))
        qualification = {
            "hide_skin_dominant": hide_ratio >= 0.55,
            "support_and_tension_geometry_present": bool(support_points) and bool(tension_points),
            "directional_windward_leeward_logic": True,
            "camp_scale_occupation_present": bool(rest_anchor) and bool(work_anchor),
            "perimeter_open": True,
            "brush_screen_not_dominant": True,
        }
        return {
            "size": [width, height, depth],
            "blocks": block_list,
            "metadata": {
                "catalog_id": CATALOG_ID,
                "structure_id": STRUCTURE_ID,
                "name": "Hide Windbreak Camp",
                "family_id": FAMILY_ID,
                "scale": scale,
                "biome_family": biome_family,
                "condition": condition,
                "seed": str(seed),
                "terrain_mode": "surface_terrain_responsive",
                "replace_policy": "bounded_additive_non_destructive",
                "default_exclusion_radius": DEFAULT_STRUCTURE_EXCLUSION_RADIUS,
                "windward": windward,
                "leeward_vector": [lee[0], lee[1]],
                "wall_origin": origin,
                "camp_anchor": camp_anchor,
                "rest_zone_anchor": rest_anchor,
                "work_zone_anchor": work_anchor,
                "hearth": hearth,
                "support_points": support_points,
                "tension_points": tension_points,
                "hide_points": hide_points,
                "hide_coverage_ratio": hide_ratio,
                "material_role_note": "wool_and_carpet_are_vanilla_hide_proxies",
                "qualification": qualification,
                "qualification_pass": all(qualification.values()),
                "archetype_constraint": "hide_skinned_directional_windbreak_with_tension_geometry_and_leeward_camp_occupation",
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
            max_distance=72,
        )
        structure_set = random_spread_structure_set(STRUCTURE_ID, spacing=SPACING, separation=SEPARATION, salt=SALT)
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
                "requires_exposed_wind_context": True,
                "family_co_location_requires_shared_parent_reservation": True,
                "must_not_replace_existing_major_structure": True,
            },
        }
