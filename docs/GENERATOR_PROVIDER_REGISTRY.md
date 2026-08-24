# Generator Provider Registry

Procedural generation is deliberately dispatched through one registry instead of hard-coding every structure family into `StructureCapability.generate()`.

## Semantic structure type versus generation method

`structure_type` describes **what the artifact is**: for example `building`, `ruin`, `settlement`, `ship`, `underwater`, `infrastructure`, or `underground_complex`.

`generation.kind` describes **how geometry/layout is produced**: for example the built-in `dungeon`, `dungeon_layout`, or `modular_dungeon` aliases.

These are intentionally independent. A laboratory, bunker, sewer, temple, or derelict station can all use the same modular spatial provider while retaining distinct purposes, themes, contexts, validation rules, and later detail passes.

## Built-in provider

`NativeDungeonProvider` wraps the native modular layout engine and optional NBT skeleton compiler. It declares aliases, reports its capabilities, normalizes compatibility inputs, runs the fitness gate, and returns generation metadata plus zero or more binary artifacts.

## Registering another provider

A provider needs:

- an `aliases` iterable;
- `describe()` returning JSON-serializable capability metadata;
- `generate(structure_request, registry_resolver)` returning a generation result.

Register it on the same capability instance:

```python
cap.register_generator(MySettlementProvider())
```

The provider is then resolved from `request.generation.kind` and receives the same authoritative request model, discovered registry resolver, planning lifecycle, and final snapshot path as built-in generation.

A provider result should use the following shape:

```python
{
    "provider_id": "example_settlement_v1",
    "status": "MATERIALIZED",  # provider-defined machine-readable state
    "generated_layout": {...},
    "structure_artifact": {...},
    "artifact_bytes": {
        "piece_000.nbt": b"..."
    }
}
```

`artifact_bytes` may be `None` for planning/layout-only providers. When binary artifacts are returned, the capability copies them into the final immutable generation snapshot and records their hashes.

## Intended provider families

The registry is the extension boundary for future systems such as settlements, roads/rail, bridges, ships, megastructures, terrain-integrated ruins, underwater sites, jigsaw pools, WorldEdit/Litematica adapters, and project-specific authored/rebuild generators. Those future providers should reuse the existing purpose, culture/theme, context, clearance, registry-awareness, fitness, snapshot, and review contracts instead of growing parallel APIs.
