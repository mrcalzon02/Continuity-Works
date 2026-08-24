from __future__ import annotations


def facility_layout(req, rng):
    civic = req.module_type == "civic_facility"
    facility_kind = req.facility_kind or ("civic_services_center" if civic else "industrial_service_works")
    if civic:
        base = (40, 36) if req.variant == "urban" else (48, 40)
        zones = ["public_entry", "service_counter", "offices", "records", "staff", "utilities"]
        if req.variant == "rural":
            zones += ["community_room", "emergency_store"]
    else:
        base = (56, 44) if req.variant == "urban" else (72, 56)
        zones = ["gate", "workshop", "storage", "utilities", "loading", "staff"]
        if req.variant == "rural":
            zones += ["yard", "bulk_storage"]

    width = base[0] + rng.choice((0, 4, 8))
    depth = base[1] + rng.choice((0, 4, 8))
    zone_modules = []
    cursor = 0
    for index, zone in enumerate(zones):
        span = max(4, width // max(3, len(zones) // 2))
        zone_modules.append({
            "id": zone,
            "module": [span, max(6, depth // 3)],
            "sequence": index,
            "access": "public" if zone in {"public_entry", "service_counter", "community_room"} else "controlled",
            "offset_hint": cursor,
        })
        cursor = (cursor + span) % width

    return {
        "profile": facility_kind,
        "facility_class": "civic" if civic else "industrial",
        "context_variant": req.variant,
        "footprint_blocks": [width, depth],
        "frontage": "street_edge" if req.variant == "urban" else "setback_access_road",
        "zones": zone_modules,
        "required_access": ["pedestrian", "service"] if civic else ["staff", "freight", "service"],
        "road_interface": {
            "preferred": "inner_city_road" if req.variant == "urban" else "local_access_road",
            "connector_width": req.connector_width,
        },
        "voxel_plan": [
            {"primitive": "shell", "role": "facility_envelope", "width": width, "depth": depth, "height": 8 if civic else 10},
            *[{"primitive": "zone", **zone} for zone in zone_modules],
        ],
    }
