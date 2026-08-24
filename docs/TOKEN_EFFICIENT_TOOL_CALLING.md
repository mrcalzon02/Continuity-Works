# Token-Efficient Tool Calling

StructureSmith is intended to replace repeated prompt-space reconstruction of Minecraft structure logic with small, deterministic calls into reusable code.

## Design rule

Clients should use **progressive disclosure**:

1. Fetch the compact capability index.
2. Select one tool.
3. Fetch only that tool's contract.
4. Optionally select one reusable preset.
5. Supply only the variables that differ for the current operation.
6. Resolve the request before invoking the expensive generator/content tool.

Do not load the complete tool catalog, every structure doctrine, every Minecraft-version rule, and every preset into model context for each operation.

## Compact discovery

HTTP:

```text
GET /v1/tools/index
GET /v1/tools/index?group=layout
GET /v1/tools/dungeon_layout
GET /v1/presets
GET /v1/presets/layout.modular_dungeon
POST /v1/resolve
```

The legacy/full catalog remains available at `GET /v1/tools` for compatibility. It should be used when a client genuinely needs the complete schema set, not as the normal per-operation prompt payload.

The same behavior is available through query parameters:

```text
GET /v1/tools?mode=compact
GET /v1/tools?mode=compact&group=minecraft_content
GET /v1/tools?name=minecraft_book_generate
```

## Local CLI

```text
structure-capability tools --compact
structure-capability tools --compact --group layout
structure-capability tools --name structure_generate
structure-capability presets
structure-capability presets layout.urban_road_tile
structure-capability resolve request.json
```

A resolver request is intentionally small:

```json
{
  "tool": "structure_generate",
  "preset_id": "structure.modular_dungeon_nbt",
  "overrides": {
    "structure_id": "example:research_lab",
    "target_version": "1.20.1",
    "purpose": {
      "kind": "laboratory",
      "required_zones": ["entry", "laboratory", "utilities", "secure_core"]
    },
    "generation": {
      "layout": {
        "seed": 42
      }
    }
  }
}
```

The resolver merges the preset and overrides, applies declared schema defaults, reports missing variables, rejects unknown top-level variables where the selected schema is closed, and returns a request ready for the selected tool.

## Built-in reusable presets

The generic core includes reusable starting points for:

- modular dungeon/complex NBT generation;
- layout-only macro/meso/micro dungeons;
- tileable urban road segments;
- modular highway segments;
- version-compatible written books;
- version-compatible chest loot tables.

Project-specific presets belong in `config/tool_presets.json`. This keeps cultural identities, project loot, narrative books, corporate/faction palettes, or map-specific dimensions out of the generic core while allowing a consuming project to reduce repeated variables even further.

## Variable discipline

A preset is not permission to hide meaningful design choices. Defaults should cover stable mechanical facts and reusable geometry. The request should still expose variables that materially distinguish the current structure, such as:

- target Minecraft version;
- structure ID and purpose;
- scale/footprint constraints;
- cultural or architectural theme;
- required functional zones;
- seed when determinism matters;
- damage/condition requirements;
- loot/book content unique to this structure;
- integration contracts for consuming mods/worldgen systems.

That boundary is the intended efficiency gain: **stable logic lives in StructureSmith; unique design intent stays in the call.**

## Tileability

Tileable providers should express stable connector dimensions, module spans, and assembly rules in presets/providers instead of forcing callers to restate them. Callers should normally specify only the variables that vary between instances: orientation, length/extent, seed, purpose depth, target version, and any intentional overrides.

## Compatibility policy

Progressive disclosure does not bypass validation. The resolved request still flows through the same version, registry, fitness, materialization, and runtime/visual boundaries as a full request.
