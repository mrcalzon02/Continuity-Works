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
| E01-016 | Lower Paleolithic / Early Human | Watering-Hole Camp | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-017 | Lower Paleolithic / Early Human | Riverbank Foraging Camp | NEXT | — | — | — |

## Last completed run

**E01-016 — Watering-Hole Camp**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-016_WATERING_HOLE_CAMP.md`.

The specification defines a temporary/repeated camp organized around a bounded freshwater margin: dry setback terrace, water-access lane, external dry approach, hearth/rest zone, temporary windbreak traces, light activity, dry-side refuse, animal spoor/trample cues, biome/culture variants, condition states, additive family relationships, sparse loot/occupancy hooks, validation criteria, and production-readiness gates.

Archetype distinction is explicit: E01-016 is a camp organized around a standing or slow-refresh watering place. It does not become an engineered reservoir, river-linear foraging site, generic dry-land hearth camp, or carcass-processing landscape.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_watering_hole.py`.

The deterministic generator provides:
- S/M/L envelopes of 31×8×27, 43×9×37, and 57×10×49;
- seed-derived water-facing/dry-side orientation;
- bounded irregular freshwater-margin and bank proxies;
- arid reduction of water footprint;
- dry camp terrace with scale/culture-dependent setback;
- terrace-to-water access lane and separate external approach lane;
- subordinate hearth/rest zone and temporary windbreak traces;
- light tool/activity evidence;
- dry-side refuse projection;
- separate animal spoor/trample sector;
- optional medium/large carcass-opportunism traces that remain subordinate;
- active/recent/repeated/abandoned/weathered/flood-reworked/scavenger-reworked/repurposed conditions;
- post-transform restoration of critical circulation;
- explicit semantic material roles, qualification gates, and deterministic fingerprints.

Focused test source: `tests/test_early_human_watering_hole.py` covers deterministic replay, seed variation, S/M/L bounds, watering-hole qualification, arid water reduction/no-moss behavior, cautious-observation setback/spoor behavior, subordinate carcass opportunism, invalid inputs, additive compatibility, spacing validity, and minimum 500-block structure/jigsaw protection.

Public export: `WateringHoleCampGenerator` and `WateringHoleCampGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`WateringHoleCampGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_water_access`;
- structure ID `continuityworks:e01_016_watering_hole_camp`;
- start pool `continuityworks:early_human/e01_016_watering_hole_camp`;
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
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that the new focused tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-016 is production-admitted.**

## Next run

Proceed with **E01-017 — Riverbank Foraging Camp** through Stage 1 hero specification, Stage 2 build, and Stage 3 worldgen integration unless a higher-priority defect or user-visible repair supersedes it.
