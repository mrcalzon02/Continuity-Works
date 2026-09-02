# E01-011 — Quartzite Quarry

Status: Stage 1 HERO_SPEC_COMPLETE
Era: Lower Paleolithic / Early Human
Family: `continuityworks:early_human_lithic_source`
Default unrelated-structure exclusion: minimum 500 blocks
Compatibility: additive and non-destructive; compatible family pieces may compose only under one explicit parent reservation/assembly.

## Purpose and identity

The Quartzite Quarry is a repeated-use lithic extraction landscape focused on obtaining large, durable quartzite blanks from a naturally exposed bed, ridge, outcrop, or boulder field. It is larger, more face-oriented, and more materially intensive than E01-010 Flint Procurement Pit. It may include coarse primary reduction needed to free or test transportable blanks, but it must not read as E01-009 Stone Tool Knapping Ground, where reduction debris and finished-tool production dominate.

The visual order must read: **source exposure → working face/bench → extraction scar → heavy rejected fragments/spoil → selected blank staging → haul route**.

## Historical and technological context

The archetype represents Lower Paleolithic procurement using direct percussion, hard hammerstones, opportunistic levering, natural joints, repeated blows, and gravity. Technology is intentionally pre-industrial and pre-engineered. Valid evidence includes battering, broken source blocks, coarse reduction fragments, cleared work footing, reused faces, and transport staging.

Prohibited identity drift includes cut ashlar, drilled blast holes, metal wedges, hoists, cranes, carts, rails, ladders as engineered quarry infrastructure, timber shoring, shafts, galleries, masonry retaining systems, paved haul roads, powered processing, or modern bench geometry.

## Footprint and scale classes

### Small
- nominal envelope: 23 × 8 × 19 blocks;
- 1 principal exposure or boulder cluster;
- 1–2 working-face segments;
- 1 extraction apron;
- short haul path;
- limited selected-blank staging.

### Medium
- nominal envelope: 37 × 10 × 31 blocks;
- 1 dominant exposure with 2–4 working-face segments;
- partial natural bench or terrace;
- 2–3 extraction/apron concentrations;
- recognizable coarse-debris field;
- dedicated staging edge and haul lane.

### Large
- nominal envelope: 57 × 12 × 45 blocks;
- elongated source ridge/outcrop;
- 4–7 working-face segments;
- multiple reused natural benches/ledges;
- broad but irregular heavy-fragment apron;
- several selected-blank staging points;
- persistent haul corridor and legacy exhausted face.

Scale must increase process complexity and reuse evidence, not simply stretch dimensions.

## Architectural / archaeological program

This is an extraction landscape, not a building. Required spatial components are:

1. **Natural source exposure** — quartzite-role stone must be legible as part of an outcrop/ridge rather than scattered decorative blocks.
2. **Working face** — at least one exposed near-vertical or stepped natural face showing repeated material removal.
3. **Work footing / natural bench** — stable irregular surface adjacent to the face; never a fully engineered platform.
4. **Extraction scars** — localized recesses, notches, broken ledges, or missing face cells.
5. **Heavy fragment apron** — large coarse rejects and spoil concentrated downslope/outward from the face.
6. **Hammerstone / battering zone** — sparse durable-stone proxies immediately associated with extraction points.
7. **Primary reduction zone** — optional but expected at medium/large scale; coarse preparation only, subordinate to extraction.
8. **Selected blank staging** — small clusters of source material positioned for transport.
9. **Haul route** — cleared/compacted irregular route leaving the face and avoiding the densest fragment apron.
10. **Legacy/exhausted face** — repeated-use conditions may preserve older scars or depleted segments.

There are no required enclosed rooms.

## Procedural generation logic

Generation must use deterministic named random streams derived from world seed, catalog ID, and function. Minimum streams: source orientation, face topology, bench layout, extraction scars, coarse debris, hammerstones, staging, haul routing, chronology, condition, biome/material, and culture variation.

1. Choose a valid surface or shallow-slope source context.
2. Generate an elongated source ridge/outcrop with a dominant strike direction.
3. Select one side as the accessible working face based on slope and open-space fitness.
4. Break the face into irregular segments rather than a continuous manufactured wall.
5. Carve bounded extraction scars into selected segments.
6. Establish natural benches/work footing at the base of viable face segments.
7. Project coarse fragment/spoil aprons outward and slightly downslope; distribution must be anisotropic.
8. Place sparse hammerstone/battering proxies close to active scars.
9. At medium/large scale, create coarse primary-reduction clusters, but enforce a lower density and lower fine-debris signature than E01-009.
10. Place selected blanks at a safe staging edge.
11. Route a haul corridor from staging to the site boundary while avoiding the densest fragment hazard cells.
12. Apply chronology/condition transforms without destroying the extraction-first identity.

Named substreams must make seed replay stable and allow one subsystem to change without re-randomizing unrelated systems.

## Biome and environmental adaptations

- Temperate: stone/diorite/calcite-role source with coarse dirt and gravel footing.
- Boreal: stone/tuff host rock, gravel debris, sparse moss only outside active extraction cells.
- Tundra: exposed stone, gravel/frozen-looking footing, minimal vegetation.
- Savanna: granite/stone host, coarse dirt apron, high-exposure open quarry face.
- Arid: sandstone/gravel host surfaces with quartzite-role source remaining visually distinct; no vegetation bedding proxies.
- Tropical: weathered stone, dirt margins, limited moss on abandoned surfaces but never across active face scars.
- Coastal: gravel/stone terraces; reject sites vulnerable to partial sediment reworking.

