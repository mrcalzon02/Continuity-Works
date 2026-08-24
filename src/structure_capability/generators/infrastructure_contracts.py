from __future__ import annotations

import hashlib
import json
import math
import random
from typing import Any

INNER_CITY_ROAD_WIDTH = 6
INNER_CITY_TERRAIN_PADDING = 5
VALID_SPAWN_MODES = ("tileable_grid", "randomized_coordinate", "sequential_jigsaw")
VALID_MODULE_TYPES = ("inner_city_road", "highway", "civic_facility", "industrial_facility")
VALID_VARIANTS = ("urban", "rural")
PURPOSE_DEPTH_LABELS = {
    0: "geometry_only", 1: "access_and_clearance", 2: "functional_zoning",
    3: "ecosystem_integration", 4: "narrative_and_operational_depth",
}


def stable_int(*parts: Any) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)


def fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def jigsaw_contract(req, layout):
    if not req.jigsaw_enabled:
        return {"enabled": False, "connectors": []}
    width = min(req.connector_width, layout["footprint_blocks"][0])
    if req.module_type in {"inner_city_road", "highway"}:
        facing = ("north", "south") if req.orientation == "north_south" else ("east", "west")
        connectors = [
            {"name": "start", "facing": facing[0], "joint": "aligned", "pool": req.jigsaw_pool, "width": width},
            {"name": "end", "facing": facing[1], "joint": "aligned", "pool": req.jigsaw_pool, "width": width},
        ]
    else:
        connectors = [
            {"name": "frontage", "facing": "south", "joint": "aligned", "pool": req.jigsaw_pool, "width": width, "target": "road"},
            {"name": "service", "facing": "east", "joint": "rollable", "pool": req.jigsaw_pool, "width": width, "target": "service_access"},
        ]
    return {"enabled": True, "pool": req.jigsaw_pool, "max_depth": req.jigsaw_max_depth, "assembly": "sequential_jigsaw", "connectors": connectors}


def lost_cities_contract(req, layout):
    if not req.lost_cities_enabled:
        return {"enabled": False, "spawn_modes": [], "adapter_status": "DISABLED"}
    footprint = layout["footprint_blocks"]
    footprint_chunks = [math.ceil(footprint[0] / 16), math.ceil(footprint[1] / 16)]
    return {
        "enabled": True,
        "spawn_modes": list(req.spawn_modes),
        "adapter_status": "CONTRACT_READY_RUNTIME_TEST_REQUIRED",
        "tileable_grid": {
            "enabled": "tileable_grid" in req.spawn_modes,
            "alignment": "chunk_grid",
            "requested_tile_span_chunks": req.tile_span_chunks,
            "required_footprint_chunks": footprint_chunks,
            "reservation_strategy": "single_span" if max(footprint_chunks) <= req.tile_span_chunks else "multi_tile_reservation",
            "footprint_blocks": footprint,
        },
        "randomized_coordinate": {
            "enabled": "randomized_coordinate" in req.spawn_modes,
            "radius_blocks": req.random_radius_blocks,
            "spacing_blocks": req.random_spacing_blocks,
            "salt": req.random_salt,
        },
        "sequential_jigsaw": {
            "enabled": "sequential_jigsaw" in req.spawn_modes,
            "pool": req.jigsaw_pool,
            "max_depth": req.jigsaw_max_depth,
        },
    }


def spawn_contract(req, layout):
    derived = stable_int(req.world_seed, req.random_salt, req.module_type, req.variant, req.seed)
    rng = random.Random(derived)
    radius = max(req.random_spacing_blocks, req.random_radius_blocks)
    spacing = req.random_spacing_blocks
    x = round(rng.randrange(-radius, radius + 1) / spacing) * spacing
    z = round(rng.randrange(-radius, radius + 1) / spacing) * spacing
    return {
        "world_seed_authorized": True,
        "derivation": "sha256(world_seed|salt|module_type|variant|seed)",
        "candidate_anchor": {"x": x, "z": z},
        "grid_snap_blocks": spacing,
        "footprint_blocks": layout["footprint_blocks"],
    }


def purpose_contract(req, layout):
    if req.module_type == "inner_city_road":
        primary = "urban circulation and parcel frontage"
        users = ["pedestrians_at_edges", "local_traffic", "service_access"]
        dependencies = ["adjacent_parcels", "intersections", "terrain_blend"]
    elif req.module_type == "highway":
        primary = "high-capacity through movement"
        users = ["regional_traffic", "service_and_emergency_access"]
        dependencies = ["ramps_or_jigsaw_links", "grade_clearance", "barriers"]
    elif req.module_type == "civic_facility":
        primary = "public services and local administration"
        users = ["public", "staff", "service_personnel"]
        dependencies = ["public_frontage", "accessible_entry", "utilities", "records_or_service_core"]
    else:
        primary = "production, maintenance, storage, and logistics"
        users = ["staff", "freight", "service_personnel"]
        dependencies = ["freight_access", "utilities", "loading", "safe_public_separation"]
    return {
        "depth": req.purpose_depth,
        "depth_label": PURPOSE_DEPTH_LABELS[req.purpose_depth],
        "primary_function": primary,
        "users": users,
        "dependencies": dependencies,
        "zones": [zone["id"] for zone in layout.get("zones", [])],
        "validation_rule": "depth>=2 and all declared dependencies represented by layout or integration contract",
    }


def fitness(req, layout, jigsaw, lost_cities, purpose):
    findings = []
    if req.module_type == "inner_city_road":
        if layout["roadbed_width"] != INNER_CITY_ROAD_WIDTH:
            findings.append({"code": "INNER_CITY_WIDTH", "severity": "error"})
        padding = layout["terrain_padding"]
        if padding["left"] != 5 or padding["right"] != 5:
            findings.append({"code": "INNER_CITY_PADDING", "severity": "error"})
    if req.module_type == "highway" and req.elevated and not layout["supports"]:
        findings.append({"code": "ELEVATED_WITHOUT_SUPPORTS", "severity": "error"})
    if jigsaw["enabled"] and not jigsaw["connectors"]:
        findings.append({"code": "JIGSAW_WITHOUT_CONNECTORS", "severity": "error"})
    if req.lost_cities_enabled and lost_cities["adapter_status"] == "DISABLED":
        findings.append({"code": "LOST_CITIES_CONTRACT_MISSING", "severity": "error"})
    if purpose["depth"] < 2:
        findings.append({"code": "PURPOSE_DEPTH_TOO_SHALLOW", "severity": "error", "required": 2, "actual": purpose["depth"]})
    if req.module_type in {"civic_facility", "industrial_facility"} and len(layout.get("zones", [])) < 5:
        findings.append({"code": "FACILITY_ZONING_INCOMPLETE", "severity": "error"})
    return {
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "checks": {
            "strict_inner_city_cross_section": req.module_type != "inner_city_road" or not findings,
            "jigsaw_assembly": not req.jigsaw_enabled or bool(jigsaw["connectors"]),
            "lost_cities_contract": not req.lost_cities_enabled or lost_cities["adapter_status"].startswith("CONTRACT_READY"),
            "purpose_depth": purpose["depth"] >= 2,
        },
    }
