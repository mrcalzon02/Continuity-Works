# Hero Structure Specification — E01-004 Temporary Brush Shelter

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 4 of 750
Structure ID: `cw:e01_temporary_brush_shelter`
Primary family: habitation / ephemeral constructed shelter
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate only as an explicitly registered child of one early-human camp reservation sharing parent placement, exclusion ownership, and deterministic layout.

## Purpose

Temporary Brush Shelter is the catalog's first primarily human-constructed shelter. It represents a deliberately assembled, short-lived enclosure or cover made from branches, brush, grasses, leaves, bark-like materials, hides where culturally valid, and opportunistically placed stones. Its purpose is immediate protection from wind, precipitation, sun, cold, insects, or visual exposure rather than durability.

Its hero identity is construction with almost no architecture: a small human-made microclimate fitted to terrain. It must remain visibly more ephemeral than later huts, lodges, tents, longhouses, or permanent dwellings, and more constructed than E01-001 Rock Overhang Camp, E01-002 Cave Mouth Occupation, or E01-003 Deep Cave Refuge.

## Historical / Technological Context

The archetype represents Lower Paleolithic / early-human shelter behavior using materials that can be gathered, broken, carried, leaned, bent, piled, weighted, or draped without assuming advanced woodworking.

Permitted capabilities include opportunistic poles and branches, brush bundles, leafy or grassy cover, simple hide cover where culture rules allow, stone weights, shallow bedding, hearth use near rather than inside poorly ventilated variants, and exploitation of trees, boulders, banks, fallen trunks, or terrain hollows as structural anchors.

The base template must not imply sawn lumber, dimensional planks, formal joinery, nails, metal, ceramic, masonry, doors, hinges, windows, engineered chimneys, deep post foundations, woven architectural panels unless explicitly supported by a later archetype, permanent flooring, standardized modules, or settlement-scale construction.

## Archetype Boundary Contract

A valid Temporary Brush Shelter must satisfy all of the following:

1. More than half of the shelter-defining enclosure is deliberately assembled rather than naturally occurring.
2. Construction remains light, irregular, repairable, and plausibly achievable with extremely simple tools.
3. Terrain or natural anchors materially influence form; freestanding geometry is possible but should be less common.
4. Interior usable area is small and directly related to immediate occupants.
5. The structure has no permanent architectural circulation system or formal room plan.
6. Weather orientation is legible in wall density, opening direction, roof pitch, shade geometry, or anchor selection.
7. Removal or decay of organic cover would leave little durable architecture.

Reject or reclassify candidates that read as durable huts, tents with sophisticated frames, fenced compounds, storage buildings, or natural shelters with only incidental brush.

## Footprint and Scale Classes

### S — Individual / Pair Shelter
- External footprint: 3–6 by 3–6 blocks.
- Covered usable area: 4–14 blocks.
- Height: 2–4 blocks.
- Occupancy: 1–2 individuals.
- Forms: lean-to, brush screen with partial roof, tree-base shelter, boulder-backed shelter.
- Hearth: normally external; optional nearby fire.

### M — Small Group Shelter
- External footprint: 5–9 by 4–8 blocks.
- Covered usable area: 12–30 blocks.
- Height: 2–5 blocks.
- Occupancy: 2–6 individuals.
- Default hero scale.
- Forms: asymmetric A-like brush frame, curved wind shelter, double-anchor lean-to, low dome analogue, fallen-trunk shelter.
- May include a distinct bedding zone and exterior work/hearth patch.

### L — Extended Temporary Shelter
- External footprint: 8–14 by 6–12 blocks.
- Covered usable area: 28–70 blocks.
- Height: 3–6 blocks.
- Occupancy: 5–12 individuals.
- Must remain one shelter or a tightly coupled cover system, not a permanent house.
- Increased scale should add irregular bays, multiple anchors, partial screens, and repair layers rather than formal rooms.

## Architectural / Behavioral Program

The program is organized around shelter performance rather than rooms:

1. **Weather face** — densest barrier against prevailing wind, rain, snow, or sun.
2. **Protected opening** — entrance/open side oriented away from dominant exposure or toward desired solar gain/view.
3. **Structural anchors** — trees, rocks, fallen trunks, branch forks, terrain banks, or a minimal freestanding pole frame.
4. **Cover plane** — layered brush/leaf/grass/hide analogue that sheds weather or produces shade.
5. **Sleeping/rest pocket** — driest protected floor, usually against the sheltered side.
6. **Bedding layer** — optional leaves, grasses, hides, or equivalent target-system material.
7. **Stone weighting / brace points** — sparse stabilization at cover edges or pole feet.
8. **Exterior hearth zone** — normally offset from the opening so smoke does not fill the shelter or ignite cover.
9. **Work patch** — optional small exterior daylight zone.
10. **Drainage edge** — shelter must avoid or redirect only trivial surface flow through placement; no engineered ditch network.
11. **Material discard/repair patch** — optional loose branches or exhausted cover near the structure.

