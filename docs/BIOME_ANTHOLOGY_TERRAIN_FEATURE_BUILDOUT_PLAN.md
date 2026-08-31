# Continuity Works — Biome Anthology & Terrain Feature Procedural Buildout Plan

**Status:** AUTHORITATIVE IMPLEMENTATION BACKLOG / LIVING ACCEPTANCE TRACKER  
**Repository:** `mrcalzon02/Continuity-Works`  
**Branch:** `main`  
**Runtime target:** Minecraft Java 1.20.1 / Forge / TerraBlender  
**Planning baseline:** 2026-08-30/31  
**Purpose:** Track what is actually implemented, what was discussed but never committed, how the terrain-feature system applies across the biome anthology, and the exact incremental acceptance sequence required to finish the mod without losing work or overstating progress.

---

## 0. Why This Document Exists

This document is deliberately corrective.

The Biome Expander work reached a point where intended content, generated-but-uncommitted work, partially committed work, and actually active runtime content were being discussed as though they were the same thing. They are not.

From this point forward, **a biome, terrain feature, ecology feature, resource system, settlement system, or technology feature is not considered implemented merely because it was designed, generated in a scratch environment, described in chat, or partially committed.** It is implemented only when the relevant source/data chain exists on `main` and the acceptance state in this document has been updated to reflect that committed reality.

This file is therefore the continuity anchor for the biome project.

Every subsequent biome/terrain implementation pass should follow this order:

1. identify the next tracker item;
2. implement only the bounded component or batch;
3. commit it to `main`;
4. read the committed source/data back;
5. perform the available local/manual developer acceptance checks;
6. update this tracker with the new status and commit SHA;
7. only then advance to the next component.

No giant uncommitted anthology generation pass should be treated as durable progress.

---

# 1. Non-Negotiable Project Rules

## 1.1 Runtime behavior

The final template mod must be conventional and plug-and-play:

```text
Minecraft 1.20.1
+ Forge
+ required embedded/runtime biome library dependencies
+ Continuity Works biome JAR in mods/
= biome content active during ordinary runtime
```

The end user must not need to run a validator, generator, preflight script, server harness, configuration verifier, repository task, or external content materializer before the mod becomes active.

Development-time acceptance is allowed and required. **Development acceptance must never become a runtime prerequisite.**

## 1.2 Configuration

Biomes must remain individually configurable.

The intended behavior is:

- biome registry entries remain loaded;
- enabled biomes participate in new natural world generation;
- disabled biomes stop being selected for newly generated terrain after restart;
- disabling a biome must not invalidate existing chunks or worlds;
- related feature-family toggles may be added later, but biome toggles remain the primary user-facing control.

## 1.3 Compatibility

Continuity Works compatibility remains additive and non-destructive.

The fixed compatibility invariant remains:

```text
mode = append_only
non_destructive = true
base_authority = preserved
```

The biome mod may:

- register new biomes;
- register new blocks/items/features;
- append biome tags;
- append placed features through supported loader mechanisms;
- add structures and structure affinity;
- add optional compatibility adapters;
- use TerraBlender or equivalent supported providers to add natural placement.

It must not:

- replace vanilla biome definitions;
- replace a third-party biome wholesale;
- clear existing biome feature lists;
- remove upstream spawns;
- replace the vanilla Overworld biome source;
- take exclusive ownership of third-party generation tables;
- require destructive compatibility patches.

## 1.4 Repository workflow

- `main` is authoritative.
- Use the simplest direct edit/commit path.
- Do not create side branches for ordinary implementation.
- Do not add stacked mutation scripts to rewrite authoritative files after generation.
- **Do not add GitHub Actions for this work.**
- No GitHub Actions are required for building, validating, packaging, materializing, testing, or accepting biome content unless explicitly requested in a future instruction.
- Development checks are local/manual or performed through the currently available execution tools.

---

# 2. Status Vocabulary

Every tracker item uses one of these states.

| Status | Meaning |
|---|---|
| `COMMITTED` | Authoritative implementation source/data exists on `main`. |
| `PARTIAL` | Some implementation exists on `main`, but one or more required runtime links are missing. |
| `PLANNED` | Design is captured here but no authoritative implementation exists yet. |
| `ACCEPTANCE_PENDING` | Source/data is committed, but local/manual compile or runtime acceptance remains outstanding. |
| `ACCEPTED` | Committed implementation has passed the applicable developer acceptance procedure. |
| `BLOCKED` | Cannot progress because of a concrete external/tool/dependency limitation. |
| `DEFERRED` | Intentionally postponed until a prerequisite stage is complete. |
| `REJECTED` | Attempt was deliberately discarded and must not be treated as implementation. |

**Important:** `COMMITTED` does not automatically mean `ACCEPTED`.

---

# 3. Current Committed Reality

This section records what is actually present on `main` at the planning baseline.

## 3.1 Runtime shell

| Component | State | Notes |
|---|---|---|
| Forge 1.20.1 runtime project | `COMMITTED` | Conventional mod project under `examples/biome_expander/runtime_mod/1.20.1/`. |
| Forge common config | `COMMITTED` | Eight foundation biome toggles plus Abyssal family/member toggles. |
| TerraBlender region | `PARTIAL` | Current `BiomeTemplateRegion` selects only the eight foundation land biomes. |
| Surface-rule integration | `COMMITTED` | Registered through ordinary mod setup. |
| Abyssal feature registries | `COMMITTED` | Seafloor, terrain, sediment, and ecology registries exist. |
| Runtime user validation/preflight requirement | `REJECTED` | The mod must not require one. |
| Biome-specific GitHub Actions | `REJECTED` | Removed and prohibited by this plan. |

## 3.2 Foundation land biomes currently committed

The following eight land biomes exist as registry definitions, keys, config toggles, and TerraBlender parameter mappings:

1. `temperate_grove`
2. `flowering_meadow`
3. `misty_highlands`
4. `marshland`
5. `frosted_taiga`
6. `dry_scrubland`
7. `rocky_badlands`
8. `ash_wastes`

### Current state

