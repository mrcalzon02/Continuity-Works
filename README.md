# Structure Generation Capability API

A standalone, vanilla-first, mod-aware **AI-callable Minecraft structure generation, auditing, contextualization, snapshotting, and review API** extracted and generalized from the structure-development methods used by **Infinite Domain**.

The repository is intended to stand on its own and be referenced by other projects and developers. It treats a Minecraft structure as an engineered artifact with purpose, spatial constraints, cultural language, version requirements, world-placement contracts, and validation gates—not merely a pile of blocks.

## Authoritative lifecycle

**discover → inventory → contextualize → audit → grade → plan → generate/refit → validate → snapshot → independently review → promote → iterate**

The framework keeps these concerns separate:

1. **Mechanical validity** — can the structure parse, place, rotate, connect, and preserve required integration?
2. **Fitness for purpose** — does the building or environmental feature actually work as the thing it claims to be?
3. **Context and cultural identity** — does it belong at this location, terrain, biome, culture, faction, institution, and technological level?
4. **Procedural structure logic** — can a generator satisfy scale, clearances, modularity, required zones, circulation, and target-version constraints?
5. **Visual quality** — does the result actually look professionally designed? Automated generation never grants its own visual approval.

## Built-in generation: modular dungeon / spatial skeletons

The first native procedural generator is a deterministic modular layout engine suitable for more than fantasy dungeons. Its purpose profiles can drive laboratories, crypts, fortresses, warehouses, temples, residences, ruins, underground complexes, and project-defined structure classes.

It supports:

- deterministic seeds;
- purpose-defined minimum and maximum footprint;
- explicit caller size envelope and preferred size;
- scale multipliers;
- required functional zones;
- room-count constraints;
- straight, bent, or more connected labyrinth routing;
- floor count and verticality contracts;
- connector-width checks;
- **triple-fold modularity**:
  - macro = site/program/wing composition;
  - meso = room and circulation modules;
  - micro = block/detail construction modules;
- purpose-fitness evaluation before materialization;
- deterministic Minecraft structure NBT skeleton materialization for supported namespaced-ID versions;
- automatic version-aware fragmentation of oversized structures into fixed-offset NBT piece sets;
- explicit generator-provider registration so new structural systems share the same API lifecycle;
- final generated-artifact snapshots with hashes.

The generator deliberately produces an **architectural skeleton**, not falsely self-certified finished architecture. Theme/detail providers can refine the artifact through the existing graded rebuild pipeline.

## Minecraft version targeting

Layout generation currently accepts Java Edition **1.12.x and newer 1.x targets**. Exact release metadata is bundled for common modding targets including 1.12.2, 1.16.5, 1.18.2, 1.19.2, 1.19.4, 1.20.1, 1.21, and 1.21.1.

Native namespaced structure-NBT materialization currently begins at **1.13+**. A 1.12.x request can still use the version-neutral layout system, but final block materialization requires a legacy numeric/block-state adapter. Unknown patch versions are never assigned a guessed DataVersion; callers must provide an explicit verified value.

When a materialized structure exceeds the target family's vanilla structure-template envelope, `materialization_mode: "auto"` fragments it along meso-module/floor boundaries and returns a fixed-offset piece set rather than silently emitting a structure-block-hostile monolith. Full jigsaw-pool compilation remains a provider extension, not a falsely claimed completed feature.

## donjon `dungeon.pl` relationship

The requested upstream reference is:

`https://donjon.bin.sh/code/dungeon/dungeon.pl`

Its source header identifies the code as **CC BY-NC 3.0**. To avoid silently imposing a noncommercial restriction on the reusable runtime, this repository keeps donjon as an **isolated reference/optional legacy-provider target** under `reference/donjon/`. The built-in `native_modular_v1` generator is an original dependency-free implementation and does not link or copy the donjon runtime code.

A fetch helper is included for environments where the exact upstream source should be pulled into the reference directory for comparison or explicitly noncommercial use. The exact `dungeon.pl` file is intentionally **not vendored in this package**; the compatibility adapter accepts its familiar option vocabulary while the native runtime remains independently implemented.

## Vanilla-first and mod-aware