## Required Components

Hero admission requires:
- a deliberate assembled cover or screen defining protected space;
- at least one structural anchor relationship;
- a readable opening/access side;
- a protected usable floor;
- orientation responsive to local weather/environment proxies;
- locally plausible organic materials;
- irregular/non-industrial construction;
- no later-era construction technology;
- stable traversable geometry without floating cover elements.

M/L variants additionally require at least two readable functional zones among sleeping, exterior hearth, work patch, repair/material patch, or secondary sheltered bay.

Recommended probabilistic components include bedding, exterior hearth/ash trace, stone weights, branch stockpile, lithic scatter, food/bone traces, windbreak extension, repaired cover layers, and compacted entrance ground.

## Procedural Generation Logic

### 1. Candidate micro-site search
Score terrain cells for dryness, local slope, wind exposure, solar/shade context, flood risk, vegetation/resource availability, anchor objects, nearby usable ground, access, and structure reservation conflicts. Reject sites requiring major terrain flattening.

### 2. Exposure-vector derivation
Derive a deterministic dominant exposure vector from biome/climate inputs and local terrain. Depending on environment this may represent prevailing wind, precipitation direction, cold exposure, or solar load. The shelter's dense face should oppose harmful exposure while its opening favors protection, useful warmth, or visibility.

### 3. Anchor classification
Classify available anchor topology as:
- `TREE_SINGLE`
- `TREE_PAIR`
- `BOULDER`
- `FALLEN_TRUNK`
- `BANK_SLOPE`
- `ROCK_TREE_COMPOSITE`
- `FREESTANDING_MINIMAL`

Prefer natural anchors when available. Never modify a third-party structure to create an anchor.

### 4. Form selection
Choose a form compatible with anchors and climate:
- single-plane lean-to;
- curved brush screen plus partial cover;
- low ridge/A-like cover;
- boulder-backed half enclosure;
- fallen-trunk roof/screen;
- tree-pair suspended/leaned cover analogue;
- low brush dome analogue;
- shade canopy in hot/dry settings.

Forms must be asymmetric through terrain fit, material variation, edge damage, and nonuniform cover density.

### 5. Structural skeleton pass
Place the smallest plausible branch/pole skeleton. Validate support chains from cover blocks to anchors/ground. No unsupported floating organic masses. Avoid perfectly repeated spacing.

### 6. Cover-density pass
Generate a cover field with three bands: structural core, weather-facing dense cover, and feathered/patchy edges. Climate determines required density. Openings must remain readable and traversable.

### 7. Floor/use-zone pass
Preserve natural ground. Select the driest protected interior cells for rest/bedding. Minimal local clearing is allowed; broad flooring or foundation construction is not.

### 8. Fire-safety pass
If a hearth is generated, place it outside or at a safely open edge, with clearance from combustible cover and a smoke path away from the interior. Fully enclosed brush shelters should strongly suppress hearth generation.

### 9. Human-use evidence pass
Distribute sparse occupation evidence using deterministic substreams: bedding, lithic scatter, branch repair pile, food/bone trace, stone weights, compacted entrance, and ash.

### 10. Weathering/condition pass
Apply condition after structural logic so damage removes or sags cover without destroying the archetype's readable construction logic.

### 11. Terrain integration and reservation pass
Blend only minimally into terrain. Preserve existing vegetation/geology outside the negotiated footprint. Reserve a minimum 500-block radius against unrelated independent structures; registered camp-family children share one parent reservation rather than stacking exclusions.

## Seed Determinism

Identical world seed, structure seed, generator version, biome/environment context, culture configuration, and condition configuration must reproduce site, anchor selection, form, orientation, skeleton, cover density, use zones, and condition.

Recommended named substreams:
- `site_candidate`
- `exposure_vector`
- `anchor_topology`
- `scale`
- `form`
- `skeleton`
- `cover_density`
- `opening`
- `bedding`
- `hearth`
- `occupation_trace`
- `condition`
- `culture_hook`

Later decorative additions must not reshuffle primary geometry.

## Biome / Environment Adaptations

### Temperate forest
Abundant branches/leaves; tree-anchored forms common; strong rain-shedding pitch; damp-ground rejection; leafy bedding and repair piles likely.

### Boreal / cold forest
Denser low walls, smaller openings, steeper or layered cover, stronger hearth association outside entrance, conifer-like branch palette where available, and wind exposure strongly weighted.

