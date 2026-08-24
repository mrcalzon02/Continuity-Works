from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from .infrastructure_contracts import (
    INNER_CITY_ROAD_WIDTH,
    INNER_CITY_TERRAIN_PADDING,
    PURPOSE_DEPTH_LABELS,
    VALID_MODULE_TYPES,
    VALID_SPAWN_MODES,
    VALID_VARIANTS,
    fingerprint,
    fitness,
    jigsaw_contract,
    lost_cities_contract,
    purpose_contract,
    spawn_contract,
    stable_int,
)
from .infrastructure_facilities import facility_layout


def _as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return bool(value)


@dataclass(frozen=True)
class InfrastructureLayoutRequest:
    module_type: str = "inner_city_road"
    variant: str = "urban"
    seed: int = 0
    world_seed: int = 0
    orientation: str = "north_south"
    segment_length: int = 64
    road_width: int = 6
    terrain_padding: int = 5
    lane_count: int = 4
    lane_width: int = 3
    shoulder_width: int = 1
    median_width: int = 2
    highway_profile: str = "elevated_urban_water_crossing"
    elevated: bool = False
    support_spacing: int = 12
    deck_thickness: int = 2
    min_clearance: int = 6
    jigsaw_enabled: bool = True
    jigsaw_pool: str = "structuresmith:infrastructure"
    connector_width: int = 3
    lost_cities_enabled: bool = False
    spawn_modes: tuple[str, ...] = VALID_SPAWN_MODES
    tile_span_chunks: int = 1
    random_radius_blocks: int = 4096
    random_spacing_blocks: int = 256
    random_salt: int = 734287
    jigsaw_max_depth: int = 8
    purpose_depth: int = 3
    facility_kind: str | None = None

    @classmethod
    def from_dict(cls, request: dict[str, Any] | None):
        d = dict(request or {})
        lost, jigsaw = dict(d.get("lost_cities") or {}), dict(d.get("jigsaw") or {})
        random_spawn, road = dict(d.get("random_spawn") or {}), dict(d.get("road") or {})
        highway, purpose = dict(d.get("highway") or {}), dict(d.get("purpose") or {})
        module_type = str(d.get("module_type", "inner_city_road"))
        profile = str(highway.get("profile", d.get("highway_profile", "elevated_urban_water_crossing")))
        return cls(
            module_type=module_type,
            variant=str(d.get("variant", "urban")),
            seed=int(d.get("seed", 0)),
            world_seed=int(d.get("world_seed", d.get("seed", 0))),
            orientation=str(d.get("orientation", "north_south")),
            segment_length=int(d.get("segment_length", 64)),
            road_width=int(road.get("width", d.get("road_width", 6))),
            terrain_padding=int(road.get("terrain_padding", d.get("terrain_padding", 5))),
            lane_count=int(highway.get("lane_count", d.get("lane_count", 4))),
            lane_width=int(highway.get("lane_width", d.get("lane_width", 3))),
            shoulder_width=int(highway.get("shoulder_width", d.get("shoulder_width", 1))),
            median_width=int(highway.get("median_width", d.get("median_width", 2))),
            highway_profile=profile,
            elevated=_as_bool(highway.get("elevated", d.get("elevated")), module_type == "highway" and profile.startswith("elevated_")),
            support_spacing=int(highway.get("support_spacing", d.get("support_spacing", 12))),
            deck_thickness=int(highway.get("deck_thickness", d.get("deck_thickness", 2))),
            min_clearance=int(highway.get("min_clearance", d.get("min_clearance", 6))),
            jigsaw_enabled=_as_bool(jigsaw.get("enabled", d.get("jigsaw_enabled")), True),
            jigsaw_pool=str(jigsaw.get("pool", d.get("jigsaw_pool", "structuresmith:infrastructure"))),
            connector_width=int(jigsaw.get("connector_width", d.get("connector_width", 3))),
            lost_cities_enabled=_as_bool(lost.get("enabled", d.get("lost_cities_enabled")), False),
            spawn_modes=tuple(lost.get("spawn_modes", d.get("spawn_modes", VALID_SPAWN_MODES))),
            tile_span_chunks=int(lost.get("tile_span_chunks", d.get("tile_span_chunks", 1))),
            random_radius_blocks=int(random_spawn.get("radius_blocks", d.get("random_radius_blocks", 4096))),
            random_spacing_blocks=int(random_spawn.get("spacing_blocks", d.get("random_spacing_blocks", 256))),
            random_salt=int(random_spawn.get("salt", d.get("random_salt", 734287))),
            jigsaw_max_depth=int(jigsaw.get("max_depth", d.get("jigsaw_max_depth", 8))),
            purpose_depth=int(purpose.get("depth", d.get("purpose_depth", 3))),
            facility_kind=d.get("facility_kind"),
        )