| Area | State |
|---|---|
| Registry definitions | `COMMITTED` |
| Resource keys | `COMMITTED` |
| Per-biome config toggles | `COMMITTED` |
| TerraBlender natural placement mapping | `COMMITTED` |
| Surface identity | `COMMITTED` / basic |
| Vanilla flora/features | `COMMITTED` / basic |
| Generalized terrain-feature system | `PLANNED` |
| Distinct erosion/deposition systems | `PLANNED` |
| Signature biome-specific terrain landmarks | `PLANNED` |
| Custom ore/resource identity | `PLANNED` |
| Settlement/civilization identity | `PLANNED` |
| Technology-era integration | `PLANNED` |

The foundation biomes are therefore **real biomes but not finished showcase biomes**.

## 3.3 Infinite Domain Abyssal registry family currently committed

Primary imported family:

1. `western_continental_slope`
2. `western_abyssal_plain`
3. `western_fracture_field`
4. `western_hadal_trench`
5. `eastern_continental_slope`
6. `eastern_abyssal_plain`
7. `eastern_fracture_field`
8. `eastern_hadal_trench`

Compatibility IDs also exist for:

- `western_abyssal_ocean`
- `eastern_abyssal_ocean`

### Critical missing runtime link

The current `BiomeTemplateRegion` does **not** add the Abyssal family to TerraBlender natural placement.

Therefore:

- Abyssal biome registry definitions are present;
- Abyssal config toggles are present;
- Abyssal feature selectors and feature systems are present;
- but the imported Abyssal biome family is **not yet proven to participate in ordinary natural Overworld selection through the current TerraBlender region**.

This is tracked below as a required implementation item, not as completed work.

## 3.4 Abyssal terrain/feature work already committed

### Landmark structures

| ID | Feature | State | Notes |
|---|---|---|---|
| SF-REVIEW-002 | Fracture Vent Field | `COMMITTED`, `ACCEPTANCE_PENDING` | Selector, structure, pool, placement set, corrected 1.20.1 NBT committed. |
| SF-REVIEW-003 | Hadal Vent Complex | `COMMITTED`, `ACCEPTANCE_PENDING` | Selector, structure, pool, placement set, 1.20.1 NBT committed. |

### Reusable procedural features

| ID | Feature | Mechanism | State |
|---|---|---|---|
| OSF-005 | Pillow-lava Fields | Procedural seafloor morphology | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-006 | Cooled Lava / Magma-tube Systems | Flooded procedural tube network | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-007 | Tube Skylight / Collapse Variant | Correlated OSF-006 variant | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-019 | Pockmark Fields | True seabed excavation/deformation | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-023 | Shelf Sand-wave / Ripple Fields | Sediment deposition/morphology | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-027 | Turbidity-current Channels | Seeded continuous erosion + levees | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-037 | Polymetallic Nodule Analogues | Decorative/resource-neutral seabed scatter | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-045 | Whale-fall Ecological Sites | 3:2:2 ecological variant family | `COMMITTED`, `ACCEPTANCE_PENDING` |
| OSF-049 | Natural Wood-fall Sites | 3:3:2 ecological variant family | `PARTIAL` |

### OSF-049 exact missing link

The Wood Fall Java implementation, registry entry, biome selector, configured feature, and placed feature were committed.

The final additive Forge biome modifier attaching the placed Wood Fall feature to `abyssal_wood_fall_biomes` was **not committed before the previous process stopped**.

This remains an explicit unfinished task.

---

# 4. Work Previously Described but Not Actually Committed

This section exists specifically to prevent verbal/generated progress from being mistaken for repository state.

## 4.1 The 128-biome anthology

A 128-biome anthology was previously described as though it had been generated into the runtime mod.

At this planning baseline, **that anthology is not committed to `main`.**

Repository search does not show the expected anthology signatures such as `Grid Core Metropolis` or the planned primordial anthology content.

Therefore the anthology state is:

```text
DESIGNED / PLANNED
NOT AUTHORITATIVELY IMPLEMENTED
```

## 4.2 The previously discussed totals

The intended long-term primary biome count is now formalized as:

- 8 foundation land biomes already committed;
- 128 anthology biomes still to implement;
- 8 primary Abyssal biomes already registered but still needing complete natural-placement acceptance.

**Target primary biome count: 144**

The two Abyssal compatibility IDs are not counted as additional primary design biomes.

## 4.3 Previously described feature totals

Any earlier statements claiming hundreds of finalized resources, dozens of finished technology blocks, 69 village-enabled anthology biomes, or a complete 136-biome generated resource layer must be treated as **non-authoritative unless the corresponding files are found and read from `main`.**

This planning tracker replaces those conversational counts.

---

# 5. Target Anthology — 128 Missing Biomes

The anthology is divided into eight 16-biome families. Each family represents a technological/cultural/ecological era while remaining a physical Minecraft biome rather than merely a themed structure set.

Every family must eventually support terrain, vegetation/ecology, resources, civilization, structures, and technology identity.

## 5.1 Family A — Primordial / Caveman Era

**Status: `PLANNED` — 0/16 committed**

1. Flintgrass Steppe
2. Mammoth Tundra
3. Giant Fern Basin
4. Cycad Lowlands
5. Tar Pit Savanna
6. Obsidian Ridge
7. Karst Hunterlands
8. Redwood Primeval
9. Riverstone Valley
10. Bonefield Flats
11. Firebreak Scrub
12. Megafauna Marsh
13. Basalt Cave Uplands
14. Amber Forest
15. Glacial Hunter Coast
16. Thunder Plateau

### Family identity

- minimally engineered landscape;
- strong geology and megaflora;
- caves, overhangs, flint/chert analogues, obsidian, exposed stone resources;
- hunter camps and primitive shelters rather than villages everywhere;
- early-fire, stone, bone, hide, charcoal and primitive pottery technological identity.

## 5.2 Family B — Ancient / Classical Era

**Status: `PLANNED` — 0/16 committed**

1. Reed Kingdom Floodplain
2. Sunstone Desert
3. Marble Coast
4. Olive Hills
5. Imperial Steppe
6. Sacred Cedar Highlands
7. Terraced River Valley
8. Bronze Quarrylands
9. Oasis Caravan Basin
10. Red Clay Delta
11. Temple Karst
12. Salt Road Flats
13. Volcanic Polis Slopes
14. Cypress Necropolis
15. Copper Wadi
16. Ancient Harbor Coast

### Family identity

- river engineering, early roads, quarries, terraces, canals and harbors;
- bronze/copper/tin resource emphasis;
- ancient villages/market settlements;
- monuments and ritual landscapes used as rare landmarks rather than biome-wide clutter.

