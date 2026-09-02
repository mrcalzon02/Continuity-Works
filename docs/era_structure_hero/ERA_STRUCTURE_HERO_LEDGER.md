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
| E01-015 | Lower Paleolithic / Early Human | Marrow Processing Ground | NEXT | — | — | — |

## Last completed run

**E01-014 — Bone-Breaking Station**

### Catalog recovery
The prior ledger had lost the E01-014 label. Reconciliation against the authoritative era structure master catalog recovered E01-014 as **Bone-Breaking Station** and E01-015 as **Marrow Processing Ground**. The recovered catalog labels are now materialized here so later sessions do not repeat the false blocker.

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-014_BONE_BREAKING_STATION.md`.

The specification defines a concentrated heavy-bone percussion and marrow-access station with clean-side heavy-bone staging, mandatory anvil/impact points, hammerstone evidence, cleared operator stances, anisotropic fracture fans, marrow handling, spent-bone discard, carry lanes, biome and culture hooks, condition states, semantic vanilla proxies, additive family rules, sparse loot/occupancy hooks, validation criteria, and production-readiness gates.

Archetype distinction is explicit: E01-014 processes already-separated heavy bones. It does not generate a dominant carcass axis, broad hide-processing program, hearth-centered camp topology, or primary lithic-production landscape.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_bone_breaking.py`.

The deterministic generator provides:
- S/M/L envelopes of 17×6×15, 25×7×21, and 35×8×29;
- 1–5 scale/culture-dependent impact stations;
- explicit clean and dirty directional vectors;
- heavy-bone staging on the clean/incoming side;
- stable anvil/impact and hammerstone proxies;
- cleared operator stances;
- anisotropic fracture fans projected to the dirty side;
- marrow-handling pocket and spent-bone discard margin;
- staging-to-impact carry lane;
- culture profiles for marrow intensity, single-station reuse, distributed percussion, and clean staging priority;
- active/recent/repeated/abandoned/weathered/scavenger-reworked/sediment-reworked/repurposed conditions;
- optional subordinate hearth logic;
- explicit material semantics, qualification gates, and deterministic fingerprints.

Focused test source: `tests/test_early_human_bone_breaking.py` covers deterministic replay, seed variation, S/M/L bounds, qualification topology, scale progression, culture variants, arid weathering, invalid inputs, additive compatibility, spacing validity, and minimum 500-block structure/jigsaw protection.

Public export: `BoneBreakingStationGenerator` and `BoneBreakingStationGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`BoneBreakingStationGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_carcass_processing`;
- structure ID `continuityworks:e01_014_bone_breaking_station`;
- start pool `continuityworks:early_human/e01_014_bone_breaking_station`;
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
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, and this ledger update are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-014 is production-admitted.**

## Next run

Proceed with **E01-015 — Marrow Processing Ground** through Stage 1 hero specification, Stage 2 build, and Stage 3 worldgen integration before advancing to E01-016 Food Cache Pit.
