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
| E01-002 | Lower Paleolithic / Early Human | Cave Mouth Occupation | HERO_SPEC_COMPLETE | NEXT | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-003 | Lower Paleolithic / Early Human | Deep Cave Refuge | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-004 | Lower Paleolithic / Early Human | Temporary Brush Shelter | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-005 | Lower Paleolithic / Early Human | Lean-To Windbreak | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-006 | Lower Paleolithic / Early Human | Hide Windbreak Camp | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-007 | Lower Paleolithic / Early Human | Hearth Circle | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-008 | Lower Paleolithic / Early Human | Multi-Hearth Gathering Site | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-009 | Lower Paleolithic / Early Human | Stone Tool Knapping Ground | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | QUEUED_AFTER_BACKLOG | — | — | — |

## Last completed implementation run

**E01-001 — Rock Overhang Camp**

### Stage 1
Already complete under `docs/era_structure_hero/E01-001_ROCK_OVERHANG_CAMP.md`.

### Stage 2 source implementation
Committed implementation now includes:
- public `EarlyHumanStructureGenerator` implementation in `src/structure_capability/early_human.py`;
- deterministic named random streams derived from seed + stream name;
- small, medium, and large physical output classes;
- terrain-first connected overhang/rear support mass rather than a freestanding roof;
- protected occupation floor and sparse approach apron;
- offset hearth placement;
- daylight-side work scatter using valid placeable-block proxies;
- climate-bounded bedding treatment;
- sheltered sleeping zone and lateral refuse edge;
- active/recent/abandoned/collapsed/buried condition handling;
- biome-family geological palettes;
- physical structure output in `{size, blocks, metadata}` form;
- deterministic structure fingerprint metadata;
- additive/non-destructive replacement metadata;
- focused unit tests in `tests/test_early_human.py` for determinism, seed variation, bounds, geology/hearth presence, arid palette restrictions, scale rejection, worldgen protection, and placement spacing.

The generator is exported from `structure_capability.__init__`.

### Stage 3 source integration
`EarlyHumanStructureGenerator.worldgen_bundle("E01-001")` now binds the structure to the existing Continuity Works Minecraft worldgen contract using:
- `jigsaw_structure(...)` placement metadata;
- `random_spread_structure_set(...)`;
- family identity `continuityworks:early_human_camp`;
- structure ID `continuityworks:e01_001_rock_overhang_camp`;
- start pool `continuityworks:early_human/e01_001_rock_overhang_camp`;
- minimum 500-block structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw piece protection;
- existing `validate_geospatial_worldgen(...)` checks.

### DEEFM claim boundary
Observed repository evidence proves the Stage 2 implementation source, test source, package export, and Stage 3 worldgen contract are committed on `main`. **No claim is made that the tests have executed successfully in the authoritative runtime, that a final binary NBT/template pool has been materialized and loaded by Minecraft, or that E01-001 is production-admitted.** Those require additional observed evidence.

## Previously completed Stage 1 specs

- E01-002 — Cave Mouth Occupation
- E01-003 — Deep Cave Refuge
- E01-004 — Temporary Brush Shelter
- E01-005 — Lean-To Windbreak
- E01-006 — Hide Windbreak Camp
- E01-007 — Hearth Circle
- E01-008 — Multi-Hearth Gathering Site
- E01-009 — Stone Tool Knapping Ground

## Authoritative catalog recovery

The previously unresolved E01-010 title is recoverable from the era structure master catalog in the originating planning conversation: **E01-010 — Flint Procurement Pit**. The following Lower Paleolithic sequence continues with E01-011 Quartzite Quarry, E01-012 Butchery Site, E01-013 Large-Carcass Processing Site, E01-014 Bone-Breaking Station, and onward. E01-010 is intentionally queued rather than started because the Stage 2/3 backlog gate now takes precedence.

## Next run

Build and worldgen-integrate **E01-002 — Cave Mouth Occupation**. Preserve its threshold/daylight/twilight identity and do not let its generator collapse into either E01-001 Rock Overhang Camp or E01-003 Deep Cave Refuge.
