# E01-017 — Riverbank Foraging Camp

Status: **HERO_SPEC_COMPLETE**
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_water_access`

## Purpose and archetype identity

E01-017 represents a temporary or repeatedly reused camp organized along a riverbank where people collect, sort, process, consume, and stage portable riparian resources. Its primary spatial signal is **linear water-edge use**: a flowing-water margin, dry setback activity terrace, several return paths from distinct foraging patches, compact processing loci, a clear water-access lane, and dry-side refuse. It is not a generic waterside camp.

The site must read first as a river-linear foraging and light-processing landscape. It fails qualification if it reads as E01-016 Watering-Hole Camp, a fishing village, engineered fishery, agricultural settlement, carcass-processing site, lithic workshop, or permanent riverside architecture.

## Historical and technological context

The technological ceiling is Lower Paleolithic. Permitted behaviors include hand gathering of edible plants, roots, seeds, shellfish or other accessible shoreline foods where locally plausible; simple pounding, cutting, scraping, rinsing, sorting, and immediate consumption; expedient flakes and hammerstones; carrying gathered material by hand; and opportunistic fire. No agriculture, irrigation, pottery, storage jars, fish traps, nets, boats, metal, formal docks, permanent drying racks, masonry, or later specialist processing equipment are required or generated.

The generator models functional constraints rather than assigning a named hominin population. Culture profiles alter gathering emphasis, return-path organization, camp duration, and processing intensity without changing the era.

## Footprint and scale classes

- **Small:** 29×8×25 blocks. Short river-edge segment, one dry activity terrace, 2 foraging-return paths, 1–2 processing pockets, one hearth/rest locus.
- **Medium:** 41×9×35 blocks. Longer riparian edge, 3 return paths, 2–3 processing pockets, separated staging and refuse sectors, clearer circulation.
- **Large:** 55×10×47 blocks. Broad linear river margin, 4–5 return paths, 3–5 processing pockets, repeated-use traces, multiple staging areas, and substantial dry-side refuse while remaining temporary and open.

Scale is expressed by river-edge length, number of foraging-return paths, and number of processing/staging loci—not by permanent construction.

## Architectural program and required components

This is an open task landscape. Required components are:

1. **Linear river margin** — an elongated flowing-water proxy and irregular bank, not a bounded pond.
2. **Dry setback terrace** — stable activity ground parallel to but separated from the wet margin.
3. **Water-access lane** — direct clear route from terrace to the river edge.
4. **Foraging-return paths** — at least two distinct routes entering the terrace from riverbank/resource sectors.
5. **Gathered-resource staging** — compact clean-side clusters near processing pockets.
6. **Processing pockets** — pounding/cutting/sorting loci with simple tool and ground-disturbance evidence.
7. **Rest/hearth locus** — subordinate social/rest area on dry ground.
8. **Dry-side refuse margin** — discarded shells/bones/plant-processing proxies away from water access and clean staging.
9. **Optional temporary windbreak traces** — sparse and non-enclosing.
10. **Optional opportunistic animal/aquatic traces** — subordinate to foraging identity.

No formal rooms, roofs, dock, bridge, boat, fish weir, agricultural plot, storage building, or permanent perimeter is permitted.

## Procedural generation logic

Generation is deterministic from world seed plus catalog ID and named random streams. A seed-derived river axis defines an elongated water strip with controlled lateral meander. The dry-bank normal establishes a setback terrace parallel to the river. Scale determines river-edge length, terrace radius, processing-pocket count, and return-path count.

Foraging-return anchors are distributed along the river margin and connected to the dry terrace by short clear paths. Gathered-resource staging is placed between return paths and processing pockets. Each processing pocket receives a compact ground-disturbance lens plus sparse tool/food proxies and an adjacent clear stance. A water-access lane is generated independently so gathering paths cannot erase direct drinking/rinsing access. Dry refuse projects away from the river and main approach. Condition transforms occur after core topology qualifies, then critical circulation is restored.

The generator must emit deterministic fingerprints, explicit component metadata, material semantics, qualification results, and worldgen protection metadata.

## Biome and environmental adaptations

Supported biome families are temperate, boreal, tundra, savanna, arid, tropical, and coastal-transition river mouths.

- **Temperate:** dirt/coarse dirt banks, oak riparian traces, mixed gravel.
- **Boreal:** podzol/coarse dirt, spruce traces, stony banks.
- **Tundra:** gravel/stone banks, sparse vegetation, no wet-biome moss assumption.
- **Savanna:** coarse dirt, acacia/dead vegetation traces, seasonal-bank dryness.
- **Arid:** narrow river ribbon with sand/red-sand banks and concentrated green-edge proxies; water remains river-linear rather than becoming an oasis pond.
- **Tropical:** rooted dirt/dirt, jungle vegetation traces, stronger flood-overprint in degraded states.
- **Coastal transition:** gravel/sand/cobblestone near river mouth while retaining freshwater-river geometry.

Placement prefers traversable river-adjacent surface terrain. Terrain adaptation must remain bounded and non-destructive; the generator does not replace the biome's actual river system or flatten unrelated terrain.

## Culture-variant hooks

- **broad_spectrum_foraging** — balanced plant/shoreline collection and multiple return paths.
- **root_seed_processing** — strengthens pounding/tool evidence and dry processing pockets.
- **shoreline_gathering** — increases bank-edge collection anchors and compact staging close to water.
- **repeated_return** — denser hearth, stain, path, and refuse traces while remaining temporary.

Profiles change emphasis, not technological era or archetype identity.

## Material palette logic

Only valid Minecraft blocks are emitted, with semantic proxy roles documented honestly:

- **River-margin proxy**: water;
- **Bank and activity-ground roles**: dirt/coarse dirt/podzol/sand/gravel/stone;
- **Gathered/riparian vegetation role**: short grass/fern/dead bush or biome-appropriate leaves;
- melon/pumpkin seeds are not placed as blocks; gathered-food evidence uses valid ground/vegetation proxies rather than invented literal crops;
- **Expedient tool/pounding role**: stone/andesite/granite/cobblestone;
- **Mixed food-processing/refuse role**: bone block/gravel where appropriate;
- **Subordinate hearth role**: campfire/coal block.

No proxy is claimed to be a literal archaeological material beyond its declared visual/functional role.

## Condition variants

- **active** — clear paths/staging/processing, lit subordinate hearth.
- **recent** — readable topology without active occupancy.
- **repeated** — stronger path wear, hearth traces, processing stains, and refuse.
- **abandoned** — reduced staging clarity; durable circulation and refuse remain.
- **weathered** — selective surface loss and biome-appropriate vegetation overprint.
- **flood_reworked** — bankward sediment disturbance and displaced light debris while terrace topology remains recoverable.
- **sediment_reworked** — partial burial of processing/refuse signatures.
- **repurposed** — sparse later task traces may overlay without replacing river-foraging identity.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_017_riverbank_foraging_camp`
Start pool: `continuityworks:early_human/e01_017_riverbank_foraging_camp`
Family: `continuityworks:early_human_water_access`

