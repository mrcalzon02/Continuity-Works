# Compatibility Policy: Additive and Non-Destructive

## Project invariant

All StructureSmith compatibility work is an **additive overlay**. Compatibility must extend an upstream system without replacing, deleting, disabling, clearing, or taking ownership of that system's native behavior.

This applies to every current and future compatibility layer: world generation, structures, roads, highways, railways, loot tables, recipes, palettes, selectors, registries, jigsaw pools, mod integration metadata, and any other compatibility surface.

The fixed policy is:

```text
mode = append_only
non_destructive = true
base_authority = preserved
```

Allowed compatibility operations include appending entries, extending tables, registering additional parts, adding optional selectors, adding namespaced resources, and attaching adapter metadata.

Forbidden operations include replacing existing entries, overriding native generators, deleting or clearing existing tables, disabling native behavior, or making StructureSmith an exclusive replacement for an upstream system.

The runtime validator rejects destructive compatibility requests such as `mode: replace`, `replace_existing: true`, `disable_native: true`, or `table_strategy: replace`.

## Lost Cities reference policy

The public Lost Cities repository is an approved behavioral reference:

- repository: `McJtyMods/LostCities`
- compatibility baseline currently inspected: branch `1.20`

StructureSmith may inspect that source to infer how supplemental assets should fit the native street, highway, railway, building-part, palette, and selector systems. The source is a compatibility reference; StructureSmith does not replace those systems.

### Streets

Lost Cities has a native hierarchical street model with `PRIMARY`, `SECONDARY`, and `TERTIARY` planned road types and cardinal connection metadata. StructureSmith road compatibility should therefore contribute additional compatible road parts or selector/table entries while preserving the native street planner and its existing entries.

Relevant upstream references:

- `src/main/java/mcjty/lostcities/worldgen/street/PlannedRoadType.java`
- `src/main/java/mcjty/lostcities/worldgen/street/PlannedStreetInfo.java`
- `src/main/java/mcjty/lostcities/worldgen/street/StreetPlannerSettings.java`

The StructureSmith strict urban road cross-section remains `5 padding | 6 roadbed | 5 padding`, which is exactly 16 blocks wide and can therefore be adapted cleanly to a chunk-width road part without replacing Lost Cities' planner.

### Highways

Lost Cities highways are native chunk-level worldgen. The generator selects open, bridge, or tunnel part families and supports straight, crossing, bend, and T-junction geometry. Highways also track X/Z direction, same-level intersections, and multi-level intersections.

StructureSmith highway compatibility should add compatible part candidates, palettes, or optional selector entries to those existing families. It must not disable or supplant the Lost Cities highway planner.

Relevant upstream references:

- `src/main/java/mcjty/lostcities/worldgen/lost/Highway.java`
- `src/main/java/mcjty/lostcities/worldgen/gen/Highways.java`
- `src/main/java/mcjty/lostcities/worldgen/highway/HighwayInfo.java`
- `src/main/java/mcjty/lostcities/worldgen/highway/HighwayPlannerSettings.java`

### Railways

Lost Cities railways are a separate native system with explicit chunk types for surface and underground stations, station extensions, descent sections, horizontal and vertical track, three-way splits, double bends, and rail endpoints. The native logic also resolves highway conflicts by moving affected stations underground when necessary.

StructureSmith railway compatibility must therefore be expressed as additional compatible rail parts, station variants, palettes, or selector/table entries. It must not replace the native railway grid, station-placement logic, or highway-conflict handling.

Relevant upstream references:

- `src/main/java/mcjty/lostcities/worldgen/lost/Railway.java`
- `src/main/java/mcjty/lostcities/api/RailChunkType.java`
- `src/main/java/mcjty/lostcities/worldgen/lost/regassets/data/RailwayParts.java`
- `src/main/java/mcjty/lostcities/worldgen/lost/regassets/data/RailSettings.java`

## Implementation rule for adapters

An adapter should conceptually produce a patch/overlay such as:

```json
{
  "compatibility": {
    "mode": "append_only",
    "preserve_existing": true
  },
  "additions": {
    "parts": ["structuresmith:..."],
    "selectors": ["structuresmith:..."],
    "table_entries": ["structuresmith:..."]
  }
}
```

It should never produce instructions equivalent to:

```json
{
  "replace_existing": true,
  "disable_native": true,
  "table_strategy": "replace"
}
```

## Validation boundary

Static source analysis can establish a strong compatibility hypothesis and can validate that StructureSmith's output follows the upstream model. It cannot certify runtime compatibility by itself. Fresh-world testing remains required for actual placement, selector behavior, cross-mod interactions, terrain handling, and version-specific execution.

The distinction is deliberate:

**source-informed additive compatibility -> static validation -> runtime test -> promotion**

Never promote a compatibility layer by replacing upstream behavior merely because an additive integration is harder to implement.
