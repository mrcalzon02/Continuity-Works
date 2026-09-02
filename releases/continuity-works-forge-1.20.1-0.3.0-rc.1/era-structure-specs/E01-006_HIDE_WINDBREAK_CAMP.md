# Hero Structure Specification — E01-006 Hide Windbreak Camp

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 6 of 750
Structure ID: `cw:e01_hide_windbreak_camp`
Primary family: habitation / portable hide windbreak camp
Default exclusion radius: 500 blocks
Compatible family exception: explicitly registered camp children may share one parent reservation and deterministic layout contract.

## Purpose

Hide Windbreak Camp represents a short-lived open camp whose defining constructed element is one or more animal hides tensioned, draped, pegged, weighted, or lashed against simple supports to interrupt prevailing wind. The hide surface is the primary environmental technology. The structure remains open-sided, low-mass, portable, repairable, and recoverable when the group moves.

It is distinct from E01-005 Lean-To Windbreak, which is primarily a leaned structural plane assembled from brush, branches, vegetation, and local supports. E01-006 must visibly depend on hide membranes and their tension/weighting system. It is also distinct from later hide tents: the protected zone is not fully enclosed, no continuous tent envelope is required, and the windbreak should normally protect a lee-side activity/sleeping pocket rather than define an interior room.

## Historical / Technological Context

The archetype assumes Lower Paleolithic / early-human capabilities only: animal procurement or scavenging, hide removal and crude handling, simple stone tools, fire, opportunistic cordage/sinew/plant-fiber analogues where configured, branches/poles, stones, bone, and terrain anchors.

The design must not imply tailored sewn tent panels, regular manufactured rope, milled poles, permanent post foundations, ceramic storage, formal furniture, masonry, metal fasteners, doors, chimneys, or durable framed architecture. Hide availability is an explicit resource constraint; a culture/environment configuration without plausible large hides must strongly suppress or disable this archetype.

## Archetype Boundary Contract

A valid instance must satisfy all of the following:

1. Hide membrane is the dominant constructed weather barrier.
2. Barrier responds to a derived exposure/wind direction.
3. Construction remains open-sided and non-room-like.
4. At least one readable tension, weighting, draping, or anchoring relationship exists.
5. Structural mass remains low enough to read as portable or readily dismantled.
6. Protected occupation occurs principally in the lee of the hide surface.
7. No later-era tent architecture or durable hut logic appears.

If the hide is merely decorative on a brush structure, classify as E01-005 or E01-004 instead.

## Footprint and Scale Classes

### S — Single-Hide Screen
- Barrier length: 3–7 blocks.
- Effective height: 2–3 blocks.
- Lee protection depth: 3–6 blocks.
- Reservation footprint: approximately 8–14 by 8–14 blocks.
- Supports/anchors: 2–4.
- Hearths: 0–1.
- Occupancy: 1–4 individuals.
- Typical use: overnight hunting stop, carcass-processing pause, emergency exposed-ground shelter.

### M — Family Hide Windbreak Camp
- Barrier length: 6–12 blocks, straight or shallow-curved.
- Effective height: 2–4 blocks.
- Lee protection depth: 5–10 blocks.
- Reservation footprint: approximately 14–24 by 12–22 blocks.
- Supports/anchors: 3–8.
- Hearths: 0–1 primary, optional prior hearth trace.
- Occupancy: 4–10 individuals.
- Default hero scale.

### L — Multi-Screen Hide Camp
- Combined barrier length: 10–22 blocks across 2–4 linked screens.
- Effective height: 2–4 blocks.
- Lee protection depth: 8–16 blocks across overlapping wind shadows.
- Reservation footprint: approximately 22–38 by 18–34 blocks.
- Supports/anchors: 6–16.
- Hearths: 1–2 maximum.
- Occupancy: 8–18 individuals.
- Must remain a camp of screens and open occupation pockets, not become a ring tent or enclosed compound.

## Architectural / Behavioral Program

The archetype uses environmental zones rather than rooms:

1. **Exposure edge** — windward terrain from which the principal environmental load arrives.
2. **Anchor/support line** — stones, poles, trees, terrain edges, bone/wood supports, or combinations thereof.
3. **Hide membrane** — irregular dominant barrier with visible sag, overlap, edge variation, or weighting.
4. **Tension/weight points** — locations where membrane geometry visibly relates to anchors.
5. **Primary lee pocket** — highest-value protected ground immediately behind the screen.
6. **Sleeping/rest zone** — driest and least exposed part of the lee pocket.
7. **Hearth zone** — optional; placed to benefit from protection without igniting the membrane or trapping smoke.
8. **Work zone** — tool repair, hide work, food processing, or sorting near light and circulation.
9. **Hide maintenance edge** — optional scraping/drying/repair evidence separated from clean sleeping ground.
10. **Cache zone** — sparse portable resources near the occupied pocket.
11. **Approach/circulation gap** — intentionally open route into the protected side.
12. **Discard edge** — downwind or lateral to sleeping and food handling.

