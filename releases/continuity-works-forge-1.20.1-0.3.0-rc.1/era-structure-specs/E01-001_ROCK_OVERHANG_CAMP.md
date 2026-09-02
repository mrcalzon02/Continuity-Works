# Hero Structure Specification — E01-001 Rock Overhang Camp

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 1 of 750
Structure ID: `cw:e01_rock_overhang_camp`
Primary family: habitation / temporary camp
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate inside an explicitly composed early-human campsite complex when reservation ownership is shared by the same parent placement.

## Purpose

The Rock Overhang Camp is the first Continuity Works era archetype and establishes the minimum architectural threshold for a recognizable human-made place. It is not a house inserted beneath a cliff. It is a naturally selected shelter whose useful qualities have been amplified by repeated occupation: a defensible dry edge, fire control, sleeping area, tool work, food processing, refuse behavior, wind screening, and short-lived material additions.

The structure must read first as terrain and second as occupation. Human intervention should occupy a minority of the total visible mass while still producing an unmistakable functional pattern.

## Historical / Technological Context

This archetype represents highly mobile Lower Paleolithic groups using naturally protective terrain rather than constructing permanent architecture. Available technologies are deliberately limited: percussion stone tools, opportunistic timber, brush, hide where culture hooks permit it, fire, carried stone, bone, and simple storage/cache behavior.

The template must avoid anachronistic woodworking, masonry, shaped plank construction, formal doors, ceramic containers, agriculture, permanent fencing, sophisticated furniture, symmetrical floor plans, decorative monumentalism, or later-period hearth engineering.

The hero treatment is therefore derived from behavioral organization rather than construction complexity.

## Footprint and Scale Classes

### S — Opportunistic Refuge
- Reservation footprint: 14–22 blocks wide, 8–16 deep.
- Occupied floor: 35–90 usable blocks.
- Hearths: 0–1.
- Likely occupancy: 1–4 individuals.
- Intended use: overnight refuge, weather shelter, hunting pause.

### M — Household Camp
- Reservation footprint: 22–36 blocks wide, 12–24 deep.
- Occupied floor: 90–220 usable blocks.
- Hearths: 1–2.
- Likely occupancy: 4–10 individuals.
- Default hero scale.

### L — Repeated Group Camp
- Reservation footprint: 34–56 blocks wide, 18–34 deep.
- Occupied floor: 220–500 usable blocks.
- Hearths: 2–4.
- Likely occupancy: 8–20 individuals over one or multiple occupation episodes.
- May expose stronger refuse and work-zone patterning without becoming a permanent village.

Vertical clearance beneath the overhang should normally range from 3–10 blocks, with irregular local compression and expansion. Overhang thickness and rock mass must be sufficient that the shelter reads as geologically plausible rather than as a floating roof.

## Architectural Program

The structure is organized as a gradient from exposed exterior to protected interior rather than as rooms.

1. **Approach apron** — trampled or naturally open ground that connects surrounding terrain to shelter.
2. **Drip-line threshold** — the visible transition between exposed and protected ground.
3. **Primary hearth zone** — located far enough inside to resist rain but not so deep that smoke has no escape.
4. **Sleeping/rest zone** — drier, quieter interior edge with minimal traffic.
5. **Tool-working zone** — compact patch with lithic debris and usable seating stone/log opportunities.
6. **Food-processing zone** — may overlap hearth but should not consume the sleeping zone.
7. **Refuse edge** — peripheral discard concentration, preferably downhill or outward from occupation.
8. **Material cache** — optional stone, fuel, bone, or gathered-resource cache in a crevice.
9. **Windbreak attachment points** — optional brush/log/hide screen along one exposed side.
10. **Escape/secondary access** — only where terrain naturally supports it; never force a second doorway-like opening.

No element is guaranteed except protected floor, a readable occupation zone, and at least one human-use signal.

## Required Components

