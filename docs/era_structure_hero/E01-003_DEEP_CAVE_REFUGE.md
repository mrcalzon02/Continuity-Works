# Hero Structure Specification — E01-003 Deep Cave Refuge

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 3 of 750
Structure ID: `cw:e01_deep_cave_refuge`
Primary family: habitation / deep-subterranean temporary refuge
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate inside an explicitly composed early-human cave-complex reservation when linked components share one parent placement, deterministic topology contract, and bounded reservation ownership.

## Purpose

Deep Cave Refuge represents short-duration human occupation beyond the normal daylight and twilight zones of a cave, where darkness, constrained access, navigation risk, smoke accumulation, moisture, cold, predators, and limited escape routes materially shape survival behavior.

The archetype is not a normal cave campsite moved deeper underground. Its identity comes from the cost and difficulty of occupying the interior. People use it because the deep cave offers extraordinary protection, concealment, thermal stability, emergency shelter, or refuge from severe exterior conditions, despite being less convenient than an entrance camp.

Compared with E01-002 Cave Mouth Occupation, primary activity must occur beyond reliable natural daylight and outside ordinary entrance ventilation. Compared with later ritual caves, mines, subterranean settlements, and fortified caves, this structure must remain temporary, low-technology, minimally modified, and survival-driven.

## Historical / Technological Context

This template represents Lower Paleolithic / early-human groups making deliberate use of deep cave interiors without assuming technologies or cultural practices that belong to later eras.

Available capabilities are deliberately constrained:
- fire carried or established using period-valid means;
- percussion stone tools;
- carried toolstone and hammerstones;
- opportunistic branches, brush, hides, bone, and plant material where environmentally plausible;
- simple resource caches;
- stone rearrangement for wayfinding, hearth control, resting surfaces, and hazard marking;
- memorized or materially marked routes through natural cave topology.

The generator must not imply:
- permanent artificial lighting networks;
- engineered ventilation shafts;
- mine excavation or systematic tunneling;
- masonry partitions;
- permanent doors or gates;
- shaped plank construction;
- ceramic storage;
- formal drainage;
- ritual painting or sanctuary functions unless explicitly supplied by a later and distinct overlay/archetype;
- deep permanent settlement;
- agriculture, livestock housing, metal, glass, or powered infrastructure.

The hero treatment must communicate intelligent adaptation to a hostile interior rather than architectural sophistication.

## Archetype Boundary Contract

A valid Deep Cave Refuge must satisfy all of the following identity tests:

1. **Deep-zone occupation** — the primary refuge zone lies beyond direct exterior daylight and beyond the normal Cave Mouth Occupation envelope.
2. **Access cost** — reaching the refuge requires traversing at least one meaningful cave transition such as a bend, slope, choke point, descending passage, chamber sequence, or daylight-loss boundary.
3. **Navigation dependency** — the route must be legible enough to survive but not so formalized that it reads as a road, mine, or constructed corridor.
4. **Ventilation scarcity** — fire placement and occupancy must respond to limited airflow rather than assuming unrestricted smoke escape.
5. **Temporary use** — the site is an emergency or episodic refuge, not an underground village.
6. **Natural cave dominance** — geology overwhelmingly controls geometry.
7. **Sparse intervention** — human modifications remain local and reversible-looking.

If these conditions are not met, the candidate should be rejected or classified as another archetype.

## Footprint and Scale Classes

### S — Emergency Deep Pocket
- Route distance from daylight-loss boundary: approximately 8–24 blocks.
- Reserved local refuge footprint: 10–20 blocks wide, 8–18 deep.
- Usable refuge floor: 25–80 blocks.
- Access complexity: one bend, squeeze, descent, or chamber transition.
- Hearths: 0–1, with no-fire variants common.
- Likely occupancy: 1–5 individuals.
- Duration: hours to a few days.
- Primary use: immediate concealment, storm/cold refuge, predator avoidance, emergency shelter.

### M — Protected Interior Refuge
- Route distance from daylight-loss boundary: approximately 18–60 blocks.
- Reserved local refuge footprint: 18–34 blocks wide, 14–30 deep.
- Usable refuge floor: 70–220 blocks.
- Access complexity: two or more meaningful topology transitions.
- Hearths: 0–2, conditional on ventilation fitness.
- Likely occupancy: 4–12 individuals.
- Default hero scale.
- May include one staging/rest point along the approach route.

