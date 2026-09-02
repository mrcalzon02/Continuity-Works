# E01-014 — Bone-Breaking Station

Status: **HERO_SPEC_COMPLETE**
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_carcass_processing`

## Purpose and archetype identity

E01-014 represents a concentrated station where already-separated large bones are deliberately fractured to access marrow and recover usable fragments. Its defining spatial signal is a repeated relationship between heavy-bone staging, impact/anvil points, dense fractured-bone scatter, and a cleared working stance. The station is a secondary processing landscape: carcass disarticulation has already occurred elsewhere or is subordinate.

The site must read first as a heavy percussion and marrow-extraction station. It fails qualification if it reads as an ordinary butchery site, a large-carcass processing landscape, a stone-tool knapping ground, a generic refuse scatter, a hearth-centered camp, or permanent architecture.

## Historical and technological context

The technological ceiling is Lower Paleolithic. Permitted behaviors include transport of separated limb bones, placement against stable stone or ground anvils, repeated hammerstone percussion, marrow extraction, grease-rich discard, expedient use of sharp bone fragments, and occasional nearby fire. No metal tools, saws, formal butcher blocks, masonry workstations, storage buildings, carts, constructed drainage, or later specialist processing equipment are permitted.

The structure encodes the mechanical requirements of heavy-bone processing rather than assigning a named archaeological culture. Culture hooks alter intensity, staging, and reuse patterns without changing the era.

## Footprint and scale classes

- **Small:** 17×6×15 blocks. One principal anvil/impact station, one bone staging cluster, one fracture fan, one operator stance.
- **Medium:** 25×7×21 blocks. Two to three impact stations, differentiated incoming-bone staging, dense fracture field, multiple operator stances, limited marrow discard separation.
- **Large:** 35×8×29 blocks. Three to five impact stations, broad heavy-bone staging, overlapping fracture lenses, explicit clean incoming-bone lane, dirty fracture/refuse side, and repeated-use chronology.

The footprint is intentionally smaller than E01-012/E01-013 carcass-processing landscapes because E01-014 processes selected bones rather than whole carcasses. Density of fractured material, not footprint alone, communicates scale.

## Architectural program and required components

This is an open task station, not a building. Required components are:

1. **Heavy-bone staging zone** — incoming long-bone elements placed before percussion.
2. **Primary impact/anvil point** — mandatory stable stone/anvil proxy with surrounding impact evidence.
3. **Hammerstone cluster** — one or more heavy percussion tools represented with valid stone block proxies.
4. **Operator stance** — a relatively clear area immediately adjacent to the impact point.
5. **Fracture fan** — anisotropic concentration of bone and gravel fragments projected away from the operator stance.
6. **Marrow extraction pocket** — secondary clean-side zone where opened bones are temporarily handled.
7. **Spent-bone discard margin** — lower-value fragments moved away from the active impact zone.
8. **Approach/carry lane** — short clear route connecting incoming bone staging to the workstation.
9. **Optional subordinate hearth** — permitted only as a secondary feature for immediate consumption/warmth and never as the spatial organizer.

No carcass axis, hide-processing yard, residential sleeping program, roof, enclosure, formal table, or road is required.

## Procedural generation logic

Generation is deterministic from seed plus catalog ID and named random streams. The generator first establishes an impact orientation and clean/dirty sides. One or more impact stations are placed with enough separation to preserve operator stances. Heavy-bone staging is biased to the clean/incoming side. Each impact station receives a hammerstone/anvil signature, then projects a fracture fan along the dirty vector.

Fracture intensity scales with site size and condition. Large and repeated-use variants may overlap old fracture lenses, but active operator stances and carry lanes remain partially cleared. Marrow handling occupies a smaller clean-side pocket between staging and the main impact area. Condition transforms are applied only after the primary functional topology has qualified.

The generator must emit explicit metadata for impact stations, staging, stance cells, fracture cells, carry lane, culture profile, condition, material semantics, qualification results, and deterministic fingerprint.

## Biome and environmental adaptations

Supported biome families are temperate, boreal, tundra, savanna, arid, tropical, and coastal. The functional program remains unchanged while ground and stone proxies adapt to local material context.

- Temperate: coarse dirt, andesite/stone, gravel.
- Boreal: podzol/stone, gravel, limited moss weathering only in degraded states.
- Tundra: gravel/stone, pale mineral palette, no wet-biome mossing.
- Savanna: coarse dirt/granite, dry fracture apron.
- Arid: sand/red sand/stone; no moss or moisture-rich surface treatment.
- Tropical: dirt/rooted dirt/andesite with stronger organic overprint in weathered states.
- Coastal: gravel/stone/sand mixtures while remaining a terrestrial heavy-bone station.

Placement prefers firm, reasonably level ground able to support repeated percussion. Terrain integration must remain bounded and additive rather than flattening unrelated terrain.

## Culture-variant hooks

- **marrow_intensive** — increases impact count, opened-bone scatter, and concentrated fracture density.
- **single_station_reuse** — favors one heavily reused impact point with layered debris lenses.
- **distributed_percussion** — favors several smaller stations and broader work-area spread.
- **clean_staging_priority** — enlarges incoming-bone staging and carry-lane clarity.

Culture profiles change organization and intensity only; they do not add later technologies.

## Material palette logic

All emitted blocks must be valid Minecraft block IDs. Semantic proxies are explicitly documented:

- `minecraft:bone_block` = heavy-bone / fractured-bone role;
- stone/andesite/granite/cobblestone = anvil or hammerstone role;
- gravel = small fracture/debris role;
- coarse dirt/red terracotta/red sand/rooted dirt = processing stain/ground-disturbance role;
- coal block/campfire = optional hearth trace only.

No proxy is claimed to be a literal archaeological material beyond its declared visual/functional role.

## Condition variants

- **active** — clear operator stance, readable staging, dense fresh fracture fan, optional lit subordinate hearth.
- **recent** — same topology without active fire/occupancy.
- **repeated** — overlapping fracture lenses, denser spent-bone discard, visibly reused anvil points.
- **abandoned** — reduced staging clarity while fracture concentrations persist.
- **weathered** — partial loss and biome-appropriate ground overprint.
- **scavenger_reworked** — bone fragments displaced outward from the fracture field.
- **sediment_reworked** — partial burial while anvil/fracture relationship remains recoverable.
- **repurposed** — sparse later activity may overlay the station without replacing its core signature.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_014_bone_breaking_station`
Start pool: `continuityworks:early_human/e01_014_bone_breaking_station`
Family: `continuityworks:early_human_carcass_processing`