The core has **no third-party runtime dependency**. Minecraft content defaults to verified `minecraft:*` material roles. Mod assets are used only when discovered locally or explicitly supplied in registry inventory. Unknown mod IDs are never invented.

Theme palette roles can feed procedural materialization: a downstream culture/institution profile may nominate foundation, structural, roof, floor, wall, technology, signage, and other role candidates while the registry resolver chooses only verified IDs.

## AI tool calling

The API publishes a portable JSON-Schema tool catalog:

```text
GET /v1/tools
```

The initial tool set exposes:

- `structure_capabilities`
- `structure_inventory`
- `structure_audit`
- `structure_plan`
- `structure_generate`
- `dungeon_layout`
- `minecraft_version`

The same operations remain callable through Python, CLI, and HTTP so an AI client does not require a separate implementation path.

## Python

```python
from structure_capability import StructureCapability

cap = StructureCapability(project_root=".")
result = cap.generate({
    "structure_id": "example:abandoned_research_complex",
    "structure_type": "underground_complex",
    "target_version": "1.20.1",
    "purpose": {
        "kind": "laboratory",
        "required_zones": ["entry", "laboratory", "utilities", "storage", "secure_core"]
    },
    "generation": {
        "kind": "modular_dungeon",
        "materialize_nbt": True,
        "materialization_mode": "auto",
        "layout": {
            "seed": 9001,
            "size": {"preferred_width": 72, "preferred_depth": 60},
            "modularity": {"triple_fold": True, "macro_module": 12, "meso_module": 4, "micro_module": 1}
        }
    }
})
print(result["generated_layout"]["fitness"])
print(result["structure_artifact"])
```

## CLI

```bash
python -m structure_capability.cli capabilities
python -m structure_capability.cli tools
python -m structure_capability.cli inventory --project /path/to/modpack
python -m structure_capability.cli plan examples/requests/heavy_rebuild.json
python -m structure_capability.cli dungeon-layout examples/requests/dungeon_layout.json
python -m structure_capability.cli generate examples/requests/generate_dungeon_structure.json
python -m structure_capability.cli minecraft-version 1.20.1
python -m structure_capability.cli serve --host 127.0.0.1 --port 8787
```

## HTTP JSON API

```text
GET  /v1/health
GET  /v1/capabilities
GET  /v1/tools
POST /v1/inventory
POST /v1/audit
POST /v1/plan
POST /v1/generate
POST /v1/dungeon/layout
POST /v1/minecraft/version
POST /v1/resume
```

## Rebuild gradient

| Level | Name | Intent |
|---:|---|---|
| 0 | AUDIT_ONLY | Observe and report; no geometry mutation |
| 1 | TOUCH_UP | Tiny repairs, obvious defects, compatibility fixes |
| 2 | REFIT | Local circulation, palette, fixtures, entrances, damaged details |
| 3 | DETAIL_PASS | Architectural depth, interiors, utilities, site context |
| 4 | FUNCTIONAL_REBUILD | Rework program/circulation while preserving major identity |
| 5 | HEAVY_REBUILD | Treat rough asset as a program diagram; rebuild substantially |
| 6 | FULL_RECONTEXTUALIZATION | Re-author footprint/massing/site relationship while preserving required integration contracts |

The requested level is a ceiling, not permission to mutate everything. The planner should choose the lowest intervention that satisfies failed gates.

## Snapshot model

Every meaningful generation is resumable. For built-in materialization, the final snapshot is chained to the planning snapshot and stores the generated `.nbt` artifact itself with a content hash.

Snapshots record source hashes, discovered mods/namespaces, request and contextual contracts, rebuild grade, preserved/frozen properties, generated artifacts, validation status, unresolved visual review, and next eligible action.

See `docs/SNAPSHOTS_AND_GENERATIONAL_EXECUTION.md`, `docs/DUNGEON_LAYOUT_AND_MODULARITY.md`, and `docs/GENERATOR_PROVIDER_REGISTRY.md`.

## Design rule

**Reuse → audit → repair → refine → generate/rebuild only as far as necessary → validate → snapshot → review.**

Never substitute a pretty render for a valid shipping structure, and never substitute a passing serializer/hash check for visual review.