## Required Components

Hero admission requires:
- a derived exposure vector;
- at least one dominant hide screen;
- readable support/anchor relationship;
- an open lee-side occupation zone;
- traversable approach without passing through the membrane;
- era-valid support and anchoring materials;
- low structural mass;
- no full enclosure;
- no unsupported floating membrane geometry;
- default 500-block reservation against unrelated structures.

M/L variants additionally require distinct rest and work/hearth relationships and at least one visible repair, overlap, weighting, or tension variation preventing the screen from reading as a perfect wall.

Recommended probabilistic components include hearth/ash lens, bedding analogue, carried toolstone, bone/food traces, spare hide or hide-working trace, fuel bundle, hammerstone, edge weights, abandoned anchor stones, and repeated-occupation scars.

## Procedural Generation Logic

### 1. Candidate micro-site search

Score terrain for dryness, moderate slope, usable lee floor, access, nearby fuel/resources, hide-resource plausibility, absence of flood channels, absence of conflicting reservations, and availability of natural anchors. Avoid excessive terrain flattening.

### 2. Exposure-vector derivation

Derive a deterministic dominant exposure vector from biome/climate configuration, terrain openness, ridgelines, coastlines, valley alignment, and local obstruction. If the host platform lacks wind simulation, this vector remains a structure-generation environmental proxy.

### 3. Hide-resource gate

Before geometry generation, evaluate a `hide_availability` score from fauna/culture/environment configuration. Classify as:
- `HIDE_ABSENT` — archetype rejected;
- `HIDE_SCARCE` — S only or patched small M;
- `HIDE_AVAILABLE` — normal S/M;
- `HIDE_ABUNDANT` — M/L eligible.

This resource gate is essential to the archetype rather than decorative flavor.

### 4. Anchor classification

Select among natural trees, deadwood, boulders, rock faces, shallow driven poles, forked branches, heavy stones, or mixed anchors. Prefer existing terrain features. Driven supports must remain sparse and primitive.

### 5. Barrier spine

Generate a short irregular line or shallow arc broadly transverse to exposure. Permit asymmetry, stagger, gaps, and terrain-driven bends. Reject perfect long straight walls and closed loops.

### 6. Membrane assembly

Construct hide surfaces as one or more irregular panels. Depending on target block resolution, represent them through approved palette blocks, thin elements, entities, or modular micro-templates. Vary bottom clearance, sag proxy, overlap, torn edges, and attachment height. Do not create a rigid rectangular billboard.

### 7. Tension and weighting pass

Every major membrane segment must resolve to plausible anchors. Generate combinations of upper lash/tension points, lower stone weights, draped-over-support relationships, edge pegs, or heavy-object pinning. No membrane section may float without structural explanation.

### 8. Lee-zone extraction

Project a deterministic wind-shadow proxy behind the screen using barrier height, width, permeability/gaps, terrain shielding, and exposure strength. Sleeping and cache zones favor the strongest lee values; work and hearth may occupy transitional lee areas.

### 9. Hearth safety pass

Classify candidate hearth positions by membrane distance, downwind smoke path, dry fuel proximity, overhead clearance, and circulation. Reject hearths likely to ignite hide/brush. A no-fire variant is valid.

### 10. Camp activity pass

Place rest, work, hide maintenance, cache, fuel, and discard evidence according to scale. Keep traces sparse and spatially meaningful.

### 11. Wear/repair pass

Add deterministic panel overlap, replacement patches, shifted weights, re-tensioned edges, old peg/anchor traces, or prior screen alignment for recurrent camps.

### 12. Terrain integration

Preserve existing vegetation, rocks, drainage, and slope except for minimal occupation wear. The camp adapts to terrain rather than terraforming it.

### 13. Reservation pass

Reserve the footprint plus the minimum 500-block exclusion against unrelated independent structures. Compatible camp children may occupy the same reservation only through explicit family registration and parent ownership.

## Seed Determinism

Identical seed, generator version, biome/environment state, culture configuration, and condition state must reproduce placement and primary geometry. Recommended named random substreams:
- `micro_site`
- `exposure`
- `hide_availability`
- `scale`
- `anchor_set`
- `barrier_spine`
- `hide_panels`
- `tension_weights`
- `lee_zone`
- `hearth`
- `activity_zones`
- `repair_history`
- `condition`
- `culture_hook`