## 5.3 Family C — Medieval Era

**Status: `PLANNED` — 0/16 committed**

1. Feudal Farmlands
2. Greenwood March
3. Castle Highlands
4. Monastery Vale
5. Heathland Commons
6. Fogbound Moor
7. Alpine Holdfast
8. River Mill Country
9. Walled Market Plain
10. Old Growth Hunting Forest
11. Iron Mine Hills
12. Fenland Causeways
13. Shepherd Downs
14. Battlefield Heath
15. Coastal Fishing Shires
16. Plaguewood Ruins

### Family identity

- hedgerows, fields, managed woodland, roads, quarries and mine cuts;
- iron/silver resource identity;
- villages and specialist villagers appropriate to settlement-oriented regions;
- castles, mills, bridges, monasteries and fortified hills as structure affinities.

## 5.4 Family D — Renaissance / Clockwork Era

**Status: `PLANNED` — 0/16 committed**

1. Terraced Vineyard
2. Canal Republic
3. Windmill Polders
4. Clockwork Garden
5. Observatory Highlands
6. Gunpowder Quarrylands
7. Merchant Coast
8. Printing City Hinterland
9. Glassmaker Dunes
10. Hydraulic Gardens
11. Copperwork Hills
12. Academy Grove
13. Foundry Canal District
14. Baroque Estates
15. Airship Moorings
16. Mechanist Citadel

### Family identity

- water management, polders, canals, terracing and increasingly engineered terrain;
- copper, zinc-like, saltpeter/gunpowder and glass-making resource themes;
- clockwork/mechanical structures without making every block a machine;
- denser road, canal and settlement affinity than medieval families.

## 5.5 Family E — Industrial Era

**Status: `PLANNED` — 0/16 committed**

1. Coal Basin
2. Ironworks Valley
3. Railcut Highlands
4. Textile Mill Country
5. Smog City Fringe
6. Slag Heath
7. Quarry Megaplex
8. Petroleum Marsh
9. Steel River
10. Factory Coast
11. Workers' Row District
12. Steamworks Plateau
13. Telegraph Plains
14. Cinder Forest
15. Canal Freightlands
16. Dynamo Ridge

### Family identity

- rail cuts, spoil heaps, quarries, slag/cinder deposits, canalized waterways;
- coal, iron, lead, petroleum and industrial mineral emphasis;
- factories, rail infrastructure, warehouses and dense settlements;
- visible anthropogenic terrain should coexist with natural remnants rather than flatten entire biomes.

## 5.6 Family F — Atomic / Post-Collapse Era

**Status: `PLANNED` — 0/16 committed**

1. Blast Crater Expanse
2. Glassed Desert
3. Fallout Pine Barrens
4. Flooded Metro Basin
5. Bunker Steppe
6. Reactor Marsh
7. Rustbelt Ruins
8. Mutant Orchard
9. Trench Scar Plains
10. Ashen Suburbs
11. Collapsed Dam Valley
12. Radstorm Badlands
13. Wreckage Coast
14. Black Rain Forest
15. Emergency Habitat Zone
16. Dead Transmission Hills

### Family identity

- craters, rubble, trenches, collapsed infrastructure, glassed surfaces and contaminated-looking terrain;
- uranium/radiological themes must use the mod's own safe mechanics rather than uncontrolled external IDs;
- ruins, bunkers and emergency infrastructure;
- ecology should show succession and disturbance, not just uniformly dead ground.

## 5.7 Family G — Advanced Science Fiction Era

**Status: `PLANNED` — 0/16 committed**

1. Terraforming Prairie
2. Crystal Reactor Highlands
3. Arcology Basin
4. Fusion Desert
5. Orbital Elevator Exclusion Zone
6. Bioengineered Forest
7. Nanite Flats
8. Gravity Quarry
9. Quantum Geode Valley
10. Spaceport Barrens
11. Hydroponic Megafarm
12. Shielded Habitat Ridge
13. Solar Mirror Desert
14. Antimatter Research Wastes
15. Helium-3 Mining Plateau
16. Synthetic Wetlands

### Family identity

- engineered geomorphology, giant infrastructure footprints and advanced materials;
- cobalt/titanium/high-grade alloys plus synthetic/crystalline resource identity;
- arcologies, research sites, orbital/space infrastructure and controlled ecology;
- still traversable Minecraft terrain, not a structure pasted over every chunk.

## 5.8 Family H — Neon / Virtual / Tron-Esque Era

**Status: `PLANNED` — 0/16 committed**

1. Neon City Grid
2. Grid Core Metropolis
3. Circuit Forest
4. Hologram Gardens
5. Data Spire Basin
6. Chromatic Glass Desert
7. Pulseway Corridor
8. Synthwave Coast
9. Luminous Canal District
10. Blacklight Badlands
11. Pixelated Mesa
12. Photon Marsh
13. Cyber Shrine Highlands
14. Vector Plains
15. Recursive Ruins
16. Null Sector

### Family identity

- physical terrain with deliberately synthetic geometry;
- luminous materials, glass, dark structural bases, data/crystal motifs;
- grid terraces, geometric ravines, circuit-like forests and neon canal systems;
- dense city-biome variants such as Grid Core Metropolis use layered structures and terrain engineering while preserving navigation and chunk performance;
- no dependence on an external shader to make the biome legible.

---

# 6. General Terrain Feature Architecture

The successful Abyssal import established a useful pattern: terrain variety should not be a single monolithic generator.

The broader biome system will use multiple generator families with clear responsibilities.

## 6.1 Terrain deformation

Changes the physical elevation/shape of the generated land after base terrain is available.

Examples:

- pockmarks and sinkholes;
- gullies and arroyos;
- craters;
- shallow ravines;
- ridge spines;
- tors and outcrops;
- glacial hollows;
- trench scars;
- engineered terraces;
- technogenic cuts.

Rule: deformation must preserve protected blocks and must not blindly excavate arbitrary mod blocks or structures.

## 6.2 Erosion and channel systems

Continuous or semi-continuous features driven by absolute world coordinates and seed-aware fields.

Examples:

- braided stream channels;
- dry washes;
- turbidity-style land channels;
- glacial melt channels;
- industrial drainage cuts;
- collapsed canal beds;
- neon coolant/data channels.

Preferred implementation for long features: deterministic global field or chunk-continuous reconstruction, not disconnected 16×16 stamps.