### L — Multi-Chamber Refuge Complex
- Route distance from daylight-loss boundary: approximately 40–120 blocks, subject to target-engine cave scale.
- Reserved connected refuge footprint: 30–60 blocks wide across one or more chambers, 24–54 deep.
- Usable refuge floor: 180–500 blocks across connected zones.
- Access complexity: branch, choke point, descent, or chamber chain plus deterministic return-path logic.
- Hearths: 1–3 maximum and only in ventilation-safe chambers.
- Likely occupancy: 8–20 individuals across temporary refuge episodes.
- May include separated sleep, cache, and lookout/staging pockets but must not read as a permanent subterranean settlement.

Large variants must increase topological complexity rather than simply enlarging a rectangular room.

## Architectural / Behavioral Program

The structure is organized as a route-and-refuge system rather than a conventional floor plan.

1. **Exterior reference anchor** — not necessarily part of the occupied structure, but a deterministic relationship to the cave mouth or known entrance route must exist.
2. **Daylight-loss boundary** — the point beyond which natural exterior light is no longer a reliable navigation source.
3. **Approach route** — a traversable natural cave path from daylight loss to the refuge.
4. **Hazard transition** — optional squeeze, bend, step, rubble slope, shallow water edge, or narrow passage that increases refuge defensibility while remaining traversable.
5. **Route markers** — sparse natural-material clues such as arranged stones, charcoal marks represented by target-valid blocks/entities, bone placement, or distinctive carried stones where supported.
6. **Staging pocket** — optional intermediate rest or equipment/cache spot before the primary refuge.
7. **Primary refuge chamber** — driest, safest, most defensible connected deep-zone surface.
8. **Low-smoke hearth pocket** — optional and only if ventilation proxy passes.
9. **Sleeping/rest cluster** — sheltered from route traffic, water, and hearth smoke.
10. **Resource cache** — carried fuel, toolstone, food remains, bone, or bedding analogue.
11. **Waste edge** — positioned away from sleeping and limited water sources.
12. **Escape decision point** — if topology permits, a secondary route or branching fallback may exist; it must be natural rather than engineered.
13. **Interior hazard boundary** — deeper shafts, flood channels, unstable rubble, or untraversable passages should be visibly or behaviorally avoided.

## Required Components

Hero admission requires:
- a natural cave system with a genuine deep-dark zone;
- a traversable route from an exterior-connected entrance to the refuge;
- primary occupation beyond reliable daylight;
- at least one meaningful access/topology transition;
- one readable refuge focus such as rest cluster, cache, arranged stones, hearth trace, or concentrated occupation debris;
- explicit ventilation fitness logic for any active hearth;
- at least one navigation/route-readability mechanism for M/L scale;
- dry or plausibly usable refuge floor;
- no permanent later-era construction;
- no destructive conversion of the cave into regular rooms or corridors.

M/L variants additionally require:
- separation between primary circulation and sleep/rest area;
- at least two distinct behavioral zones;
- route continuity validation from entrance to refuge and back;
- an identifiable reason the chamber is safer or more useful than adjacent deep cave space.

Recommended probabilistic components:
- carried fuel cache;
- charcoal/ash traces;
- route marker stones;
- stone seating/rest ledges;
- sleeping vegetation or hide analogue;
- toolstone cache;
- bone/food remains;
- repeated-use compacted patches;
- water collection point only if potable and outside flood risk;
- animal-use traces in abandoned states.

## Procedural Generation Logic

### 1. Entrance-linked cave graph extraction

Begin from an exterior-connected cave entrance and derive a traversability graph through connected cave cells/chambers.

Each graph node should record or approximate:
- distance from exterior;
- direct/indirect daylight exposure;
- vertical position relative to entrance;
- local chamber volume;
- floor usability;
- slope;
- water presence;
- choke-point count along route;
- alternate-route count;
- ceiling clearance;
- ventilation proxy;
- hazard score;
- path reversibility;
- conflicting structure reservations.

The generator must understand the refuge as a location reached through topology, not as an isolated deep coordinate.

### 2. Deep-zone qualification

A candidate refuge node must lie beyond the Cave Mouth Occupation zone. Qualification should use deterministic proxies such as:
- no direct sky/exterior visibility;
- minimum path distance from the mouth or daylight-loss plane;
- one or more occluding bends/chamber transitions;
- low natural-light score;
- sustained cave enclosure.

