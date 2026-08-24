from __future__ import annotations


def _structure_request_schema() -> dict:
    return {
        "type": "object",
        "required": ["structure_id"],
        "properties": {
            "structure_id": {"type": "string", "description": "Stable namespaced structure identifier."},
            "operation": {"enum": ["audit", "plan", "generate"]},
            "structure_type": {"type": "string", "description": "Open structure class such as building, dungeon, ruin, settlement, infrastructure, underwater, ship, or underground_complex."},
            "target_version": {"type": "string", "description": "Minecraft Java target, for example 1.20.1."},
            "scale": {"type": "number", "minimum": 0.25, "maximum": 4.0},
            "grade": {"oneOf": [{"type": "integer", "minimum": 0, "maximum": 6}, {"type": "string"}]},
            "source": {"type": ["string", "null"]},
            "purpose": {"type": "object"},
            "theme": {"type": "object"},
            "context": {"type": "object"},
            "physical_clearance": {"type": "string"},
            "access_clearance": {"type": "string"},
            "preserve": {"type": "array", "items": {"type": "string"}},
            "mutable": {"type": "array", "items": {"type": "string"}},
            "integration_contracts": {"type": "object"},
            "generation": {
                "type": "object",
                "description": "Generator-specific configuration dispatched through the provider registry. Built-in kind values include dungeon, dungeon_layout, modular_dungeon, infrastructure, road, highway, civic_facility and industrial_facility.",
                "properties": {
                    "kind": {"type": "string"},
                    "materialize_nbt": {"type": "boolean"},
                    "materialization_mode": {"enum": ["auto", "single", "fragmented"]},
                    "piece_limit": {"type": "integer", "minimum": 8},
                    "allow_oversize_nbt": {"type": "boolean"},
                    "emit_binary": {"type": "boolean"},
                    "data_version": {"type": "integer", "minimum": 0},
                    "layout": {"type": "object"},
                    "palette": {"type": "object", "additionalProperties": {"type": "string"}},
                },
                "additionalProperties": True,
            },
            "metadata": {"type": "object"},
        },
        "additionalProperties": True,
    }


def _dungeon_layout_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "seed": {"type": "integer"},
            "purpose": {"type": "string"},
            "scale": {"type": "number", "minimum": 0.25, "maximum": 4.0},
            "required_zones": {"type": "array", "items": {"type": "string"}},
            "room_count": {"type": ["integer", "null"], "minimum": 3},
            "layout_shape": {"enum": ["rectangle", "cross", "round", "ring"]},
            "room_layout": {"enum": ["scattered", "packed"]},
            "corridor_style": {"enum": ["straight", "bent", "labyrinth"]},
            "dead_end_policy": {"enum": ["many", "some", "none"]},
            "verticality": {"type": "string"},
            "stair_count": {"type": "integer", "minimum": 0},
            "theme": {"type": "object"},
            "purpose_constraints": {"type": "object"},
            "size": {"type": "object"},
            "modularity": {"type": "object"},
            "classic_donjon_options": {"type": "object", "description": "Optional classic dungeon.pl-style options translated into the native engine."},
            "cell_scale_blocks": {"type": "integer", "minimum": 1},
            "metadata": {"type": "object"},
        },
        "additionalProperties": True,
    }