## 6.3 Depositional morphology

Adds material accumulated by wind, water, ice, volcanic activity, collapse, or industry.

Examples:

- dunes and sand waves;
- alluvial fans;
- talus/scree fans;
- moraines;
- snow drifts;
- peat/hummock accumulation;
- volcanic ash drifts;
- slag heaps;
- rubble aprons;
- crystal dust or synthetic deposition.

## 6.4 Surface landmark morphology

Large but non-building physical features.

Examples:

- hoodoos;
- basalt columns;
- lava pillows/flows;
- giant boulders;
- stone circles when naturally/ritually appropriate;
- giant roots;
- fossil/bone beds;
- crystal spires;
- data spires;
- geometric neon mesas.

## 6.5 Ecology features

Biological or once-biological landscape features.

Examples:

- fallen logs and root plates;
- whale/wood-fall analogues underwater;
- giant fern copses;
- ancient cedars;
- orchard bands;
- deadfall fields;
- mutant groves;
- bioengineered tree arrays;
- synthetic circuit forests.

Ecology features may be weighted variants sharing one placement contract, as demonstrated by Whale Falls and Wood Falls.

## 6.6 Resource geology

Resources should be integrated as geology, not randomly scattered technology blocks.

Resource feature families include:

- normal buried veins;
- deepslate variants;
- exposed cliff veins;
- placer-style deposits;
- geodes;
- nodules;
- fossil beds;
- quarry/extraction scars;
- industrial salvage fields;
- advanced crystal/data deposits.

Resource abundance must be budgeted by biome/family so anthology variety does not multiply total world resource output uncontrollably.

## 6.7 Civilization and technology terrain interaction

Structures remain a separate capability, but terrain must expose explicit structure-affinity hooks.

Examples:

- flat castle shoulders;
- village pasture basins;
- harbor shelves;
- road/rail corridors;
- quarry benches;
- industrial brownfields;
- bunker berms;
- arcology foundations;
- spaceport flats;
- neon city blocks/grids.

Terrain features should prepare or score appropriate sites. They should not silently generate full structures inside terrain code.

---

# 7. Foundation Biome Terrain Application Matrix

The first non-Abyssal procedural acceptance stage will complete these eight because they already exist in natural placement.

## 7.1 Temperate Grove

**Current:** biome exists; rich terrain pack missing.

Planned feature profile:

- rolling knoll/hollow deformation;
- spring-fed micro-swales;
- mossy boulder/erratic clusters;
- fallen log/root-plate ecology;
- occasional giant oak grove variant;
- shallow leaf-litter depressions;
- low-density clay/iron exposure along cuts;
- optional old-road/stone-wall affinity for later civilization layers.

Signature: mature, irregular woodland with readable microtopography rather than a flat forest reskin.

## 7.2 Flowering Meadow

Planned feature profile:

- gentle hummocks and swales;
- seasonal-looking flower bands using deterministic patches;
- shallow stream/ditch meanders;
- isolated glacial stones;
- pollinator/flower ecology zones;
- rare stone circle or pastoral ruin affinity;
- low tree pressure to retain long sight lines.

Signature: broad open meadow with terrain rhythm and floral structure.

## 7.3 Misty Highlands

Planned feature profile:

- ridge spine / tor generator;
- exposed cliff shelves;
- scree/talus fans;
- waterfall-source gullies where hydrology allows;
- wind-shaped sparse tree clumps;
- fog-compatible basin morphology;
- exposed mineral seams;
- ruin/observatory/fortress affinity on high shoulders.

Signature: vertical terrain with traversable shelves, tors and erosion rather than generic mountains plus fog.

## 7.4 Marshland

Planned feature profile:

- hummock/pool mosaic;
- shallow meandering channels;
- peat/mud depositional pads;
- reed/sedge islands;
- deadfall ecology;
- occasional sink pools;
- clay/peat resource deposits;
- boardwalk/causeway/village affinity for later structure layers.

Signature: complex wetland surface with navigable dry islands and connected water channels.

## 7.5 Frosted Taiga

Planned feature profile:

- moraine ridges;
- glacial erratics;
- shallow kettle hollows;
- snow-drift accumulation;
- frozen creek channels;
- windthrow/root-plate ecology;
- exposed stone/iron pockets;
- hunting lodge/holdfast affinity.

Signature: terrain visibly shaped by ice and freeze/thaw processes.

## 7.6 Dry Scrubland

Planned feature profile:

- arroyo/gully network;
- alluvial fans;
- dry wash gravel deposits;
- low mesas/outcrops;
- thorn/scrub islands;
- rare spring/oasis microfeature;
- exposed copper-like/mineral traces;
- caravan/primitive road affinity.

Signature: erosion-driven dryland rather than flat dirt with sparse bushes.

## 7.7 Rocky Badlands

Planned feature profile:

- hoodoo field;
- mesa shoulder/scarp features;
- slot-gully network;
- talus aprons;
- dry wash channels;
- fossil/bone-bed analogues;
- exposed ore bands with strict resource budgets;
- mine/quarry/outlaw-settlement affinity.

Signature: strongly sculpted erosion landscape with vertical landmarks.

## 7.8 Ash Wastes

Planned feature profile:

- ash dune/drift morphology;
- basalt pavement and cracked crust fields;
- fumarole/vent field;
- lava crust/rift scars without uncontrolled open lava everywhere;
- dead snag ecology;
- obsidian/sulfur-like/mineralized zones using safe owned resources;
- caldera/ridge affinity;
- later industrial/atomic overlap hooks.

Signature: geologically active or recently devastated landscape with layered ash and volcanic structure.

---

# 8. Anthology Family Terrain Application Matrix

