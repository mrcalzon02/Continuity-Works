# Hero Structure Specification — E01-007 Hearth Circle

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 7 of 750
Structure ID: `cw:e01_hearth_circle`
Primary family: camp infrastructure / controlled fire focus
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate inside an explicitly composed early-human camp reservation when linked shelters, work areas, food-processing areas, and hearth features share one parent placement and deterministic layout contract.

## Purpose

Hearth Circle is the first Continuity Works archetype whose primary structure is not shelter mass but controlled fire and the spatial order created around it. The hearth is a deliberately selected and maintained fire focus that organizes heat, cooking, light, work, protection, social gathering, fuel handling, ash disposal, and movement.

A valid Hearth Circle must be readable as a purpose-built fire place even when the fire itself is absent. Its identity comes from preparation, boundary control, fuel/ash history, thermal and spark clearance, activity rings, and repeated use.

It must remain distinct from a generic campfire randomly placed near another structure, from later masonry fireplaces or ovens, and from ritual fire architecture. This is low-technology domestic/camp infrastructure.

## Historical / Technological Context

The archetype represents Lower Paleolithic / early-human management of fire using extremely simple means: cleared ground, shallow scoops, naturally fire-resistant surfaces, selected stones, carried fuel, ash handling, and repeated occupation traces.

Permitted behaviors include:
- selecting a protected but ventilated location;
- clearing combustible litter;
- arranging naturally available stones around part or all of a burn focus;
- creating a shallow depression where terrain/material permits;
- concentrating fuel nearby without creating formal storage architecture;
- using heated stones and ash/charcoal residues;
- repeated reuse of the same fire focus;
- shifting a hearth short distances as old ash or wind conditions change.

The generator must not imply:
- cut-stone masonry;
- brick or ceramic fireboxes;
- chimneys;
- grates, metal spits, iron cookware, or metal tools;
- formal ovens;
- built fireplaces;
- permanent benches;
- ritual altars or ceremonial fire courts;
- engineered flues;
- kiln-scale temperatures or industrial production.

## Archetype Boundary Contract

A Hearth Circle qualifies only when the fire focus itself controls the layout.

Required identity tests:
1. **Prepared fire focus** — ground, stone, ash, or depression indicates intentional fire management.
2. **Safety radius** — nearby combustible materials and structures respond to spark/heat risk.
3. **Activity radius** — at least one surrounding zone is positioned relative to the hearth.
4. **Fuel/ash history** — active or past use is represented through fuel, charcoal, ash, staining, heated stones, or repeated burn traces.
5. **Ventilation awareness** — placement accounts for wind, cave airflow, or shelter orientation.
6. **Low technology** — no later-period fire architecture.

A single decorative flame with no spatial consequences is invalid.

## Footprint and Scale Classes

### S — Personal / Short-Stay Hearth
- Fire focus diameter: 1–2 blocks.
- Prepared/cleared radius: 2–4 blocks.
- Total behavioral footprint: approximately 5–9 blocks across.
- Fuel cache: optional and very small.
- Occupancy: 1–4 individuals.
- Typical duration: hours to several days.

### M — Household Hearth Circle
- Fire focus diameter: 2–3 blocks.
- Prepared/cleared radius: 3–6 blocks.
- Behavioral footprint: approximately 8–14 blocks across.
- Distinct fuel, rest/social, and work sectors likely.
- Occupancy: 4–10 individuals.
- Default hero scale.

### L — Repeated Group Hearth
- Fire focus diameter: 2–4 blocks, potentially including overlapping historical burn lenses.
- Prepared/cleared radius: 5–9 blocks.
- Behavioral footprint: approximately 12–22 blocks across.
- Multiple activity sectors and stronger ash/fuel history.
- Occupancy: 8–20 individuals over one or multiple episodes.
- Must remain one primary hearth system rather than silently becoming E01-008 Multi-Hearth Gathering Site.

## Architectural / Behavioral Program

The program is radial but intentionally imperfect and environment-driven.