E01-017 may compose with E01-016 or later compatible water-access pieces only when they belong to the same parent reservation/assembly. Family membership alone never waives exclusion. Independent instances use the Continuity Works minimum **500-block unrelated-structure exclusion radius** and **500-block per-jigsaw-piece protection radius**.

Compatibility is additive and non-destructive. The structure may add registrations or family links but must never replace another mod's rivers, structures, roads, settlements, or generation system.

## Infrastructure dependencies

No constructed infrastructure is required. Functional dependencies are a river-adjacent surface position, a dry setback area, room for return paths and refuse, and stable direct access to the bank. Worldgen may align the template with existing river terrain but must not manufacture a replacement river corridor across unrelated terrain.

## Loot and occupancy hooks

Loot is sparse and task-specific: simple stone flakes/hammerstones, small food proxies, bone/shell-like semantic traces where appropriate, and limited portable material. No treasure cache or formal storage economy is appropriate.

Occupancy represents a temporary foraging party. Passive animal or scavenger hooks may vary by condition/biome. No permanent residents or village population are required.

## Validation criteria

A generated instance passes source qualification only when:

- river geometry is elongated/linear rather than pond-like;
- one dry setback terrace exists outside the water cells;
- a clear terrace-to-water access lane reaches the river margin;
- at least two distinct foraging-return paths exist;
- staging and at least one processing pocket exist on dry ground;
- each processing pocket has adjacent clear activity ground;
- refuse is biased to the dry side and does not dominate water access;
- hearth/rest logic is subordinate to foraging/processing topology;
- no engineered fishery, agriculture, dock, bridge, boat, or permanent architecture is generated;
- all blocks remain inside declared bounds;
- identical inputs replay identically and changed seeds can alter layout;
- S/M/L scales increase river-edge length and return/processing counts;
- worldgen spacing/separation passes validation;
- structure and jigsaw-piece exclusion radii remain at least 500 blocks;
- compatible tight composition requires the same parent reservation/assembly;
- compatibility remains additive and non-destructive.

## Production-readiness requirements

`HERO_SPEC_COMPLETE`, `BUILD_COMPLETE_SOURCE`, and `WORLDGEN_CONTRACT_INTEGRATED` are source milestones only. `PRODUCTION_ADMITTED` additionally requires observed executable tests, deterministic replay in the target runtime, materialized Minecraft NBT/template-pool assets where applicable, successful datapack/mod load, fresh-world river placement evidence, family/exclusion validation, and visual/runtime review confirming the site reads as a linear riverbank foraging camp rather than a watering-hole camp or permanent fishery.

Until those observations exist, production status remains `VALIDATION_PENDING`.
