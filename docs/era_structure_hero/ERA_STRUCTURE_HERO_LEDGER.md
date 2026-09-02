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
| E01-012 | Lower Paleolithic / Early Human | Butchery Site | NEXT | — | — | — |

## Last completed run

**E01-011 — Quartzite Quarry**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-011_QUARTZITE_QUARRY.md`.

The specification defines:
- extraction-first quarry identity and strict boundaries against E01-010 Flint Procurement Pit and E01-009 Stone Tool Knapping Ground;
- Lower Paleolithic direct-percussion, hard-hammer, natural-joint, levering, and gravity technology ceiling;
- S/M/L footprint classes with increasing working-face, bench, spoil, staging, and chronology complexity;
- natural source exposure, working face, natural bench/work footing, extraction scars, coarse fragment apron, hammerstone zone, subordinate primary reduction, selected blank staging, haul route, and legacy exhausted face;
- deterministic named procedural streams;
- biome and culture variants bounded by era technology;
- active, recently vacated, repeated-use, abandoned, partially collapsed, sediment-reworked, source-depleted, and repurposed conditions;
- additive family composition under one explicit parent reservation only;
- sparse task-specific loot/occupancy hooks;
- validation and production-readiness gates;
- minimum 500-block unrelated-structure exclusion.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_quartzite_quarry.py`.

The deterministic generator provides:
- S/M/L physical output envelopes of 23×8×19, 37×10×31, and 57×12×45;
- elongated source ridge/outcrop generation with deterministic strike and accessible working side;
- 1–7 irregular face segments by scale;
- bounded extraction scars carved into selected source-face cells;
- natural bench/work footing immediately outside active faces;
- anisotropic coarse fragment/spoil apron projected outward from the quarry face;
- sparse hammerstone/battering proxies;
- subordinate primary-reduction clusters only at medium/large scale;
- selected quartzite-role blank staging and an outward haul route;
- legacy/exhausted face chronology for repeated/source-depleted/repurposed conditions;
- partial collapse, sediment reworking, and climate-bounded weathering transforms;
- `minecraft:diorite` as an explicit semantic `quartzite_role_proxy`, avoiding manufactured quartz blocks and avoiding a false vanilla-geology claim;
- deterministic structure fingerprint metadata;
- bounded additive/non-destructive replacement policy;
- qualification gates for extraction primacy, source face, scars, bench, coarse apron, hammerstone zone, staging, haul route, subordinate reduction, larger-than-procurement scale, open sky, and absence of later quarry infrastructure.

Focused test source: `tests/test_early_human_quartzite_quarry.py` covers deterministic replay, seed variation, S/M/L bounds, extraction-first qualification, semantic quartzite proxy policy, source-depleted chronology, arid weathering restrictions, invalid inputs, worldgen protection/additive compatibility, and placement contract validity.

Public export: `QuartziteQuarryGenerator` and `QuartziteQuarryGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`QuartziteQuarryGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_lithic_source`;
- structure ID `continuityworks:e01_011_quartzite_quarry`;
- start pool `continuityworks:early_human/e01_011_quartzite_quarry`;
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
E01-011 qualifies only when a recognizable source face, extraction scars, natural bench, heavy coarse apron, selected blank staging, and haul route dominate the site. It fails toward E01-010 if shallow isolated procurement pits dominate without a quarry face, and fails toward E01-009 if reduction debris/work positions become the primary read. Engineered or industrial quarry systems are anachronistic and invalid.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-011 is production-admitted.**

## Next run

Proceed with **E01-012 — Butchery Site** through Stage 1 hero specification, Stage 2 deterministic build, and Stage 3 worldgen integration before advancing to E01-013.