Simple Euclidean distance is insufficient because a chamber 40 blocks from the mouth through open line-of-sight may still behave like an entrance chamber.

### 3. Refuge fitness scoring

Score deep chambers for:
- dryness;
- floor area;
- defensibility from access geometry;
- thermal enclosure;
- route reliability;
- low flood risk;
- manageable ceiling clearance;
- absence of fatal drops;
- ventilation sufficient for intended occupancy/fire behavior;
- proximity to small usable water source where present;
- separation from major predator/hazard zones;
- lack of structure conflict.

A highly defensible but lethally wet or smoke-trapping chamber must be rejected.

### 4. Route difficulty banding

Assign the path a difficulty band:

- **A — simple deep route:** one bend/descent, no serious hazard;
- **B — constrained route:** multiple transitions, mild squeeze/rubble/water edge;
- **C — complex refuge route:** branching, stronger elevation change, multiple chambers, but still reliably reversible.

Do not generate hero refuges behind unavoidable lethal drops, deep swim sections, maze-like one-way topology, or parkour requirements unless the consuming platform explicitly supports and validates them.

### 5. Wayfinding pass

Wayfinding must be sparse and period-valid. Use one or more of:
- repeated distinctive stone placements;
- isolated carried-stone palette accents;
- charcoal/ash marker proxies;
- broken-branch/organic markers where preservation allows;
- small bone clusters;
- intentionally cleared path patches;
- memorable natural landmarks deliberately incorporated into route selection.

Markers should be asymmetric, irregular, and infrequent. They are survival aids, not decorative trail signage.

### 6. Ventilation-aware occupancy model

Estimate ventilation using:
- path openness back to entrance;
- chamber volume;
- ceiling height;
- number of connected passages;
- vertical shafts that connect to breathable space without implying constructed chimneys;
- distance from dead-end pockets.

Then classify the refuge:
- `NO_FIRE_SAFE`
- `SMALL_FIRE_LIMITED`
- `HEARTH_CAPABLE`

No-fire safe variants should remain fully viable hero outputs rather than being treated as incomplete.

### 7. Behavioral zoning

Use deterministic substreams to place:
- `route`
- `marker_set`
- `staging`
- `primary_refuge`
- `sleep`
- `hearth`
- `cache`
- `water_access`
- `waste`
- `hazard_boundary`
- `secondary_escape`

Small variants may collapse several zones into one chamber. Larger variants should gain topological separation, not architectural partitions.

### 8. Occupation-history pass

Repeated refuge use may create:
- overlapping ash traces;
- several generations of route markers;
- compacted rest zones;
- depleted and replenished resource caches;
- bone/food accumulation;
- moved rubble around the safest floor;
- obsolete marker traces leading to blocked former paths;
- sediment encroachment.

### 9. Terrain preservation pass

Human edits must remain subordinate to the cave. Do not straighten passages, flatten large floors, remove major pillars, seal unrelated branches, or excavate tunnels simply to satisfy layout goals.

If the natural topology cannot support the archetype with minimal intervention, reject the candidate.

### 10. Reservation and compatibility pass

Before final placement, reserve the structure footprint plus the Continuity Works minimum 500-block exclusion zone against unrelated independent structures.

Any explicitly compatible cave-family child must share the parent reservation. A family exemption cannot propagate to unrelated cave structures or external structure systems.

## Seed Determinism

Identical world seed, structure seed, generator version, biome context, cave topology, culture configuration, and condition configuration must reproduce the same candidate, route, refuge chamber, behavioral zoning, markers, and condition state.

Recommended named deterministic substreams:
- `entrance_anchor`
- `cave_graph`
- `deep_zone`
- `scale`
- `route_selection`
- `route_markers`
- `refuge_chamber`
- `ventilation_class`
- `occupation_layout`
- `hearth`
- `cache`
- `organic_materials`
- `condition`
- `culture_hook`

Decorative or evidentiary additions introduced later must not reshuffle primary topology decisions.

## Biome / Environment Adaptations

Surface biome affects entrance conditions, carried resources, moisture, temperature gradient, and refuge motivation even though the occupied chamber is subterranean.

### Temperate forest
- Greater carried fuel and bedding availability.
- Moisture and seepage penalties remain important.
- Organic route markers are more likely in fresh occupation states.
- Refuge motivation may emphasize severe weather or concealment.

