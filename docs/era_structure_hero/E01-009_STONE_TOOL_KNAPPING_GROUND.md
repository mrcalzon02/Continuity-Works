# Hero Structure Specification — E01-009 Stone Tool Knapping Ground

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 9 of 750
Structure ID: `cw:e01_stone_tool_knapping_ground`
Primary family: production / lithic reduction worksite
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate inside an explicitly composed early-human camp, quarry, kill-site, butchery, or resource-processing reservation when every linked member shares one parent placement and deterministic layout contract.

## Purpose

The Stone Tool Knapping Ground is a task-specific lithic reduction site where the physical act of converting raw stone into usable tools creates the structure. It is not a hut, workshop building, campsite floor sprinkled with rocks, or treasure cache. The site is defined by the relationship among raw-material staging, seated or crouched work positions, hammerstones, cores, flakes, shatter, rejected pieces, finished or partly finished tools, and circulation around sharp debris.

The hero treatment must make the reduction sequence readable spatially. A player should be able to infer where stone arrived, where people worked it, where useful products were removed, where unsuitable material accumulated, and whether the site was used once or repeatedly.

## Historical / Technological Context

This archetype represents Lower Paleolithic / early-human lithic production using percussion reduction and period-valid simple stone-working behavior. It assumes no formal benches, masonry floors, anvils of later engineered form, metal tools, ceramics, grinding workshops, permanent roofed industry, mine infrastructure, carts, storage chests, or standardized factory organization.

Permitted behaviors include:
- direct hard-hammer percussion;
- opportunistic bipolar reduction where platform rules permit representation;
- use of natural stone seats, logs, packed earth, hides, or ground surfaces as work positions;
- raw cobble, nodule, slab, and core staging;
- hammerstone selection and reuse;
- transport of preferred toolstone away from its source;
- discard of cortical flakes, shatter, exhausted cores, and rejected blanks;
- limited caching of reusable cores, hammerstones, or high-quality raw material;
- repeated occupation that produces overlapping debris lenses.

The site must not imply a later craft guild, quarry industry, permanent workshop, or standardized production line.

## Archetype Boundary Contract

A valid Stone Tool Knapping Ground must satisfy all of the following:

1. **Lithic reduction is primary.** The strongest visible signal is stone-working debris and work organization, not sleeping, cooking, shelter, hunting, or storage.
2. **Reduction sequence is legible.** Raw material, work position, debris, and removed-product logic are spatially coherent.
3. **Sharp-debris circulation matters.** Paths and rest positions avoid the densest flake fields.
4. **No architectural dependence.** The site may sit beside a shelter or hearth but cannot require a building.
5. **Raw-material relationship is explicit.** Material is either local, imported, or mixed, and the generator records which.
6. **Scale reflects work intensity, not building size.** Larger variants gain more work stations, debris density, chronology, and material diversity.
7. **Technology ceiling remains early-human.** No later toolmaking infrastructure is introduced.

If lithic debris is only decorative background for another archetype, classify it as a child activity patch rather than E01-009.

## Footprint and Scale Classes

### S — Single Knapping Position
- Reservation footprint: 8–16 blocks wide, 8–14 deep.
- Active work area: 10–35 blocks.
- Work positions: 1.
- Core count proxy: 1–4.
- Hammerstones: 1–2.
- Debris field: compact and strongly directional.
- Likely users: 1–2.
- Typical use: short reduction episode, maintenance, expedient tool manufacture.

### M — Recurrent Knapping Ground
- Reservation footprint: 14–28 blocks wide, 12–24 deep.
- Active work area: 35–120 blocks.
- Work positions: 2–5.
- Core count proxy: 3–12.
- Hammerstones: 2–6.
- Debris: multiple overlapping reduction fans.
- Likely users: 2–8 across one or several episodes.
- Default hero scale.

### L — Group Lithic Production Ground
- Reservation footprint: 24–46 blocks wide, 18–38 deep.
- Active work area: 100–320 blocks.
- Work positions: 4–10.
- Core count proxy: 8–30.
- Hammerstones: 4–12.
- Debris: several distinct work clusters plus shared raw-material staging and discard margins.
- Likely users: 6–16 over repeated episodes.

Large variants must remain open task landscapes. They must not become formal workshops or industrial quarries.

## Architectural / Behavioral Program

The program is a set of functional patches rather than rooms.