Terrain adaptation must preserve major natural landform logic. The quarry may expose and articulate a source outcrop but must not flatten a large region into an artificial platform.

## Culture-variant hooks

Culture variants may alter preferred face orientation, hammerstone material choice, blank selection size, amount of on-site primary reduction, staging organization, repeated-use intensity, and path reuse. They may not add technology above the era ceiling.

Suggested bounded variants:
- transport-heavy: minimal reduction, larger selected blanks;
- source-testing: more rejected blocks and battering evidence;
- repeated-specialist: clearer face reuse and staging discipline;
- opportunistic: irregular boulder/outcrop exploitation with weak spatial formalization.

## Material palette logic

Because vanilla Minecraft has no natural quartzite block, the generator must use a declared **quartzite-role proxy** chosen from valid natural-looking vanilla blocks, with `minecraft:diorite` as the default baseline. Metadata must identify it as a semantic proxy rather than claim geological literalism.

Palette roles:
- host rock;
- quartzite-role source;
- coarse spoil/reject;
- compacted ground;
- hammerstone-role durable block;
- optional weathering material for abandoned conditions.

Manufactured quartz blocks, polished decorative masonry, bricks, concrete, metal machinery, or dimensionally cut stone are invalid baseline materials.

## Condition variants

### Active
Fresh face scars, concentrated hammerstone activity, open haul route, selected blanks staged.

### Recently vacated
Same organization with no active occupancy and modest scatter.

### Repeated use
Overlapping face scars, legacy bench cells, reused haul route, mixed-age fragment apron.

### Abandoned
Weathering and partial vegetation/sediment encroachment; quarry face remains legible.

### Partially collapsed
Localized rockfall from face/ledge, blocked cells, shifted fragment apron; no total burial.

### Sediment reworked
Water/wind/frost movement redistributes lighter apron materials while major face/scars remain.

### Source depleted
One or more face segments visibly exhausted; activity shifts laterally.

### Repurposed
Later low-intensity camp/travel use may occupy safe footing, but the quarry remains visibly older and primary. Repurposing must be additive and may not erase extraction evidence.

## Jigsaw and family relationships

Primary family: `continuityworks:early_human_lithic_source`.

Compatible same-parent relationships may include:
- E01-010 Flint Procurement Pit only where a mixed lithic-source landscape is explicitly selected;
- E01-009 Stone Tool Knapping Ground as a source-adjacent child activity zone;
- temporary camp/hearth/travel elements where one parent archaeological landscape owns the full assembly.

Family equality alone never grants overlap or exclusion bypass. Only the same explicit parent reservation/assembly may place compatible pieces inside the normal 500-block exclusion envelope. Separate structure starts remain subject to minimum 500-block exclusion.

## Infrastructure dependencies

No constructed infrastructure is required. Placement depends on environmental resources:
- exposed or shallow quartzite-role source;
- workable surface access;
- enough stable footing beside the face;
- safe outward debris projection;
- viable haul egress.

A road, village, settlement, mine network, or engineered transport system must never be required.

## Loot and occupancy hooks

Loot should be sparse and task-specific rather than chest-driven. Valid abstract hooks include selected blank material, hammerstone proxies, coarse rejected fragments, and rare useful partially reduced blanks. Default generation should not require containers.

Occupancy hooks may place a small number of workers at active face, staging, or haul positions. Occupancy must respect fragment hazards and cannot imply dense permanent settlement.

## Additive/non-destructive compatibility

Generation must not replace unrelated structures, erase third-party terrain features wholesale, or mutate another mod's structure tables destructively. Compatibility adapters may add this archetype to valid candidate pools/tags or reserve compatible family space. Terrain changes must be bounded to the quarry envelope and semantic excavation cells.

## Validation criteria

A valid E01-011 must satisfy all of the following:
- extraction is the dominant readable purpose;
- a coherent source outcrop/ridge exists;
- at least one working-face segment exists;
- extraction scars are visibly tied to the source face;
- coarse fragment/spoil apron projects away from the face;
- safe work footing exists near active faces;
- selected-material staging exists;
- haul route exists and avoids the densest hazard cells;
- primary reduction, if present, remains subordinate to extraction;
- geometry is larger/more face-oriented than E01-010 shallow procurement pits;
- no industrial/later quarry infrastructure is present;
- all material IDs are valid baseline Minecraft blocks;
- generation is deterministic for identical inputs;
- unrelated structures retain minimum 500-block exclusion;
- same-parent family exception is explicit rather than inferred from family ID;
- placement and compatibility remain additive/non-destructive.

Fail toward E01-010 if the site is primarily shallow isolated pits without a recognizable quarry face. Fail toward E01-009 if reduction debris/work positions dominate the source/extraction relationship. Fail as anachronistic if engineered quarry infrastructure dominates.

## Production-readiness requirements

Production admission requires, in addition to committed source:
- focused deterministic generator tests passing in an observed authoritative environment;
- S/M/L replay fixtures or equivalent deterministic evidence;
- worldgen structure/structure-set/protection validation passing;
- minimum 500-block exclusion and same-parent family exception tests passing;
- valid block registry/material validation;
- NBT/template-pool or equivalent runtime materialization where required by target packaging;
- actual Minecraft load/new-world generation evidence;
- visual review confirming source face, scars, apron, staging, and haul route read correctly at player scale;
- compatibility test demonstrating no destructive replacement of unrelated structures/worldgen;
- ledger update recording exact evidence and production status.

Until those gates are observed, source completion remains `VALIDATION_PENDING`, not `PRODUCTION_ADMITTED`.
