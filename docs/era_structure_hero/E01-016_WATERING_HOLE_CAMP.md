# E01-016 — Watering-Hole Camp

Status: **HERO_SPEC_COMPLETE**
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_water_access`

## Purpose and archetype identity

E01-016 represents a temporary or repeatedly reused camp established beside a standing or slow-refresh freshwater source where humans and animals converge. Its defining spatial signal is a protected camp terrace set back from a compact water margin, one or more approach lanes, a hearth/rest zone on the safer dry side, and activity traces that acknowledge both water access and animal traffic without turning the site into a hunting installation or a river-foraging landscape.

The site must read first as a camp organized around access to a watering place. It fails qualification if it reads as a generic dry-land hearth camp, a riverbank harvesting site, a butchery landscape, a permanent settlement, or an engineered reservoir.

## Historical and technological context

The technological ceiling is Lower Paleolithic. Permitted behaviors include repeated visitation to natural freshwater, drinking and water collection without ceramic vessels, observation of animal traffic, opportunistic scavenging or carcass processing, simple stone-tool use, temporary hearths, windbreak traces, resting/sleeping zones, and cautious path selection around muddy or exposed margins.

No wells, masonry basins, canals, dams, pottery, permanent storage, roads, corrals, fishing structures, constructed docks, or later hydraulic technology are permitted. The camp expresses behavioral adaptation to a natural water source rather than engineered water management.

## Footprint and scale classes

- **Small:** 31×8×27 blocks. One compact water-margin sector, one camp terrace, one hearth/rest zone, one principal approach lane, sparse animal spoor.
- **Medium:** 43×9×37 blocks. Expanded dry terrace, two approach lanes, one or two rest/activity pockets, clearer refuse separation, stronger repeated-use pathing.
- **Large:** 57×10×49 blocks. Broad standing-water margin, several access points, multiple rest/activity pockets, persistent trampled lanes, larger dry-side discard zone, and optional opportunistic carcass-processing trace.

Scale is expressed by the breadth of water access and repeated-use organization, not permanent architecture.

## Architectural program and required components

This is an open camp landscape rather than a building. Required components are:

1. **Water margin** — compact standing/slow-water edge represented with bounded valid Minecraft water and bank proxies.
2. **Dry camp terrace** — primary human occupation area set back from the water margin.
3. **Water-access lane** — clear route from camp terrace to at least one water edge access point.
4. **External approach lane** — route from the dry footprint edge toward the camp, distinct from the water-access lane.
5. **Hearth/rest zone** — one subordinate hearth with adjacent resting/activity ground.
6. **Temporary shelter/windbreak trace** — sparse wood/leaf or ground organization permitted, never a permanent enclosure.
7. **Tool/activity pocket** — light stone-tool and food-handling evidence.
8. **Dry-side refuse margin** — discard biased away from the water edge.
9. **Animal spoor/trample band** — sparse tracks or disturbed ground near alternate water access, subordinate to human camp organization.
10. **Optional opportunistic carcass trace** — permitted only in medium/large variants and must remain secondary to watering-hole camp identity.

No formal rooms, walls, roofed permanent structure, storage building, road, dock, fish weir, or constructed hydraulic feature is required or allowed to dominate.

## Procedural generation logic

Generation is deterministic from seed plus catalog ID and named random streams. A seed-derived water-facing orientation divides the footprint into water side and dry side. The generator lays a compact irregular water-margin patch near one edge, then positions the camp terrace several blocks inland. A water-access path is traced from terrace to the nearest water edge; an external approach path extends from the terrace toward a dry footprint boundary.

The hearth/rest zone is placed on the dry terrace with enough setback from water to preserve the watering-hole silhouette. Temporary windbreak traces occupy the upwind/peripheral side. Tool/activity evidence clusters near the hearth but remains subordinate. Refuse is projected to the opposite dry-side sector rather than into the water margin. Animal spoor is placed around a separate edge-access vector so the site reads as a shared watering place rather than a fully controlled human space.

Condition transforms occur after the functional topology qualifies. The generator must emit explicit component metadata, semantic material roles, qualification results, and a deterministic fingerprint.

## Biome and environmental adaptations

Supported biome families are temperate, boreal, tundra, savanna, arid, tropical, and coastal-transition. E01-016 always represents freshwater or low-salinity standing/slow water; coastal-transition variants must still use inland freshwater context and must not become marine shoreline camps.

- **Temperate:** dirt/coarse dirt banks, grass/moss only in weathered states, stone/andesite tools.
- **Boreal:** podzol/coarse dirt, stone/gravel margins, sparse spruce-like windbreak proxies.
- **Tundra:** gravel/stone banks, pale dry ground, minimal vegetation.
- **Savanna:** coarse dirt/red-brown stain, sparse dry vegetation proxies, broad trampled access.
- **Arid:** sand/red sand banks, smaller water patch, stronger trample concentration, no moss.
- **Tropical:** dirt/rooted dirt banks, denser peripheral vegetation proxy while keeping paths open.
- **Coastal-transition:** gravel/sand freshwater margin without saltwater or dock logic.

Placement prefers broadly traversable surface terrain. Terrain handling must remain bounded and additive; the structure must not flatten or replace unrelated terrain, structures, or other mods' worldgen.

## Culture-variant hooks

- **cautious_observation** — increases dry-side setback, animal spoor, and observation/rest spacing while reducing waterside activity.
- **short_stay** — compact hearth/rest activity, minimal refuse, weak repeated paths.
- **repeated_return** — stronger trample lanes, denser hearth stain, and persistent dry-side discard.
- **carcass_opportunism** — permits a small secondary bone/offcut pocket away from the main water access without becoming E01-012/E01-013.

Culture profiles modify emphasis only and do not introduce later technologies.

## Material palette logic

Only valid Minecraft block IDs may be emitted, with semantic roles documented explicitly:

- `minecraft:water` = bounded natural freshwater-margin proxy;
- dirt/coarse dirt/podzol/sand/gravel = bank, trample, and camp-ground roles;
- stone/andesite/granite/cobblestone = simple tool/hearth-ring roles;
- campfire/coal block = subordinate hearth trace;
- logs/leaves/fences are not used as permanent construction; sparse log/leaf blocks may represent temporary windbreak debris only;
- bone block/gravel = optional opportunistic carcass/refuse proxy.

No proxy is claimed to be literal archaeological material beyond its declared functional role.

## Condition variants

- **active** — clear access lanes, readable terrace, lit subordinate hearth, fresh water margin.
- **recent** — same spatial organization without active fire.
- **repeated** — stronger trampling, hearth stain, and dry-side discard while water access stays clear.
- **abandoned** — reduced temporary shelter traces and weaker terrace readability.
- **weathered** — selective surface loss and biome-appropriate overprint.
- **flood_reworked** — partial bank/water-edge displacement without erasing the terrace-to-water relationship.
- **scavenger_reworked** — optional bone/refuse displacement toward the periphery.
- **repurposed** — sparse later task traces may overlay the camp without replacing its water-oriented topology.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_016_watering_hole_camp`
Start pool: `continuityworks:early_human/e01_016_watering_hole_camp`
Family: `continuityworks:early_human_water_access`

