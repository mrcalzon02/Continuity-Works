# Era Structure Development Ledger

Authoritative sequence: Continuity Works era structure master catalog
Branch policy: `main` only
Development mode: complete each archetype through three ordered stages before advancing.

## Three-stage contract

1. **Stage 1 — HERO SPEC**: complete and commit the hero-level production design.
2. **Stage 2 — BUILD**: implement deterministic physical generation/template source and focused tests.
3. **Stage 3 — WORLDGEN**: connect the structure to the authoritative world-generation contract, including the minimum 500-block unrelated-structure exclusion/protection rule and same-parent compatible-family exceptions only.

Source completion does not equal `PRODUCTION_ADMITTED`. Production admission additionally requires observed executable validation, deterministic replay evidence, target NBT/template-pool materialization/load evidence where applicable, compatibility validation, and required visual/runtime review.

## Current position

| Catalog | Era | Archetype | Stage 1 | Stage 2 | Stage 3 | Production |
|---|---|---|---|---|---|---|
| E01-001 | Lower Paleolithic / Early Human | Rock Overhang Camp | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-002 | Lower Paleolithic / Early Human | Cave Mouth Occupation | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-003 | Lower Paleolithic / Early Human | Deep Cave Refuge | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-004 | Lower Paleolithic / Early Human | Temporary Brush Shelter | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-005 | Lower Paleolithic / Early Human | Lean-To Windbreak | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-006 | Lower Paleolithic / Early Human | Hide Windbreak Camp | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-007 | Lower Paleolithic / Early Human | Hearth Circle | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-008 | Lower Paleolithic / Early Human | Multi-Hearth Gathering Site | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-009 | Lower Paleolithic / Early Human | Stone Tool Knapping Ground | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-011 | Lower Paleolithic / Early Human | Quartzite Quarry | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-012 | Lower Paleolithic / Early Human | Butchery Site | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-013 | Lower Paleolithic / Early Human | Large-Carcass Processing Site | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-014 | Lower Paleolithic / Early Human | Bone-Breaking Station | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-015 | Lower Paleolithic / Early Human | Marrow Processing Ground | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-016 | Lower Paleolithic / Early Human | Watering-Hole Camp | NEXT | — | — | — |

## Last completed run

**E01-015 — Marrow Processing Ground**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-015_MARROW_PROCESSING_GROUND.md`.

The specification defines a post-fracture marrow-extraction and consumption landscape with clean-side opened-bone staging, one or more marrow-handling pockets, adjacent activity stances, grease/organic ground lenses, spent-fragment margins, short circulation links, condition states, biome/culture hooks, semantic vanilla material proxies, additive family relationships, sparse loot/occupancy hooks, validation criteria, and production-readiness requirements.

Archetype distinction is explicit: E01-014 remains the high-energy bone-fracture workstation. E01-015 is organized around handling already-opened or easily opened bones, distributed marrow extraction/consumption, and low-energy spent-fragment disposal. Heavy percussion is absent or limited to one subordinate final-cracking point.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_marrow_processing.py`.

The deterministic generator provides:
- S/M/L envelopes of 19×6×17, 29×7×25, and 41×8×33;
- 1–5 scale/culture-dependent marrow-handling pockets;
- seed-derived clean-to-dirty orientation;
- clean-side opened-bone staging;
- pocket-local opened-bone and grease/stain concentrations;
- clear activity stances adjacent to handling pockets;
- dirty-side spent-fragment disposal;
- staging-to-pocket circulation paths plus a disposal path;
- culture profiles for immediate consumption, distributed extraction, intensive cleaning, and repeated use;
- active/recent/repeated/abandoned/weathered/scavenger-reworked/sediment-reworked/repurposed conditions;
- optional single light-percussion point and optional subordinate hearth;
- explicit semantic material roles, qualification gates, and deterministic fingerprints.

Focused test source: `tests/test_early_human_marrow_processing.py` covers deterministic replay, seed variation, S/M/L bounds, marrow-processing qualification, scale progression, percussion suppression, repeated-use behavior, arid weathering, invalid inputs, additive compatibility, spacing validity, and minimum 500-block structure/jigsaw protection.

Public export: `MarrowProcessingGroundGenerator` and `MarrowProcessingGroundGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`MarrowProcessingGroundGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_carcass_processing`;
- structure ID `continuityworks:e01_015_marrow_processing_ground`;
- start pool `continuityworks:early_human/e01_015_marrow_processing_ground`;
- `surface_structures` generation step;
- `beard_thin` terrain adaptation;
- `WORLD_SURFACE_WG` projection;
- valid random-spread spacing/separation;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw-piece protection;
- additive/non-destructive compatibility;
- same-parent-reservation requirement for compatible-family tight composition;
- existing geospatial worldgen validation.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-015 is production-admitted.**

## Next run

Proceed with **E01-016 — Watering-Hole Camp** through Stage 1 hero specification, Stage 2 build, and Stage 3 worldgen integration before advancing to E01-017 Riverbank Foraging Camp.
