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
| E01-014 | Lower Paleolithic / Early Human | **Catalog label not yet materialized in authoritative repository** | NEXT | — | — | — |

## Last completed run

**E01-013 — Large-Carcass Processing Site**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-013_LARGE_CARCASS_PROCESSING_SITE.md`.

The specification defines one dominant megafaunal carcass axis, coordinated multi-person task bays, heavy-bone/marrow work, directional dirty-side discard, clean-side transport staging, an outward haul corridor, hide/offcut handling, biome and culture variants, condition states, semantic vanilla material proxies, additive family rules, the mandatory 500-block unrelated-structure exclusion rule, sparse occupancy/loot hooks, validation criteria, and production-readiness gates. It explicitly separates E01-013 from E01-012 by requiring a larger operational landscape and coordinated multi-bay topology rather than merely scaling ordinary butchery.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_large_carcass_processing.py`.

The deterministic generator provides:
- S/M/L envelopes of 43×8×35, 57×9×47, and 73×10×61;
- seed-derived carcass orientation with elongated spine and widened torso cells;
- 3–9 scale-dependent task bays distributed on both flanks;
- mandatory heavy-bone/marrow processing zone;
- anisotropic dirty-side bone/refuse projection;
- opposite-side clean transport staging;
- an edge-reaching haul corridor that clears conflicting discard;
- peripheral hide/offcut and scavenger traces;
- culture profiles for cooperative disarticulation, marrow intensity, transport priority, and hide retention;
- active/recent/repeated/abandoned/weathered/scavenger-reworked/sediment-reworked/repurposed conditions;
- optional subordinate hearth logic;
- deterministic fingerprints, explicit material semantics, and archetype qualification gates.

Focused test source: `tests/test_early_human_large_carcass_processing.py` covers replay determinism, seed variation, S/M/L bounds, topology, culture hooks, condition variants, arid weathering, bounds, invalid inputs, additive compatibility, placement validity, and minimum 500-block structure/jigsaw protection.

Public export: `LargeCarcassProcessingSiteGenerator` and `LargeCarcassProcessingSiteGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`LargeCarcassProcessingSiteGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_carcass_processing`;
- structure ID `continuityworks:e01_013_large_carcass_processing_site`;
- start pool `continuityworks:early_human/e01_013_large_carcass_processing_site`;
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
E01-013 qualifies only when it reads as one coordinated large-carcass processing landscape: a dominant elongated carcass axis, multiple task bays, mandatory heavy-bone processing, substantial directional refuse, clean staging, and preserved haul circulation. It fails toward E01-012 if it drops back into the ordinary-carcass footprint/organization, toward a camp if hearth/residential logic dominates, or toward a knapping ground if lithic production becomes primary.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-013 is production-admitted.**

## Next run

Proceed with **E01-014**, the next catalog ID after E01-013. The archetype label for E01-014 is not presently materialized in the authoritative repository or retrieved persistent catalog material, so it must be resolved from the authoritative master catalog before hero development rather than invented.