| Family | Primary deformation | Deposition | Ecology | Resources | Civilization/technology terrain hooks |
|---|---|---|---|---|---|
| Primordial | karst, glacial hollows, river cuts, basalt ridges | gravel bars, tar/mud basins, talus | megaflora, giant roots, bone fields | flint/chert, obsidian, copper traces | camps, cave shelters, ritual stones |
| Ancient | wadis, floodplain channels, quarry benches, terraces | delta silt, dune fields, alluvial fans | cedar/olive/reed landscapes | copper, tin, marble, clay, salt | roads, canals, harbors, quarries, temples |
| Medieval | pasture terraces, mine cuts, castle shoulders, fen channels | field banks, scree, managed soil | hedgerows, coppice, orchards, hunting woods | iron, silver, coal traces | villages, castles, mills, monasteries, bridges |
| Renaissance/Clockwork | polders, engineered canals, terraces, observatory hills | dredge banks, glass sand, quarry waste | formal gardens, vineyards, orchards | copper, zinc-like metals, saltpeter, glass sand | canals, workshops, citadels, airship pads |
| Industrial | rail cuts, quarries, channelized rivers, subsidence | slag, cinder, spoil heaps, tailings | stressed woodland, reclamation patches | coal, iron, lead, petroleum | factories, rails, warehouses, worker districts |
| Atomic/Post-collapse | craters, trenches, collapse basins, dam scars | rubble, ash, glass, debris | mutant/regrowth mosaics | uranium/owned atomic materials, scrap | bunkers, reactors, ruined metros, emergency sites |
| Advanced Sci-fi | engineered terraces, gravity pits, spaceport flats | crystal fields, processed spoil, synthetic soil | bioengineered groves, hydroponics | titanium/cobalt, advanced crystals | arcologies, research sites, fusion infrastructure |
| Neon/Virtual | grid terraces, geometric ravines, synthetic mesas | glass shards/dust, luminous deposits | circuit forests, hologram/synthetic gardens | data/quantum/neon crystals | neon districts, pulseways, data spires, Grid Core metropolis |

---

# 9. Shared Land Terrain Feature Backlog

These are the reusable procedural primitives required before the 128 anthology biomes are individually built.

## 9.1 Core helper layer

| ID | Component | State |
|---|---|---|
| TFS-CORE-001 | Safe surface-column query/placement helper | `PLANNED` |
| TFS-CORE-002 | Seed + absolute-coordinate deterministic noise/hash helper | `PLANNED` |
| TFS-CORE-003 | Rotation/mirroring transform helper for surface morphology | `PLANNED` |
| TFS-CORE-004 | Protected-block / structure-safe deformation filter | `PLANNED` |
| TFS-CORE-005 | Surface material eligibility classifier | `PLANNED` |
| TFS-CORE-006 | Chunk-continuous channel field helper | `PLANNED` |
| TFS-CORE-007 | Terrain feature registry separated from Abyssal-only registry | `PLANNED` |
| TFS-CORE-008 | Configurable feature-family enable switches | `DEFERRED` until initial features work |

## 9.2 General deformation generators

| ID | Feature | Primary users | State |
|---|---|---|---|
| TFS-DEF-001 | Rolling Knolls & Hollows | grove, meadow, farmland | `PLANNED` |
| TFS-DEF-002 | Ridge Spine / Tor Field | highlands, ancient uplands, sci-fi ridges | `PLANNED` |
| TFS-DEF-003 | Dry Arroyo / Gully Network | scrubland, desert, wasteland | `PLANNED` |
| TFS-DEF-004 | Hoodoo / Badland Pillar Field | rocky badlands, blacklight badlands | `PLANNED` |
| TFS-DEF-005 | Glacial Moraine / Kettle System | frosted taiga, mammoth tundra | `PLANNED` |
| TFS-DEF-006 | Marsh Hummock / Pool Mosaic | marshland, reactor marsh, photon marsh | `PLANNED` |
| TFS-DEF-007 | Crater Field | volcanic/atomic/sci-fi | `PLANNED` |
| TFS-DEF-008 | Karst Sinkhole / Limestone Basin | primordial/ancient karst | `PLANNED` |
| TFS-DEF-009 | Engineered Terrace System | ancient through sci-fi | `PLANNED` |
| TFS-DEF-010 | Grid Terrace / Geometric Ravine | neon family | `PLANNED` |

## 9.3 Depositional generators

| ID | Feature | State |
|---|---|---|
| TFS-DEP-001 | Scree / Talus Fan | `PLANNED` |
| TFS-DEP-002 | Alluvial Fan | `PLANNED` |
| TFS-DEP-003 | Sand Dune / Ripple Field | `PLANNED` |
| TFS-DEP-004 | Snow Drift Field | `PLANNED` |
| TFS-DEP-005 | Ash Drift Field | `PLANNED` |
| TFS-DEP-006 | Peat / Mud Accumulation | `PLANNED` |
| TFS-DEP-007 | Slag / Spoil Heap | `PLANNED` |
| TFS-DEP-008 | Rubble / Collapse Apron | `PLANNED` |
| TFS-DEP-009 | Crystal / Synthetic Deposition | `PLANNED` |

## 9.4 Continuous channel systems

| ID | Feature | State |
|---|---|---|
| TFS-CHN-001 | Temperate swale / creek field | `PLANNED` |
| TFS-CHN-002 | Marsh meander channels | `PLANNED` |
| TFS-CHN-003 | Dry wash / arroyo channels | `PLANNED` |
| TFS-CHN-004 | Glacial melt channels | `PLANNED` |
| TFS-CHN-005 | Engineered canal / drainage corridor | `PLANNED` |
| TFS-CHN-006 | Industrial channelized river/drain | `PLANNED` |
| TFS-CHN-007 | Post-collapse drainage breach | `PLANNED` |
| TFS-CHN-008 | Neon pulseway / coolant canal terrain corridor | `PLANNED` |

## 9.5 Ecology generators

| ID | Feature | State |
|---|---|---|
| TFS-ECO-001 | Fallen Log / Root Plate Field | `PLANNED` |
| TFS-ECO-002 | Giant Primordial Tree/Fern Clusters | `PLANNED` |
| TFS-ECO-003 | Hedgerow / Coppice Bands | `PLANNED` |
| TFS-ECO-004 | Orchard / Vineyard Bands | `PLANNED` |
| TFS-ECO-005 | Deadfall / Burn Scar | `PLANNED` |
| TFS-ECO-006 | Mutant / Succession Grove | `PLANNED` |
| TFS-ECO-007 | Bioengineered Tree Array | `PLANNED` |
| TFS-ECO-008 | Circuit Forest / Synthetic Tree Array | `PLANNED` |

## 9.6 Resource geology generators

