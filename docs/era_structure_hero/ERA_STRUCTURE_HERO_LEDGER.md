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
| E01-011 | Lower Paleolithic / Early Human | Quartzite Quarry | NEXT | — | — | — |

## Last completed run

**E01-010 — Flint Procurement Pit**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-010_FLINT_PROCUREMENT_PIT.md`.

The specification defines:
- extraction-first purpose and strict distinction from E01-009 Stone Tool Knapping Ground and E01-011 Quartzite Quarry;
- Lower Paleolithic shallow-procurement technology ceiling;
- S/M/L footprint, pit-count, and depth classes;
- source exposure, overburden removal, procurement pits, working faces, spoil aprons, rejected/tested nodules, selected-material staging, carry-out, safe circulation, and legacy pit program;
- deterministic source-lens, pit, spoil, testing, staging, circulation, chronology, condition, biome, culture, and material logic;
- active, recently vacated, repeated-use, abandoned, partially infilled, disturbed, source-depleted, and later-repurposed conditions;
- compatible lithic-source/camp/travel/knapping family hooks under one shared parent reservation only;
- sparse task-specific loot/occupancy hooks;
- validation and production-readiness gates;
- minimum 500-block unrelated-structure exclusion and additive/non-destructive compatibility.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_flint_procurement.py`.

The deterministic generator provides:
- S/M/L physical output;
- near-surface source-lens generation;
- 1–9 irregular shallow procurement pits by scale;
- explicit depth caps of 2/3/4 blocks for S/M/L;
- source exposure within pit footprints;
- lateral/down-gradient spoil projection;
- sparse tested/rejected material deliberately below knapping-ground dominance;
- selected-material staging and a carry-out route;
- repeated-use/partial-infill/source-depletion chronology;
- biome-adapted local substrate/source/spoil palettes using valid vanilla blocks;
- deterministic fingerprint metadata;
- bounded additive/non-destructive replacement metadata;
- qualification gates for extraction primacy, explicit source, shallow open pits, spoil, carry-out, staging, subordinate testing, open-sky geometry, and absence of later mining infrastructure.

Focused test source: `tests/test_early_human_flint_procurement.py` covers deterministic replay, seed variation, S/M/L bounds, procurement identity, shallow depth caps, subordinate testing, repeated-use chronology, arid material restrictions, invalid inputs, worldgen protection, additive compatibility, and placement spacing.

Public export: `FlintProcurementPitGenerator` and `FlintProcurementPitGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`FlintProcurementPitGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_lithic_source`;
- structure ID `continuityworks:e01_010_flint_procurement_pit`;
- start pool `continuityworks:early_human/e01_010_flint_procurement_pit`;
- `surface_structures` generation step;
- `beard_thin` terrain adaptation;
- `WORLD_SURFACE_WG` projection;
- valid random-spread spacing/separation;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw-piece protection;
- additive/non-destructive compatibility;
- same-parent-reservation requirement for compatible-family composition;
- existing geospatial worldgen validation.

### Archetype distinction
E01-010 qualifies only when source procurement dominates. Its shallow open pits, spoil, source exposure, staging, and carry-out must read before any testing debris. It fails toward E01-009 if lithic reduction/debris becomes primary, and fails toward E01-011 if organized large-scale quarry faces/terraces or later quarry infrastructure become dominant.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-010 is production-admitted.**

## Next run

Proceed with **E01-011 — Quartzite Quarry** through Stage 1 hero specification, Stage 2 deterministic build, and Stage 3 worldgen integration before advancing to E01-012.