1. **Approach / clean path** — low-debris access from surrounding terrain.
2. **Raw-material staging patch** — cobbles, nodules, slabs, or imported toolstone awaiting reduction.
3. **Primary work position** — seated/crouched ergonomic location with stable footing and clear swing space.
4. **Secondary work positions** — additional reduction points for M/L variants.
5. **Hammerstone cache** — small reusable concentration of suitable percussion stones.
6. **Core reduction zone** — immediate work focus around each knapper.
7. **Primary flake fan** — directional debris concentration projected away from the body position.
8. **Heavy shatter zone** — low-value fragmented material nearer hard-impact work.
9. **Rejected-material edge** — coarse unusable pieces pushed or tossed away.
10. **Reusable-core cache** — optional wall edge, stone hollow, shallow depression, or marked ground patch.
11. **Finished-tool departure path** — usually low-artifact; useful products leave the site rather than accumulating as treasure.
12. **Circulation corridor** — safe movement route between work clusters and external camp/resource nodes.
13. **Sweep/clear zone** — repeated-use variants may show deliberately displaced sharp debris.
14. **Legacy reduction lens** — older buried or weathered scatter beneath or beside current activity.

## Required Components

Hero admission requires:
- at least one stable work position;
- one coherent raw-material source/staging relationship;
- at least one hammerstone or hammerstone proxy;
- at least one core/reduction focus;
- directional flake/debitage distribution rather than uniform decoration;
- safe circulation around the densest sharp-debris field;
- no later-era manufactured equipment;
- terrain-responsive placement with minimal flattening.

M/L variants additionally require:
- multiple work positions or repeated-use lenses;
- readable separation between raw material, active reduction, and discard zones;
- at least one shared circulation route;
- explicit material-provenance state.

Recommended probabilistic components:
- natural seat stone or log;
- hide/knee pad analogue where culturally/environmentally valid;
- reusable core cache;
- rejected blank concentration;
- hammerstone wear proxy;
- exhausted cores;
- transported exotic toolstone fragments;
- minor bone/food traces only when attached to a parent camp;
- sediment burial in abandoned states.

## Procedural Generation Logic

### 1. Parent-context classification

Classify the candidate context before layout:
- `SOURCE_ADJACENT` — directly beside naturally exposed toolstone;
- `CAMP_ATTACHED` — inside a compatible habitation/gathering parent reservation;
- `KILL_BUTCHERY_ATTACHED` — short-term tool production near carcass processing;
- `TRAVEL_STOP` — expedient maintenance on a movement route;
- `INDEPENDENT_WORKSITE` — standalone recurrent knapping ground;
- `MIXED_PROVENANCE` — local and transported stone both used.

Context affects raw-material volume, product-removal expectations, debris intensity, and family links.

### 2. Surface fitness scoring

Prefer surfaces with:
- stable, reasonably dry footing;
- good natural light or open visibility;
- enough elbow/swing space;
- low vegetation obstruction;
- nearby seat stones, logs, or stable ground;
- no active water flow through the debris field;
- no severe slope causing flakes to unrealistically migrate immediately;
- low conflict with unrelated structure reservations.

Reject steep, flooded, densely obstructed, or destructively conflicting locations.

### 3. Raw-material provenance model

Assign one or more provenance states:
- `LOCAL_COBBLE`
- `LOCAL_OUTCROP`
- `TRANSPORTED_NODULE`
- `TRANSPORTED_CORE`
- `MIXED_LOCAL_IMPORTED`

Local sources should match nearby geology. Imported material may differ visibly but must remain volumetrically minor relative to structural terrain.

The generator should maintain a source-material identifier so core, flake, and discard palettes remain internally consistent.

### 4. Work-position solver

For each work position, require:
- stable floor;
- 2–4 blocks of clear body/swing space depending on target representation;
- directional debris release area;
- access to raw material;
- avoidance of active hearth flame, sleeping zones, water edge, or major circulation;
- realistic relation to seat stone/log if one is used.

Positions should be irregularly spaced and oriented to terrain, light, wind, social grouping, and parent-site circulation.

### 5. Reduction-sequence model

Each reduction episode chooses a deterministic stage profile:
- `TESTING` — few large flakes, rejected raw pieces, low product yield;
- `PRIMARY_REDUCTION` — cortical/large flakes, heavy core transformation, larger debris;
- `SECONDARY_SHAPING` — denser smaller flakes around established cores/blanks;
- `MAINTENANCE` — sparse small debris and edge-refresh activity;
- `MIXED_SEQUENCE` — overlapping stages from recurrent use.