| ID | Feature | State |
|---|---|---|
| TFS-RES-001 | Biome-aware buried ore vein wrapper | `PLANNED` |
| TFS-RES-002 | Exposed cliff vein | `PLANNED` |
| TFS-RES-003 | Placer / gravel-bar deposit | `PLANNED` |
| TFS-RES-004 | Fossil / bone bed | `PLANNED` |
| TFS-RES-005 | Geode / crystal pocket | `PLANNED` |
| TFS-RES-006 | Quarry/extraction exposure | `PLANNED` |
| TFS-RES-007 | Industrial salvage/scrap deposit | `PLANNED` |
| TFS-RES-008 | Advanced crystal/data deposit | `PLANNED` |

---

# 10. Ore and Material Progression Backlog

The anthology should eventually support an owned material progression rather than inventing unverifiable IDs from unrelated mods.

Initial target material families:

1. tin
2. copper integration / bronze support
3. silver
4. lead
5. cobalt
6. titanium
7. uranium or owned atomic equivalent
8. industrial carbon/coal derivatives
9. petroleum-associated resources
10. neon crystal / luminous mineral
11. data crystal
12. quantum crystal or equivalent advanced material

Each material requires, as applicable:

- owned registry ID;
- block/item models/textures;
- stone/deepslate or appropriate host variants;
- configured/placed ore feature;
- biome/family distribution budget;
- loot/drop behavior;
- smelting/processing recipe;
- tag compatibility;
- no accidental multiplication of global ore output when many biomes are enabled.

State: **`PLANNED` unless files are subsequently committed and recorded here.**

---

# 11. Villagers, Settlements, and Basic Technology Backlog

The requested anthology includes villagers and technological progression from caveman through sci-fi.

This must be implemented deliberately rather than by giving every biome a vanilla village.

## 11.1 Settlement classes

- uninhabited wilderness;
- primitive camp;
- hamlet;
- village;
- fortified settlement;
- city district;
- industrial district;
- ruined settlement;
- research/advanced habitat;
- arcology;
- neon megacity district.

## 11.2 Villager policy

Vanilla villagers should be reused where sensible.

Custom professions/trades may be added where they improve the technological identity, but the system should prefer additive extension over replacing vanilla professions.

Examples:

- primitive gatherer/hunter equivalent;
- ancient mason/trader;
- medieval smith/miller;
- clockmaker/mechanist;
- industrial engineer/rail worker;
- post-collapse scavenger/technician;
- advanced researcher;
- neon data broker/technician.

State: `PLANNED`.

## 11.3 Technology terrain hooks

Terrain preparation should support later structures without hard-coding structures into terrain generators.

Required site-context outputs should include:

- slope class;
- local flatness;
- water proximity;
- ridge/valley classification;
- road/canal suitability;
- settlement footprint candidates;
- harbor/coast suitability;
- resource proximity;
- exclusion zones;
- biome/family identity;
- technology era.

These can eventually feed the existing Continuity Works `SiteContext`/structure tooling.

---

# 12. Per-Biome Minimum Richness Contract

A biome is not accepted as a finished anthology biome merely because its biome JSON and TerraBlender climate point exist.

Every completed biome should normally have:

1. a distinct climate/distribution identity;
2. a distinct surface rule/material identity;
3. at least **one terrain deformation or major geomorphic behavior**;
4. at least **one erosion, depositional, or hydrologic behavior**;
5. at least **one ecology/vegetation identity**;
6. an explicit resource profile, even if that profile intentionally suppresses special resources;
7. an explicit structure/settlement affinity profile;
8. a civilization/technology-era identity where appropriate;
9. a config toggle for natural placement;
10. a family/functional tag set;
11. transition behavior that does not create absurd hard edges;
12. performance limits appropriate to its feature density.

Showcase biomes should target **6–10 active feature systems** rather than the minimum.

Examples of showcase targets:

- Misty Highlands
- Rocky Badlands
- Ash Wastes
- Giant Fern Basin
- Castle Highlands
- Canal Republic
- Coal Basin
- Blast Crater Expanse
- Arcology Basin
- Grid Core Metropolis
- Western/Eastern Fracture Fields
- Western/Eastern Hadal Trenches

---

# 13. Procedural Acceptance Contract

This is the workflow that turns a tracker row into durable implementation.

## 13.1 Step A — Select exactly one bounded unit

A unit may be:

- one shared feature primitive;
- one biome;
- one 2–4 biome micro-batch sharing the same feature profile;
- one ore family;
- one ecology family;
- one structure-affinity family.

Do not jump between unrelated units inside one acceptance cycle.

## 13.2 Step B — Implement the complete runtime chain

For a custom feature this normally means:

```text
Java Feature implementation
→ static feature registry
→ configured_feature JSON
→ placed_feature JSON
→ additive biome modifier
→ biome tag/selector
→ config relationship if required
```

For a biome this normally means:

```text
Biome registry JSON
→ ResourceKey
→ config toggle
→ TerraBlender climate mapping
→ surface rule
→ family tags
→ terrain/ecology/resource features
→ structure affinity
```

A partial chain must be marked `PARTIAL`.

## 13.3 Step C — Commit the bounded unit

Commit directly to `main`.

The commit message should identify the unit, for example:

```text
Add Temperate Grove rolling terrain feature
Add Rocky Badlands hoodoo generator
Register Primordial anthology family 01-04
Attach Wood Fall ecology to Abyssal slope/plain biomes
```

## 13.4 Step D — Read back the committed files

Immediately fetch/read the changed authoritative files from `main`.

Confirm:

- correct path;
- expected contents;
- expected IDs;
- selector references resolve to committed IDs;
- no accidental destructive tag replacement;
- no lost file due to interrupted generation.

This read-back is mandatory because it already caught binary corruption during the Abyssal import.

## 13.5 Step E — Local developer acceptance

When a functioning local Forge toolchain/runtime is available:

### Compile acceptance

- Java 17 compile succeeds;
- data/resource packaging succeeds;
- no missing owned registry IDs;
- no unresolved feature type IDs.

### Runtime load acceptance

- put the built JAR in an ordinary Forge `mods/` folder;
- launch normally;
- no external validator/preflight required;
- config file is created automatically;
- mod reaches playable/server-ready state;
- no registry/datapack rejection.

### Worldgen acceptance

For each accepted biome or feature family:

- fresh world or fresh chunks;
- biome can be naturally selected when enabled;
- disabled biome does not appear in newly generated terrain after restart;
- existing registry remains readable;
- feature appears only in eligible tags;
- continuous features cross chunk boundaries without obvious 16×16 seams;
- deformation does not eat protected structures or unrelated mod blocks;
- vanilla/third-party biomes remain present;
- representative terrain is traversable;
- feature density is not catastrophically expensive.

