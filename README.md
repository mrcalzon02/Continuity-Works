# Continuity Works

**Continuity Works** is a standalone, vanilla-first, mod-aware, AI-callable Minecraft structure generation, auditing, contextualization, snapshotting, infrastructure, and content-authoring capability.

The repository treats Minecraft structures as engineered artifacts with purpose, spatial constraints, cultural language, version requirements, world-placement contracts, deterministic generation, and explicit validation gates—not merely as piles of blocks.

The authoritative repository is `mrcalzon02/Continuity-Works` and the authoritative branch is `main`.

## Public naming convention

The old **StructureSmith** name is retired. The public service/product identity is now:

```text
Human name: Continuity Works
Machine slug: continuity-works
Python distribution: continuity-works-capability
CLI: continuity-works
OpenAPI vendor extension: x-continuity-works
Per-tool OpenAPI extension: x-continuity-works-tool
Discovery endpoint: /.well-known/continuity-works.json
Environment prefix: CONTINUITY_WORKS_*
GitHub status prefix: continuity-works/*
Minecraft example namespace: continuity_works
```

The internal Python package `structure_capability` and class `StructureCapability` remain implementation names for compatibility. They are not the public product name.

The retired `/.well-known/structuresmith.json` path is retained only as an unadvertised compatibility alias. Legacy `STRUCTURESMITH_*` environment variables are accepted only as migration fallbacks. Canonical output, documentation, OpenAPI, discovery, and client metadata use Continuity Works.

## Runtime and client boundary

GitHub Pages hosts the static **StructureForge** workbench. It does not execute Python. An executable Continuity Works runtime may be local, client-hosted, or hosted on infrastructure chosen by an integrator:

```text
AI / external client ───────┐
                            v
                  Continuity Works API
                            |
                            v
                  StructureCapability
                    /               \
          generators             content tools

StructureForge browser client ──> same API contract when configured
```

The repository includes an optional non-billable reference deployment configuration, but Continuity Works does not require the project owner to provide open public compute for third-party callers.

## Rendering and visual-review boundary

**Continuity Works does not perform server-side 3D rendering as a required part of generation.** The API returns geometry, layouts, block operations, NBT/artifacts, validation results, and the metadata required for a client to inspect or render the result.

Visual rendering and visual review are optional client responsibilities. A browser, game/editor integration, desktop tool, AI client, or other consumer that wants a 3D preview renders the returned information using compute it controls. StructureForge's browser viewport is the reference client-side implementation.

Generation is not blocked because a visual review was not performed.

## Authoritative lifecycle

```text
discover → inventory → contextualize → audit → grade → plan
→ generate/refit → validate → snapshot → optional client review → promote/iterate
```

Mechanical validity, fitness for purpose, context/cultural identity, procedural structure logic, and optional visual presentation remain separate concerns.

## Native structure generation

### Modular spatial/dungeon generation

The deterministic modular generator supports laboratories, crypts, fortresses, warehouses, temples, residences, ruins, underground complexes, and project-defined structure classes. It provides:

- deterministic seeds;
- purpose-defined footprint envelopes;
- required functional zones and room-count constraints;
- straight, bent, and labyrinth circulation;
- verticality and connector-width constraints;
- macro/meso/micro triple-fold modularity;
- purpose-fitness evaluation before materialization;
- deterministic Minecraft structure NBT for supported versions;
- automatic fragmentation of oversized templates into fixed-offset piece sets;
- provider registration and final snapshot hashes.

### Infrastructure generation

`native_infrastructure_v1` provides deterministic roads, highways, civic facilities, and industrial facilities. Important contracts include:

- inner-city roads are exactly **6 blocks wide**;
- **5 blocks of terrain/integration padding** are reserved on each side;
- highway profiles expose lanes, shoulders, median, support spacing, deck thickness, elevation, and clearance;
- jigsaw-compatible connectors are emitted for sequential assembly;
- Lost Cities compatibility is additive and non-destructive;
- world-seed-derived candidate anchors are deterministic;
- purpose-depth validation is separate from runtime/world-placement validation.

See `docs/INFRASTRUCTURE_GENERATION.md` and `docs/COMPATIBILITY_POLICY.md`.

## Minecraft version and content tools

Layout generation supports Java Edition 1.12.x and newer 1.x targets. Native namespaced structure-NBT materialization begins at 1.13+. Known modding targets include 1.12.2, 1.16.5, 1.18.2, 1.19.2, 1.19.4, 1.20.1, 1.20.5, 1.21, and 1.21.1. Unknown patch versions are not assigned guessed DataVersion values.

Content authoring capabilities include:

- books;
- loot tables;
- recipes;
- advancements;
- tags;
- datapack manifests;
- composed structure/content packages;
- registry probing;
- semantic icon assignment.

The tooling adapts across known Minecraft format boundaries, including the 1.20.5 item-component transition and 1.21 datapack directory changes. Unknown mod IDs are never invented.

## AI tool calling

Machine discovery is progressive and token-efficient:

