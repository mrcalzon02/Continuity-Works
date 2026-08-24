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
            "road": {"type": "object", "properties": {"width": {"const": 6, "description": "Strict inner-city roadbed width."}, "terrain_padding": {"const": 5, "description": "Strict terrain padding on each side of inner-city roads."}}, "additionalProperties": False},
            "highway": {"type": "object", "properties": {"profile": {"enum": ["elevated_urban_water_crossing", "surface_highway"]}, "lane_count": {"type": "integer", "minimum": 1, "maximum": 12}, "lane_width": {"type": "integer", "minimum": 2, "maximum": 5}, "shoulder_width": {"type": "integer", "minimum": 0, "maximum": 6}, "median_width": {"type": "integer", "minimum": 0, "maximum": 8}, "elevated": {"type": "boolean"}, "support_spacing": {"type": "integer", "minimum": 4, "maximum": 64}, "deck_thickness": {"type": "integer", "minimum": 1, "maximum": 8}, "min_clearance": {"type": "integer", "minimum": 0, "maximum": 64}}, "additionalProperties": False},
            "jigsaw": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "pool": {"type": "string"}, "connector_width": {"type": "integer", "minimum": 1, "maximum": 16}, "max_depth": {"type": "integer", "minimum": 1, "maximum": 64}}, "additionalProperties": False},
            "lost_cities": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "spawn_modes": {"type": "array", "items": {"enum": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"]}, "uniqueItems": True}, "tile_span_chunks": {"type": "integer", "minimum": 1, "maximum": 16}}, "additionalProperties": False},
            "random_spawn": {"type": "object", "properties": {"radius_blocks": {"type": "integer", "minimum": 16}, "spacing_blocks": {"type": "integer", "minimum": 16}, "salt": {"type": "integer"}}, "additionalProperties": False},
            "purpose": {"type": "object", "properties": {"depth": {"type": "integer", "minimum": 0, "maximum": 4}}, "additionalProperties": False},
        },
        "additionalProperties": False,
    }


def _context_properties() -> dict:
    return {"target_version": {"type": "string", "default": "1.20.1"}, "id_policy": {"enum": ["strict", "namespace", "permissive"], "default": "namespace", "description": "How aggressively unverified mod IDs are gated."}, "namespace": {"type": "string"}}


def _tool(name, description, parameters, semantic, item):
    return {"name": name, "description": description, "parameters": parameters, "x-structuresmith": {"icon": {"semantic": semantic, "item": item}, "reasoning": "public_validation_gates"}}


