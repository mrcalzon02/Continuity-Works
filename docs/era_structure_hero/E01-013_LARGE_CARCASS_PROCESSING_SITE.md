# E01-013 — Large-Carcass Processing Site

Status: **HERO_SPEC_COMPLETE**
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_carcass_processing`

## Purpose and archetype identity

E01-013 represents the processing landscape created when a single very large animal carcass requires coordinated, multi-person disarticulation, meat removal, marrow access, hide handling, and staged transport. Its hero identity is not "E01-012 but larger." The carcass itself creates a dominant long axis; work is divided into several simultaneous task bays; heavy-bone processing and refuse occupy substantial dirty-side space; clean transport staging and haul circulation remain legible on the opposite side.

The site must read first as a cooperative megafaunal-processing operation. It fails archetype qualification if it reads as a camp, a generic refuse scatter, a lithic workshop, several unrelated ordinary butchery sites, or a permanent building.

## Historical and technological context

The technological ceiling is Lower Paleolithic: expedient flakes and cores, simple cutting edges, hammerstones, anvils, direct percussion for joint separation and marrow access, manual dragging/carrying, hide removal, and opportunistic fire. No metal, wheeled transport, constructed storage, formal roads, masonry architecture, dedicated smokehouse, or later-period specialist equipment is permitted.

The structure encodes logistical organization rather than unsupported claims about a particular hominin culture. Culture variants alter task emphasis and spatial choices without asserting a named archaeological population.

## Footprint and scale classes

- **Small:** 43×8×35 blocks. One large carcass, 3–4 coordinated task bays, compact heavy-bone zone, one staging apron.
- **Medium:** 57×9×47 blocks. One dominant carcass, 4–6 task bays, differentiated disarticulation and marrow zones, larger refuse fan, explicit haul lane.
- **Large:** 73×10×61 blocks. One very large carcass, 6–9 task bays, multiple heavy-bone stations, broad hide/offcut edge, high-volume discard and transport staging.

All scales intentionally exceed the E01-012 39×7×33 ceiling so silhouette and operational organization remain distinct.

## Architectural program and required components

This is an open task landscape rather than a building. Required components are:

1. **Dominant carcass axis** — one continuous, elongated primary carcass zone that establishes orientation.
2. **Disarticulation task bays** — multiple work positions distributed along both sides of the carcass axis.
3. **Heavy-bone / marrow zone** — hammerstone/anvil evidence and concentrated bone processing, mandatory at every scale.
4. **Dirty-side discard field** — anisotropic bone/offcut/refuse fan projected away from active work and transport circulation.
5. **Hide/offcut handling edge** — peripheral area separated from the clean staging side.
6. **Clean-side transport staging** — selected portions represented by semantic vanilla proxies, spatially separated from dirty refuse.
7. **Haul corridor** — continuous outward route from staging to a footprint edge; generated after discard so conflicts are cleared.
8. **Scavenger/peripheral trace band** — sparse edge evidence that can intensify in relevant condition states.
9. **Optional subordinate hearth** — permitted only as an accessory feature and never the organizing center.

No enclosed room, roof, wall perimeter, storage building, formal road, or residential sleeping program is required or allowed to dominate.

## Procedural generation logic

Generation is deterministic from world seed plus catalog ID and named random streams. A seed-derived carcass angle defines axial and perpendicular vectors. The generator lays one elongated carcass spine with widened torso cells, then allocates scale-dependent task bays along both flanks. Each bay receives tool/ground evidence and contributes an outward-biased discard vector.

A dedicated heavy-bone station is placed away from clean staging. Dirty-side discard uses directional projection rather than isotropic random scatter. Clean staging is deliberately biased to the opposite side of the carcass. A haul corridor is traced from staging to the nearest practical footprint edge and removes conflicting discard cells to preserve movement. Hide/offcut traces occupy a separate peripheral sector. Condition transforms occur only after the primary operational topology exists.

The generator must emit a deterministic fingerprint, explicit component metadata, semantic material roles, and qualification results.

## Biome and environmental adaptations

Supported biome families are temperate, boreal, tundra, savanna, arid, tropical, and coastal. Palette choices adapt surface traces to local ground and available stone proxies while preserving the same functional program. Wet/vegetated settings may develop moss/ground overprint when weathered; arid settings use dry mineral/sand proxies and must not acquire wet-biome mossing. Tundra favors stone/gravel preservation and pale hide proxies. Coastal variants remain terrestrial processing sites and do not become marine processing facilities.

Placement prefers broadly traversable surface terrain. The structure may blend with local surface height through the established worldgen contract but must not destructively flatten unrelated terrain or overwrite existing structures.

## Culture-variant hooks

- **cooperative_disarticulation** — emphasizes numerous balanced work bays and broad task distribution.
- **marrow_intensive** — increases heavy-bone/anvil evidence and fractured-bone scatter.
- **transport_priority** — expands clean staging and reinforces the haul corridor.
- **hide_retention** — expands peripheral hide/offcut handling while keeping processing primary.

Variants change emphasis, not technological era or fundamental archetype identity.

## Material palette logic

Only valid Minecraft blocks are emitted. Vanilla blocks are semantic visual proxies and must be described honestly in metadata: bone block = carcass/heavy-bone role; terracotta/coarse dirt = organic-processing stain role; carpet = hide/offcut role; stone/andesite/granite = tool/hammer/anvil role; gravel/stone = refuse role. A proxy is never claimed to be the literal archaeological material it represents.

## Condition variants

- **active** — maximum task readability; optional lit subordinate hearth.
- **recent** — fresh processing topology without active occupation.
- **repeated** — denser discard and additional fractured-bone evidence while retaining one primary carcass organization.
- **abandoned** — ephemeral hide traces heavily reduced.
- **weathered** — selective surface loss and climate-appropriate overprint.
- **scavenger_reworked** — some bone elements displaced toward the periphery without erasing the dominant axis.
- **sediment_reworked** — partial burial/ground replacement while core geometry remains recoverable.
- **repurposed** — later use may add sparse secondary task traces but may not convert the generator into a settlement archetype.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_013_large_carcass_processing_site`
Start pool: `continuityworks:early_human/e01_013_large_carcass_processing_site`
Family: `continuityworks:early_human_carcass_processing`

