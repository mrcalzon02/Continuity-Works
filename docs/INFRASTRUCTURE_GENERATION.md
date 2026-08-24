# StructureForge Infrastructure Generation

## Purpose

`native_infrastructure_v1` extends StructureSmith with deterministic infrastructure and common-facility layout contracts that can be consumed by humans, AI tool callers, datapack/Forge/Fabric adapters, or downstream Minecraft structure compilers.

The generator is intentionally not a black-box city builder. Every generated result includes its spatial contract, purpose depth, jigsaw connectors, placement derivation, compatibility manifest, fitness findings, and explicit runtime gates.

## Reference-derived highway language

The supplied visual reference is treated as a **design input**, not copied geometry. Its useful structural language is represented by the `elevated_urban_water_crossing` profile:

- broad elevated deck suitable for multi-lane traffic;
- continuous outer barriers;
- repeating pier/support rhythm;
- explicit vertical clearance for water, lower roads, or terrain;
- approach grading metadata so the elevated segment cannot simply terminate in mid-air;
- jigsaw endpoints for continuation and branching.

Lane count, lane width, shoulder width, median width, support spacing, deck thickness, and clearance remain explicit parameters. This means a visual reference can influence the profile while the actual Minecraft dimensions remain auditable and reusable.

## Hard inner-city cross-section

Inner-city road modules enforce this cross-section and reject incompatible overrides:

```text
5 blocks terrain padding | 6 blocks roadbed | 5 blocks terrain padding
```

The total module width is therefore **16 blocks**, which also makes the strict road module naturally chunk-width compatible without changing the requested 6-block road surface.

The five-block margins are integration space. They may be resolved by a runtime/materialization adapter into sidewalk, verge, retaining wall, frontage setback, utility trench, landscaping, terrain blend, or other project-defined edge treatment, but the reserved width itself is not silently removed.

## Public API

### Dedicated layout endpoint

```http
POST /v1/infrastructure/layout
Content-Type: application/json
```

Example:

```json
{
  "module_type": "highway",
  "variant": "urban",
  "seed": 9001,
  "world_seed": 20260824,
  "orientation": "east_west",
  "segment_length": 96,
  "highway": {
    "profile": "elevated_urban_water_crossing",
    "lane_count": 4,
    "lane_width": 3,
    "shoulder_width": 1,
    "median_width": 2,
    "elevated": true,
    "support_spacing": 12,
    "deck_thickness": 2,
    "min_clearance": 7
  },
  "jigsaw": {
    "enabled": true,
    "pool": "structuresmith:infrastructure",
    "connector_width": 3,
    "max_depth": 8
  },
  "lost_cities": {
    "enabled": true,
    "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"],
    "tile_span_chunks": 2
  },
  "random_spawn": {"radius_blocks": 4096, "spacing_blocks": 256, "salt": 734287},
  "purpose": {"depth": 3}
}
```

The same layout object can be supplied through the authoritative structure-generation API:

```json
{
  "structure_id": "example:urban_highway",
  "structure_type": "highway",
  "purpose": {"kind": "transport"},
  "generation": {"kind": "infrastructure", "layout": {"...": "same infrastructure_layout payload"}}
}
```

The `infrastructure_layout` entry in `/v1/tools` publishes the complete JSON-Schema variable surface for AI/function-calling clients.

## UX/API parity

The StructureForge web interface exposes the same infrastructure variables in the **StructureForge Infrastructure** dropdown:

- module type and urban/rural variant;
- deterministic module seed and world seed;
- orientation and segment length;
- strict road width and terrain padding;
- highway reference profile and all lane/deck/support dimensions;
- jigsaw enablement, pool, connector width, and maximum depth;
- Lost Cities master toggle and spawn-mode selection;
- tile span, randomized spawn radius/spacing/salt;
- depth of purpose;
- optional facility kind.

The request preview shows the actual `/v1/generate` payload produced by the form. There is no separate hidden frontend configuration model for infrastructure.

## Lost Cities compatibility contract

`lost_cities.enabled` is the master compatibility switch. When enabled, one or more spawn modes can be requested.

### `tileable_grid`

Emits a chunk-aligned tile contract and the module footprint. It is suitable for a Lost Cities adapter that assigns structures to city/grid lots.

### `randomized_coordinate`

Emits a deterministic candidate anchor derived from:

```text
SHA-256(world_seed | salt | module_type | variant | module_seed)
```

The coordinate is snapped to the requested spacing. Changing the world seed changes the deterministic placement stream without making the generator non-reproducible.

### `sequential_jigsaw`

Emits a jigsaw pool, maximum assembly depth, and explicit named connectors. Road/highway modules receive start/end connectors; facility modules receive frontage and service connectors.

### Runtime boundary

StructureSmith can validate the **contract** without pretending it has run the Lost Cities mod. Returned results therefore use:

```text
CONTRACT_READY_RUNTIME_TEST_REQUIRED
```

A fresh-world game test remains mandatory before claiming real Lost Cities placement compatibility. This distinction is recorded in every result and archived example.

## Depth of purpose

Every module carries a purpose level:

| Level | Meaning |
| --- | --- |
| 0 | geometry only |
| 1 | access and clearance |
| 2 | functional zoning — minimum valid generation depth |
| 3 | ecosystem/intramodule integration |
| 4 | narrative and operational depth |

Generation below level 2 fails the fitness gate. Civic and industrial examples are archived at level 4 so the module must represent users, dependencies, circulation/service needs, and functional zones rather than merely produce a rectangular shell.

## Common civic and industrial facilities

The initial facility family intentionally provides four context variants:

| Archive | Facility | Context | Purpose characteristics |
| --- | --- | --- | --- |
| `civic_urban.json` | civic services center | urban | street frontage, public counter, offices, records, staff and utilities |
| `civic_rural.json` | civic services center | rural | larger setback, community room, emergency storage, public/service access |
| `industrial_urban.json` | industrial service works | urban | compact loading/workshop/storage program, separated freight/service access |
| `industrial_rural.json` | industrial service works | rural | expanded yard, bulk storage, freight circulation and service road interface |

These are **structural program/layout contracts**, not final art-direction templates. A theme/palette/materialization layer remains responsible for turning the validated program into project-specific Minecraft architecture.

## Archived deterministic example runs

Run:

```bash
python scripts/archive_infrastructure_examples.py
```

The script generates the four files under `examples/infrastructure/archives/` and then immediately repeats each request. The archive is written only if:

- both runs produce the same SHA-256 result fingerprint;
- static fitness is `PASS`;
- the world-seed placement contract is active.

The manifest records the seed, fingerprint, candidate anchor, fitness state, and deterministic replay result for each example.

## Validation layers

A generated infrastructure result has two deliberately separate validation levels.

**Static/authoring validation** can be automated in StructureSmith: dimensional invariants, purpose depth, zone presence, deterministic placement derivation, jigsaw connector presence, and Lost Cities adapter contract completeness.

**Runtime validation** cannot be honestly simulated by static Python output: fresh-world placement, actual Lost Cities lot/grid behavior, collision with real terrain/city generation, jigsaw expansion inside the selected Minecraft/mod version, and gameplay traversal. Those remain explicit runtime gates instead of being falsely marked complete.