### Tundra / alpine
Sparse timber lowers frequency or forces low stone-weighted brush/hide forms. Shelters hug boulders/banks, remain low, and orient aggressively against wind. Do not invent timber abundance.

### Savanna / dry grassland
Shade and wind protection dominate; lighter cover and more open sides; branch/grass materials; larger shaded work/rest area relative to enclosed volume.

### Arid / desert
Generation requires plausible gathered material or imported organic material under culture hooks. Boulder/bank shade shelters favored. Sparse brush cover and stone weighting dominate; flash-flood channels rejected.

### Tropical / humid
High ventilation, steep rain-shedding cover, raised density only overhead rather than sealed walls, rot-prone condition logic, and drainage strongly weighted.

### Coastal
Wind exposure and salt/storm conditions influence orientation. Driftwood-like anchors/materials may be used where target palette supports them. Storm-surge and tidal zones are rejected.

### Snow conditions
Snow-load proxy increases pitch/support density and may add partial snow banking in occupied condition, but the base structure cannot become a later snow-house archetype.

## Culture-Variant Hooks

Culture packs may alter preferred shelter form, group size, opening orientation priorities, hide versus vegetation cover probability, branch selection, bedding arrangement, hearth relationship, repair behavior, reuse frequency, stone-weight pattern, and camp-family associations.

Culture hooks cannot introduce later joinery, woven wall architecture beyond era support, standardized house plans, permanent foundations, symbolic decoration unsupported by the era, or claims tied simplistically to modern ethnic identities.

## Material Palette Logic

### Structural organics
Use locally available branch/log analogues at primitive scale. Structural members should look gathered or broken rather than milled. Palette weighting follows biome vegetation.

### Cover
Use leaves, brush, grasses, bark-like blocks, hide/fur analogues where supported, snow as environmental overlay, and limited earth/duff only as edge weighting. Cover must not resemble tiled roofing.

### Stone
Use local loose stone for weights, braces, hearth edging, or sleeping-edge stabilization. No coursed masonry.

### Ground
Retain local soil, grass, sand, gravel, snow, or rock with only small cleared/compacted patches.

Forbidden base materials include planks, bricks, cut masonry, glass, metal fittings, doors, chests, barrels, lanterns, permanent torches, powered blocks, formal stairs, manufactured furniture, or standardized roofing.

## Condition Variants

### Active / intact
Fresh dense cover, readable bedding, stocked repair branches, clear entrance, recent occupation traces.

### Maintained / repeatedly reused
Patchwork cover of different ages, replaced braces, compacted entrance, multiple hearth traces, accumulated material pile.

### Temporarily vacant
Structure remains mostly weatherproof but bedding and cover begin to settle; hearth cold; minor vegetation intrusion.

### Weather-damaged
Wind/rain/snow removes sections of cover, bends frame, exposes one side, and scatters organic material along plausible vectors.

### Partially collapsed
One structural anchor or frame segment fails; roof/cover sags toward support loss while enough geometry remains to identify the shelter.

### Abandoned / decayed
Most soft cover disappears, frame fragments remain, bedding decays, vegetation returns, and durable traces are limited to stones, ash, and artifact scatter.

### Archaeological trace
Only stone weights, post/anchor impressions where representable, charcoal, compacted floor, and sparse artifact concentrations remain. This state must not falsely display preserved timber in climates where it is implausible.

### Later-era repurposed
A later occupant may reuse the location or surviving anchors through an explicit overlay. The original shelter trace remains recoverable; the later structure is additive and cannot overwrite the archetype record.

## Jigsaw / Family Relationships

Default placement is standalone with a 500-block exclusion radius against unrelated independent structures.

Compatible children under one shared camp reservation may include:
- E01-007 Hearth Circle;
- E01-009 Stone Tool Knapping Ground;
- E01-012 Butchery Site;
- E01-015 Bone-Breaking Station;
- E01-027 Tool-Stone Cache;
- E01-028 Food Cache Pit;
- small refuse scatter;
- water-access path marker.

Natural shelters E01-001 through E01-003 may occur in the same broader cultural landscape but are not automatically exempt from exclusion. A family exemption requires explicit parent composition.

E01-005 Lean-To Windbreak is a distinct subsequent archetype and must not be swallowed by this template: E01-004 prioritizes overhead/combined shelter, while E01-005 will prioritize directional wind protection with lean-to behavior.

## Infrastructure Dependencies

Required built infrastructure: none.

Preferred environmental dependencies are gatherable shelter material, stable dry ground, one or more anchor opportunities, safe access, optional nearby water, optional fuel, and optional work/hunting/foraging territory.