1. **Fire focus** — active flame, ember bed, cold ash lens, or prepared burn surface.
2. **Containment edge** — stones, cleared mineral soil, shallow scoop, packed earth, or naturally noncombustible boundary.
3. **Spark-clearance band** — reduced grass, brush, bedding, and loose fuel immediately around fire.
4. **Primary tending sector** — safest side for adding fuel and manipulating food/materials.
5. **Warmth/social sector** — seating/resting positions determined by heat, wind, and smoke.
6. **Food/work sector** — optional processing location close enough for heat/light without blocking tending access.
7. **Fuel cache** — placed near enough for convenience but beyond direct spark hazard.
8. **Ash/charcoal discard** — controlled dump or rake direction, often downwind/downhill or peripheral.
9. **Smoke corridor** — directional open zone that should not terminate beneath low cover or sleeping areas.
10. **Circulation gap** — at least one clear path between hearth and surrounding camp components.
11. **Hot-stone zone** — optional heated-stone use, represented without implying later cookware technology.
12. **Legacy hearth ghosts** — optional prior burn surfaces from repeated occupation.

## Required Components

Hero admission requires:
- intentional fire focus or unambiguous extinguished hearth trace;
- a prepared or naturally fire-safe substrate;
- a readable containment or clearance strategy;
- at least one activity sector positioned relative to the hearth;
- fuel/ash/charcoal history or equivalent occupation evidence;
- wind/smoke relationship;
- safe separation from combustible shelter material;
- no later-era fire technology.

M/L variants additionally require:
- at least two differentiated sectors around the hearth;
- deterministic circulation gap;
- explicit fuel storage and ash-disposal logic;
- evidence of either repeated use or stronger spatial organization.

Recommended probabilistic components:
- selected stone ring or partial ring;
- shallow hearth scoop;
- ash lens;
- charcoal concentration;
- scorched substrate;
- heated/cracked stone proxy;
- fuelwood stack/scatter;
- bone/food processing traces;
- tool-working debris;
- seating stone/log opportunities;
- old hearth stain or shifted burn focus.

## Procedural Generation Logic

### 1. Parent-context classification

Classify the hearth context as:
- open camp;
- rock overhang;
- cave mouth;
- deep cave refuge;
- brush shelter compound;
- lean-to windbreak compound;
- hide windbreak compound;
- standalone activity site.

Context modifies wind, ventilation, spark, and material rules but does not change the hearth's core identity.

### 2. Candidate micro-site scoring

Score candidate cells for:
- local slope;
- substrate combustibility;
- overhead clearance;
- wind exposure;
- smoke escape;
- proximity to shelter walls/membranes;
- drainage/water risk;
- fuel access;
- activity-space availability;
- circulation connectivity;
- conflicting structures/reservations.

Reject sites that require destructive flattening or unsafe proximity to combustible shelter fabric.

### 3. Fire substrate classification

Assign one of:
- `BARE_MINERAL_SAFE`
- `STONE_SAFE`
- `CLEARABLE_SOIL`
- `SHALLOW_SCOOP_SUITABLE`
- `COMBUSTIBLE_HIGH_RISK`
- `WET_OR_FLOOD_PRONE`

High-risk and flood-prone sites should normally be rejected rather than forcibly converted.

### 4. Wind and smoke vector derivation

Derive a deterministic prevailing local vector from environment plus structure orientation. In caves or sheltered areas use entrance/open-volume direction as the dominant smoke proxy.

Use this vector to place:
- smoke corridor downwind;
- social/rest sector crosswind or upwind where practical;
- fuel cache away from likely sparks;
- ash disposal downwind/downhill where safe;
- shelter fabrics outside direct smoke/spark path.

### 5. Fire-focus geometry

Generate an irregular focus rather than a perfect decorative circle. Select among:
- shallow circular/oval scoop;
- partial stone ring;
- complete loose-stone ring;
- flat rock hearth;
- cleared-earth patch;
- reused natural stone pocket.

Geometry depends on local materials, occupation duration, and condition state.

Perfect symmetry should be uncommon.

### 6. Clearance-band generation

Create an irregular safety band around the fire based on:
- flame size;
- local vegetation;
- wind strength;
- shelter material;
- dry/wet climate;
- slope.

The clearance band may remove or suppress loose combustible decoration only inside the negotiated hearth volume. It must not destructively overwrite external third-party content.

### 7. Activity-sector generation

Use angular sectors rather than uniform rings. Candidate sectors include:
- tending;
- social/rest;
- cooking/food processing;
- lithic/tool work;
- drying/warming;
- fuel;
- ash/refuse;
- circulation.