Later decoration additions must not reshuffle primary placement decisions.

## Biome / Environment Adaptations

### Temperate forest
Natural tree anchors are common; hides compete with readily available brush, so spawn weighting should depend strongly on culture/resource context. Damp ground raises drainage penalties.

### Boreal / cold
Hide barriers receive increased thermal/wind-protection value. Fur-bearing hide analogues and compact lee-side sleeping clusters are favored. Snow must not seal circulation.

### Tundra / alpine
High archetype fitness where hides are available. Timber supports are scarce; stone weights, bone/antler analogues, and low-profile screens become more common. Barrier height trends lower under severe exposure.

### Savanna / dry grassland
Portable hide screens work well in exposed camps. Poles may be sparse; screens may use carcass-processing resources and stones. Shade benefit may complement wind protection.

### Arid / desert
Strong weighting toward low, heavily weighted membranes. Avoid washes and flash-flood paths. Organic structural material is scarce; hide preservation may be high in abandoned dry states.

### Tropical / humid
Lower weighting because hide membranes deteriorate rapidly and ventilation is valuable. Screens become more permeable and smaller. Rot/damage progression accelerates.

### Coastal
Exposure vector may derive strongly from shoreline orientation. Heavy stone weighting is common. Salt spray and storms increase wear. Tidal/flood zones are rejected.

## Culture-Variant Hooks

Culture packs may modify hide procurement/scavenging assumptions, panel size, preferred animal-hide class, support style, weighting style, screen curvature, group size, hearth probability, reuse frequency, hide-working intensity, sleeping arrangement, and whether hides are removed when camp is abandoned.

Hooks may not introduce sewn fitted tents, regular woven canvas, metal fittings, manufactured rope, permanent frames, formal doors, or unsupported claims about named historical peoples.

## Material Palette Logic

### Hide membrane
Use target-approved hide/fur/leather analogues appropriate to era and fauna configuration. Palette variation may encode species class, weathering, hair-on/hair-off treatment, patching, or smoke staining without implying industrial tanning.

### Supports
Local branches, saplings, deadwood, bone/antler analogues where structurally plausible, existing trees, rock faces, and boulders.

### Anchors and weights
Local stone dominates. Carried stones may appear sparingly where useful. No shaped masonry.

### Ground treatment
Existing substrate should dominate. Permit compressed soil, displaced grass, sparse bedding vegetation, ash, charcoal, bone, and small lithic scatter.

Forbidden base materials include planks, bricks, cut masonry, glass, metal fixtures, chains, manufactured rope, ceramics, doors, chests, barrels, permanent torches/lanterns, redstone/powered systems, and formal furniture.

## Condition Variants

### Active / intact
Membranes are tensioned and substantially complete; weights/anchors are readable; occupation traces are fresh.

### Maintained / patched
One or more panels show overlap or patch proxies, shifted anchors, replacement weights, or re-tensioned edges.

### Temporarily vacant
Hide screen remains standing but hearth is cold and portable items are reduced.

### Weather-damaged
One edge has torn loose, sagged, or partially collapsed; lee function remains inferable.

### Partially dismantled
Some hides have been removed for travel while anchors, weights, poles, and occupation traces remain. This is a particularly important portability state.

### Abandoned / organic decay
Membrane survival decreases according to climate. Poles, weights, ash, bone, and compacted ground may outlast hides.

### Archaeological trace
Hide is normally absent. Recognizable evidence consists of patterned anchor stones/weights, post traces where supported, hearth/ash, lithics, bone, and occupation surface relationships. It must not fabricate impossible preserved hide in hostile preservation contexts.

### Later-era repurposed
A later group may reuse the sheltered micro-site or surviving anchors. Later additions are an explicit overlay; the original trace remains recoverable and is never rewritten as later architecture.

## Jigsaw / Family Relationships

Default placement is standalone with 500-block exclusion against unrelated structures.

Compatible children within one shared parent camp reservation may include E01-007 Hearth Circle, E01-009 Stone Tool Knapping Ground, E01-012 Butchery Site, E01-15 Marrow Processing Ground, E01-27 Tool-Stone Cache, E01-28 Food Cache Pit, small refuse scatters, and water-access or game-trail relationships when those archetypes are implemented.

E01-004 Temporary Brush Shelter and E01-005 Lean-To Windbreak are siblings, not automatic children. Mixed shelter camps require an explicit compound-family recipe so the compatibility exception remains bounded and non-destructive.

## Infrastructure Dependencies

Required built infrastructure: none.

