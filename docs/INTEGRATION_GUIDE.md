# GitHub / External Project Integration

## As a library

Add this repository as a normal Python dependency (Git URL, submodule, vendored package, or published package). Import `StructureCapability`.

## As a sidecar API

Run the bundled HTTP server beside a generator, agent, Codex workflow, CI job, or game-tooling process. Other languages can call the `/v1/*` JSON endpoints.

## As an AI tool provider

Use `GET /v1/tools` or `structure-capability tools` to retrieve the portable function catalog. Keep the tool names stable and route all mutations through the same Python API rather than building a second AI-only generation implementation.

## As a GitHub-referenced capability

Recommended repository policy:

1. pin a release/tag or commit;
2. inventory the consuming project before generation;
3. submit structure requests as JSON;
4. preserve snapshots and generated artifact hashes;
5. require repository-specific mechanical/runtime validators before promotion;
6. require independent visual review before declaring visual completion;
7. keep project-specific cultures, purposes, factions, loot, quests and world selectors in the consuming repository.

## Project adapter contract

A consuming project should provide or extend:

- authoritative structure inventory;
- mod/registry inventory;
- purpose/theme profiles;
- geospatial/worldgen selectors;
- format adapters where native NBT is insufficient;
- detailed architectural authoring providers;
- render/review workflow;
- runtime placement validation;
- promotion gates.

The generic core should not contain project-specific faction names or quest IDs.

## Dungeon / procedural extension

The built-in modular dungeon generator is intentionally a reusable spatial engine. Consumers may supply custom `purpose_constraints`, required zones, theme profiles, scale envelopes, modularity rules, and final palettes without modifying the generator itself.

For commercial-capable integrations, keep the isolated donjon CC BY-NC reference outside the runtime path unless the project has independently resolved the license implications.

## CI

The included workflow runs unit tests and compilation. Add project-specific materialization, target-version, registry-integrity, in-game placement, FTB/quest detection, loot/evidence, and fixed-camera review jobs in consuming repositories as needed.