The site must not distribute every artifact type uniformly. The chosen profile controls size, density, and location of debris classes.

### 6. Debris projection

Generate a directional flake fan from each work position using:
- knapper facing/orientation;
- dominant strike direction;
- local slope;
- obstacles;
- wind only for very light proxy particles, not stone displacement;
- repeated sweeping/clearing behavior.

Use anisotropic scatter rather than radial noise. Large fragments remain closer to work positions; lighter/smaller debris may extend farther within target-engine limits.

### 7. Sharp-debris hazard map

Combine debris fans into a local hazard field.

Classify cells as:
- `CLEAN`
- `LIGHT_SCATTER`
- `WORK_EDGE`
- `DENSE_SHARP`
- `DISCARD_HEAP`

Primary circulation and resting positions should strongly prefer `CLEAN` and `LIGHT_SCATTER`. Repeated-use sites may include deliberately cleared lanes that cut through older debris lenses.

### 8. Core and hammerstone lifecycle

For each work cluster, determine:
- raw core count;
- partially reduced cores;
- exhausted cores;
- rejected cores;
- removed cores;
- active hammerstones;
- discarded/broken hammerstones;
- cached reusable hammerstones.

Useful cores and finished tools should usually leave the site. A knapping ground filled with pristine finished tools is invalid unless an explicit abandonment event explains it.

### 9. Chronology / repeated-use pass

Repeated episodes may produce:
- overlapping flake fans with different weathering states;
- old cleared lanes;
- buried earlier scatter;
- exhausted-core concentrations at margins;
- reused seat stones;
- material-provenance changes across episodes;
- abandoned cache remains;
- movement of old debris away from active work positions.

Chronology should add spatial history rather than simply increase random density.

### 10. Family reservation pass

Apply the Continuity Works minimum 500-block exclusion radius against unrelated independent structures.

Compatible family members may occupy the same parent reservation only through explicit composition. E01-009 can attach to camps, gathering sites, lithic-source sites, kill/butchery sites, or movement stops without gaining an independent overlap exemption.

## Seed Determinism

Given the same world seed, structure seed, generator version, parent context, material geology, culture configuration, and condition state, the site must reproduce the same work positions, provenance, reduction stages, debris fans, caches, chronology, and circulation.

Recommended named deterministic substreams:
- `parent_context`
- `surface_fitness`
- `scale`
- `material_provenance`
- `work_positions`
- `reduction_stage`
- `debris_projection`
- `hazard_field`
- `core_lifecycle`
- `hammerstones`
- `cache`
- `chronology`
- `condition`
- `culture_hook`

Later decorative additions must not reshuffle primary production geometry.

## Biome / Environment Adaptations

### Temperate forest
- Clear small work patches beneath or beside canopy openings.
- Leaf litter may partially mask older debris.
- Logs and natural seat stones are more available.
- Wet-ground penalties increase after rain-prone conditions.

### Boreal / cold
- Favor dry sheltered clearings, cave-mouth edges, or wind-protected work positions.
- Snow cover may obscure abandoned scatters while active sites retain cleared patches.
- Frozen ground can preserve sharp spatial boundaries.

### Tundra / alpine
- Low vegetation improves visibility of scatter.
- Frost-heave/weathering can disperse old debris modestly.
- Stone seating and direct source adjacency are more common.
- Exposure penalties favor lee-side work positions.

### Savanna / dry grassland
- Shade proximity and open visibility both matter.
- Sparse vegetation preserves readable debris fields.
- Travel-stop maintenance variants become more common.

### Arid / desert
- Windblown sediment may partly bury older scatters.
- Raw stone contrast against substrate can be visually strong.
- Avoid dry-wash channels where flood events would destroy site logic.

### Tropical / humid
- Organic seating/bedding traces decay rapidly.
- Dense vegetation makes maintained clear work patches more important.
- Heavy runoff and soil movement penalize poor surfaces.

### Coastal / riverine
- Cobble procurement may be locally abundant.
- Rounded hammerstones and raw-material staging can be stronger.
- Keep active work above flood/tide zones.
- Distinguish toolstone cobbles from generic shoreline decoration through clustering and reduction evidence.

## Culture-Variant Hooks

