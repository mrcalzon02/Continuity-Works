# Structure Generation Capability API

A standalone, vanilla-first, mod-aware **AI-callable Minecraft structure generation, auditing, contextualization, snapshotting, and review API** extracted and generalized from the structure-development methods used by **Infinite Domain**.

The repository is intended to stand on its own and be referenced by other projects and developers. It treats a Minecraft structure as an engineered artifact with purpose, spatial constraints, cultural language, version requirements, world-placement contracts, and validation gates—not merely a pile of blocks.

## Public deployment boundary

**GitHub Pages is the static StructureForge frontend only. It does not execute the Python API.** The persistent API is configured as a separate Python web service and both external AI clients and StructureForge call that same HTTPS boundary:

```text
Gemini / ChatGPT / external client -> public HTTPS StructureSmith API -> StructureCapability -> generators/content tools
GitHub Pages StructureForge frontend -> same public HTTPS StructureSmith API
```

Configured production API base URL after the one-time Render Blueprint activation:

```text
https://structuresmith-mrcalzon02-api.onrender.com
```

Machine-discovery endpoints:

```text
GET /.well-known/structuresmith.json
GET /openapi.json
GET /v1/tools
GET /v1/health
```

The repository includes `render.yaml`; its start command runs the existing dependency-free server through `scripts/run_api.py`, binding to `0.0.0.0` and the host-assigned `PORT`. StructureForge defaults to the same public API base rather than assuming `/v1/*` exists under `mrcalzon02.github.io/StructureSmith/`. See `docs/DEPLOYMENT.md` for activation, CORS, external-agent usage, and smoke-test instructions.

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

## Built-in generation: infrastructure, roads, and common facilities

`native_infrastructure_v1` adds a deterministic infrastructure provider for roads, highways, civic facilities, and industrial facilities.

Key contracts include:

- **inner-city roads are always exactly 6 blocks wide**;
- **5 blocks of terrain/integration padding are reserved on each side**, producing a 16-block total cross-section;
- highway derivatives expose lane count, lane width, shoulders, median, deck thickness, support spacing, elevation, and clearance;
- the `elevated_urban_water_crossing` highway profile captures the useful structural language of the current visual reference: wide elevated deck, continuous barriers, repeating piers, and clean lower-level/water clearance;
- jigsaw-compatible start/end or frontage/service connectors are emitted for sequential assembly;
- an explicit Lost Cities compatibility contract exposes tileable-grid, randomized-coordinate, and sequential-jigsaw spawn modes;
- world-seed-derived candidate anchors are deterministic and reproducible;
- every generated module has a **depth-of-purpose** level and fails static fitness below functional-zoning depth;
- civic and industrial facilities have urban and rural program variants;
- static contract validation is kept separate from fresh-world Lost Cities/runtime placement validation.

Detailed architecture, schemas, runtime boundaries, and archived deterministic examples are documented in `docs/INFRASTRUCTURE_GENERATION.md`.

## Minecraft version targeting

Layout generation currently accepts Java Edition **1.12.x and newer 1.x targets**. Exact release metadata is bundled for common modding targets including 1.12.2, 1.16.5, 1.18.2, 1.19.2, 1.19.4, 1.20.1, **1.20.5**, 1.21, and 1.21.1.

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

Content-tool inventory now also indexes discoverable recipe, loot-table, structure, item-tag, and item model/texture resource IDs. Deliberate content calls return confidence as `vanilla`, `exact`, `candidate`, `namespace`, or `unknown`; callers can select `id_policy: strict | namespace | permissive` and receive an explicit promotion/materialization gate instead of a guessed mod ID.

## Minecraft content authoring tools

Books, loot tables, recipes, **advancements, tags, datapack manifests, composed structure/content packages**, registry probing, and semantic icons are first-class API capabilities rather than disconnected helper snippets. Their output adapts across known Minecraft format boundaries, including the 1.20.5 item-component transition and the 1.21 datapack directory rename. Every authoring result contains deterministic public gate codes and a `materialization_allowed` decision; the API does not expose hidden chain-of-thought.

The content-package composer can dispatch an optional structure request through the same authoritative generation path and bind named generated books into named loot tables as genuinely guaranteed one-roll evidence pools. It then returns grouped artifacts, a file manifest, resolved links, and one aggregate package gate.

Icon assignment prefers a known/discoverable Minecraft item icon and can fall back to a deterministic lightweight SVG badge when a suitable item icon cannot be established. See `docs/MINECRAFT_CONTENT_API_TOOLS.md` for the compatibility, composition, and gate contract.

## AI tool calling

The API publishes a portable JSON-Schema tool catalog:

```text
GET /v1/tools
```

It also publishes a standards-compatible OpenAPI 3.1 description and discovery document:

```text
GET /openapi.json
GET /.well-known/structuresmith.json
```

The schema-version **1.3** tool set exposes 17 deliberate calls:

- `structure_capabilities`
- `structure_inventory`
- `structure_audit`
- `structure_plan`
- `structure_generate`
- `dungeon_layout`
- `infrastructure_layout`
- `minecraft_version`
- `minecraft_registry_probe`
- `minecraft_book_generate`
- `minecraft_loot_table_generate`
- `minecraft_recipe_generate`
- `minecraft_advancement_generate`
- `minecraft_tag_generate`
- `minecraft_datapack_manifest_generate`
- `minecraft_content_package_generate`
- `minecraft_icon_assign`

The infrastructure tool schema publishes the same road/highway/Lost Cities/jigsaw/world-seed/purpose variables exposed in the StructureForge web UI. The same operations remain callable through Python and HTTP so an AI client does not require a separate implementation path.

External clients can retrieve the live catalog with:

```bash
curl -fsS https://structuresmith-mrcalzon02-api.onrender.com/v1/tools
```

and execute a real capability through the same service:

```bash
curl -fsS -H 'Content-Type: application/json' \
  -d '{"module_type":"inner_city_road","road":{"width":6,"terrain_padding":5},"purpose":{"depth":3}}' \
  https://structuresmith-mrcalzon02-api.onrender.com/v1/infrastructure/layout
```

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

Infrastructure can be called directly:

```python
layout = cap.infrastructure_layout({
    "module_type": "inner_city_road",
    "seed": 9001,
    "world_seed": 20260824,
    "road": {"width": 6, "terrain_padding": 5},
    "jigsaw": {"enabled": True, "pool": "structuresmith:infrastructure"},
    "lost_cities": {
        "enabled": True,
        "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"]
    },
    "purpose": {"depth": 3}
})
```

Content tools use the same object:

```python
book = cap.minecraft_book_generate({
    "target_version": "1.20.5",
    "title": "Containment Log",
    "author": "VCF",
    "pages": ["Entry one", {"text": "Entry two", "bold": True}],
})

loot = cap.minecraft_loot_table_generate({
    "target_version": "1.21",
    "table_id": "example:chests/evidence",
    "items": [{"id": "minecraft:iron_ingot", "weight": 4}],
    "guaranteed": [{"id": "minecraft:paper", "count": 1}],
})

package = cap.minecraft_content_package_generate({
    "package_id": "example:quest_site",
    "target_version": "1.20.5",
    "books": [{
        "name": "evidence",
        "title": "Containment Log",
        "author": "VCF",
        "pages": ["Entry one"]
    }],
    "loot_tables": [{"name": "evidence_chest", "items": [{"id": "minecraft:iron_ingot", "weight": 4}]}],
    "bindings": [{"type": "book_as_guaranteed_loot", "book": "evidence", "loot_table": "evidence_chest"}]
})
```

## CLI

```bash
python -m structure_capability.cli capabilities
python -m structure_capability.cli tools
python -m structure_capability.cli inventory --project /path/to/modpack
python -m structure_capability.cli plan examples/requests/heavy_rebuild.json
python -m structure_capability.cli dungeon-layout examples/requests/dungeon_layout.json
python -m structure_capability.cli infrastructure-layout examples/requests/infrastructure_layout.json
python -m structure_capability.cli generate examples/requests/generate_dungeon_structure.json
python -m structure_capability.cli minecraft-version 1.20.1
python -m structure_capability.cli serve --host 127.0.0.1 --port 8787
```

`scripts/archive_infrastructure_examples.py` regenerates and validates the canonical four civic/industrial example archives.

## HTTP JSON API

```text
GET  /.well-known/structuresmith.json
GET  /openapi.json
GET  /v1/health
GET  /v1/capabilities
GET  /v1/tools
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

The reusable HTTP proof command is:

```bash
python scripts/http_smoke.py https://structuresmith-mrcalzon02-api.onrender.com
```

The smoke harness requires the machine-readable catalog and metadata plus a successful real infrastructure capability call. A static GitHub Pages response is not treated as API execution proof.

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

See `docs/SNAPSHOTS_AND_GENERATIONAL_EXECUTION.md`, `docs/DUNGEON_LAYOUT_AND_MODULARITY.md`, `docs/GENERATOR_PROVIDER_REGISTRY.md`, `docs/INFRASTRUCTURE_GENERATION.md`, `docs/MINECRAFT_CONTENT_API_TOOLS.md`, and `docs/DEPLOYMENT.md`.

## Design rule

**Reuse → audit → repair → refine → generate/rebuild only as far as necessary → validate → snapshot → review.**

Never substitute a pretty render for a valid shipping structure, and never substitute a passing serializer/hash check for visual review.