E01-014 may appear as an explicit same-parent family component near E01-012 or E01-013 only when the parent reservation owns the entire assembly and spacing/collision rules permit it. Family identity alone never grants overlap. Independent E01-014 instances observe the Continuity Works minimum **500-block unrelated-structure exclusion radius**, including per-jigsaw-piece protection.

Compatibility is additive and non-destructive. E01-014 must never replace or suppress another mod's structure, village, road, cave, or worldgen system.

## Infrastructure dependencies

No constructed infrastructure is required. Environmental dependencies are firm working ground, access to heavy bones from a nearby kill/butchery context or transported source, usable hammerstone/anvil material, and enough lateral space for a fracture fan and clear operator stance.

The station may be family-attached to carcass-processing structures but must remain independently recognizable when spawned alone.

## Loot and occupancy hooks

Loot hooks are sparse and task-specific: simple stone hammer/cutting-tool proxies, small food/marrow traces, and limited bone material. No treasure economy, formal chest room, or permanent storage is appropriate.

Occupancy hooks represent one or several temporary processors. Scavenger occupancy may occur in abandoned/reworked states. Occupancy is not required for archetype recognition.

## Validation criteria

A generated instance passes source qualification only when:

- at least one impact/anvil station exists;
- heavy-bone staging exists on the incoming/clean side;
- a clear operator stance exists adjacent to each primary impact point;
- fracture debris is anisotropic and denser on the dirty side than around the incoming lane;
- hammerstone/anvil evidence is present;
- marrow handling is subordinate but legible;
- spent-bone discard exists outside the primary stance;
- a carry/approach lane connects staging to at least one impact station;
- no dominant carcass axis is generated;
- no hide-processing program dominates;
- no hearth organizes the site;
- no permanent architecture is generated;
- all blocks remain inside declared bounds;
- deterministic replay holds for identical inputs and changed seeds can alter layout;
- S/M/L scales increase station count and/or fracture density without becoming E01-012/E01-013;
- worldgen spacing/separation validation passes;
- both structure and jigsaw-piece exclusion radii remain at least 500 blocks;
- same-family tight composition requires the same parent reservation/assembly;
- compatibility remains additive and non-destructive.

## Production-readiness requirements

Repository milestones `HERO_SPEC_COMPLETE`, `BUILD_COMPLETE_SOURCE`, and `WORLDGEN_CONTRACT_INTEGRATED` are not equivalent to production admission. `PRODUCTION_ADMITTED` additionally requires observed executable tests, deterministic replay in the target runtime, materialized Minecraft NBT/template-pool assets where required, successful datapack/mod load, new-world placement evidence, exclusion/family compatibility validation, and visual/runtime review proving that the site reads as a bone-breaking/marrow-extraction station rather than generic butchery or refuse.

Until those observations exist, production status remains `VALIDATION_PENDING`.
