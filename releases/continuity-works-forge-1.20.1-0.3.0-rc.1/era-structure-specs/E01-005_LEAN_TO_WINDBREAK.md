# Hero Structure Specification — E01-005 Lean-To Windbreak

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 5 of 750
Structure ID: `cw:e01_lean_to_windbreak`
Primary family: habitation support / directional shelter
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate only inside an explicitly composed early-human camp reservation with shared parent ownership and deterministic layout.

## Purpose

Lean-To Windbreak represents the smallest clearly intentional built shelter whose dominant function is directional protection from wind rather than complete enclosure or overhead weatherproofing. It should read as an adaptive barrier first and a shelter second: a sparse framework leaned against terrain, a tree, boulder, fallen trunk, or simple support line, with brush, hide, reeds, grasses, or branches arranged to reduce wind exposure around a sleeping, working, or hearth zone.

Its identity depends on asymmetric orientation toward a prevailing exposure vector. It must remain open on at least one major side and should normally preserve an obvious relationship between protected lee space and exposed windward face.

Compared with E01-004 Temporary Brush Shelter, this archetype provides less enclosure and substantially less roof coverage. If the generated form encloses occupants on most sides or creates a substantial roofed interior, it has crossed into Temporary Brush Shelter territory and must be rejected or reclassified.

## Historical / Technological Context

The archetype represents extremely early, low-investment construction using gathered local material and opportunistic anchors. Valid technologies include hand-placed branches, brush, reeds, grass bundles, hides where culturally supported, stones used as weights, forked sticks, fallen timber, and simple leaning or wedging.

The template must not imply shaped lumber, joinery, permanent posts with sophisticated foundations, woven wall panels beyond the consuming culture's permitted technology ceiling, masonry, doors, formal flooring, chimneys, ceramic storage, metal fasteners, or fixed furniture.

The hero quality comes from environmental reasoning: site selection, wind reading, orientation, anchor use, material economy, fire relationship, and believable wear.

## Archetype Boundary Contract

A valid Lean-To Windbreak must satisfy all of the following:

1. **Directional purpose** — the structure has a clearly identifiable windward face and protected lee side.
2. **Open-sided form** — at least one major side remains substantially open.
3. **Partial overhead cover** — roof-like cover may occur locally but cannot dominate the structure.
4. **Minimal framework** — structural members remain sparse and irregular.
5. **Local adaptation** — geometry responds to terrain and available anchors.
6. **Temporary character** — the build should look repairable, replaceable, and low-investment.
7. **No durable dwelling semantics** — no formal doorway, room, permanent wall set, or enclosed sleeping chamber.

## Footprint and Scale Classes

### S — Personal Windbreak
- Barrier length: 3–7 blocks.
- Height: 1–3 blocks.
- Protected lee depth: 2–5 blocks.
- Reservation footprint: 8–14 by 8–14 blocks.
- Likely occupancy: 1–3 individuals.
- Overhead coverage: normally under 20% of protected area.

### M — Household Lean-To
- Barrier length: 6–12 blocks.
- Height: 2–4 blocks.
- Protected lee depth: 4–8 blocks.
- Reservation footprint: 12–22 by 10–20 blocks.
- Likely occupancy: 3–8 individuals.
- Overhead coverage: normally under 35%.
- Default hero scale.

### L — Group Windbreak Line
- Barrier length: 10–22 blocks, optionally kinked or segmented.
- Height: 2–5 blocks.
- Protected lee depth: 5–12 blocks.
- Reservation footprint: 18–34 by 14–28 blocks.
- Likely occupancy: 6–16 individuals.
- May include two linked barriers forming a shallow angle, but must remain open and directional.
- Overhead coverage: normally under 40%.

Large variants should increase protected frontage and social use rather than become hut-sized enclosures.

## Architectural / Behavioral Program

1. **Windward barrier face** — primary constructed surface facing the exposure vector.
2. **Support/anchor line** — boulder, tree, trunk, forked sticks, slope, or sparse post/branch supports.
3. **Lean geometry** — members slope toward or against an anchor rather than forming a vertical finished wall.
4. **Protected lee pocket** — principal occupation area immediately downwind.
5. **Sleeping/rest patch** — optional flattened or bedded zone in the lee.
6. **Hearth relationship** — optional small hearth placed where the barrier reduces wind without trapping smoke or risking ignition.
7. **Work patch** — optional knapping, food-processing, or repair area.
8. **Material/fuel cache** — optional branches, brush, stone, or fuel kept near an end of the barrier.
9. **Open circulation edge** — at least one unobstructed side for entry/exit.
10. **Repair edge** — localized evidence of added brush, replacement branches, stones, or lash-point proxies.