The number of active sectors scales with S/M/L class.

### 8. Heat and spark constraints

Approximate risk using deterministic distance bands:
- `HOT_CORE`
- `EMBER_BAND`
- `SPARK_RISK`
- `WARMTH_BAND`
- `SAFE_OCCUPATION`

Combustible membranes, brush roofs, bedding, fuel piles, and dense vegetation cannot occupy HOT_CORE or EMBER_BAND. Spark-sensitive elements require greater clearance under dry/windy conditions.

### 9. Repeated-use history pass

For recurrent variants add one or more of:
- deepened ash lens;
- overlapping scorch patches;
- displaced ring stones;
- cracked/heated stone proxies;
- charcoal spread;
- old hearth ghost offset from active focus;
- compacted social/tending sectors;
- fuel-depletion patches.

Do not simply increase decoration density everywhere.

### 10. Extinguished-state generation

The hearth must remain readable without visible flame. Cold variants should preserve enough geometry and residue to communicate prior fire management.

### 11. Terrain integration

Preserve natural microtopography where possible. Minimal leveling is allowed inside the core hearth and immediate tending sector; broad terrain flattening is not.

### 12. Reservation and compatibility

Standalone Hearth Circle placement receives the default minimum 500-block unrelated-structure exclusion radius.

Inside an explicitly composed camp, the hearth may coexist within that radius only when all members are registered to one parent reservation. The exception does not extend to unrelated worldgen structures.

## Seed Determinism

Identical world seed, structure seed, generator version, environment, culture configuration, condition state, and parent-camp context must reproduce the same site, hearth geometry, vectors, sectors, material decisions, and history traces.

Recommended named deterministic substreams:
- `context`
- `micro_site`
- `scale`
- `substrate`
- `wind_smoke`
- `hearth_geometry`
- `containment`
- `clearance`
- `activity_sectors`
- `fuel`
- `ash_history`
- `condition`
- `culture_hook`

Later decorative additions must not reshuffle primary geometry or safety relationships.

## Biome / Environment Adaptations

### Temperate forest
- Abundant wood fuel.
- Strong litter/vegetation clearance requirement.
- Moderate spark radius.
- Ash and charcoal persistence moderate.

### Boreal / cold
- Higher hearth-use probability and larger warmth sector.
- Fuel reserves more prominent.
- Snow may naturally create a noncombustible margin but cannot block circulation.
- Shelter/fire spacing remains strict.

### Tundra / alpine
- Sparse wood; allow brush, bone/fat proxy hooks only where target content and culture rules support them.
- Stone-heavy containment likely.
- Wind strongly influences sector placement.
- Fire may be smaller despite high thermal value because fuel is scarce.

### Savanna / dry grassland
- High wildfire/spark risk in dry season.
- Larger cleared band.
- Fuel may be abundant but fragmented.
- Hearth placement strongly favors bare soil or rock.

### Arid / desert
- Sparse fuel.
- Rock hearths and shallow protected scoops favored.
- Strong nighttime thermal value.
- Windblown ash and sand burial likely in abandoned states.

### Tropical / humid
- Fuel dryness becomes a constraint.
- Smoke management and rainfall shelter relationships are important.
- Wet substrate rejection common.
- Ash signatures may degrade rapidly.

### Coastal
- Driftwood fuel hooks where plausible.
- Wind vector strongly influences placement.
- Sand/stone substrates common.
- Tidal/flood zones are invalid hearth sites unless demonstrably above hazard envelope.

### Cave contexts
- Natural airflow replaces surface wind vector.
- Hearth size constrained by chamber ventilation classification.
- Dead-end, low-ceiling smoke traps are invalid.
- Deep Cave Refuge parent may prohibit fire entirely when classified `NO_FIRE_SAFE`.

## Culture-Variant Hooks

Culture packs may alter:
- preference for stone ring versus cleared-earth focus;
- average hearth size;
- fuel type weighting;
- household/group seating arrangement;
- food-processing sector probability;
- frequency of repeated hearth reuse;
- hot-stone use;
- ash disposal behavior;
- relationship between hearth and shelter entrance;
- willingness to maintain multiple historical hearth ghosts.

Culture hooks may not introduce later cooking vessels, masonry ovens, chimneys, metal implements, formal ritual fire architecture, or unsupported claims about specific modern ethnic groups.