class InfrastructureGenerator:
    provider_id = "native_infrastructure_v1"

    def generate(self, request):
        req = request if isinstance(request, InfrastructureLayoutRequest) else InfrastructureLayoutRequest.from_dict(request)
        self._validate(req)
        rng = random.Random(stable_int(req.world_seed, req.seed, req.module_type, req.variant, req.orientation))
        if req.module_type == "inner_city_road":
            layout = self._inner_city(req)
        elif req.module_type == "highway":
            layout = self._highway(req)
        else:
            layout = facility_layout(req, rng)

        jigsaw = jigsaw_contract(req, layout)
        lost = lost_cities_contract(req, layout)
        purpose = purpose_contract(req, layout)
        fit = fitness(req, layout, jigsaw, lost, purpose)
        result = {
            "engine": self.provider_id,
            "module_type": req.module_type,
            "variant": req.variant,
            "seed": req.seed,
            "world_seed": req.world_seed,
            "orientation": req.orientation,
            "layout": layout,
            "purpose": purpose,
            "jigsaw": jigsaw,
            "lost_cities": lost,
            "spawn": spawn_contract(req, layout),
            "fitness": fit,
            "runtime_validation": {
                "static_contract": "PASS" if fit["status"] == "PASS" else "FAIL",
                "lost_cities_runtime": "REQUIRED" if req.lost_cities_enabled else "NOT_REQUESTED",
                "fresh_world_placement": "REQUIRED",
                "note": "Static generation validates deterministic contracts; actual Lost Cities/worldgen placement requires a modded runtime test.",
            },
        }
        result["determinism"] = {
            "stable_seed": stable_int(req.world_seed, req.seed, req.module_type, req.variant, req.orientation),
            "fingerprint": fingerprint(result),
        }
        return result

    @staticmethod
    def _validate(req):
        if req.module_type not in VALID_MODULE_TYPES:
            raise ValueError(f"module_type must be one of {VALID_MODULE_TYPES}")
        if req.variant not in VALID_VARIANTS:
            raise ValueError(f"variant must be one of {VALID_VARIANTS}")
        if req.orientation not in {"north_south", "east_west"}:
            raise ValueError("orientation must be north_south or east_west")
        if not 16 <= req.segment_length <= 512:
            raise ValueError("segment_length must be between 16 and 512 blocks")
        if req.module_type == "inner_city_road" and req.road_width != INNER_CITY_ROAD_WIDTH:
            raise ValueError("inner-city road width is strict: 6 blocks")
        if req.module_type == "inner_city_road" and req.terrain_padding != INNER_CITY_TERRAIN_PADDING:
            raise ValueError("inner-city terrain padding is strict: 5 blocks on each side")
        if not 1 <= req.lane_count <= 12 or not 2 <= req.lane_width <= 5:
            raise ValueError("highway lane_count/lane_width outside supported range")
        if req.connector_width < 1 or not 1 <= req.tile_span_chunks <= 16:
            raise ValueError("connector_width/tile_span_chunks outside supported range")
        unknown = set(req.spawn_modes) - set(VALID_SPAWN_MODES)
        if unknown:
            raise ValueError(f"unsupported Lost Cities spawn modes: {sorted(unknown)}")
        if req.lost_cities_enabled and not req.spawn_modes:
            raise ValueError("Lost Cities integration requires at least one spawn mode")
        if req.random_spacing_blocks < 16:
            raise ValueError("random_spacing_blocks must be at least one chunk")
        if req.purpose_depth not in PURPOSE_DEPTH_LABELS:
            raise ValueError("purpose depth must be an integer from 0 through 4")

    @staticmethod
    def _inner_city(req):
        return {
            "profile": "inner_city_strict_v1",
            "footprint_blocks": [req.road_width + 2 * req.terrain_padding, req.segment_length],
            "roadbed_width": req.road_width,
            "terrain_padding": {"left": req.terrain_padding, "right": req.terrain_padding},
            "cross_section": [
                {"role": "terrain_padding_left", "width": req.terrain_padding},
                {"role": "roadbed", "width": req.road_width},
                {"role": "terrain_padding_right", "width": req.terrain_padding},
            ],
            "surfaces": {"roadbed": "palette:road", "padding": "terrain:blend"},
            "voxel_plan": [
                {"primitive": "rect", "role": "roadbed", "width": req.road_width, "length": req.segment_length, "y": 0},
                {"primitive": "strip", "role": "terrain_padding_left", "width": req.terrain_padding, "length": req.segment_length, "y": 0},
                {"primitive": "strip", "role": "terrain_padding_right", "width": req.terrain_padding, "length": req.segment_length, "y": 0},
            ],
        }

    @staticmethod
    def _highway(req):
        roadbed = req.lane_count * req.lane_width
        deck_width = roadbed + 2 * req.shoulder_width + req.median_width
        profile = {
            "name": req.highway_profile,
            "lane_count": req.lane_count,
            "lane_width": req.lane_width,
            "shoulder_width": req.shoulder_width,
            "median_width": req.median_width,
            "barriers": "continuous_edge",
            "grading": "elevated_transition" if req.elevated else "terrain_following",
        }
        if req.highway_profile == "elevated_urban_water_crossing":
            profile.update({
                "reference_character": "wide elevated urban crossing with repeating supports, edge barriers, and clean water/terrain clearance",
                "water_span_ready": True,
                "support_style": "repeating_piers",
            })
        supports = [
            {"distance": d, "role": "pier_pair", "clearance": req.min_clearance}
            for d in range(req.support_spacing, req.segment_length, req.support_spacing)
        ] if req.elevated else []
        return {
            "profile": profile,
            "footprint_blocks": [deck_width, req.segment_length],
            "roadbed_width": roadbed,
            "deck_width": deck_width,
            "deck_thickness": req.deck_thickness,
            "min_clearance": req.min_clearance if req.elevated else 0,
            "supports": supports,
            "voxel_plan": [
                {"primitive": "rect", "role": "highway_deck", "width": deck_width, "length": req.segment_length, "thickness": req.deck_thickness},
                {"primitive": "line", "role": "edge_barrier_left", "length": req.segment_length},
                {"primitive": "line", "role": "edge_barrier_right", "length": req.segment_length},
                *[{"primitive": "pier_pair", **support} for support in supports],
            ],
        }


def generate_infrastructure_layout(request):
    return InfrastructureGenerator().generate(request)
