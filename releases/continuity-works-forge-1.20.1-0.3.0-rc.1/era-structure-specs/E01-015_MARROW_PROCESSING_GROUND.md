# E01-015 — Marrow Processing Ground

Status: **HERO_SPEC_COMPLETE**
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_carcass_processing`

## Purpose and archetype identity

E01-015 represents an open processing ground where already-opened or easily opened bones are handled for marrow extraction, immediate consumption, fragment sorting, and discard. Its defining archaeological and procedural signal is not a dominant impact station but a distributed set of marrow-handling loci: opened-bone clusters, working/seated pockets, grease-rich ground disturbance, clean incoming-bone staging, and spent-fragment margins connected by short carry paths.

The site must read first as a post-fracture marrow-processing and consumption landscape. It fails qualification if it reads as E01-014 Bone-Breaking Station, E01-012 Butchery Site, E01-013 Large-Carcass Processing Site, a generic hearth camp, a stone-tool workshop, or a refuse dump.

## Historical and technological context

The technological ceiling is Lower Paleolithic. Permitted behaviors include transport of separated or previously fractured bones, limited final cracking with expedient hammerstones, manual marrow extraction, scraping or picking marrow from opened shafts, immediate consumption, simple sorting of usable fragments, and opportunistic fire nearby. The site does not require containers, boiling, pottery, rendered-fat technology, metal tools, constructed tables, permanent storage, or later specialist equipment.

The design is deliberately behavior-first and does not assign the structure to a named hominin population. Culture hooks alter intensity, spatial concentration, consumption behavior, and reuse without changing the technological era.

## Footprint and scale classes

- **Small:** 19×6×17 blocks. One main marrow-handling pocket, one clean staging cluster, one spent-fragment edge, one short carry path.
- **Medium:** 29×7×25 blocks. Two to three marrow-handling pockets, expanded opened-bone scatter, differentiated clean/dirty sides, multiple activity stances, and a clear disposal margin.
- **Large:** 41×8×33 blocks. Three to five handling pockets, broad opened-bone field, multiple short circulation links, repeated-use grease/stain lenses, and substantial spent-fragment disposal while remaining smaller and less carcass-oriented than E01-013.

Scale is expressed through the number and persistence of marrow-handling loci rather than a larger carcass or stronger fracture workstation.

## Architectural program and required components

This is an open task landscape rather than a building. Required components are:

1. **Incoming opened-bone staging** — clean-side cluster of transported or previously fractured bones.
2. **Marrow-handling pockets** — one or more compact loci where opened bones are processed and consumed.
3. **Activity stances** — clear adjacent ground for seated/crouched processing positions.
4. **Opened-bone scatter** — dense but low-energy bone distribution near handling pockets.
5. **Grease/organic ground lenses** — semantic stain proxies around repeated extraction/consumption areas.
6. **Spent-fragment margin** — dirty-side discard of depleted shafts and fragments.
7. **Short carry/circulation paths** — staging-to-handling and handling-to-discard links kept substantially clear.
8. **Optional light percussion point** — at most one small final-cracking station, subordinate to marrow handling.
9. **Optional subordinate hearth** — may support warmth/immediate consumption but cannot organize the site.

No dominant carcass axis, hide yard, extensive disarticulation field, dense knapping fan, enclosure, roof, formal storage, or constructed infrastructure is allowed to dominate.

## Procedural generation logic

Generation is deterministic from seed plus catalog ID and named random streams. A seed-derived clean-to-dirty orientation establishes staging and discard sides. Scale determines the number of marrow-handling pockets. Pockets are placed around the center with enough separation to preserve distinct activity stances and circulation.

Incoming opened-bone staging is placed up-gradient on the clean side. Each handling pocket receives opened-bone proxies, ground-stain/grease traces, and a clear adjacent stance. Spent fragments are projected toward the dirty side in broader low-energy fans than E01-014 fracture debris. Short carry paths are traced from staging to handling pockets and from handling pockets toward discard; these paths clear conflicting loose fragments.

A light final-cracking point may appear in some variants but is strictly capped so E01-014 remains the high-energy fracture archetype. Condition transforms occur after the primary topology has qualified. The generator emits explicit component metadata, semantic material roles, qualification results, and a deterministic fingerprint.

## Biome and environmental adaptations

Supported biome families are temperate, boreal, tundra, savanna, arid, tropical, and coastal. Functional topology remains constant while ground and weathering proxies adapt.

- **Temperate:** coarse dirt, stone/andesite, gravel, moderate organic stain.
- **Boreal:** podzol/stone, gravel, limited moss overprint only in degraded states.
- **Tundra:** gravel/stone, pale dry palette, no wet-biome mossing.
- **Savanna:** coarse dirt/granite, dry red-brown stain roles.
- **Arid:** sand/red sand/stone with no moss or moisture-rich overprint.
- **Tropical:** dirt/rooted dirt/andesite with stronger degraded organic overprint.
- **Coastal:** gravel/sand/cobblestone mixture while remaining a terrestrial marrow-processing ground.

Placement prefers stable, traversable surface terrain. Adaptation must remain bounded and additive rather than flattening unrelated terrain or replacing external structures.

## Culture-variant hooks

- **immediate_consumption** — concentrates opened-bone and stain traces close to compact activity pockets.
- **distributed_extraction** — maximizes the number of distinct handling pockets across the footprint.
- **intensive_cleaning** — increases scraped/opened-bone evidence and reduces large spent fragments near active stances.
- **repeated_use** — emphasizes overlapping grease/stain lenses and persistent disposal margins.

Culture profiles modify emphasis and spatial organization without introducing later technologies.

## Material palette logic

Only valid Minecraft block IDs may be emitted, with semantic roles documented explicitly:

- `minecraft:bone_block` = opened/spent heavy-bone proxy;
- stone/andesite/granite/cobblestone = occasional light percussion/tool proxy;
- gravel = small spent-fragment/debris proxy;
- coarse dirt/red terracotta/red sand/rooted dirt = organic/grease ground-disturbance proxy;
- coal block/campfire = optional subordinate hearth trace only.

No semantic proxy is represented as a literal archaeological material beyond its declared visual/function role.

## Condition variants

- **active** — staging, handling pockets, and circulation are clear; optional subordinate fire may be lit.
- **recent** — strong marrow-processing topology without active fire.
- **repeated** — denser overlapping stain lenses and disposal margins, with circulation still legible.
- **abandoned** — staging clarity diminishes while handling/discard signatures remain.
- **weathered** — selective loss and biome-appropriate surface overprint.
- **scavenger_reworked** — spent bone is displaced outward without erasing the central handling pattern.
- **sediment_reworked** — partial burial while several handling pockets remain recoverable.
- **repurposed** — sparse later task traces may overlay the site without replacing its marrow-processing identity.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_015_marrow_processing_ground`
Start pool: `continuityworks:early_human/e01_015_marrow_processing_ground`
Family: `continuityworks:early_human_carcass_processing`