### Boreal / cold
- Deep thermal stability receives a strong positive score.
- Larger carried fuel caches where ventilation allows.
- Compact sleep clusters.
- Entrance icing/snow obstruction must not break validated return access.

### Tundra / alpine
- Shelter value and wind/cold protection are high.
- Sparse timber reduces fuel and organic markers.
- Stone/bone route markers become more likely.
- Freeze/thaw rubble and vertical hazard checks increase.

### Savanna / dry grassland
- Deep refuge may function as thermal shelter or emergency concealment.
- Fuel remains limited but possible.
- Water availability may strongly affect viable duration.
- Avoid implying habitual permanent underground residence.

### Arid / desert
- Thermal buffering can strongly favor deep chambers.
- Flash-flood channels and dry-cave flood signatures are severe rejection criteria.
- Organic traces are sparse.
- Dust/sand intrusion affects abandoned and sealed-mouth variants.

### Tropical / humid
- Ventilation, humidity, standing water, insects/fauna, and microbial decay strongly constrain habitability.
- Dry elevated interior pockets are preferred.
- Organic material survival is low outside recently occupied states.
- Flood-connected cave systems require strict rejection logic.

### Coastal
- Sea caves may qualify only if the deep refuge remains above dangerous tidal/flood envelopes.
- Marine food traces may occur through culture/environment hooks.
- Saltwater intrusion and surge risk are major penalties.

## Culture-Variant Hooks

Culture packs may modify:
- willingness to occupy deep interiors;
- preferred group size;
- duration/frequency of refuge use;
- marker style and material;
- fire tolerance and hearth probability;
- carried toolstone preference;
- bedding organization;
- cache behavior;
- use of bone/hide/plant materials;
- group movement pattern through choke points;
- preference for single-entry defensibility versus alternate escape routes.

Culture hooks may not introduce later-period ritual sanctuary functions, formal cave art programs, constructed fortifications, mine workings, permanent subterranean architecture, or unsupported claims about specific historical peoples.

## Material Palette Logic

### Geological structure
At least 90% of visible structural mass must come from local cave geology or directly compatible strata. The generator should inherit neighboring cave blocks and material transitions rather than stamp a separate decorative rock palette.

### Carried material
Carried toolstone, fuel, bone, hide, bedding, and marker stones may differ from local cave materials, but their volume must be small and behaviorally justified.

### Human rearrangement
Permitted modifications include:
- moving loose stones;
- small hearth surrounds;
- limited rubble clearing;
- compacted rest surfaces;
- small resource piles;
- sparse route markers.

Forbidden base materials include:
- planks;
- masonry blocks implying shaped construction;
- bricks;
- glass;
- metal fixtures;
- ceramics;
- doors/gates;
- chests/barrels as default storage;
- permanent torches/lanterns;
- redstone/powered components;
- engineered ladders/stairs as routine route infrastructure;
- structural mine supports;
- ventilation ducts.

## Condition Variants

### Active emergency refuge
- Fresh route markers.
- Concentrated sleep/rest cluster.
- Small active or recently extinguished fire only if ventilation class permits.
- Carried food/fuel/toolstone cache.
- Minimal sediment intrusion.

### Temporarily vacant
- Route remains legible.
- Cold hearth or no-fire occupation traces.
- Partial cache.
- Limited animal disturbance.

### Repeated refuge
- Multiple marker generations.
- Compacted floor.
- Overlapping ash/bone/tool traces.
- Repeatedly selected safe sleeping pocket.
- Small local rubble rearrangement.

### Abandoned
- Markers fade or become incomplete.
- Sediment and moisture encroach.
- Organic traces decay.
- Animals may dominate the chamber.

### Entrance-blocked legacy refuge
- A former route is partially collapsed or silted but the original refuge remains identifiable from another valid access or archaeological configuration.
- Never generate an explorable active-state refuge with no validated exit.

### Partially collapsed
- Ceiling/rubble failure reduces usable space.
- Primary route must remain safe enough for the selected gameplay state or the structure must be explicitly classified inaccessible.
- No floating or unsupported collapse masses.

### Flood-damaged
- High-water deposits, displaced artifacts, and unusable lower surfaces.
- Active occupancy is prohibited until a dry valid refuge surface exists.