Recommended development sampling:

- minimum 3 seeds for ordinary features;
- minimum 5 seeds for continuous terrain systems or showcase biomes;
- inspect at least one biome boundary/transition.

This is developer acceptance only. It is **not a user-side runtime prerequisite**.

## 13.6 Step F — Update this tracker

After a component is committed and its known acceptance state is established, update the corresponding row here.

Each accepted row should eventually record:

```text
status:
implementation_commit:
tracker_update_commit:
compile_status:
runtime_status:
worldgen_status:
known_limitations:
next_component:
```

Then commit the tracker update.

This creates a durable two-part audit trail:

1. implementation commit;
2. planning/acceptance-state commit.

---

# 14. Incremental Build Program

## Stage 0 — Tracker baseline

**Goal:** establish this document as the authoritative gap/acceptance tracker.

Status: `IN PROGRESS` until this file is committed and read back.

Acceptance:

- document exists on `main`;
- current committed reality is recorded accurately;
- uncommitted anthology is explicitly marked unimplemented;
- missing Abyssal links are recorded;
- terrain feature architecture and application matrix are recorded;
- no unrelated code changes bundled into the tracker commit.

## Stage 1 — Close existing Abyssal loose ends

### ABY-FIX-001 — Wood Fall final biome modifier

State: `PLANNED` / source chain otherwise `PARTIAL`.

Required:

```text
forge/add_features
biomes = #continuityworks_biomes:abyssal_wood_fall_biomes
features = continuityworks_biomes:abyssal/wood_fall
step = local_modifications
```

### ABY-FIX-002 — Abyssal natural placement integration

State: `PLANNED`.

Required:

- extend TerraBlender region or create a dedicated additive Abyssal region;
- map all eight primary Abyssal biomes to appropriate climate/continentalness/depth/weirdness conditions;
- honor family/member config toggles;
- avoid replacing vanilla ocean source;
- preserve strong deep-ocean character.

### ABY-FIX-003 — Abyssal config/feature relationship review

State: `PLANNED`.

Ensure biome disable switches also prevent biome-targeted features from producing unreachable or unintended generation side effects.

Do not make user-side validation necessary.

## Stage 2 — Shared land terrain foundation

Implement in this order:

1. `TFS-CORE-001` safe surface-column helper;
2. `TFS-CORE-002` deterministic world-coordinate field helper;
3. `TFS-CORE-004` protected-block deformation filter;
4. `TFS-CORE-007` generalized land terrain registry;
5. first small deformation feature.

First acceptance target should be a low-risk feature such as **Rolling Knolls & Hollows** or **Fallen Log / Root Plate Field**, not the most complicated neon city terrain.

## Stage 3 — Foundation eight biome terrain completion

Recommended order:

1. Temperate Grove
2. Flowering Meadow
3. Misty Highlands
4. Marshland
5. Frosted Taiga
6. Dry Scrubland
7. Rocky Badlands
8. Ash Wastes

Why this order:

- moves from lower-risk gentle morphology to more aggressive deformation;
- exercises forest/open/highland/wetland/cold/dry/badland/volcanic cases;
- produces reusable primitives needed by the anthology.

Stage complete only when all eight meet the minimum richness contract.

## Stage 4 — Primordial anthology family

Implement 16 biomes in micro-batches of 2–4.

Primary reusable systems to establish:

- giant fern/cycad ecology;
- karst terrain;
- tar/mud basins;
- bone/fossil beds;
- glacial/megafauna terrain;
- primitive camp/cave affinity;
- flint/obsidian resource profile.

## Stage 5 — Ancient anthology family

Establish:

- floodplain and delta systems;
- ancient terraces;
- oasis/wadi systems;
- quarry benches;
- early roads/canals;
- bronze resource profile;
- harbor/coastal settlement affinity.

## Stage 6 — Medieval anthology family

Establish:

- hedgerow/coppice systems;
- farm field banks;
- castle/fortification shoulders;
- mine cuts;
- causeway/fen terrain;
- iron/silver resource identity;
- village and specialist-settlement affinity.

## Stage 7 — Renaissance / Clockwork family

Establish:

- polders;
- hydraulic canals;
- formal terraces;
- vineyards/orchards;
- glass sand/quarry resources;
- mechanical/clockwork structure affinity.

## Stage 8 — Industrial family

Establish:

- rail cuts and embankments;
- slag/spoil/tailings systems;
- quarries;
- channelized waterways;
- industrial resource budget;
- factory/warehouse/rail infrastructure affinity.

## Stage 9 — Atomic / Post-collapse family

Establish:

- crater systems;
- glassed ground;
- trench scars;
- rubble/collapse deposition;
- ruined hydrology;
- succession/mutant ecology;
- bunker/reactor/ruin affinity.

## Stage 10 — Advanced Sci-fi family

Establish:

- engineered terrain terraces;
- crystal/geode systems;
- synthetic ecology;
- spaceport pads and infrastructure-ready flats;
- arcology/research affinity;
- advanced owned resource families.

## Stage 11 — Neon / Virtual family

Establish:

- grid terrain primitives;
- geometric ravines;
- luminous canal/pulseway corridors;
- circuit forest ecology;
- glass/crystal deposition;
- data spires;
- scalable city-grid terrain support;
- Grid Core Metropolis as a showcase integration of terrain + infrastructure + structures.

## Stage 12 — Villagers, technologies, structures and integrations

Once the underlying terrain families exist:

- village/settlement placement;
- profession/trade extensions;
- era-appropriate structures;
- technology blocks/items;
- resource processing recipes;
- road/rail/canal integration;
- structure affinity through Continuity Works context;
- optional mod compatibility adapters.

Do not use structure generation as a substitute for missing terrain identity.

## Stage 13 — Family transitions and distribution balance

Required:

- biome adjacency review;
- family coverage budgets;
- no one family dominates default Overworld generation;
- transition/ecotone features;
- resource output normalization;
- structure-density normalization;
- performance review.

## Stage 14 — Export readiness

The final export-ready state requires:

- ordinary Forge JAR build;
- normal `mods/` loading;
- default biomes enabled;
- all config toggles generated automatically;
- no user preflight;
- no required repository automation;
- no GitHub Actions dependency;
- no missing runtime resources;
- documentation for config and biome families;
- plug-and-play runtime behavior.

---

# 15. First Procedural Acceptance Queue

This is the exact queue to resume implementation after this tracker is committed.

## Queue 1 — repair existing incomplete Abyssal chain

1. `ABY-FIX-001` — add Wood Fall final biome modifier.
2. Read back modifier from `main`.
3. Update this tracker from `PARTIAL` to `COMMITTED / ACCEPTANCE_PENDING`.

## Queue 2 — make Abyssal biomes actually naturally selectable

1. `ABY-FIX-002A` — design dedicated/additive Abyssal TerraBlender parameter mapping.
2. `ABY-FIX-002B` — implement west/east continental slopes.
3. `ABY-FIX-002C` — implement west/east Abyssal plains.
4. `ABY-FIX-002D` — implement fracture fields.
5. `ABY-FIX-002E` — implement hadal trenches.
6. Ensure individual config toggles gate each mapping.
7. Commit each bounded mapping stage.
8. Read back.
9. Update tracker.

## Queue 3 — generalized land terrain core

1. `TFS-CORE-001` SafeSurfacePlacement helper.
2. `TFS-CORE-002` WorldField deterministic coordinate helper.
3. `TFS-CORE-004` TerrainProtection classifier.
4. `TFS-CORE-007` LandTerrainFeatures registry.
5. Commit and tracker update.

## Queue 4 — first foundation biome acceptance

**Temperate Grove**

1. Rolling Knolls & Hollows.
2. Fallen Log / Root Plate ecology.
3. Mossy Erratic/Boulder Field.
4. Spring/Swale micro-hydrology.
5. Resource exposure budget.
6. Structure-affinity tags.
7. Commit each reusable primitive individually.
8. Attach to Temperate Grove through additive biome modifiers.
9. Update tracker.

Then repeat the same disciplined sequence for Flowering Meadow through Ash Wastes.

## Queue 5 — begin anthology only after generalized primitives are real

Start Family A — Primordial in 2–4 biome micro-batches.

Recommended first batch:

- Flintgrass Steppe
- Giant Fern Basin
- Karst Hunterlands
- Redwood Primeval

This batch intentionally exercises open terrain, dense ecology, karst deformation and giant-tree ecology before the remaining primordial variants are committed.

---

# 16. Completion Dashboard

## 16.1 Biome totals

| Category | Target | Committed registry | Natural placement accepted | Finished richness contract |
|---|---:|---:|---:|---:|
| Foundation land | 8 | 8 | 0 formally accepted | 0 |
| Abyssal primary | 8 | 8 | 0 formally accepted | 0 |
| Primordial anthology | 16 | 0 | 0 | 0 |
| Ancient anthology | 16 | 0 | 0 | 0 |
| Medieval anthology | 16 | 0 | 0 | 0 |
| Renaissance/Clockwork | 16 | 0 | 0 | 0 |
| Industrial | 16 | 0 | 0 | 0 |
| Atomic/Post-collapse | 16 | 0 | 0 | 0 |
| Advanced sci-fi | 16 | 0 | 0 | 0 |
| Neon/Virtual | 16 | 0 | 0 | 0 |
| **Total primary** | **144** | **16** | **0 formally accepted** | **0** |

This table is intentionally conservative. It records accepted reality rather than optimistic generation counts.

## 16.2 Terrain system totals

| System | Committed | Planned/required |
|---|---:|---:|
| Abyssal landmark structures | 2 | additional Infinite Domain catalog items remain |
| Abyssal reusable procedural feature identities | 9+ | additional catalog items remain |
| General land terrain primitives | 0 | 10 deformation + helper layer |
| General land deposition primitives | 0 | 9 initial |
| General continuous land channels | 0 | 8 initial |
| General land ecology primitives | 0 | 8 initial |
| General resource geology primitives | 0 | 8 initial |

## 16.3 Immediate known incomplete items

- [ ] OSF-049 Wood Fall final Forge biome modifier.
- [ ] Abyssal family natural TerraBlender placement.
- [ ] Formal local compile/runtime acceptance of newly committed Abyssal Java feature families.
- [ ] Shared land terrain helper layer.
- [ ] Terrain enrichment of all eight foundation biomes.
- [ ] All 128 anthology biomes.
- [ ] Anthology ore/material progression.
- [ ] Anthology villager/settlement system.
- [ ] Era-specific technology features.
- [ ] Era-specific structure integration.
- [ ] Family transition and distribution balancing.
- [ ] Final plug-and-play export JAR acceptance.

---

# 17. Tracker Update Template

Use this block whenever an item advances:

```text
TRACKER ITEM:
NAME:
PREVIOUS STATUS:
NEW STATUS:
IMPLEMENTATION COMMIT:
FILES:
READ-BACK: PASS / FAIL
COMPILE: PASS / FAIL / NOT RUN
RUNTIME LOAD: PASS / FAIL / NOT RUN
WORLDGEN: PASS / FAIL / NOT RUN
CONFIG TOGGLE: PASS / FAIL / NOT RUN / N/A
NON-DESTRUCTIVE COMPATIBILITY: PASS / FAIL / NOT RUN
KNOWN LIMITATIONS:
NEXT ITEM:
```

If a step fails, preserve the last good commit, record the failure, apply the smallest non-destructive correction, then continue the same tracker item.

---

# 18. Definition of Final Success

Biome Expander is considered fully built out when:

- the 144 primary biome target is implemented or deliberately revised in this tracker;
- every enabled biome can participate in intended natural generation;
- every biome has a meaningful terrain/ecology/resource identity;
- terrain systems are reusable instead of copied into hundreds of one-off generators;
- custom ores and resource budgets remain balanced;
- villages and technology features reflect biome/era identity without appearing everywhere;
- structures use terrain affinity rather than replacing terrain generation;
- Abyssal seafloor complexity remains available as one layer of the broader terrain system;
- vanilla and third-party compatibility remains additive;
- individual biome toggles work for new generation;
- the finished mod loads conventionally from `mods/`;
- no user-side validation or configuration verification is required;
- no GitHub Actions are required;
- all significant implementation progress is represented by committed source plus a tracker state update.

Until those conditions are met, this document should make the remaining work visible rather than allowing intended work to disappear into conversation history.