## Required Components

Hero admission requires:
- one directional barrier or lean-to plane;
- an explicit protected lee zone;
- a deterministic exposure vector driving orientation;
- at least one plausible anchor/support relationship;
- open-sided circulation;
- locally plausible material selection;
- no later-era manufactured elements;
- no enclosure geometry that would qualify as E01-004.

M/L variants additionally require:
- readable relationship between barrier, occupation zone, and prevailing wind;
- at least one secondary behavioral zone such as sleep, hearth, work, or cache;
- structural support validation across the full leaned face.

Recommended probabilistic components:
- weighted base stones;
- brush/thatch infill;
- hide patching;
- shallow bedding;
- fuel stack;
- ash patch or hearth;
- repair patches;
- trampled ground;
- scattered stone-tool debris.

## Procedural Generation Logic

### 1. Micro-site scoring

Evaluate candidate sites for:
- wind exposure potential;
- available natural anchors;
- ground slope;
- drainage;
- flood risk;
- nearby fuel/brush availability;
- fire safety;
- clear lee-side occupancy space;
- access to water/resources;
- absence of conflicting reservations.

Reject sites that require broad terrain flattening or destructive removal of existing features.

### 2. Exposure-vector derivation

Generate a deterministic local exposure vector from available environmental inputs. Preferred sources, in priority order:
- biome/climate wind metadata if available;
- terrain-channel inference from valleys, passes, coasts, ridgelines, or open plains;
- configured regional weather vector;
- deterministic seed-derived fallback constrained by terrain openness.

The structure's windward face should oppose the dominant exposure vector within a bounded angular tolerance. Perfect cardinal alignment is not required or preferred.

### 3. Anchor classification

Select one anchor family:
- `TREE_TRUNK`
- `FALLEN_LOG`
- `BOULDER`
- `ROCK_FACE`
- `SLOPE_BANK`
- `FORKED_BRANCH_SUPPORT`
- `SPARSE_FREE_STANDING_SUPPORT`

Natural anchors are preferred over free-standing construction where available.

### 4. Barrier skeleton generation

Create an irregular support chain sized to scale class. Members should vary slightly in spacing, height, and angle while preserving physical plausibility.

Rules:
- no perfectly straight long wall unless forced by a natural anchor;
- no identical repeated spacing;
- no fully vertical palisade appearance;
- each primary member must terminate against ground, anchor, or supporting member;
- unsupported floating members are invalid.

### 5. Lean-plane construction

Generate one dominant leaned plane or partial segmented plane. Angle should respond to material and anchor family.

Cover density is allowed to vary:
- low density: sparse branches/brush, strongest airflow but weak protection;
- medium density: layered brush/reeds/grasses;
- high density: tightly layered organic material for cold/exposed environments.

Even high-density variants must retain rough permeability and temporary character.

### 6. Lee-zone extraction

Project the barrier's protected region downwind using barrier height, length, orientation, and local terrain. Place occupation behavior only where the generated wind-shadow proxy is meaningful.

### 7. Hearth placement

Optional hearth placement must satisfy:
- sufficient distance from flammable wall material;
- adequate upward and leeward smoke escape;
- no placement directly against a hide/brush panel;
- protection from strongest wind gusts;
- no blockage of circulation.

If safe placement is unavailable, generate a no-fire variant.

### 8. Occupation zoning

Use deterministic named zones:
- `windward_face`
- `anchor_line`
- `lee_core`
- `sleep`
- `hearth`
- `work`
- `cache`
- `circulation`
- `repair`

Small variants may merge sleep/work/lee core.

### 9. Weathering and use pass

Condition logic may introduce:
- sagging infill;
- missing brush;
- shifted weights;
- snapped supports;
- repaired sections;
- trampled lee ground;
- ash scatter;
- windblown litter accumulation on the protected side.

### 10. Reservation and compatibility pass

Reserve the structure and enforce the Continuity Works minimum 500-block exclusion against unrelated independent structures.

Only explicitly registered camp-family children may share the parent reservation. The exception cannot propagate to unrelated structures.