```text
GET /.well-known/continuity-works.json
GET /openapi.json
GET /v1/tools
GET /v1/tools/index
GET /v1/tools/{tool_name}
GET /v1/presets
GET /v1/presets/{preset_id}
POST /v1/resolve
```

The schema-version 1.3 catalog exposes these 17 deliberate capability tools:

```text
structure_capabilities
structure_inventory
structure_audit
structure_plan
structure_generate
dungeon_layout
infrastructure_layout
minecraft_version
minecraft_registry_probe
minecraft_book_generate
minecraft_loot_table_generate
minecraft_recipe_generate
minecraft_advancement_generate
minecraft_tag_generate
minecraft_datapack_manifest_generate
minecraft_content_package_generate
minecraft_icon_assign
```

Published tool metadata appears under `x-continuity-works`. Each tool's canonical HTTP route, deployment state, and manual UI classification are attached there by the publication boundary.

## HTTP JSON API

```text
GET  /.well-known/continuity-works.json
GET  /openapi.json
GET  /v1/health
GET  /v1/serviceability
GET  /v1/capabilities
GET  /v1/tools
GET  /v1/tools/index
GET  /v1/tools/{tool_name}
GET  /v1/presets
GET  /v1/presets/{preset_id}
POST /v1/resolve
POST /v1/inventory
POST /v1/audit
POST /v1/plan
POST /v1/generate
POST /v1/dungeon/layout
POST /v1/infrastructure/layout
POST /v1/minecraft/version
POST /v1/minecraft/registry/probe
POST /v1/minecraft/book
POST /v1/minecraft/loot-table
POST /v1/minecraft/recipe
POST /v1/minecraft/advancement
POST /v1/minecraft/tag
POST /v1/minecraft/datapack-manifest
POST /v1/minecraft/content-package
POST /v1/minecraft/icon
POST /v1/resume
```

## Python

```python
from structure_capability import StructureCapability

cap = StructureCapability(project_root=".")

layout = cap.infrastructure_layout({
    "module_type": "inner_city_road",
    "seed": 9001,
    "world_seed": 20260824,
    "road": {"width": 6, "terrain_padding": 5},
    "jigsaw": {"enabled": True, "pool": "continuity_works:infrastructure"},
    "lost_cities": {
        "enabled": True,
        "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"]
    },
    "purpose": {"depth": 3}
})
```

The public tool catalog returned by `StructureCapability.tools()` uses `x-continuity-works`, while the internal module/class names remain stable for existing Python integrations.

## CLI and local runtime

Install and run locally:

```bash
python -m pip install -e .
continuity-works capabilities
continuity-works tools
HOST=0.0.0.0 PORT=8787 python scripts/run_api.py
```

The legacy `structure-capability` executable remains an alias during migration.

Validate a running local service:

```bash
python scripts/http_smoke.py http://127.0.0.1:8787
python scripts/public_serviceability.py --api http://127.0.0.1:8787
```

`PUBLIC_SERVICEABILITY` deliberately distinguishes local implementation readiness from true external reachability. A remote endpoint is never declared verified merely because local tests pass.

## Rebuild gradient

| Level | Name | Intent |
|---:|---|---|
| 0 | AUDIT_ONLY | Observe/report; no geometry mutation |
| 1 | TOUCH_UP | Tiny repairs and compatibility fixes |
| 2 | REFIT | Local circulation, palette, fixtures, entrances, damage details |
| 3 | DETAIL_PASS | Architectural depth, interiors, utilities, site context |
| 4 | FUNCTIONAL_REBUILD | Rework program/circulation while preserving major identity |
| 5 | HEAVY_REBUILD | Treat the rough asset as a program diagram and rebuild substantially |
| 6 | FULL_RECONTEXTUALIZATION | Re-author footprint/massing/site relationship while preserving required integration contracts |

The requested level is a ceiling, not permission to mutate everything. The planner chooses the lowest intervention that satisfies failed gates.

## Compatibility doctrine

Compatibility is additive and non-destructive. Compatibility adapters may add registrations, table entries, spawn contracts, jigsaw links, or integration metadata; they must not replace another mod's native roads, highways, railways, registries, or world-generation systems merely to achieve integration.

## donjon reference boundary

The upstream `dungeon.pl` reference is kept isolated under `reference/donjon/` because its source identifies a CC BY-NC license. The built-in `native_modular_v1` engine is an independent dependency-free implementation and does not copy/link the upstream runtime.

## Further documentation

- `docs/API.md`
- `docs/DEPLOYMENT.md`
- `docs/PUBLIC_SERVICEABILITY.md`
- `docs/INFRASTRUCTURE_GENERATION.md`
- `docs/MINECRAFT_CONTENT_API_TOOLS.md`
- `docs/COMPATIBILITY_POLICY.md`
- `docs/SNAPSHOTS_AND_GENERATIONAL_EXECUTION.md`

**Design rule:** reuse → audit → repair → refine → generate/rebuild only as far as necessary → validate → snapshot → optional client-owned review.