Culture packs may alter:
- preferred toolstone types;
- transport distance tolerance;
- typical reduction-stage mix;
- work-position spacing;
- group versus solitary knapping behavior;
- hammerstone selection;
- core reuse intensity;
- cache frequency;
- degree of debris clearing;
- preferred attachment to hearth, shelter, kill, or travel contexts.

Culture hooks may not introduce later formal workshops, metallurgy, grinding industries, ceramics, standardized benches, or unsupported claims tied to modern ethnic identities.

## Material Palette Logic

### Structural terrain
The site should remain overwhelmingly local ground, stone, vegetation, and natural terrain. There is little to no built structural mass.

### Toolstone palette
Toolstone derives from provenance state. A single episode should use a coherent palette unless a mixed-provenance state is explicitly selected.

### Hammerstone palette
Hammerstones should be mechanically plausible: dense rounded or durable stones, usually visually distinct in shape/placement from flakes and cores.

### Organic palette
Optional logs, branches, hides, grass, or leaves may support sitting/kneeling or parent-camp context but remain secondary.

### Forbidden base materials
No planks, bricks, masonry, glass, metal fixtures, ceramics, chests, barrels, permanent torches/lanterns, redstone/powered devices, machine blocks, formal workbenches, or mine supports.

## Condition Variants

### Active
Fresh raw-material staging, active cores, clear work positions, strong debris gradients, reusable hammerstones, and clean circulation lanes.

### Recently vacated
Work organization remains sharp, but useful finished products are largely absent. Some reusable cores/hammerstones may remain cached.

### Repeated-use
Multiple reduction lenses, overlapping material phases, cleared lanes, exhausted cores, reused seating, and stronger discard margins.

### Abandoned
Weathering, vegetation/sediment intrusion, dispersed surface debris, depleted caches, and no active staging.

### Partially buried
Sediment or litter covers older debris while a subset remains visible or archaeologically recoverable.

### Eroded / disturbed
Slope wash, frost action, animal activity, or flooding has shifted portions of the scatter. Core spatial logic must remain partially recoverable or the structure should fail hero readability.

### Source-depleted
A formerly source-adjacent site remains after the best nearby raw material has been exhausted or removed; imported material may appear in later episodes.

### Later repurposed
A later-era camp, path, structure, or workshop may overlay the site only through an explicit additive relationship. Earlier lithic evidence remains recoverable and is not overwritten at the archetype-definition level.

## Jigsaw / Family Relationships

Default behavior is standalone placement with the minimum 500-block exclusion radius against unrelated independent structures.

Compatible children or parents within one shared reservation may include:
- E01-001 Rock Overhang Camp;
- E01-002 Cave Mouth Occupation;
- E01-004 Temporary Brush Shelter;
- E01-005 Lean-To Windbreak;
- E01-006 Hide Windbreak Camp;
- E01-007 Hearth Circle;
- E01-008 Multi-Hearth Gathering Site;
- raw-material source/procurement sites;
- kill/butchery processing sites;
- migration/travel camps.

E01-009 remains distinct from generic camp debris. A parent camp may include a small knapping patch, but only a task-dominant lithic production surface qualifies as the independent archetype.

## Infrastructure Dependencies

Required constructed infrastructure: none.

Environmental/resource dependencies:
- stable work surface;
- usable toolstone supplied locally or by transport;
- hammerstone material;
- safe circulation;
- adequate light for active reduction;
- optional shelter/hearth relationship;
- optional source outcrop or cobble field.

Formal roads, buildings, permanent storage, utilities, mine galleries, engineered floors, and workshop furniture are invalid dependencies for the base era.

## Loot / Occupancy Hooks

Loot should represent production residue and reusable work material, not a chest of finished gear.

Potential finds:
- raw toolstone nodules;
- partially reduced cores;
- exhausted cores;
- hammerstones;
- flakes/debitage proxies;
- rejected blanks;
- occasional unfinished tool proxy;
- rare finished-tool abandonment only under an explicit interruption/abandonment state.

Loot distribution should be spatially tied to work zones, caches, staging patches, and discard margins.

Occupancy hooks should place small numbers of active workers consistent with work-position count. Parent-camp populations may move through the site, but resting/sleeping occupancy should avoid dense sharp-debris zones.

## Gameplay / Readability Requirements

