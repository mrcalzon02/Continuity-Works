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

The catalog currently has a Stage 2/3 backlog from E01-001 through E01-009. **Do not create additional Stage 1 hero specifications until that backlog is built and worldgen-integrated in sequence.** Work E01-001 → E01-009 through Stage 2 and Stage 3 first. After the backlog clears, resume Stage 1 at E01-010.

## Status legend

- `HERO_SPEC_COMPLETE` — Stage 1 completed and committed.
- `BUILD_COMPLETE_SOURCE` — Stage 2 implementation and tests committed; executable validation still requires observed test evidence.
- `WORLDGEN_CONTRACT_INTEGRATED` — Stage 3 worldgen placement/protection contract committed; target runtime/load validation may still be pending.
- `IMPLEMENTATION_PENDING` — Stage 2 has not yet been completed.
- `WORLDGEN_PENDING` — Stage 3 has not yet been completed.
- `PRODUCTION_ADMITTED` — implementation, deterministic validation, compatibility validation, target load/export evidence, and required visual/runtime gates have all passed.

## Current position

| Catalog | Era | Archetype | Stage 1 | Stage 2 | Stage 3 | Production |
|---|---|---|---|---|---|---|
| E01-001 | Lower Paleolithic / Early Human | Rock Overhang Camp | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-002 | Lower Paleolithic / Early Human | Cave Mouth Occupation | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-003 | Lower Paleolithic / Early Human | Deep Cave Refuge | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-004 | Lower Paleolithic / Early Human | Temporary Brush Shelter | HERO_SPEC_COMPLETE | NEXT | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-005 | Lower Paleolithic / Early Human | Lean-To Windbreak | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-006 | Lower Paleolithic / Early Human | Hide Windbreak Camp | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-007 | Lower Paleolithic / Early Human | Hearth Circle | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-008 | Lower Paleolithic / Early Human | Multi-Hearth Gathering Site | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-009 | Lower Paleolithic / Early Human | Stone Tool Knapping Ground | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | QUEUED_AFTER_BACKLOG | — | — | — |

## Last completed implementation run

**E01-003 — Deep Cave Refuge**

### Stage 1
Already complete under `docs/era_structure_hero/E01-003_DEEP_CAVE_REFUGE.md`.

### Stage 2 source implementation
Committed implementation in `src/structure_capability/early_human_deep_cave.py` includes:
- deterministic S/M/L deep-cave refuge generation;
- named topology, route, refuge, occupation, ventilation, and condition random streams;
- explicit daylight-loss boundary;
- long winding access route with deterministic turn count and route-complexity scoring;
- primitive repeated wayfinding markers distributed along the access route;
- enlarged refuge chamber beyond the daylight-loss and route-complexity thresholds;
- ventilation classification (`restricted`, `moderate`, `drafted`);
- hearth suppression under restricted ventilation rather than unconditional deep-cave fire;
- refuge, rest, and cache anchors;
- biome-family geological/floor palette adaptation;
- active/recent/repeated/abandoned/collapsed/flooded/animal-reoccupied condition behavior;
- explicit qualification gates for daylight loss, minimum route length, route complexity, and refuge depth;
- deterministic physical structure fingerprint;
- bounded additive/non-destructive replacement metadata.

The generator is exported through `structure_capability.__init__`. Focused tests in `tests/test_early_human_deep_cave.py` cover deterministic replay, seed variation, S/M/L bounds, deep-refuge qualification, distinction from threshold occupation, ventilation/hearth suppression, invalid-scale rejection, underground placement behavior, 500-block protection, and spacing validity.

### Stage 3 source integration
`DeepCaveRefugeGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_cave_complex`;
- structure ID `continuityworks:e01_003_deep_cave_refuge`;
- start pool `continuityworks:early_human/e01_003_deep_cave_refuge`;
- generation step `underground_structures`;
- `bury` terrain adaptation;
- no surface heightmap projection;
- default absolute subterranean anchor Y = -24;
- random-spread placement with separation lower than spacing;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw piece protection;
- existing geospatial worldgen validation.

### Archetype distinction
E01-003 is not a deeper copy of E01-002. E01-002 terminates its primary occupation at an explicit daylight/twilight interior stop-line. E01-003 instead requires daylight loss, a substantial access route, nontrivial route complexity, primitive wayfinding evidence, ventilation classification, and a refuge chamber beyond those thresholds before it qualifies as this archetype.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 2 generator source, package export, focused test source, and Stage 3 worldgen contract are committed on authoritative `main`. **No claim is made that the tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-003 is production-admitted.**

## Previously completed backlog items

- E01-001 — Rock Overhang Camp — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-002 — Cave Mouth Occupation — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING

## Queued Stage 1 continuation

E01-010 — Flint Procurement Pit remains queued until E01-001 through E01-009 clear the Stage 2/3 backlog.

## Next run

Build and worldgen-integrate **E01-004 — Temporary Brush Shelter**. Preserve its lightweight ephemeral plant-material construction, temporary occupancy, incomplete enclosure, terrain-responsive anchoring, and strict distinction from E01-005 Lean-To Windbreak and later enclosed hut/tent archetypes.