Hero admission requires:
- naturally integrated overhang or shallow rock shelter;
- dry/protected occupation floor with traversable access;
- one readable activity focus (hearth, knapping scatter, butchery trace, or sleeping bedding analogue);
- exterior/interior transition;
- at least two distinct behavioral sub-zones for M/L scales;
- no later-era manufactured blocks or implied technologies;
- terrain support beneath and behind the rock mass;
- navigable player clearance through the occupied area.

Recommended but probabilistic:
- hearth ring or ash patch;
- charred material;
- scattered stone-tool debris;
- bone remains;
- brush windbreak;
- fuelwood stack;
- sleeping vegetation/fur analogue;
- water proximity evidence;
- small cache niche.

## Procedural Generation Logic

### 1. Candidate terrain search
Prefer existing cliff faces, escarpments, ravine lips, boulder masses, canyon walls, and steep slopes. Score candidates for:
- rock ceiling depth;
- protected floor area;
- slope stability;
- exterior access;
- drainage;
- smoke egress potential;
- nearby water/resource access;
- absence of conflicting reserved structures.

The generator should reject a site rather than flatten unsuitable terrain into compliance.

### 2. Terrain-first formation
Where a world seed does not supply an adequate natural overhang, procedural terrain construction may extend the local geology, but must preserve stratigraphic/material continuity and irregularity. No freestanding rectangular canopy is permitted.

Use asymmetric erosion fields, weighted cellular masks, and low-frequency noise to define ceiling edge, wall recesses, fallen stones, and floor undulation. Generated geology should blend outward beyond the occupied footprint.

### 3. Occupation plane extraction
Determine the largest connected walkable protected surface. Preserve small slopes and natural obstacles. Only minimal leveling is allowed around the hearth and primary sleeping/work zones.

### 4. Behavioral zoning
Seed zones using distance fields:
- hearth: 2–6 blocks behind drip line, with overhead escape volume;
- sleeping: farther from approach traffic and refuse edge;
- tool work: adjacent to light/exterior but sheltered;
- refuse: outside primary circulation, biased downslope/downwind;
- cache: wall crevice or rear margin.

Zones may overlap at small scale but should become increasingly distinct for M/L variants.

### 5. Human intervention pass
Apply sparse, technology-valid additions. Maximum obvious constructed coverage should normally remain under 20–30% of occupied floor area.

### 6. Wear and occupation pass
Use compact irregular patches rather than decorative scatter. Repeated occupation may deepen ash, increase lithic debris, expose compacted floor, and produce multiple hearth ghosts.

### 7. Integration pass
Restore biome surface transitions around the reservation boundary, preserve watercourses, and avoid cutting roads, structures, or external terrain systems. Placement is additive and non-destructive outside its reserved generation volume.

## Seed Determinism

Given identical world seed, structure seed, era/culture configuration, biome context, and generator version, candidate choice, scale class, behavioral zones, component selection, weathering state, and orientation must reproduce exactly.

Random decisions must be derived from named deterministic substreams so later addition of optional decoration does not reshuffle primary geometry.

Recommended substreams:
- `geology`
- `scale`
- `occupation_layout`
- `hearth`
- `work_scatter`
- `organic_materials`
- `condition`
- `culture_hook`

## Biome / Environment Adaptations

### Temperate forest
Greater brush/timber availability, leaf/grass bedding, dampness-aware hearth position, heavier fuelwood traces.

### Boreal / cold
Deeper shelter preference, stronger windbreak probability, larger hearth probability, compact sleeping cluster, snow-sheltered threshold logic.

### Tundra / alpine
Sparse timber, stone-weighted windbreaks, hide hooks where culturally permitted, low-profile occupation, high exposure penalty in candidate scoring.

### Savanna / dry grassland
Shade value becomes a strong site-selection driver; brush screens are lighter; hearth may be peripheral; water-distance score becomes more important.

### Arid / desert
Prioritize thermal shade, canyon/rock shelters, minimal organic construction, dust/sand ingress, sparse fuel traces, stronger stone-use probability.