Compatibility is additive and non-destructive. E01-013 may compose with a compatible carcass-processing family piece only when both are owned by the same parent reservation/assembly. Family membership never waives protection for unrelated structures. The default minimum unrelated-structure exclusion radius and per-jigsaw-piece protection radius are **500 blocks**.

## Infrastructure dependencies

No constructed infrastructure is required. The operational dependencies are a surface task area, room for an outward haul route, and sufficient local clearance for the carcass/process footprint. The structure must not require roads, villages, buildings, or replacement of another mod's content.

## Loot and occupancy hooks

Loot, if materialized later, must be sparse and task-specific: simple stone cutting tools, hammerstone proxies, small bone/food traces, and limited portable materials. No treasure economy is appropriate. Occupancy hooks represent a temporary cooperative processing group rather than permanent residents. Hostile/scavenger occupancy may be condition-driven but must not be mandatory to identify the structure.

## Validation criteria

A generated instance passes source qualification only when all of the following are true:

- exactly one dominant primary carcass axis is present and sufficiently elongated;
- at least 3 task bays exist and scale increases their count;
- heavy-bone/marrow processing evidence exists at every scale;
- dirty discard is directional and substantial;
- clean staging exists away from the principal dirty field;
- a continuous haul corridor reaches the footprint boundary and remains substantially clear of discard;
- hide/offcut handling is present but subordinate to carcass processing;
- any hearth is subordinate;
- no permanent architecture is generated;
- the footprint exceeds the E01-012 ordinary-butchery scale ceiling;
- all blocks remain inside declared bounds;
- identical inputs replay identically and changed seeds can alter layout;
- worldgen validation passes spacing/separation and the 500-block structure/jigsaw protection requirements;
- compatibility remains additive/non-destructive and same-parent-only for family composition.

## Production-readiness requirements

`HERO_SPEC_COMPLETE`, `BUILD_COMPLETE_SOURCE`, and `WORLDGEN_CONTRACT_INTEGRATED` are repository-source milestones only. `PRODUCTION_ADMITTED` additionally requires observed executable tests, deterministic replay evidence in the target runtime, materialized Minecraft NBT/template-pool assets where required, successful datapack/mod load, actual new-world placement verification, exclusion/family compatibility checks, and visual/runtime review confirming the site reads as a coordinated large-carcass processing landscape.

Until those observations exist, production status remains `VALIDATION_PENDING`.
