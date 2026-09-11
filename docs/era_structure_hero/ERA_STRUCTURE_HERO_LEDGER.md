# Era Structure Development Ledger

Authoritative sequence: materialized catalog identities recorded in this ledger; the canonical source catalog is not currently present in the repository
Branch policy: `main` only
Development mode: complete each archetype through three ordered stages before advancing.

## Catalog authority provenance

The current repository and its accessible Git history do not contain a standalone era structure master-catalog artifact that can be read back as present-day authority. Do not cite an unavailable catalog file as though it were retrievable repository evidence, and do not infer a missing label from neighboring archetypes.

Known recovered labels are authoritative only where they have been materialized into tracked project state with reproducible Git provenance. Commit `bcbb6ad2c10395a3b4f8ca17d794d0247a95990d` corrected the previously stale sequence and materialized E01-014 as **Bone-Breaking Station**, E01-015 as **Marrow Processing Ground**, and E01-016 as **Watering-Hole Camp**. That recovery explicitly replaced an incorrect successor label and therefore cannot be extrapolated to later catalog IDs. E01-017 is independently materialized by its committed hero specification, generator, tests, worldgen contract, and ledger transition culminating in commit `6b8556b2103b39c9811afbd45e76667199b01143`.

E01-018 remains unresolved. It may advance only when one of these reproducible authority forms supplies its exact canonical label: a recovered catalog artifact with provenance, an existing commit/file/blob that explicitly names E01-018, or a user-supplied authoritative catalog source. Repository searches, neighboring sequence patterns, obsolete labels, and conversational guesses are insufficient. Until one of those authorities exists, E01-018 stays blocked rather than being invented.

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
| E01-017 | Lower Paleolithic / Early Human | Riverbank Foraging Camp | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-018 | Lower Paleolithic / Early Human | **Catalog label not yet materialized in authoritative repository** | NEXT | — | — | — |

## Last completed run

**E01-017 — Riverbank Foraging Camp**

### Stage 1 — HERO SPEC
Committed specification: `docs/era_structure_hero/E01-017_RIVERBANK_FORAGING_CAMP.md`.

The specification defines an ephemeral or repeatedly reused camp organized along a linear river margin rather than a bounded watering place. Required topology includes a dry setback terrace, direct water-access lane, multiple foraging-return paths, gathered-resource staging, compact processing pockets with adjacent activity stances, subordinate hearth/rest logic, dry-side refuse, biome/culture variants, condition states, additive family relationships, sparse loot/occupancy hooks, validation criteria, and production-readiness gates.

Archetype distinction is explicit: E01-017 is organized around river-linear gathering and light processing. It does not become E01-016 Watering-Hole Camp, an engineered fishery, agricultural settlement, dock/boat site, generic hearth camp, or permanent riverside architecture.

### Stage 2 — BUILD
Committed implementation: `src/structure_capability/early_human_riverbank_foraging.py`.

The deterministic generator provides:
- S/M/L envelopes of 29×8×25, 41×9×35, and 55×10×47;
- seed-derived river-axis and dry-bank orientation;
- elongated controlled-meander river margins with biome-sensitive width;
- dry setback terrace parallel to the river;
- independent terrace-to-water access lane;
- 2–5 scale/culture-dependent foraging-return paths from bank anchors;
- 1–5 processing pockets with gathered-resource staging and clear activity stances;
- subordinate hearth/rest and temporary windbreak traces;
- dry-side refuse projection;
- broad-spectrum, root/seed-processing, shoreline-gathering, and repeated-return culture profiles;
- active/recent/repeated/abandoned/weathered/flood-reworked/sediment-reworked/repurposed conditions;
- post-transform restoration of critical circulation;
- explicit semantic material roles, qualification gates, and deterministic fingerprints.

Focused test source: `tests/test_early_human_riverbank_foraging.py` covers deterministic replay, seed variation, S/M/L bounds, linear-river qualification, scale progression, culture behavior, arid/no-moss behavior, flood-reworked preservation, invalid inputs, additive compatibility, spacing validity, and minimum 500-block structure/jigsaw protection.

Public export: `RiverbankForagingCampGenerator` and `RiverbankForagingCampGenerationError` are exported through `structure_capability.__init__`.

### Stage 3 — WORLDGEN
`RiverbankForagingCampGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_water_access`;
- structure ID `continuityworks:e01_017_riverbank_foraging_camp`;
- start pool `continuityworks:early_human/e01_017_riverbank_foraging_camp`;
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

### Validation repair and observed verification
The first authoritative validation run after Stage 3 exposed three E01-017 failures. The common root cause was the river-linearity qualification: diagonal rivers were measured with axis-aligned X/Z bounding boxes, causing genuinely elongated river ribbons to appear too wide.

Committed repair: `9513491b6e04da994f5330cda198db19b04694ad` (`Fix E01-017 river-axis linearity qualification`). The qualification now projects generated water cells onto the generator's river axis and perpendicular dry-bank axis before comparing major and minor spans.

Observed validation on that repair commit:
- Python installation and compile completed successfully;
- source-tree agent discovery completed successfully;
- full unit/API-contract/PUBLIC_SERVICEABILITY test step completed successfully;
- Continuity Works frontend build completed successfully;
- zero-JavaScript Pages discovery candidate stamping completed successfully;
- local executable API and public-boundary smoke completed successfully;
- `continuity-works/validate` published `success` for the repair commit.

This closes the source-level E01-017 regression introduced during this run. It does **not** establish final Minecraft production admission.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 1 hero specification, Stage 2 generator source, focused test source, public export, Stage 3 worldgen contract, the river-axis qualification repair, successful repository validation on repair commit `9513491b6e04da994f5330cda198db19b04694ad`, and this ledger update are on authoritative `main`. **No claim is made that final Minecraft NBT/template-pool artifacts have been materialized and loaded in Minecraft, that fresh-world river placement has been accepted, that visual/runtime review has passed, or that E01-017 is production-admitted.**

## Next run

Attempt E01-018 recovery only from the explicit authority forms defined above. Do not repeatedly treat the same repository search as new evidence and do not infer the label from sequence adjacency. If no qualifying catalog authority is available, keep E01-018 blocked and select the next dependency-valid repository-owned repair or validation gap rather than fabricating a catalog identity.
