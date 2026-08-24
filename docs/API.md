# API Reference

## `StructureCapability(project_root, state_root=None)`

### `.capabilities()`
Returns the stable API version, supported lifecycle operations, rebuild grades, procedural-generation features, Minecraft version/content policy, and review requirements.

### `.tools()`
Returns the portable JSON-Schema AI function/tool catalog used by `GET /v1/tools`. Tool entries include StructureSmith semantic-icon metadata and declare the deterministic public validation-gate reasoning contract. Catalog schema version 1.3 exposes 17 deliberate tools.

### `.inventory_project()`
Returns discovered local mods, namespaces, explicit registry inventory, discoverable Minecraft resource IDs/candidates, and the inventory hash.

### `.audit(request)`
Parses/inspects the source when supported, checks context and clearance requirements, evaluates fitness, and creates an immutable snapshot.

### `.plan(request)`
Creates the audit plus rebuild-grade plan, preservation/frozen contracts and ordered pass sequence.

### `.generate(request)`
Runs the authoritative generation lifecycle.

For generator kinds `dungeon`, `dungeon_layout`, or `modular_dungeon`, the built-in engine generates a deterministic purpose-sized layout. With `generation.materialize_nbt=true`, a passing layout is compiled to a conservative Minecraft structure-NBT architectural skeleton and saved into the final generation snapshot. `generation.materialization_mode` accepts `auto`, `single`, or `fragmented`; `auto` converts oversized builds into a fixed-offset piece set using the target version profile rather than silently treating them as one universally loadable structure-block template.

Other generator kinds retain the provider-oriented behavior and receive a generation dossier rather than fabricated geometry.

### `.dungeon_layout(request)`
Runs the version-neutral native modular layout generator directly. The response includes rooms, functional zones, corridor paths, doors, optional stairs, footprint resolution, macro/meso/micro modularity metadata, and a fitness result.

### `.infrastructure_layout(request)`
Runs the deterministic infrastructure generator directly for inner-city roads, highways, civic facilities, and industrial facilities. The public contract includes strict 6-block city roads with 5-block terrain padding per side, highway dimensions, jigsaw connectors, Lost Cities placement modes, purpose depth, and world-seed-derived candidate anchors. Runtime/fresh-world placement remains a separate validation gate.

### `.minecraft_version(version)`
Resolves known target-version metadata and compatibility features. The resolver refuses to invent exact DataVersion values for unknown patch versions. Exact bundled metadata includes Minecraft Java 1.20.5 (`DataVersion 3837`, resource-pack format `32`, data-pack format `41`).

### `.minecraft_registry_probe(request)`
Checks a vanilla or modded resource location against the scanned project inventory. Responses include a confidence level (`vanilla`, `exact`, `candidate`, `namespace`, or `unknown`), evidence, an `accepted` flag, and deterministic gate reason codes.

### `.minecraft_book_generate(request)`
Assembles a version-aware written-book item payload plus a loot-compatible item representation. Pre-1.20.5 targets use the legacy written-book tag/SNBT shape and retain the legacy 100-page gate; 1.20.5+ targets use `minecraft:written_book_content` and do not enforce the removed legacy page-count ceiling.

### `.minecraft_loot_table_generate(request)`
Builds a loot-table JSON artifact with weighted pools and separate one-roll guaranteed pools. Resource packaging adapts to the target Minecraft version. Custom item data is emitted through legacy `minecraft:set_nbt` before 1.20.5 or `minecraft:set_components` on 1.20.5+, and referenced item IDs are gated against the mod-aware inventory.

### `.minecraft_recipe_generate(request)`
Builds shaped, shapeless, cooking, or stonecutting recipe JSON. Result item stacks, ingredient syntax, and datapack folder names adapt across Minecraft format boundaries. Unsupported/custom serializer types are rejected by a public gate instead of guessed.

### `.minecraft_advancement_generate(request)`
Builds an advancement with explicit criteria/triggers, optional parent/display/requirements/rewards, version-aware display icon representation, and version-aware `advancements`/`advancement` resource directories. Empty criteria fail materialization rather than producing a knowingly invalid advancement.

### `.minecraft_tag_generate(request)`
Builds datapack tags for `item`, `block`, `fluid`, `entity_type`, `function`, or `game_event` registries. Paths adapt to Minecraft 1.21's singular tag registry directories, and item values participate in mod-aware ID gating.

### `.minecraft_datapack_manifest_generate(request)`
Builds `pack.mcmeta`. Exact bundled releases use their verified data-pack format. Unknown releases require an explicit `pack_format`; the capability fails rather than guessing one.

### `.minecraft_content_package_generate(request)`
Composes an optional authoritative structure-generation request with books, loot tables, recipes, advancements, tags, and `pack.mcmeta`. The first typed cross-artifact binding, `book_as_guaranteed_loot`, injects a named generated book into its own one-roll pool in a named loot table. Child gates and optional structure generation are aggregated into one package-level `materialization_allowed` decision. The optional structure request is dispatched through `.generate()` rather than a parallel structure implementation.

### `.minecraft_icon_assign(request)`
Returns a semantic Minecraft item icon when available or a deterministic lightweight SVG badge fallback. This is intentionally a simple no-network icon path, not a substitute for authored texture art.

### `.resume(snapshot_id)`
Loads the persisted snapshot manifest.

## HTTP

Run:

```bash
python -m structure_capability.cli serve --project /path/to/project
```

Endpoints:

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

## AI tool catalog

`GET /v1/tools` returns function definitions with inline JSON Schema parameters. This is intentionally transport-neutral: an OpenAI-style function caller, a local orchestration agent, a GitHub automation, or another API client can adapt the same catalog without creating a second structure-generation contract.

Content-authoring tools return stable validation findings and `materialization_allowed` rather than hidden chain-of-thought. See `MINECRAFT_CONTENT_API_TOOLS.md` for the version, composition, and registry-confidence contract.

## Provider extension points

Call `cap.register_generator(provider)` to add a provider whose aliases can be selected by `generation.kind`. `structure_type` remains a semantic artifact classification and does not have to equal the provider alias. See `GENERATOR_PROVIDER_REGISTRY.md`.

A downstream repository can add:

- structure-type generators and procedural authors;
- legacy 1.12 palette/block-state materialization;
- schematic/WorldEdit/Litematica adapters;
- jigsaw pool compilers;
- culture/faction theme packs;
- purpose and real-world precedent libraries;
- site/biome/terrain samplers;
- preview renderers and fixed-camera reviews;
- runtime placement validators;
- advanced loot/progression/evidence validators and functions;
- loader/mod-specific recipe serializer providers;
- command/function version-matrix providers;
- authored icon/texture providers.

Keep project-specific identities and content outside the generic core whenever possible.
