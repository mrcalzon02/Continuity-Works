# Dungeon Layout, Scaling, and Triple-Fold Modularity

The dungeon subsystem is a **general spatial-layout capability**, not a theme-locked fantasy dungeon generator. It can provide structural skeletons for laboratories, crypts, fortresses, warehouses, temples, residences, ruins, underground transit facilities, and downstream project-specific purposes.

## Three modular layers

`triple_fold: true` activates three deliberate scales:

1. **Macro module** — site/program composition: wings, major districts, courtyards, secure cores, loading zones, encounter regions.
2. **Meso module** — rooms and circulation: room dimensions, corridor routing, connector rhythm, repeatable bays.
3. **Micro module** — block/detail construction: wall thickness, trim, doors, machinery clearances, decoration and palette application.

The layout resolves its footprint to a compatible modular quantum when possible. If the strict macro quantum cannot fit the declared purpose envelope, it may fall back to meso quantization but reports that resolution explicitly.

This separation is deliberate: a downstream generator may replace the micro materializer without changing the room graph, or replace the macro planner without throwing away validated connector and block-module contracts.

## Fitness-for-purpose sizing

Purpose is allowed to constrain size. A request combines:

- purpose-family minimum/maximum footprint;
- caller minimum/maximum footprint;
- preferred footprint;
- scalar size multiplier;
- required functional zones;
- requested room count;
- connector width;
- floor count and verticality;
- modular room minimum/maximum dimensions.

The generator returns a `fitness` object. A layout fails rather than self-approving when required zones are missing, the footprint violates explicit limits, the room graph is incomplete, or modular alignment fails.

Built-in purpose profiles are defaults rather than a closed taxonomy. `purpose_constraints` and `required_zones` let projects describe new functional programs without forking the engine.

## Layout and circulation controls

The native provider currently exposes:

- shapes: `rectangle`, `cross`, `round`, `ring`;
- room packing: `scattered` or `packed`;
- corridor behavior: `straight`, `bent`, or `labyrinth`;
- dead-end policy: `many`, `some`, or `none`;
- deterministic stair markers and floor contracts;
- explicit connector width and modular room dimensions.

The grid is an intermediate spatial contract. `R` cells are room modules, `.` cells are circulation, and `X` cells are outside the active shape mask.

## donjon compatibility bridge

The requested upstream reference is `https://donjon.bin.sh/code/dungeon/dungeon.pl`. Its source header applies CC BY-NC 3.0, so the native runtime does **not** copy or link that implementation.

`classic_donjon_options` provides a compatibility bridge for familiar inputs including:

- `dungeon_layout`: `None`, `Box`, `Cross`, `Round`;
- `room_layout`: `Packed`, `Scattered`;
- `corridor_layout`: `Labyrinth`, `Bent`, `Straight`;
- `remove_deadends` percentage;
- `room_min` / `room_max`;
- `n_rows` / `n_cols`;
- `add_stairs`.

Those options are translated into the native block-scaled, purpose-aware request and can then be overridden by the richer macro/meso/micro contract. The exact upstream Perl source is not vendored; `reference/donjon/fetch_donjon_reference.py` is the explicit opt-in fetch path for comparison or separately licensed/noncommercial use.

## NBT materialization and oversized structures

The spatial engine is version-neutral; the built-in NBT compiler currently targets namespaced-ID Minecraft Java structures (1.13+). Materialization modes are:

- `auto` — use one template when it fits, otherwise fragment it;
- `single` — require one template and reject an oversized result unless the caller explicitly permits an oversize NBT artifact;
- `fragmented` — deliberately create a piece set.

Fragmentation occurs on meso-module boundaries in X/Z and complete floor groups in Y. Every piece records its fixed offset from the structure origin. Shared-boundary openings are evaluated against the **global** layout mask so a fragment seam does not accidentally gain a wall.

The returned `structure_artifact` declares the overall size, target-version metadata, effective piece limit, piece count, piece sizes, offsets, hashes, palette, and an assembly contract. It is presently a **fixed-offset piece set**; jigsaw-pool/worldgen conversion is intentionally left as a provider extension rather than presented as already implemented.

Each generated binary is copied into the final `generate` snapshot and content-hashed so an AI or CI client can resume from the exact materialized generation.

## Authoring quality boundary

Passing spatial fitness means the generated structure has a coherent program envelope and connected spatial skeleton. It does **not** constitute visual approval. Architectural detailing, cultural language, damage storytelling, loot/progression integration, terrain blending, and fixed-camera visual review remain separate gates in the broader structure lifecycle.