def tool_catalog() -> dict:
    """Portable JSON-Schema function catalog for AI/tool-calling clients."""
    structure_request = _structure_request_schema()
    dungeon_request = _dungeon_layout_schema()
    infrastructure_request = _infrastructure_layout_schema()
    ctx = _context_properties()

    book_schema = {"type": "object", "required": ["title", "author", "pages"], "properties": {**ctx, "title": {"type": "string"}, "author": {"type": "string"}, "pages": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "description": "Legacy targets before 1.20.5 are gated to 100 pages; 1.20.5+ uses the removed page-count ceiling."}, "generation": {"type": "integer", "minimum": 0, "maximum": 3}, "resolved": {"type": "boolean"}, "item_id": {"type": "string", "default": "minecraft:written_book"}}, "additionalProperties": False}
    loot_entry = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "weight": {"type": "integer", "minimum": 1}, "quality": {"type": "integer"}, "count": {"type": "integer", "minimum": 0}, "min_count": {"type": "integer", "minimum": 0}, "max_count": {"type": "integer", "minimum": 0}, "components": {"type": "object", "description": "1.20.5+ item components emitted through minecraft:set_components."}, "nbt": {"type": "string", "description": "Legacy pre-1.20.5 SNBT emitted through minecraft:set_nbt."}}, "additionalProperties": False}
    guaranteed_entry = {"type": "object", "required": ["id"], "properties": {key: value for key, value in loot_entry["properties"].items() if key not in {"weight", "quality"}}, "additionalProperties": False}
    loot_schema = {"type": "object", "required": ["table_id"], "properties": {**ctx, "table_id": {"type": "string"}, "type": {"type": "string", "default": "minecraft:chest"}, "rolls": {"oneOf": [{"type": "integer", "minimum": 0}, {"type": "object"}]}, "bonus_rolls": {"oneOf": [{"type": "number"}, {"type": "object"}]}, "items": {"type": "array", "items": loot_entry}, "guaranteed": {"type": "array", "description": "Each entry receives its own one-roll pool, making that entry guaranteed.", "items": guaranteed_entry}}, "additionalProperties": False}
    recipe_schema = {"type": "object", "required": ["recipe_id", "type", "result"], "properties": {**ctx, "recipe_id": {"type": "string"}, "type": {"enum": ["crafting_shaped", "crafting_shapeless", "smelting", "blasting", "smoking", "campfire_cooking", "stonecutting"]}, "group": {"type": "string"}, "category": {"type": "string"}, "pattern": {"type": "array", "items": {"type": "string"}}, "key": {"type": "object"}, "ingredients": {"type": "array"}, "ingredient": {}, "result": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "experience": {"type": "number"}, "cookingtime": {"type": "integer", "minimum": 1}, "cooking_time": {"type": "integer", "minimum": 1}}, "additionalProperties": False}
    advancement_schema = {"type": "object", "required": ["advancement_id", "criteria"], "properties": {**ctx, "advancement_id": {"type": "string"}, "parent": {"type": "string"}, "display": {"type": "object", "properties": {"title": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "description": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "icon": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "frame": {"enum": ["task", "goal", "challenge"]}, "show_toast": {"type": "boolean"}, "announce_to_chat": {"type": "boolean"}, "hidden": {"type": "boolean"}, "background": {"type": "string"}}, "additionalProperties": False}, "criteria": {"type": "object", "minProperties": 1, "additionalProperties": {"oneOf": [{"type": "string"}, {"type": "object"}]}}, "requirements": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "rewards": {"type": "object", "properties": {"experience": {"type": "integer", "minimum": 0}, "loot": {"type": "array", "items": {"type": "string"}}, "recipes": {"type": "array", "items": {"type": "string"}}, "function": {"type": "string"}}, "additionalProperties": False}, "sends_telemetry_event": {"type": "boolean"}}, "additionalProperties": False}
    tag_schema = {"type": "object", "required": ["tag_id", "registry", "values"], "properties": {**ctx, "tag_id": {"type": "string"}, "registry": {"enum": ["item", "block", "fluid", "entity_type", "function", "game_event"]}, "replace": {"type": "boolean"}, "values": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "required": {"type": "boolean"}}, "additionalProperties": False}]}}}, "additionalProperties": False}
    manifest_schema = {"type": "object", "properties": {"target_version": {"type": "string", "default": "1.20.1"}, "description": {"oneOf": [{"type": "string"}, {"type": "object"}]}, "pack_format": {"type": "integer", "minimum": 1, "description": "Optional override when exact release metadata is not bundled."}, "supported_formats": {"oneOf": [{"type": "integer"}, {"type": "array"}, {"type": "object"}]}}, "additionalProperties": False}
    probe_schema = {"type": "object", "required": ["id"], "properties": {**ctx, "id": {"type": "string"}, "kind": {"enum": ["item", "item_tag", "recipe", "loot_table", "structure", "registry"]}}, "additionalProperties": False}
    icon_schema = {"type": "object", "properties": {"subject": {"type": "string"}, "kind": {"type": "string"}, "target_version": {"type": "string"}, "item_id": {"type": "string"}, "label": {"type": "string", "maxLength": 3}, "mode": {"enum": ["auto", "minecraft_item", "badge"]}}, "additionalProperties": False}

    package_book = {"type": "object", "required": ["title", "author", "pages"], "properties": {"name": {"type": "string"}, **book_schema["properties"]}, "additionalProperties": False}
    package_loot = {"type": "object", "properties": {"name": {"type": "string"}, **loot_schema["properties"]}, "additionalProperties": False}
    package_recipe = {"type": "object", "required": ["type", "result"], "properties": {"name": {"type": "string"}, **recipe_schema["properties"]}, "additionalProperties": False}
    package_advancement = {"type": "object", "required": ["criteria"], "properties": {"name": {"type": "string"}, **advancement_schema["properties"]}, "additionalProperties": False}
    package_tag = {"type": "object", "required": ["registry", "values"], "properties": {"name": {"type": "string"}, **tag_schema["properties"]}, "additionalProperties": False}
    package_schema = {"type": "object", "required": ["package_id"], "properties": {**ctx, "package_id": {"type": "string"}, "link_policy": {"enum": ["strict", "warn"], "default": "strict"}, "structure": structure_request, "books": {"type": "array", "items": package_book}, "loot_tables": {"type": "array", "items": package_loot}, "recipes": {"type": "array", "items": package_recipe}, "advancements": {"type": "array", "items": package_advancement}, "tags": {"type": "array", "items": package_tag}, "bindings": {"type": "array", "items": {"type": "object", "required": ["type", "book", "loot_table"], "properties": {"type": {"const": "book_as_guaranteed_loot"}, "book": {"type": "string", "description": "Book name alias in this package."}, "loot_table": {"type": "string", "description": "Loot table name alias in this package."}}, "additionalProperties": False}}, "manifest": manifest_schema}, "additionalProperties": False}

    tools = [
        _tool("structure_capabilities", "Inspect supported structure-generation, audit, version, modularity, Minecraft content and review capabilities.", {"type": "object", "properties": {}, "additionalProperties": False}, "structure", "minecraft:bricks"),
        _tool("structure_inventory", "Inventory the connected Minecraft project for mods, namespaces and discoverable resource IDs before authoring.", {"type": "object", "properties": {}, "additionalProperties": False}, "registry", "minecraft:knowledge_book"),
        _tool("structure_audit", "Audit an existing Minecraft structure source for mechanical validity, context and fitness-for-purpose requirements.", structure_request, "audit", "minecraft:spyglass"),
        _tool("structure_plan", "Build a graded, preserve-aware structure revision or authoring plan with independent visual review gates.", structure_request, "plan", "minecraft:map"),
        _tool("structure_generate", "Run the authoritative generation path. Built-in modular dungeon generation can produce deterministic Minecraft NBT; infrastructure generation emits deterministic road/facility, jigsaw, Lost Cities and placement contracts.", structure_request, "structure", "minecraft:bricks"),
        _tool("dungeon_layout", "Generate a deterministic purpose-sized modular spatial layout with macro/meso/micro modularity and a fitness gate.", dungeon_request, "structure", "minecraft:stone_bricks"),
        _tool("infrastructure_layout", "Generate deterministic urban/highway/civic/industrial infrastructure contracts including strict 6-block inner-city roads with 5-block terrain padding per side, jigsaw connectors, Lost Cities placement modes, purpose depth, and world-seed-derived spawn anchors.", infrastructure_request, "infrastructure", "minecraft:rail"),
        _tool("minecraft_version", "Resolve compatibility metadata for a Minecraft Java target version without guessing unknown DataVersion values.", {"type": "object", "required": ["version"], "properties": {"version": {"type": "string"}}, "additionalProperties": False}, "version", "minecraft:clock"),
        _tool("minecraft_registry_probe", "Probe a vanilla or modded resource ID against the connected inventory and return explicit confidence/gate results.", probe_schema, "registry", "minecraft:knowledge_book"),
        _tool("minecraft_book_generate", "Assemble a version-aware written book item payload and a loot-compatible item representation; legacy book NBT is used before 1.20.5 and written_book_content components on 1.20.5+.", book_schema, "book", "minecraft:written_book"),
        _tool("minecraft_loot_table_generate", "Generate a version-aware loot-table JSON artifact with weighted and guaranteed pools, custom item component/NBT support, and mod-ID gates.", loot_schema, "loot_table", "minecraft:chest"),
        _tool("minecraft_recipe_generate", "Generate a version-aware crafting/cooking/stonecutting recipe artifact with mod-ID gates and post-1.20.5 result adaptation.", recipe_schema, "recipe", "minecraft:crafting_table"),
        _tool("minecraft_advancement_generate", "Generate a version-aware advancement with explicit criteria, display metadata, rewards, icon adaptation, and 1.21 directory migration.", advancement_schema, "advancement", "minecraft:experience_bottle"),
        _tool("minecraft_tag_generate", "Generate version-aware datapack tags for items, blocks, fluids, entity types, functions, or game events, including 1.21 singular tag directories.", tag_schema, "tag", "minecraft:name_tag"),
        _tool("minecraft_datapack_manifest_generate", "Generate a gated pack.mcmeta using exact bundled data-pack metadata or an explicit caller-supplied pack_format.", manifest_schema, "datapack", "minecraft:bundle"),
        _tool("minecraft_content_package_generate", "Compose one deliberate structure/content package containing an optional generated structure, books, guaranteed evidence loot, recipes, advancements, tags, pack.mcmeta, cross-artifact bindings, and an aggregate materialization gate.", package_schema, "package", "minecraft:chest_minecart"),
        _tool("minecraft_icon_assign", "Assign a semantic Minecraft item icon when available or return a deterministic lightweight SVG badge fallback.", icon_schema, "registry", "minecraft:painting"),
    ]
    return {"schema_version": "1.3", "api_version": "v1", "reasoning_contract": "deterministic_public_gates", "tools": tools}