Roads, formal paths, agriculture, permanent drainage, utilities, fences, settlement grids, and engineered foundations are invalid dependencies.

## Loot / Occupancy Hooks

Loot represents carried necessities and occupation traces rather than treasure. Potential finds include raw toolstone, simple stone-tool proxies, flakes/debitage, bone fragments, charcoal/ash, small food remains, hide/fiber fragments where supported, and gathered fuel/branches.

No chest/container is required or preferred. Finds should appear in bedding edges, small caches, work patches, hearth deposits, or archaeology-aware target-system deposits.

Occupancy must respect protected floor area and fire safety. Spawn logic should avoid placing occupants inside cover blocks or outside the shelter's functional relationship.

## Additive / Non-Destructive Compatibility

- Enforce the default minimum 500-block exclusion against unrelated independent structures.
- Compatible camp-family children may violate that distance only through explicit shared-parent registration.
- Do not clear third-party structures, trees, terrain features, roads, caves, or infrastructure to force placement.
- Candidate failure causes rejection or reselection, not destructive adaptation.
- Existing terrain may be used as an anchor only when doing so requires no destructive mutation outside the structure's owned footprint.
- Compatibility integrations add candidate anchors, palette mappings, or family relationships; they do not replace the core generator.
- Never silently overwrite another system's reserved volume.

## Validation Criteria

### Geometry
- All structural cover has plausible support/anchor chains.
- Entrance is traversable.
- Protected floor is reachable and usable.
- No floating branch/brush masses.
- No impossible roof spans for the chosen primitive form.

### Archetype distinction
- More constructed than E01-001 through E01-003.
- Less durable/formal than later huts, tents, lodges, and houses.
- Primarily overhead/combined shelter rather than only a directional windbreak.

### Historical/technological fitness
- No later-era materials or joinery.
- Construction can plausibly be assembled with simple gathering, breaking, carrying, leaning, weighting, and draping behavior.
- Scale remains appropriate to immediate temporary occupancy.

### Environmental fitness
- Orientation responds to exposure proxy.
- Floor avoids obvious flood/runoff hazards.
- Materials are locally plausible or explicitly culture-carried.
- Hearth placement passes combustible-clearance logic.

### Procedural
- Deterministic replay passes.
- S/M/L classes remain within bounds.
- Form selection responds to anchor topology rather than stamping one universal shape.
- Condition overlays do not alter deterministic base-layout selection.

### Compatibility
- 500-block exclusion passes for unrelated structures.
- Shared-family exceptions prove common parent reservation.
- Third-party terrain/structure ownership remains intact.

### Visual/readability
A reviewer should identify an intentionally constructed, temporary early-human shelter without labels, understand its weather-facing side and entrance, and see why it occupies that micro-site.

## Production-Readiness Requirements

Hero specification completion does not equal runtime production admission.

Production admission requires observed evidence of:
1. implemented generator/template representation in the authoritative runtime path;
2. deterministic seed replay across representative seeds;
3. successful S/M/L generation;
4. all anchor classes intended for release exercised or explicitly deferred;
5. biome adaptation validation across forest, cold, open/dry, humid, and sparse-material environments;
6. support-chain validation with no floating cover;
7. fire-safety validation where hearths generate;
8. active, damaged, collapsed, abandoned, and archaeological conditions exercised;
9. 500-block exclusion validation;
10. explicit shared-parent family exception validation;
11. third-party/non-destructive compatibility test;
12. visual review from exterior weather face, opening, and interior rest zone;
13. target load/export validation;
14. no unresolved blocker in production ledger.

Until those are observed, production status remains `IMPLEMENTATION_PENDING`.

## Hero Acceptance Checklist

- [x] Purpose defined.
- [x] Historical/technological limits defined.
- [x] Archetype boundary contract defined.
- [x] S/M/L footprint and occupancy classes defined.
- [x] Architectural/behavioral program defined.
- [x] Required and probabilistic components defined.
- [x] Terrain/anchor/exposure-driven procedural logic defined.
- [x] Seed determinism contract defined.
- [x] Biome/environment adaptations defined.
- [x] Culture hooks defined.
- [x] Material palette logic defined.
- [x] Intact, damaged, ruined/decayed, archaeological, and repurposed states defined.
- [x] Jigsaw/family relationships defined.
- [x] Infrastructure dependencies defined.
- [x] Loot/occupancy hooks defined.
- [x] 500-block exclusion and family exception defined.
- [x] Additive/non-destructive compatibility defined.
- [x] Validation criteria defined.
- [x] Production-readiness gates defined.

Hero specification status: **COMPLETE**.
Runtime production status: **IMPLEMENTATION_PENDING**.
