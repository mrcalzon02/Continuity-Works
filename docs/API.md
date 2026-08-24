# API Reference

## `StructureCapability(project_root, state_root=None)`

### `.capabilities()`
Returns the stable API version, supported lifecycle operations, rebuild grades, procedural-generation features, Minecraft version policy, and review requirements.

### `.tools()`
Returns the portable JSON-Schema AI function/tool catalog used by `GET /v1/tools`.

### `.inventory_project()`
Returns discovered local mods, namespaces and explicit registry inventory hash.

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

### `.minecraft_version(version)`
Resolves known target-version metadata and compatibility features. The resolver refuses to invent exact DataVersion values for unknown patch versions.

### `.resume(snapshot_id)`
Loads the persisted snapshot manifest.

## HTTP

Run:

```bash
python -m structure_capability.cli serve --project /path/to/project
```

Endpoints:

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

## AI tool catalog

`GET /v1/tools` returns function definitions with inline JSON Schema parameters. This is intentionally transport-neutral: an OpenAI-style function caller, a local orchestration agent, a GitHub automation, or another API client can adapt the same catalog without creating a second structure-generation contract.

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
- loot/progression/evidence validators.

Keep project-specific identities and content outside the generic core whenever possible.