Without labels, the player should be able to infer:
1. stone was deliberately brought to or selected at this spot;
2. people sat or crouched in identifiable work positions;
3. impact debris spread directionally from those positions;
4. useful products mostly left while waste remained;
5. movement avoided the sharpest debris;
6. repeated use changed the pattern over time;
7. the site is a work surface, not a dwelling or later workshop.

## Additive / Non-Destructive Compatibility

- Reserve a minimum 500 blocks against unrelated independent structures.
- Family exceptions require one explicit parent reservation.
- Do not erase terrain features, third-party structures, roads, caves, or other protected content to force placement.
- Reject or relocate on unresolved conflict.
- Preserve external geology, water flow, and vegetation systems outside the agreed generation volume plus blend margin.
- Later overlays attach additively; they do not rewrite the early-human archetype.
- A source-adjacent variant may reference a lithic-source structure without consuming or replacing that structure's identity.

## Validation Criteria

### Archetype validation
- Lithic production is the dominant readable activity.
- At least one complete raw-material → work position → debris/discard relationship is visible.
- Site does not read as a generic camp scatter.
- Site does not read as a permanent workshop.

### Spatial validation
- Work positions have plausible clearance.
- Debris fields are anisotropic and tied to work orientation.
- Dense sharp-debris zones do not occupy primary circulation or sleeping areas.
- Staging and discard zones are distinct at M/L scale.

### Material validation
- Core, flake, and raw-material palettes are provenance-consistent.
- Imported stone remains clearly transported rather than structural geology.
- Hammerstones are visually/semantically distinct from ordinary scatter where target assets allow.

### Historical / technological validation
- No later-era tools, furniture, storage, masonry, metalworking, or engineered infrastructure appear.
- Finished-tool abundance remains low unless condition history justifies it.
- Organization arises from behavior rather than architecture.

### Procedural validation
Before production admission, test at least 100 deterministic seeds per supported major environment/context family for:
- valid work positions;
- stable surfaces;
- coherent debris projection;
- provenance consistency;
- safe circulation;
- cache/staging validity;
- exclusion/reservation correctness;
- deterministic replay.

### Compatibility validation
- Verify minimum 500-block exclusion against unrelated structures.
- Verify family exceptions only inside shared parent reservations.
- Verify source-site relationships do not grant blanket overlap permissions.
- Verify placement rejects rather than destructively overwrites protected content.

### Visual hero bar
- No uniform circular scatter fields.
- No evenly spaced workstations.
- No decorative carpet of identical flakes.
- No chest-centered loot presentation.
- At least three seed examples must show materially different but archaeologically coherent reduction histories.
- From several viewing angles, debris should still point back toward plausible work positions.

## Production-Readiness Requirements

Hero specification completion does not equal runtime production admission.

Production admission requires:
1. registry/schema entry for `cw:e01_stone_tool_knapping_ground`;
2. deterministic procedural implementation or target-format template implementation;
3. work-position solver tests;
4. provenance and palette-coherence tests;
5. directional debris-field tests;
6. sharp-debris circulation validation;
7. core/hammerstone lifecycle validation;
8. S/M/L scale validation;
9. biome/context adaptation tests;
10. active, vacated, repeated-use, abandoned, buried, disturbed, and repurposed state tests;
11. minimum 500-block exclusion tests;
12. family-reservation exception tests;
13. prohibited-technology/material audit;
14. export/load validation in supported target environment;
15. visual review of multiple deterministic seeds;
16. confirmation that useful finished-tool loot does not dominate normal outputs;
17. confirmation that the site remains distinct from camps, quarries, and later workshops.

Until those requirements are observed and verified, production status remains `IMPLEMENTATION_PENDING`.

## Hero Acceptance Checklist

A hero-quality E01-009 must answer yes to all of the following:
- Is lithic reduction clearly the reason this place exists?
- Can the raw stone source or transport relationship be inferred?
- Are work positions plausible?
- Do debris fans reflect those positions rather than random scatter?
- Are sharp-debris hazards reflected in circulation?
- Are reusable cores and hammerstones treated differently from waste?
- Does chronology affect spatial pattern in repeated-use variants?
- Does local geology control environmental material while toolstone follows provenance?
- Are later technologies absent?
- Is the 500-block unrelated-structure exclusion contract preserved?
- Are family exceptions explicit and parent-owned?
- Does the structure remain readable without labels or treasure containers?

If any answer is no, the structure is not ready for production admission.