### Tropical / humid
Drainage and elevated dry floor dominate selection; dense organic traces decay rapidly; hearth positioning prioritizes ventilation and runoff avoidance.

### Coastal
Permit shell/bone/refuse signatures and marine-food processing hooks while preventing the archetype from mutating into the later specialized coastal camp family.

## Culture-Variant Hooks

Culture packs may alter behavior and material expression without changing the technological ceiling or core identity. Supported hooks include:
- preferred hearth geometry;
- typical group size;
- sleeping arrangement;
- raw material preference for lithics;
- hunting vs scavenging evidence weighting;
- hide-use probability;
- bone-processing intensity;
- pigment presence only when era/culture evidence permits;
- reuse frequency;
- preferred exposure/orientation relative to wind and sun.

Culture hooks must not hard-code modern ethnic analogues or claim unsupported archaeological specificity. The base archetype remains broadly early-human.

## Material Palette Logic

### Geological palette
Derive at least 80% of exposed structural stone from local geology or compatible adjacent strata. Accent stone may represent carried hammerstones/toolstone but must be volumetrically minor.

### Organic palette
Use locally plausible wood, leaves/brush, grasses, hides/furs if available through the target content set, bone, ash, and charcoal analogues. Organic preservation should respond to condition state and climate.

### Human-made palette restrictions
Forbidden by default: planks, bricks, cut stone blocks suggesting masonry, glass, metal, ceramics, woven architectural blocks, doors, chests, barrels, lanterns, torches as permanent fixtures, stairs/slabs used as visibly manufactured furniture, and any powered/redstone component.

## Condition Variants

### Active / recently occupied
Fresh hearth, concentrated activity debris, fuel reserve, readable sleeping/work zones, minimal vegetation intrusion.

### Temporarily vacant
Cold hearth, retained debris and bedding traces, small resource cache, limited regrowth.

### Repeatedly occupied
Multiple hearth lenses, denser lithic scatter, compacted floor, overlapping activity traces, limited small-scale rearrangement of stones.

### Abandoned
No fresh fuel/food, partial organic decay, sediment intrusion, diffuse debris.

### Partially collapsed
Fallen roof blocks reduce usable floor while preserving original shelter logic. Must remain geologically supported and traversable if generated as an explorable structure.

### Buried / archaeological
Sediment covers most occupation evidence with controlled exposures. Use only when the consuming experience supports archaeological interpretation; never rely on invisible metadata alone to communicate the structure.

### Repurposed
Later-era systems may occupy the same natural shelter through an explicit overlay relationship. The original early-human signature must remain recoverable and the later overlay must be generated additively rather than replacing the base record.

## Jigsaw / Family Relationships

Default behavior is standalone placement with a 500-block exclusion radius against unrelated generated structures.

Explicit compatible children within a shared parent reservation may include:
- exterior butchery patch;
- nearby knapping patch;
- resource cache;
- short-lived windbreak annex;
- carcass-processing apron;
- water-access path marker;
- refuse scatter.

The following are separate catalog archetypes and must not be silently absorbed as full replacements: Cave Mouth Occupation, Deep Cave Refuge, Temporary Brush Shelter, Hearth Circle, Stone Tool Knapping Ground, Butchery Site, Watering-Hole Camp, Seasonal Migration Camp.

A composed campsite may reference those families only through explicit compatibility/jigsaw rules.

## Infrastructure Dependencies

Required infrastructure: none.

Preferred environmental dependencies:
- reachable natural terrain;
- viable protected floor;
- optional nearby fresh water;
- optional lithic raw material source;
- optional game trail/resource area.

Roads, formal paths, utilities, agriculture, permanent storage infrastructure, and settlement grids are invalid dependencies for the base era.

## Loot / Occupancy Hooks

Loot must represent traces of activity rather than treasure storage.

Potential low-value finds:
- raw stone/toolstone;
- simple stone tool proxies where supported;
- bone fragments;
- charcoal;
- raw/processed food remnants appropriate to integration;
- hide/fiber fragments where available;
- rare culturally valid pigment/mineral pieces only through explicit hooks.

