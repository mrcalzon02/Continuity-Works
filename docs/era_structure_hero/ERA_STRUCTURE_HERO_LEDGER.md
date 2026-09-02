# Era Structure Development Ledger

Authoritative sequence: Continuity Works era structure master catalog
Branch policy: `main` only
Development mode: complete each archetype through three ordered stages before advancing beyond an accumulated backlog.

## Three-stage contract

1. **Stage 1 — HERO SPEC**: complete and commit the hero-level production design.
2. **Stage 2 — BUILD**: implement a deterministic physical structure generator/template in the authoritative Continuity Works implementation and add focused tests.
3. **Stage 3 — WORLDGEN**: connect the built structure to the authoritative world-generation contract, including the minimum 500-block unrelated-structure exclusion/protection rule and explicit same-parent family exceptions only.

A structure is not `PRODUCTION_ADMITTED` merely because Stages 1–3 are represented in source. Production admission additionally requires observed executable validation, target materialization/load evidence where applicable, deterministic replay evidence, compatibility validation, and any archetype-specific visual/runtime gates.

## Backlog gate

The accumulated Stage 2/3 backlog from E01-001 through E01-009 is now cleared at the source-integration level. All nine have deterministic build source, focused test source, and authoritative worldgen contracts committed on `main`. Runtime execution/materialization validation remains pending, so none is promoted beyond `VALIDATION_PENDING` without additional evidence.

Stage 1 catalog development may now resume at E01-010.

## Status legend

- `HERO_SPEC_COMPLETE` — Stage 1 completed and committed.
- `BUILD_COMPLETE_SOURCE` — Stage 2 implementation and tests committed; executable validation still requires observed test evidence.
- `WORLDGEN_CONTRACT_INTEGRATED` — Stage 3 worldgen placement/protection contract committed; target runtime/load validation may still be pending.
- `VALIDATION_PENDING` — source stages are complete, but production admission evidence is not yet complete.
- `PRODUCTION_ADMITTED` — implementation, deterministic validation, compatibility validation, target load/export evidence, and required visual/runtime gates have all passed.

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
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | NEXT | — | — | — |

## Last completed implementation run

**E01-009 — Stone Tool Knapping Ground**

### Stage 1
Already complete under `docs/era_structure_hero/E01-009_STONE_TOOL_KNAPPING_GROUND.md`.

### Stage 2 source implementation
Committed implementation in `src/structure_capability/early_human_knapping_ground.py` includes:
- S/M/L open-worksite footprints with work intensity scaling instead of building mass;
- deterministic parent-context and raw-material provenance classification;
- local, transported, and mixed toolstone palette states;
- irregular stable work-position placement;
- testing, primary-reduction, secondary-shaping, maintenance, and mixed-sequence reduction profiles;
- anisotropic debris fans derived from deterministic worker-facing vectors;
- raw-material staging, hammerstone placement, active/rejected core proxies, and debris/discard fields;
- explicit dense-sharp hazard cells;
- cleared circulation routes that exclude dense hazard cells;
- repeated-use/partially-buried/disturbed/source-depleted legacy reduction lenses;
- condition-loss handling without erasing the underlying reduction topology;
- qualification gates requiring lithic-production primacy, directional debris, explicit provenance, hammerstones, safe circulation, no architectural dependence, and era-valid technology;
- deterministic physical fingerprints;
- bounded additive/non-destructive replacement metadata;
- explicit shared-parent-reservation requirement for compatible family composition.

Focused tests in `tests/test_early_human_knapping_ground.py` cover deterministic replay, seed variation, S/M/L bounds, production identity, directional debris, circulation/hazard separation, repeated-use chronology, source-adjacent provenance, invalid inputs, 500-block worldgen protection, additive compatibility, and placement spacing.

The generator is exported through `structure_capability.__init__`.

### Stage 3 source integration
`StoneToolKnappingGroundGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_lithic_production`;
- structure ID `continuityworks:e01_009_stone_tool_knapping_ground`;
- start pool `continuityworks:early_human/e01_009_stone_tool_knapping_ground`;
- generation step `surface_structures`;
- `beard_thin` terrain adaptation;
- `WORLD_SURFACE_WG` projection;
- random-spread placement with separation below spacing;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw-piece protection;
- additive/non-destructive compatibility mode;
- same-parent-reservation requirement for compatible-family co-location;
- existing geospatial worldgen validation.

### Archetype distinction
E01-009 is admitted only when lithic reduction is the dominant spatial signal. Raw-material staging, work positions, directional debris, cores/hammerstones, hazard-aware circulation, and provenance must remain legible. Generic camp scatter or later workshop architecture does not qualify.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 2 generator source, focused tests, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-009 is production-admitted.**

## Completed Stage 2/3 backlog

- E01-001 — Rock Overhang Camp — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-002 — Cave Mouth Occupation — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-003 — Deep Cave Refuge — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-004 — Temporary Brush Shelter — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-005 — Lean-To Windbreak — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-006 — Hide Windbreak Camp — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-007 — Hearth Circle — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-008 — Multi-Hearth Gathering Site — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-009 — Stone Tool Knapping Ground — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING

## Next run

Resume Stage 1 hero development with **E01-010 — Flint Procurement Pit**. After its hero specification is committed, continue directly through Stage 2 build and Stage 3 worldgen integration before advancing to E01-011, unless a new backlog rule is explicitly established.