### Animal-reoccupied
- Human traces remain recoverable while nesting, bones, spoor, or bedding-like animal use dominates.
- This is an overlay state, not a separate archetype.

### Later-era repurposed
- Later occupants may add lighting, storage, ritual, defensive, mining, or habitation features only through an explicit overlay relationship.
- The original early-human refuge route and occupation signature must remain recoverable.
- Later layers are additive and cannot rewrite the base definition.

## Jigsaw / Family Relationships

Default placement is standalone with a 500-block exclusion radius against unrelated independent structures.

Explicitly compatible children within one shared parent reservation may include:
- route-marker chain;
- small staging pocket;
- carried-resource cache;
- water collection pocket;
- exterior or threshold orientation marker;
- small refuge annex chamber when naturally connected;
- abandoned alternate-route trace.

Related archetypes that remain distinct:
- E01-001 Rock Overhang Camp;
- E01-002 Cave Mouth Occupation;
- E01-004 Temporary Brush Shelter;
- E01-007 Hearth Circle;
- E01-009 Stone Tool Knapping Ground;
- E01-012 Butchery Site;
- E01-026 Seasonal Migration Camp;
- later-era ritual caves, mines, fortified caves, underground settlements, and engineered shelters.

A composed cave complex may contain multiple catalog families only through explicit compatibility records and one authoritative reservation owner.

## Infrastructure Dependencies

Required built infrastructure: none.

Required environmental dependencies:
- exterior-connected natural cave system;
- qualified deep-dark zone;
- reversible traversable route;
- viable refuge chamber or chamber set;
- tolerable water/flood conditions;
- occupancy-compatible ventilation classification.

Optional dependencies:
- accessible fresh water;
- nearby exterior resource territory;
- naturally defensible choke point;
- memorable cave landmark suitable for route orientation.

Invalid dependencies for the base era:
- roads;
- formal permanent paths;
- artificial mine shafts;
- built stairs/ladders as required circulation;
- utilities;
- agriculture;
- permanent drainage;
- settlement grids;
- engineered ventilation;
- artificial-light infrastructure.

## Loot / Occupancy Hooks

Loot is environmental evidence, not treasure storage.

Possible distributed finds:
- raw toolstone;
- simple stone-tool proxies where supported;
- hammerstones;
- bone fragments;
- charcoal/ash;
- low-value food remains;
- carried fuel;
- hide/fiber/bedding fragments where target content supports them;
- marker stones distinguishable from local geology;
- rare mineral/pigment traces only through explicit era/culture hooks and without converting the site into a ritual-gallery archetype.

Default storage should use floor scatter, crevice caches, stone-lined niches, natural ledges, or archaeology-aware target containers. Chests are not preferred.

Occupancy caps must respect:
- usable refuge floor;
- ventilation class;
- route width;
- available escape capacity;
- water availability;
- temporary-refuge identity.

No-fire variants must not spawn populations that require a permanent heating/cooking installation.

## Gameplay / Readability Requirements

Without labels, a player should be able to infer:
1. this is meaningfully deeper than an entrance camp;
2. reaching it required deliberate navigation;
3. the refuge chamber was chosen for protection, concealment, stability, or safety;
4. occupants managed darkness and route memory using primitive means;
5. fire was absent, constrained, or carefully located because ventilation is scarce;
6. the site was used temporarily or episodically rather than as a permanent underground settlement;
7. geology dictated the structure rather than being carved into a prefab building.

## Additive / Non-Destructive Compatibility

- Reserve a minimum 500 blocks against unrelated independent structure placement.
- Compatible cave-family components may violate that radius only when explicitly registered under the same parent reservation.
- Family exemptions never apply transitively to unrelated structures.
- Do not overwrite third-party caves, structures, roads, rail, utilities, biome features, or reserved content.
- If an existing protected feature conflicts with the required refuge or route volume, reject or relocate the candidate.
- Preserve cave continuation outside the negotiated reservation.
- Do not seal unrelated branches simply to simplify navigation.
- Later overlays attach additively rather than replacing this archetype.

## Validation Criteria

### Geometry / topology
- Refuge lies beyond reliable daylight.
- Valid path exists from an exterior-connected entrance to refuge and back.
- Path contains at least one meaningful topology transition.
- No floating rock or unsupported collapse geometry.
- No unavoidable lethal drop, one-way choke, or invalid swim dependency in standard variants.
- Player clearance is valid across all mandatory route segments.
- Refuge floor is sufficiently stable and usable for selected scale.