No chest is required or preferred. Loot should be distributed through floor scatter, cache nodes, work surfaces, hearth deposits, or archaeology-compatible containers supplied by the consuming platform.

Occupancy hooks may spawn or represent a very small mobile group, but population systems must respect shelter carrying capacity and avoid permanent-village behavior.

## Gameplay / Readability Requirements

The player must be able to infer, without a label, that:
1. the rock shelter is naturally advantageous;
2. someone deliberately used it;
3. fire/work/rest happened in distinguishable places;
4. it belongs to a technological context with extremely limited construction;
5. the terrain was not bulldozed to place a prefab building.

The hero structure should reward close observation rather than visual monumentality.

## Additive / Non-Destructive Compatibility

- Reserve 500 blocks against unrelated independent structure placement by default.
- Do not erase external structures, roads, biome features, or third-party structures to make room.
- If placement conflicts after reservation negotiation, reject or relocate this structure.
- Compatible compound members must share a parent reservation and deterministic layout contract.
- Terrain edits must be restricted to the agreed generation volume plus blend margin.
- Later cultural/condition layers attach as overlays or parameterized variants, not destructive replacements of the archetype definition.

## Validation Criteria

### Geometry
- Overhang is physically supported and connected to plausible geology.
- No floating ceiling mass.
- Occupied floor is reachable and traversable.
- Minimum clearances meet target game/platform requirements.
- Collapse variants cannot seal all intended access unless explicitly classified as inaccessible archaeology.

### Historical / technological fitness
- No later-era technology appears in the base template.
- Constructed elements remain subordinate to natural shelter.
- Activity zoning is plausible for shelter exposure, smoke, traffic, and drainage.

### Procedural fitness
- At least 100 deterministic seed samples per supported biome family should generate without fatal overlap, unsupported geology, inaccessible floor, or invalid component placement before production admission.
- Re-running the same seed/configuration must produce byte-equivalent structure decisions or documented deterministic-equivalent output.
- Scale variants must remain recognizably the same archetype.

### Compatibility
- Verify 500-block unrelated-structure exclusion behavior.
- Verify compound-family exception does not leak reservation exemptions to unrelated structures.
- Verify rejection instead of destructive overwrite when an existing protected feature occupies the target volume.

### Visual hero bar
- No broad flat artificial cliff wall.
- No obvious repeated decoration stamps.
- No perfectly centered hearth by default.
- Human traces tell a coherent behavioral story from multiple viewing angles.
- Exterior silhouette remains primarily geological.
- At least three materially distinct hero seed examples should survive expert review without reading as simple palette swaps.

## Production-Readiness Requirements

Hero specification completion does **not** by itself mean runtime production admission. Production admission requires all of the following:

1. schema/registry representation for `cw:e01_rock_overhang_camp`;
2. procedural generator implementation or target-format template implementation consistent with this specification;
3. deterministic seed tests;
4. terrain-support and accessibility validation;
5. biome adaptation tests;
6. 500-block reservation/exclusion validation;
7. explicit compound-family compatibility tests;
8. prohibited-material/technology audit;
9. visual review of S/M/L examples;
10. intact, abandoned, repeated-occupation, and collapse-state tests;
11. export/load validation in the supported target environment;
12. no destructive compatibility regressions.

Production state therefore remains `SPEC_COMPLETE_IMPLEMENTATION_PENDING` until runtime evidence satisfies these gates.

## Hero Acceptance Statement

This archetype is hero-level when procedural instances consistently communicate a natural rock shelter deliberately organized by highly mobile early humans, with geology doing most of the architectural work and sparse human interventions producing believable fire, work, rest, processing, and discard patterns. Complexity must come from environmental fit and behavioral coherence, not from importing later architectural vocabulary.

## Continuation

Completed catalog item: **E01-001 — Rock Overhang Camp**.

Next undeveloped archetype: **E01-002 — Cave Mouth Occupation**.