## Seed Determinism

Identical seed, generator version, biome/environment state, culture configuration, condition configuration, and parent reservation must reproduce orientation, anchor type, scale, skeleton, material density, zone layout, and condition state.

Recommended named random substreams:
- `site`
- `exposure_vector`
- `anchor`
- `scale`
- `skeleton`
- `cover_density`
- `occupation_layout`
- `hearth`
- `repair`
- `condition`
- `culture_hook`

Decorative changes must not reshuffle primary geometry.

## Biome / Environment Adaptations

### Temperate forest
- Tree/fallen-log anchors common.
- Brush and leaf material abundant.
- Medium cover density.
- Drainage and damp bedding penalties matter.

### Boreal / cold
- Barrier height and cover density increase.
- Lean angle may become steeper for snow shedding.
- Hearth probability rises where safe.
- Lee pocket becomes more compact.

### Tundra / alpine
- Stone/boulder anchors and weighted hides/brush become more common.
- Sparse timber reduces long framework members.
- Low-profile barriers resist wind better.
- Exposure-vector fidelity is especially important.

### Savanna / grassland
- Grass/reed infill common.
- Barrier may be longer and lower.
- Shade is secondary; airflow reduction remains primary.

### Arid / desert
- Brush may be sparse.
- Rock/slope anchors preferred.
- Windblown sand deposition can accumulate on lee side.
- Fire variants are less common where fuel is scarce.

### Tropical / humid
- Ventilation remains important, so cover density decreases.
- Drainage and rot penalties increase.
- Rapid material decay strengthens repair-state variation.

### Coastal
- Exposure may derive strongly from shoreline orientation.
- Driftwood/reed anchors and materials become possible.
- Salt/sand weathering should affect abandoned variants.

## Culture-Variant Hooks

Culture packs may modify:
- preferred barrier curvature;
- support spacing;
- cover density;
- hide vs brush weighting;
- hearth proximity norms;
- group sleeping arrangement;
- repair style;
- preferred anchor family;
- material carrying distance;
- repeated-use frequency.

Culture hooks cannot introduce shaped carpentry, durable walls, formal doors, masonry, permanent roofing, or later-period decorative motifs.

## Material Palette Logic

### Structural members
Use local or plausibly carried branches, small logs, driftwood, reeds bundled around supports where allowed, and occasional stones as weights.

### Infill
Use brush, grasses, reeds, leaf bundles, bark-like proxies, hides/furs where supported, and other lightweight organic material.

### Ground treatment
Use only minimal trampling, bedding material, ash, loose stones, and displaced vegetation. No formal floor.

### Forbidden base materials
No planks, bricks, cut-stone masonry, glass, metal, ceramics, doors, chests, barrels, permanent torches/lanterns, redstone/powered systems, formal slabs/stairs as furniture, or engineered roofing systems.

## Condition Variants

### Active / newly built
- taut or recently placed cover;
- readable windward/lee relationship;
- fresh bedding and fuel where present;
- minimal degradation.

### Maintained / repeatedly used
- patchwork repairs;
- denser trampled ground;
- replacement branches;
- multiple ash traces where hearths recur.

### Temporarily vacant
- intact structure with minor sag;
- cold hearth;
- residual bedding/cache traces.

### Weather-damaged
- partial infill loss;
- shifted stones;
- one or more bent supports;
- occupation zone still legible.

### Partially collapsed
- one section fallen into the lee side;
- enough geometry remains to identify the original windward plane.

### Abandoned
- heavy sag/rot;
- vegetation intrusion;
- scattered structural pieces;
- protected-ground signature fading.

### Archaeological trace
- post/branch impressions represented by target-valid proxies;
- weight stones;
- hearth/ash trace;
- localized artifact scatter;
- no implausible preservation of full organic walls unless environment supports it.

### Later-era repurposed
A later group may attach or reuse the windbreak location through an explicit overlay. Original early-human layout should remain recoverable and the overlay must be additive.

## Jigsaw / Family Relationships

Default placement is standalone with a minimum 500-block exclusion radius against unrelated structures.

Compatible same-parent children may include:
- E01-004 Temporary Brush Shelter;
- E01-007 Hearth Circle;
- E01-009 Stone Tool Knapping Ground;
- E01-012 Butchery Site;
- small sleeping patch;
- fuel/material cache;
- refuse scatter;
- water-access trail marker.

