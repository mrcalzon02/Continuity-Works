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
| E01-013 | Lower Paleolithic / Early Human | Large-Carcass Processing Site | NEXT | — | — | — |

## Last completed run

**E01-012 — Butchery Site**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-012_BUTCHERY_SITE.md`.

The specification defines:
- task-specific ordinary-carcass processing identity and strict separation from camps, generic refuse scatters, and E01-013 Large-Carcass Processing Site;
- Lower Paleolithic direct-percussion, stone-tool, hammerstone/anvil, marrow-access, hide-removal, and opportunistic-fire technology ceiling;
- S/M/L envelopes of 17×5×15, 27×6×23, and 39×7×33;
- primary carcass-processing center, anatomically biased work positions, directional bone/offcut discard, marrow/anvil zone, hide/offcut edge, selected transport staging, circulation, and carry-out route;
- biome adaptations and culture hooks for expedient field dressing, transport focus, marrow intensity, and consumption bias;
- active, recent, repeated, abandoned, weathered, scavenger-reworked, sediment-reworked, and repurposed conditions;
- vanilla block proxy semantics explicitly recorded rather than misrepresented as literal archaeological materials;
- additive same-parent family composition and the minimum 500-block unrelated-structure exclusion rule;
- sparse task-specific loot/occupancy hooks;
- validation and production-readiness gates.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_butchery_site.py`.

The deterministic generator provides:
- seed-derived carcass orientation and non-rectilinear central processing footprint;
- 1–7 work positions depending on scale;
- directional discard fans projected away from worker positions rather than isotropic random debris;
- medium/large marrow/anvil evidence with culture-driven intensification;
- selected transport staging placed away from the dirty core;
- an outward carry route that clears conflicting discard cells to preserve circulation;
- peripheral hide/offcut traces;
- optional subordinate hearth association;
- culture-profile variants for expedient field dressing, transport focus, marrow intensity, and consumption bias;
- condition transforms for repeated use, abandonment/weathering, scavenger reworking, and sediment reworking;
- deterministic fingerprints and explicit material-role semantics;
- qualification gates requiring processing center, work positions, directional discard, staging, carry route, circulation, scale-appropriate marrow evidence, subordinate hearth, no permanent architecture, and sub-E01-013 scale.

Focused test source: `tests/test_early_human_butchery_site.py` covers deterministic replay, seed variation, S/M/L bounds, processing qualification, marrow requirements, culture hooks, arid weathering restrictions, scavenger-reworked survival, invalid inputs, additive worldgen protection, and placement validity.

Public export: `ButcherySiteGenerator` and `ButcherySiteGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`ButcherySiteGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_carcass_processing`;
- structure ID `continuityworks:e01_012_butchery_site`;
- start pool `continuityworks:early_human/e01_012_butchery_site`;
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
E01-012 qualifies only when the site reads first as carcass processing: a dominant processing center, nearby worker/tool positions, directional discard, selected transport staging, and a carry route. It fails toward a generic camp if hearth/shelter logic dominates, toward a knapping ground if lithic production dominates, and toward E01-013 if the footprint and biomass organization exceed the ordinary-carcass scale ceiling.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-012 is production-admitted.**

## Next run

Proceed with **E01-013 — Large-Carcass Processing Site** through Stage 1 hero specification, Stage 2 deterministic build, and Stage 3 worldgen integration before advancing to E01-014.