def _infrastructure_layout_schema() -> dict:
    """Complete public variable surface mirrored by the StructureForge Infrastructure panel."""
    return {
        "type": "object",
        "properties": {
            "module_type": {"enum": ["inner_city_road", "highway", "civic_facility", "industrial_facility"]},
            "variant": {"enum": ["urban", "rural"]},
            "seed": {"type": "integer", "description": "Deterministic module seed."},
            "world_seed": {"type": "integer", "description": "World seed used in deterministic placement derivation."},
            "orientation": {"enum": ["north_south", "east_west"]},
            "segment_length": {"type": "integer", "minimum": 16, "maximum": 512},
            "facility_kind": {"type": ["string", "null"]},
            "road": {
                "type": "object",
                "properties": {
                    "width": {"const": 6, "description": "Strict inner-city roadbed width."},
                    "terrain_padding": {"const": 5, "description": "Strict terrain padding on each side of inner-city roads."},
                },
                "additionalProperties": False,
            },
            "highway": {
                "type": "object",
                "properties": {
                    "profile": {"enum": ["elevated_urban_water_crossing", "surface_highway"]},
                    "lane_count": {"type": "integer", "minimum": 1, "maximum": 12},
                    "lane_width": {"type": "integer", "minimum": 2, "maximum": 5},
                    "shoulder_width": {"type": "integer", "minimum": 0, "maximum": 6},
                    "median_width": {"type": "integer", "minimum": 0, "maximum": 8},
                    "elevated": {"type": "boolean"},
                    "support_spacing": {"type": "integer", "minimum": 4, "maximum": 64},
                    "deck_thickness": {"type": "integer", "minimum": 1, "maximum": 8},
                    "min_clearance": {"type": "integer", "minimum": 0, "maximum": 64},
                },
                "additionalProperties": False,
            },
            "jigsaw": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "pool": {"type": "string"},
                    "connector_width": {"type": "integer", "minimum": 1, "maximum": 16},
                    "max_depth": {"type": "integer", "minimum": 1, "maximum": 64},
                },
                "additionalProperties": False,
            },
            "lost_cities": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "spawn_modes": {
                        "type": "array",
                        "items": {"enum": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"]},
                        "uniqueItems": True,
                    },
                    "tile_span_chunks": {"type": "integer", "minimum": 1, "maximum": 16},
                },
                "additionalProperties": False,
            },
            "random_spawn": {
                "type": "object",
                "properties": {
                    "radius_blocks": {"type": "integer", "minimum": 16},
                    "spacing_blocks": {"type": "integer", "minimum": 16},
                    "salt": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "purpose": {
                "type": "object",
                "properties": {
                    "depth": {"type": "integer", "minimum": 0, "maximum": 4},
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    }


def tool_catalog() -> dict:
    """Portable JSON-Schema function catalog for AI/tool-calling clients."""
    structure_request = _structure_request_schema()
    dungeon_request = _dungeon_layout_schema()
    infrastructure_request = _infrastructure_layout_schema()
    tools = [
        {
            "name": "structure_capabilities",
            "description": "Inspect supported structure-generation, audit, version, modularity and review capabilities.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "structure_inventory",
            "description": "Inventory the connected Minecraft project for mods, namespaces and known registry IDs before authoring.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "structure_audit",
            "description": "Audit an existing Minecraft structure source for mechanical validity, context and fitness-for-purpose requirements.",
            "parameters": structure_request,
        },
        {
            "name": "structure_plan",
            "description": "Build a graded, preserve-aware structure revision or authoring plan with independent visual review gates.",
            "parameters": structure_request,
        },
        {
            "name": "structure_generate",
            "description": "Run the authoritative generation path. Built-in modular dungeon generation can produce deterministic Minecraft NBT; infrastructure generation emits deterministic road/facility, jigsaw, Lost Cities and placement contracts.",
            "parameters": structure_request,
        },
        {
            "name": "dungeon_layout",
            "description": "Generate a deterministic purpose-sized modular spatial layout with macro/meso/micro modularity and a fitness gate.",
            "parameters": dungeon_request,
        },
        {
            "name": "infrastructure_layout",
            "description": "Generate deterministic urban/highway/civic/industrial infrastructure contracts including strict 6-block inner-city roads with 5-block terrain padding per side, jigsaw connectors, Lost Cities placement modes, purpose depth, and world-seed-derived spawn anchors.",
            "parameters": infrastructure_request,
        },
        {
            "name": "minecraft_version",
            "description": "Resolve compatibility metadata for a Minecraft Java target version without guessing unknown DataVersion values.",
            "parameters": {
                "type": "object", "required": ["version"],
                "properties": {"version": {"type": "string"}}, "additionalProperties": False,
            },
        },
    ]
    return {"schema_version": "1.1", "api_version": "v1", "tools": tools}