Environmental/resource dependencies:
- usable dry ground;
- plausible hide supply;
- anchors or primitive support materials;
- exposure sufficient to justify a windbreak;
- optional nearby fuel, water, hunting/scavenging territory, and toolstone.

Roads, agriculture, permanent settlement grids, engineered drainage, utilities, and formal fortification are invalid dependencies.

## Loot / Occupancy Hooks

Loot represents portable traces, not treasure storage. Potential finds include raw toolstone, flakes/debitage proxies, hammerstones, bone fragments, hide/fur scraps where preservation permits, sinew/fiber analogues where configured, charcoal/ash, food remains, and rare carried stones.

No chest is required or preferred. Distribution should use floor scatter, cache pockets, hearth deposits, hide-maintenance zones, crevices, or archaeology-aware target-system containers.

Occupancy must be capped by usable lee area, membrane coverage, exposure severity, and hearth safety. L variants may represent several related household/activity groups but cannot behave as permanent villages.

## Additive / Non-Destructive Compatibility

- Enforce minimum 500-block exclusion against unrelated independent structures.
- Exempt only explicitly registered family members sharing one parent reservation.
- Never overwrite third-party structures, protected blocks, or unrelated structure reservations.
- Adapt around terrain and existing natural features rather than flattening them.
- Compatibility integrations add candidate anchors, palettes, family links, or placement opportunities; they never replace another system's structures or generation tables.
- If safe placement cannot be negotiated, reject or relocate this structure.

## Validation Criteria

### Geometry
- Membranes have physical support/anchor explanations.
- No floating panels or impossible weight relationships.
- Approach and lee zones remain traversable.
- Structure remains open-sided.

### Archetype distinction
- Hide membrane is dominant, not decorative.
- Wind/exposure response is readable.
- It does not resemble a generic brush lean-to, enclosed hide tent, hut, fence, or wall.
- Portability is visually and procedurally credible.

### Historical/technological fitness
- No later-era manufactured materials or construction methods.
- Hide availability is validated rather than assumed universally.
- Intervention remains temporary and low-mass.

### Environmental fitness
- Barrier orientation responds to exposure.
- Occupation avoids flood/runoff hazards.
- Hearth does not create obvious membrane fire/smoke failure.
- Biome materials are locally plausible or explicitly carried.

### Procedural fitness
- Fixed inputs reproduce fixed primary geometry.
- Multiple seeds produce meaningful variation in anchors, panels, orientation, scale, and condition.
- Optional decoration cannot perturb major geometry.

### Compatibility
- 500-block unrelated exclusion passes.
- Family exceptions share parent reservation ownership.
- Third-party/protected content remains intact.
- Rejected conflicts fail cleanly without destructive fallback.

### Visual readability
A reviewer without labels should infer: an exposed camp; animal hide intentionally erected against weather; protected activity occurring behind it; primitive anchors/weights; temporary occupation; and plausible dismantling/reuse.

## Production-Readiness Requirements

`HERO_SPEC_COMPLETE` does not imply runtime implementation.

Production admission requires observed evidence of:
1. schema/registry entry for `cw:e01_hide_windbreak_camp`;
2. runtime generator/template implementation;
3. hide-resource gating implementation;
4. exposure-vector and anchor selection implementation;
5. supported membrane/tension geometry;
6. S/M/L generation across representative seeds;
7. biome adaptation tests;
8. condition-state tests including partial dismantling and archaeological trace;
9. deterministic repeat-generation hash/geometry equivalence;
10. 500-block exclusion tests;
11. compatible-family shared-reservation tests;
12. conflict tests proving non-destructive rejection/relocation;
13. visual inspection proving archetype distinction;
14. target platform load/export validation;
15. no unresolved validation errors.

Until these are observed, production status remains `IMPLEMENTATION_PENDING`.

## Hero Acceptance Checklist

- [x] Purpose defined.
- [x] Historical/technological ceiling defined.
- [x] S/M/L scale classes defined.
- [x] Behavioral program defined.
- [x] Required/probabilistic components defined.
- [x] Procedural generation logic defined.
- [x] Hide-resource gate defined.
- [x] Exposure and lee logic defined.
- [x] Biome adaptations defined.
- [x] Culture hooks defined.
- [x] Material palette logic defined.
- [x] Condition variants defined.
- [x] Jigsaw/family relationships defined.
- [x] Infrastructure dependencies defined.
- [x] Loot/occupancy hooks defined.
- [x] 500-block exclusion doctrine preserved.
- [x] Additive/non-destructive compatibility preserved.
- [x] Validation criteria defined.
- [x] Production-admission requirements defined.

Hero specification: COMPLETE.
Runtime implementation: NOT YET CLAIMED.
