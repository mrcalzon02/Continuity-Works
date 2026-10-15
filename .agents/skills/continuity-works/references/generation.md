# Purpose-first generation and mutator sequencing

Use these as **planning instructions**; the actual generator schema and supported mutators must be read from the current API or Python catalog. Never pass an undocumented parameter because it appears here.

## Decision chain

```text
target version/modpack/world seed
  → inventory + registry probes
  → archetype/purpose/scale
  → biome + height + terrain envelope
  → select generator/preset
  → macro layout + footprint + exclusion reservation
  → meso rooms, circulation, functional zones, connectors
  → micro palettes, details, states, loot, occupancy
  → generator fitness gates + artifact snapshot
  → worldgen integration + fresh-world placement tests
```

Keep each step reproducible with a stable seed, explicit inputs, and a short checkpoint. A mutator changes one logically bounded part of the proposed structure. If a gate fails, revise that step instead of regenerating unrelated completed decisions. A constrained inference model can emit one short mutation directive per call while an external orchestrator retains the schema and accumulated state.

## Archetype requirements

Determine purpose and era/technology, human-use scale, footprint classes, architectural program, required functional zones, entrances, circulation, utilities, stairs or other vertical links, terrain transitions, material families, climate/biome adaptations, lore/culture variants, intact/ruined/repurposed states, jigsaw/family relationships, and loot/occupancy only where relevant. Select only the features the authorized target modpack actually supports.

For procedural interiors, respect macro/meso/micro modularity, deterministic seeds, zone constraints, route connections, and gate-derived evidence. On supported targets, oversized NBT may require deterministic fragmentation into fixed-offset pieces rather than pretending a single structure-block template has unlimited dimensions.

## World placement and 500-block protection

By default, **independent structures may not overlap one another's footprints or the project's minimum 500-block exclusion/reservation zones**. Resolve anchor, footprint, rotated bounding envelope, any overhangs, and registered/reserved neighbors before committing placement. Reject and reseed/reselect conflicting candidates rather than writing over existing structures. Explicitly related jigsaw/family components may be colocated only under a defined family-compatibility rule; "same biome" does not make structures a family.

A layout or prospective anchor does **not** prove runtime exclusion. Check the target mod's actual registration and spawn-protection implementation, dimension/world-seed behavior, world-save persistence, and placement hooks. When enforcement is missing or untested, surface the outstanding adapter/runtime gate.

## Compatibility and contexts

The project's compatibility doctrine is append-only and non-destructive, including Lost Cities support. The city-road section is exactly **6 road blocks plus 5 blocks integration padding on each side**. Highway/rail/urban connections must preserve upstream planners and registers. Biome/context changes may add palettes, placement predicates, or jigsaw parts without disabling native behavior. Check target Minecraft version and loader before promising mod-specific adapters.

Read [infrastructure generation](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/INFRASTRUCTURE_GENERATION.md), [compatibility policy](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/COMPATIBILITY_POLICY.md), and [API reference](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/API.md) for current details.