E01-016 may compose with another explicit water-access family component only when both pieces belong to the same parent reservation/assembly. Family identity alone never waives exclusion. Independent instances observe the Continuity Works minimum **500-block unrelated-structure exclusion radius** and minimum **500-block per-jigsaw-piece protection radius**.

Compatibility remains additive and non-destructive. E01-016 must not replace, suppress, or destructively mutate another mod's structure, river, lake, village, road, or biome feature.

## Infrastructure dependencies

No constructed infrastructure is required. Functional dependencies are a suitable surface footprint, a bounded freshwater-margin representation, dry ground sufficient for a setback camp terrace, and path clearance between external approach, terrace, and water access.

The structure must remain independently recognizable without roads, settlements, or other generated facilities.

## Loot and occupancy hooks

Loot hooks are sparse and task-specific: simple stone flakes/tools, limited food/bone traces, and portable natural materials. No treasure cache, formal chest room, or permanent storage economy is appropriate.

Occupancy hooks represent a temporary family/group camp. Passive animal occupancy or track cues may be associated with the watering margin; scavenger/hostile occupancy may appear in abandoned states. Occupancy is not required for archetype qualification.

## Validation criteria

A generated instance passes source qualification only when:

- a bounded water-margin component exists and does not dominate the footprint;
- a dry camp terrace exists with positive setback from the water margin;
- at least one water-access lane connects terrace to water edge;
- an external approach lane connects terrace toward a dry footprint boundary;
- a hearth/rest zone exists and remains subordinate to water-oriented camp topology;
- dry-side refuse is biased away from the water edge;
- animal spoor/trample evidence exists but does not displace the human camp terrace;
- no engineered water-control feature is generated;
- no dominant carcass-processing landscape exists;
- no river-linear harvesting program dominates;
- no permanent architecture is generated;
- all blocks remain inside declared bounds;
- identical inputs replay identically and changed seeds can alter layout;
- S/M/L scales increase access/terrace complexity without becoming a settlement;
- worldgen spacing/separation validation passes;
- structure and jigsaw-piece exclusion radii remain at least 500 blocks;
- compatible tight composition requires the same parent reservation/assembly;
- compatibility remains additive and non-destructive.

## Production-readiness requirements

`HERO_SPEC_COMPLETE`, `BUILD_COMPLETE_SOURCE`, and `WORLDGEN_CONTRACT_INTEGRATED` are repository-source milestones only. `PRODUCTION_ADMITTED` additionally requires observed executable tests, deterministic replay evidence in the target runtime, materialized Minecraft NBT/template-pool assets where required, successful datapack/mod load, fresh-world placement validation, water/terrain compatibility review, exclusion/family checks, and visual/runtime review proving that the structure reads as a temporary watering-hole camp rather than a generic hearth camp or riverbank foraging site.

Until those observations exist, production status remains `VALIDATION_PENDING`.