Relationships must be explicit. The Lean-To Windbreak must not silently absorb full functionality of another catalog archetype.

## Infrastructure Dependencies

Required infrastructure: none.

Preferred environmental dependencies:
- usable local anchor or support ground;
- readable exposure direction;
- dry enough lee-side occupation surface;
- nearby local organic material;
- optional fresh water/resource access.

Formal roads, utilities, engineered drainage, permanent settlement grids, agriculture, and durable foundations are invalid dependencies.

## Loot / Occupancy Hooks

Loot should represent use traces rather than storage treasure.

Possible finds:
- raw toolstone;
- flakes/debitage analogues;
- charcoal/ash;
- bone fragments;
- low-value food remains;
- hide/fiber fragments;
- gathered brush/fuel resources.

No chest is required or preferred. Finds should appear as floor scatter, cache nodes, hearth deposits, or work-zone traces.

Occupancy should remain low and proportional to lee-space capacity. The structure should not generate village-like population behavior.

## Validation Criteria

### Geometry
- every structural member is supported;
- barrier remains open-sided;
- leaned form is visually apparent;
- no dominant enclosed roof volume;
- protected lee space is traversable;
- no floating or mechanically impossible brush wall.

### Archetype distinction
- must not read as E01-004 Temporary Brush Shelter;
- must not become a palisade, fence, hut wall, or permanent dwelling;
- directional protection remains the primary function.

### Historical/technological fitness
- no later-era materials or joinery;
- construction remains low-investment and locally sourced;
- ground modification is minimal.

### Environmental fitness
- orientation opposes the exposure vector within configured tolerance;
- lee-side occupation occurs where wind-shadow proxy is meaningful;
- drainage and flood risks pass;
- hearth placement passes ignition/smoke rules.

### Procedural fitness
Before production admission, validate at least 100 deterministic seeds per supported biome family for:
- valid anchor/support chains;
- reproducible orientation;
- non-enclosed geometry;
- traversable lee zones;
- safe hearth/no-fire classification;
- clean reservation behavior;
- absence of destructive terrain edits.

### Compatibility
- verify minimum 500-block unrelated-structure exclusion;
- verify shared-parent camp exceptions only;
- verify third-party/world features are rejected around rather than overwritten when protected;
- verify composition does not allow family exemption leakage.

### Visual hero bar
- no perfect rectangular wall;
- no uniform support spacing;
- no repeated decoration stamp appearance;
- material density varies plausibly;
- the windward/lee relationship is readable from multiple angles;
- at least three seed examples should look structurally related but materially and geometrically distinct.

## Production-Readiness Requirements

Hero specification completion does not equal runtime production admission. Production admission requires:

1. registry/schema entry for `cw:e01_lean_to_windbreak`;
2. procedural/template implementation consistent with this specification;
3. deterministic seed tests;
4. exposure-vector/orientation tests;
5. anchor and support-chain validation;
6. non-enclosure/archetype-boundary tests against E01-004;
7. biome adaptation tests;
8. hearth ignition/smoke safety validation;
9. 500-block exclusion validation;
10. explicit same-parent family compatibility tests;
11. prohibited-material/technology audit;
12. active, maintained, damaged, collapsed, abandoned, archaeological, and repurposed state tests;
13. visual review of S/M/L examples;
14. export/load validation in the supported target environment;
15. no destructive compatibility regressions.

Until these are observed and verified, production status remains `IMPLEMENTATION_PENDING`.

## Hero Acceptance Checklist

- [x] Purpose defined.
- [x] Historical/technological ceiling defined.
- [x] S/M/L scale classes defined.
- [x] Directional windbreak identity established.
- [x] Architectural/behavioral program defined.
- [x] Required/probabilistic components defined.
- [x] Exposure-vector and anchor logic defined.
- [x] Procedural generation doctrine defined.
- [x] Biome adaptations defined.
- [x] Culture hooks defined.
- [x] Material restrictions defined.
- [x] Condition variants defined.
- [x] Family/jigsaw rules defined.
- [x] 500-block exclusion and shared-parent exception defined.
- [x] Loot/occupancy hooks defined.
- [x] Validation criteria defined.
- [x] Production-admission gates defined.
- [ ] Runtime implementation observed.
- [ ] Runtime validation observed.
- [ ] Production admission verified.