E01-015 may compose near E01-012, E01-013, or E01-014 only as an explicit same-parent family component owned by the same reservation/assembly. Family identity alone never waives exclusion. Independent instances observe the Continuity Works minimum **500-block unrelated-structure exclusion radius** and minimum **500-block per-jigsaw-piece protection radius**.

Compatibility is additive and non-destructive. E01-015 may add to compatible generation tables but must not replace, suppress, or destructively mutate another mod's structure or worldgen system.

## Infrastructure dependencies

No constructed infrastructure is required. Functional dependencies are a source of opened/separated bones, stable working ground, room for short clean-to-dirty circulation, and enough peripheral area for spent-fragment disposal.

The structure may be family-attached to a carcass-processing landscape or exist independently as transported-bone processing evidence.

## Loot and occupancy hooks

Loot hooks are deliberately sparse: simple stone flakes or hammerstone proxies, small bone/food traces, and limited portable material. No formal chest room, treasure cache, or permanent storage economy is appropriate.

Occupancy represents one or several temporary processors. Scavenger occupancy may be enabled in abandoned/reworked states. Occupancy is not required for visual qualification.

## Validation criteria

A generated instance passes source qualification only when:

- at least one marrow-handling pocket exists;
- incoming opened-bone staging exists on the clean side;
- each primary handling pocket has an adjacent activity stance;
- opened-bone and grease/stain evidence is concentrated around handling pockets;
- a spent-fragment margin exists on the dirty side;
- at least one staging-to-handling circulation path remains substantially clear;
- heavy percussion is absent or strictly subordinate;
- no dominant carcass axis exists;
- no broad hide/disarticulation program dominates;
- no hearth organizes the site;
- no permanent architecture is generated;
- all blocks remain inside declared bounds;
- identical inputs replay identically and changed seeds can alter layout;
- S/M/L scales increase handling-pocket count and/or repeated-use density without becoming E01-014;
- worldgen spacing/separation validation passes;
- structure and jigsaw-piece exclusion radii remain at least 500 blocks;
- compatible tight composition requires the same parent reservation/assembly;
- compatibility remains additive and non-destructive.

## Production-readiness requirements

`HERO_SPEC_COMPLETE`, `BUILD_COMPLETE_SOURCE`, and `WORLDGEN_CONTRACT_INTEGRATED` are repository-source milestones only. `PRODUCTION_ADMITTED` additionally requires observed executable tests, deterministic replay evidence in the target runtime, materialized Minecraft NBT/template-pool assets where required, successful datapack/mod load, fresh-world placement validation, exclusion/family compatibility tests, and visual/runtime review confirming that the structure reads as distributed marrow extraction/consumption rather than a bone-breaking station or generic butchery site.

Until those observations exist, production status remains `VALIDATION_PENDING`.