### Archetype distinction
- Primary occupation is not concentrated at the mouth/twilight zone.
- Structure cannot pass as E01-001 Rock Overhang Camp.
- Structure cannot pass as E01-002 Cave Mouth Occupation.
- Structure does not read as a mine, ritual cave, bunker, fortified cave, or underground village.
- Human intervention remains sparse.

### Historical / technological fitness
- No later-era construction or storage technology.
- Wayfinding markers use period-valid natural materials.
- Fire behavior obeys ventilation classification.
- No engineered excavation is required to make the route work.

### Procedural fitness
Before production admission, test at least 100 deterministic seed samples across each supported cave/biome family where feasible.

Reject or flag samples with:
- disconnected entrance/refuge graphs;
- invalid deep-zone classification;
- smoke-incompatible active hearths;
- flooded refuge floors;
- route markers leading into invalid/dead-end paths;
- inaccessible mandatory caches or sleep areas;
- destructive cave rewriting;
- structure-reservation conflicts.

Same seed/configuration must reproduce equivalent topology decisions.

### Wayfinding validation
- M/L routes contain enough cues to remain intentionally navigable.
- Markers do not form a modern-looking trail system.
- Marker placement does not lead toward fatal or unrelated branches.
- Abandoned variants may degrade markers but should preserve interpretable history where gameplay requires it.

### Compatibility validation
- Verify minimum 500-block unrelated-structure exclusion behavior.
- Verify shared-family reservation exception only for registered compatible children.
- Verify third-party cave features are not overwritten outside reserved volume.
- Verify rejection/relocation when a protected structure conflicts with the refuge route.

### Visual hero bar
- Refuge should tell a survival story from approach route through occupation chamber.
- No rectangular carved-room silhouette unless naturally plausible and heavily irregularized by geology.
- No repeated marker stamp pattern.
- No centered decorative campfire requirement.
- Lighting/readability in previews must preserve the impression of darkness without making the hero result impossible to inspect.
- At least three materially/topologically distinct hero seed examples must survive expert review without reading as simple palette or scale swaps.

## Production-Readiness Requirements

Hero specification completion does **not** mean runtime production admission.

Production admission requires all of the following observed evidence:

1. schema/registry representation for `cw:e01_deep_cave_refuge`;
2. procedural generator or target-format implementation consistent with this specification;
3. entrance-linked cave graph extraction implemented and tested;
4. deep-zone classification validation;
5. reversible-route/access validation;
6. ventilation classification and hearth gating tests;
7. deterministic seed replay tests;
8. S/M/L scale tests;
9. biome/environment adaptation tests;
10. route-marker/wayfinding validation;
11. condition-state tests including active, vacant, repeated, abandoned, collapse, flood-damaged, animal-reoccupied, and later-overlay states as supported;
12. prohibited-material/technology audit;
13. minimum 500-block exclusion validation;
14. explicit compatible-family reservation tests;
15. non-destructive third-party/cave integration tests;
16. target export/load validation;
17. visual hero review of at least three distinct seeds/topologies;
18. production ledger update backed by direct implementation evidence.

Until these gates pass, production status remains `IMPLEMENTATION_PENDING`.

## Hero Acceptance Checklist

A hero reviewer should be able to answer **yes** to all of the following:

- Is this unquestionably a deep cave refuge rather than an entrance camp?
- Does the route itself matter to the structure's identity?
- Is darkness an actual design constraint?
- Does fire behavior respond to ventilation?
- Is there a credible reason occupants selected this chamber?
- Can a player reach and leave it through validated natural topology?
- Do primitive wayfinding clues feel behavioral rather than decorative?
- Is the refuge temporary/episodic rather than a subterranean settlement?
- Is geology still overwhelmingly dominant?
- Are human modifications sparse and technology-valid?
- Does the structure preserve the 500-block unrelated-structure exclusion doctrine?
- Are all family exceptions explicit and non-destructive?

If any answer is no, the archetype is not hero-ready.

## Completion State

Hero specification: **COMPLETE**
Runtime/template implementation: **PENDING**
Production admission: **PENDING VALIDATION**

Next catalog archetype: **E01-004 — Temporary Brush Shelter**.
