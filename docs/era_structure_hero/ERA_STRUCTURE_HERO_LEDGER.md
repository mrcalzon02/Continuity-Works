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
| E01-004 | Lower Paleolithic / Early Human | Temporary Brush Shelter | HERO_SPEC_COMPLETE | BUILD_COMPLETE_SOURCE | WORLDGEN_CONTRACT_INTEGRATED | VALIDATION_PENDING |
| E01-005 | Lower Paleolithic / Early Human | Lean-To Windbreak | HERO_SPEC_COMPLETE | NEXT | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-006 | Lower Paleolithic / Early Human | Hide Windbreak Camp | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-007 | Lower Paleolithic / Early Human | Hearth Circle | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-008 | Lower Paleolithic / Early Human | Multi-Hearth Gathering Site | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-009 | Lower Paleolithic / Early Human | Stone Tool Knapping Ground | HERO_SPEC_COMPLETE | IMPLEMENTATION_PENDING | WORLDGEN_PENDING | IMPLEMENTATION_PENDING |
| E01-010 | Lower Paleolithic / Early Human | Flint Procurement Pit | QUEUED_AFTER_BACKLOG | — | — | — |

## Last completed implementation run

**E01-004 — Temporary Brush Shelter**

### Stage 1
Already complete under `docs/era_structure_hero/E01-004_TEMPORARY_BRUSH_SHELTER.md`.

### Stage 2 source implementation
Committed implementation in `src/structure_capability/early_human_brush_shelter.py` includes:
- deterministic S/M/L ephemeral shelter generation;
- named frame, brush-skin, occupancy, and condition random streams;
- climate-adapted rib/brush/floor material palettes using placeable vanilla blocks;
- irregular rear anchor row and short bent/leaned support ribs;
- intentionally incomplete roof reach rather than a closed shell;
- patchy brush infill with a hard below-75% coverage qualification gate;
- explicit open side, entry, sheltered lee pocket, and rest-zone anchor;
- optional exterior-biased hearth rather than hearth-centered identity;
- sparse short-term occupational traces;
- active/recent/abandoned/weathered/collapsed/overgrown/repurposed condition behavior;
- explicit qualification fields requiring partial enclosure, incomplete roof, non-planar-wall identity, sub-full brush coverage, and ephemeral material logic;
- deterministic fingerprinting and bounded additive/non-destructive replacement metadata.

The generator is exported through `structure_capability.__init__`. Focused tests in `tests/test_early_human_brush_shelter.py` cover deterministic replay, seed variation, S/M/L bounds, archetype qualification, arid material restrictions, progressive weathering/collapse, invalid scale rejection, surface worldgen anchoring, 500-block protection, and spacing validity.

### Stage 3 source integration
`TemporaryBrushShelterGenerator.worldgen_bundle()` uses the existing Continuity Works Minecraft worldgen contract with:
- family `continuityworks:early_human_ephemeral_shelter`;
- structure ID `continuityworks:e01_004_temporary_brush_shelter`;
- start pool `continuityworks:early_human/e01_004_temporary_brush_shelter`;
- generation step `surface_structures`;
- `beard_thin` terrain adaptation;
- `WORLD_SURFACE_WG` heightmap projection;
- random-spread placement with separation lower than spacing;
- minimum 500-block unrelated-structure exclusion radius;
- minimum 500-block per-jigsaw-piece exclusion radius;
- mandatory jigsaw piece protection;
- existing geospatial worldgen validation;
- explicit terrain-responsive/non-destructive placement contract.

### Archetype distinction
E01-004 is structurally prevented from becoming E01-005: it cannot close its perimeter, complete a roof, or resolve into a dominant planar wall. It remains a lightweight, irregular, partly skinned shelter with a lee pocket rather than a directional windbreak surface.

### DEEFM claim boundary
Observed GitHub evidence proves the Stage 2 generator source, package export, focused test source, Stage 3 worldgen contract, and ledger update are committed on authoritative `main`. **No claim is made that the tests have executed successfully in the authoritative runtime, that final NBT/template-pool artifacts have been materialized and loaded in Minecraft, or that E01-004 is production-admitted.**

## Previously completed backlog items

- E01-001 — Rock Overhang Camp — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-002 — Cave Mouth Occupation — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING
- E01-003 — Deep Cave Refuge — BUILD_COMPLETE_SOURCE / WORLDGEN_CONTRACT_INTEGRATED / VALIDATION_PENDING

## Queued Stage 1 continuation

E01-010 — Flint Procurement Pit remains queued until E01-001 through E01-009 clear the Stage 2/3 backlog.

## Next run

Build and worldgen-integrate **E01-005 — Lean-To Windbreak**. Preserve its directional wind-blocking plane, clear windward/leeward logic, minimal overhead cover, and strict distinction from E01-004 Temporary Brush Shelter and E01-006 Hide Windbreak Camp.