## Material Palette Logic

### Hearth substrate
Prefer local:
- bare mineral soil;
- gravel;
- sand;
- local stone;
- packed earth;
- natural bedrock.

### Containment stones
Use local loose stone by default. Limited carried toolstone or distinctive stones may appear as minor behavior traces but should not form structural masonry.

### Fuel
Use environmentally plausible:
- branches;
- logs where target scale allows;
- brush;
- charcoal remnants;
- other period-valid fuel proxies only through explicit biome/culture integrations.

### Residue
Represent ash, charcoal, scorched earth, heated stone, bone/food traces, and compacted soil using the target platform's safest available material proxies.

### Forbidden base materials
No brick, cut-stone masonry, metal grates, iron spits, furnaces, camp stoves, cauldrons as default infrastructure, chimneys, ceramic fireboxes, engineered vents, lantern fixtures, redstone/powered systems, or later-period cookware.

## Condition Variants

### Active / maintained
- live fire or ember state where target runtime supports it;
- fresh fuel reserve;
- clear safety band;
- organized tending/activity sectors;
- recent food/work traces.

### Recently extinguished
- hot/cold ash;
- intact containment;
- nearby fuel;
- strong recent occupancy evidence.

### Repeatedly used
- deep ash/charcoal history;
- cracked/displaced stones;
- old scorch ghosts;
- compacted sectors;
- increased but spatially coherent debris.

### Neglected / cold
- weathered ash;
- partial vegetation/litter return;
- dispersed fuel;
- ring disturbance.

### Weather-damaged
- wind/water dispersal of ash;
- displaced stones;
- partial sediment burial;
- fire focus still recoverable.

### Abandoned
- no maintained fuel;
- substantial natural intrusion;
- hearth survives mainly through residue and stone arrangement.

### Archaeological / buried
- partial or mostly buried ash lens;
- heated-stone and charcoal traces;
- occupation layers may overlap.
- Must remain legible to archaeology-aware systems or through controlled exposures.

### Later repurposed
A later occupation may reuse the same hearth location or build over/near it through an explicit overlay. The early hearth record remains recoverable; later construction must not erase the base archetype definition.

## Jigsaw / Family Relationships

Compatible parent-family relationships include:
- E01-001 Rock Overhang Camp;
- E01-002 Cave Mouth Occupation;
- E01-003 Deep Cave Refuge where ventilation permits;
- E01-004 Temporary Brush Shelter;
- E01-005 Lean-To Windbreak;
- E01-006 Hide Windbreak Camp;
- E01-009 Stone Tool Knapping Ground;
- E01-012 Butchery Site;
- E01-013 Large-Carcass Processing Site;
- E01-014 Bone-Breaking Station;
- E01-015 Marrow Processing Ground.

The Hearth Circle may serve as a camp's thermal/social anchor, but those structures remain separate archetypes.

E01-008 Multi-Hearth Gathering Site is explicitly distinct: it requires multiple coordinated hearths and group-scale spatial organization rather than one primary hearth focus.

## Infrastructure Dependencies

Required infrastructure: none.

Environmental/resource dependencies:
- safe or clearable fire substrate;
- adequate ventilation;
- period-valid fuel availability appropriate to condition/context;
- sufficient activity and circulation space;
- safe distance from highly combustible structures/materials.

A hearth inside another hero structure depends on that parent's reservation and fire-safety geometry, not on roads, utilities, permanent settlement grids, or built drainage.

## Loot / Occupancy Hooks

Loot should be trace-like rather than treasure storage.

Potential finds:
- charcoal;
- raw or partly burned fuel;
- heated-stone proxies;
- food/bone fragments;
- simple stone tools or flakes through integration hooks;
- small carried toolstone pieces;
- ash-buried low-value artifacts.

No chest is required or preferred.

Occupancy hooks should organize actors around sectors rather than spawn them uniformly. Likely behaviors include tending fire, warming/resting, processing food, working tools, social gathering, and fetching fuel.

Population must respect hearth scale, available safe occupation radius, parent shelter capacity, and ventilation.

## Gameplay / Readability Requirements

