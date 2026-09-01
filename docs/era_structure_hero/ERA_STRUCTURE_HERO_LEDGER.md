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
| E01-003 | Lower Paleolithic / Early Human | Deep Cave Refuge | HERO_SPEC_COMPLETE | NEXT | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-004 | Lower Paleolithic / Early Human | Temporary Brush Shelter | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-005 | Lower Paleolithic / Early Human | Lean-To Windbreak | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-006 | Lower Paleolithic / Early Human | Hide Windbreak Camp | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-007 | Lower Paleolithic / Early Human | Hearth Circle | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-008 | Lower Paleolithic / Early Human | Multi-Hearth Gathering Site | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-009 | Lower Paleolithic / Early Human | Stone Tool Knapping Ground | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | QUEUED_AFTER_BACKLOG | — | — | — |

## Last completed implementation run

**E01-002 — Cave Mouth Occupation**

### Stage 1
Already complete under `docs/era_structure_hero/E01-002_CAVE_MOUTH_OCCUPATION.md`.

### Stage 2 source implementation
Committed implementation in `src/structure_capability/early_human.py` now includes:
- archetype registration for `E01-002` with structure ID `continuityworks:e01_002_cave_mouth_occupation`;
- S/M/L cave-mouth dimensions;
- deterministic cave-candidate, mouth-topology, occupation, hearth, and condition streams;
- natural cave chamber geometry with a real mouth aperture and terrain-first rock mass;
- sparse exterior approach/threshold compaction;
- explicit daylight band, twilight band, and interior stop-line metadata;
- daylight-biased work scatter;
- ventilation-proxy hearth placement kept near the entrance zone;
- sheltered rest and cache anchors constrained before the interior stop-line;
- lateral/exterior refuse placement rather than deep-cave dumping;
- active/recent/repeated/abandoned/collapsed/silted/animal-reoccupied condition handling;
- biome-family palette logic and arid bedding restriction;
- deterministic physical structure fingerprint;
- bounded additive/non-destructive replacement policy metadata.

Focused tests in `tests/test_early_human.py` cover deterministic replay, seed variation, S/M/L bounds, threshold identity, interior stop-line enforcement, arid material restrictions, worldgen protection, and spacing validity.

### Stage 3 source integration
`EarlyHumanStructureGenerator.worldgen_bundle("E01-002")` now uses:
- family `continuityworks:early_human_cave_complex`;
- structure ID `continuityworks:e01_002_cave_mouth_occupation`;
- start pool `continuityworks:early_human/e01_002_cave_mouth_occupation`;
- surface-anchored jigsaw placement with `bury` terrain adaptation so the mouth remains the world-placement anchor;
- random-spread placement with separation lower than spacing;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw piece protection;
- existing geospatial worldgen validation.

### Archetype distinction
E01-002 remains distinct from E01-001 because occupation occurs inside a bounded cave threshold rather than beneath an exterior overhang. It remains distinct from E01-003 because the work, hearth, rest, and cache anchors are constrained to the daylight/twilight envelope at or before an explicit interior stop-line.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 2 generator source, focused tests, and Stage 3 worldgen contract are committed on authoritative `main`. **No claim is made that tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-002 is production-admitted.**

## Previously completed backlog items

- E01-001 — Rock Overhang Camp — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING

## Queued Stage 1 continuation

E01-010 — Flint Procurement Pit remains queued until E01-001 through E01-009 clear the Stage 2/3 backlog.

## Next run

Build and worldgen-integrate **E01-003 — Deep Cave Refuge**. Its implementation must be topology-driven and genuinely deep-subterranean: daylight-loss qualification, route complexity, primitive wayfinding, ventilation classification, and refuge-zone behavior must distinguish it from merely extending E01-002 farther inward.