Without labels, a player should infer:
1. this location was deliberately prepared for controlled fire;
2. fire safety changed the nearby ground and object placement;
3. people gathered or worked in predictable sectors around it;
4. fuel and ash were actively managed;
5. repeated use may have left layered traces;
6. the technology remains extremely simple.

The hearth should still read when the flame is absent.

## Additive / Non-Destructive Compatibility

- Standalone generation uses the minimum 500-block unrelated-structure exclusion radius.
- Parent-camp composition may waive that spacing only for explicitly registered compatible members sharing one reservation.
- Do not erase third-party structures, roads, biome features, or other protected worldgen to place the hearth.
- If conflict exists, reject, reposition within the parent reservation, or choose another candidate.
- Terrain alteration is limited to the hearth core, safety band, activity sectors, and small blend margin.
- Later overlays attach additively and preserve recoverable early hearth evidence.

## Validation Criteria

### Geometry and fire safety
- Fire focus rests on a plausible substrate.
- Containment/clearance strategy is readable.
- No combustible shelter fabric occupies prohibited heat/ember bands.
- Fuel cache is outside direct ember hazard.
- At least one circulation path remains open.

### Smoke and environment
- Open-air hearths respect wind vector.
- Cave hearths respect ventilation proxy.
- Dead-end smoke traps fail validation.
- Flood-prone or standing-water hearths fail unless condition state intentionally represents destroyed archaeology rather than active use.

### Archetype distinction
Fail if:
- no prepared hearth evidence exists;
- fire is merely decorative inside another structure;
- multiple coordinated hearths dominate the composition (E01-008 territory);
- masonry/oven/fireplace architecture dominates;
- ritual monumentalism is required to understand the feature.

### Historical fitness
- No later-era fuel technology, cookware, masonry, or metal fixtures.
- Human intervention remains simple and local.
- Stone arrangement reads as loose selection/repositioning, not cut masonry.

### Procedural fitness
Before production admission, test at least 100 deterministic seeds per supported major environment/context class where feasible.

Verify:
- stable site selection;
- hearth geometry validity;
- safe shelter clearances;
- wind/smoke sector relationships;
- readable cold/extinguished states;
- repeated-use history without visual noise;
- absence of destructive worldgen conflicts;
- deterministic replay.

### Compatibility
- Verify minimum 500-block spacing for unrelated independent structures.
- Verify parent-reservation family exception only applies to registered compatible children.
- Verify hearth can reposition/reject instead of deleting conflicting content.
- Verify parent structures with `NO_FIRE_SAFE` classification suppress active hearth creation.

### Visual hero bar
At least three accepted hero examples should differ materially in:
- substrate;
- containment geometry;
- wind/smoke orientation;
- activity-sector arrangement;
- condition/history;
- surrounding environment.

They must not read as simple palette swaps of one perfect stone circle.

## Production-Readiness Requirements

Hero specification completion does **not** mean runtime production admission.

Production admission requires:
1. registry/schema representation for `cw:e01_hearth_circle`;
2. procedural/template implementation consistent with this specification;
3. deterministic seed replay tests;
4. substrate and slope validation;
5. wind/smoke vector tests;
6. fire-safety clearance tests against brush/hide/organic structures;
7. cave ventilation integration tests;
8. condition-state tests including cold and archaeological states;
9. S/M/L scale tests;
10. minimum 500-block unrelated-structure exclusion validation;
11. parent-reservation compatibility tests;
12. prohibited-material/technology audit;
13. target-environment export/load validation;
14. visual review of at least three materially distinct hero examples;
15. observed evidence recorded before status changes to `PRODUCTION_ADMITTED`.

## Hero Acceptance Checklist

A hero candidate passes only when all are true:
- [ ] controlled fire is the primary structural focus;
- [ ] hearth remains readable without active flame;
- [ ] safety clearance is coherent;
- [ ] smoke/wind relationship is coherent;
- [ ] fuel and ash history is represented;
- [ ] at least one surrounding activity sector responds to the hearth;
- [ ] material/technology ceiling is respected;
- [ ] camp-family relationships are explicit;
- [ ] unrelated placement respects the 500-block exclusion rule;
- [ ] compatibility remains additive/non-destructive;
- [ ] runtime implementation is not claimed without observed evidence.

## Production Status

**Hero specification:** COMPLETE.

**Runtime/template implementation:** PENDING.

**Production admission:** NOT CLAIMED.
