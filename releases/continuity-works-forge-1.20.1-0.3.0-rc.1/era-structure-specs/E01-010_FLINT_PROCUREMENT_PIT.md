# Hero Structure Specification — E01-010 Flint Procurement Pit

Status: HERO SPECIFICATION / PRODUCTION DESIGN COMPLETE
Era: 01 — Lower Paleolithic / Early Human
Catalog position: 10 of 750
Structure ID: `cw:e01_flint_procurement_pit`
Primary family: resource procurement / lithic source extraction
Default exclusion radius: 500 blocks
Compatible family exception: may co-generate only inside an explicitly composed lithic-source, camp, travel-stop, or knapping parent reservation whose members share one parent placement and deterministic layout contract.

## Purpose

The Flint Procurement Pit is a shallow, task-specific extraction site where early humans expose, test, select, and remove knappable stone from a near-surface source. Its identity comes from the relationship among source geology, shallow extraction scars, working faces, spoil, tested/rejected nodules, carry-out routes, and limited source-side testing. It is not a mine, quarry complex, knapping workshop, habitation camp, or generic terrain depression.

A hero implementation must let a player read the procurement sequence: where usable stone occurs, where overburden was removed, where extraction concentrated, where poor material was rejected, and how selected stone left the site.

## Historical / Technological Context

The archetype represents Lower Paleolithic / early-human collection and shallow excavation of flint/chert-like toolstone or equivalent knappable stone exposed in soil, gravel, weathered bedrock, nodules, seams, or shallow pits. Permitted actions include hand collection, levering, hammerstone percussion, antler/bone/wood digging analogues where culturally valid, shallow scraping, testing nodules, and repeated return to a productive exposure.

The structure may not imply shafts, galleries, timber mine supports, cranes, carts, masonry, metal picks, blasting, formal benches, drainage engineering, permanent buildings, standardized quarry roads, or later industrial extraction.

## Archetype Boundary Contract

A valid Flint Procurement Pit must satisfy all of the following:

1. Resource extraction is the dominant signal.
2. A specific source exposure or shallow source zone is explicit.
3. At least one excavation scar or shallow pit is present.
4. Spoil and rejected material are spatially related to extraction.
5. Selected material has a readable departure/carry-out route.
6. On-site reduction remains subordinate to procurement.
7. Excavation depth remains shallow and open to the surface.
8. No later mining or quarry infrastructure is present.

If directional flake fans and work positions dominate, classify the site as E01-009 Stone Tool Knapping Ground. If large organized bedrock extraction terraces dominate, classify it as the later E01-011 Quartzite Quarry archetype rather than E01-010.

## Footprint and Scale Classes

### S — Opportunistic Procurement Pit
- Reservation: 10–18 blocks wide, 8–16 deep.
- Excavations: 1–2 shallow pits or scoops.
- Maximum modeled depth: 1–2 blocks below local grade.
- Source exposures: 1.
- Spoil patches: 1–3.
- Likely users: 1–3.

### M — Recurrent Flint Procurement Site
- Reservation: 18–32 blocks wide, 14–28 deep.
- Excavations: 2–5 overlapping shallow pits.
- Maximum modeled depth: 2–3 blocks.
- Source exposures: 1–3 linked lenses/seams.
- Spoil patches: 2–6.
- Likely users: 2–8 across repeated visits.
- Default hero scale.

### L — Group Procurement Field
- Reservation: 30–52 blocks wide, 22–42 deep.
- Excavations: 4–10 shallow pits/scoops.
- Maximum modeled depth: 2–4 blocks, never shaft-like.
- Source exposures: several related near-surface lenses.
- Spoil fields: multiple overlapping discard margins.
- Likely users: 6–16 over repeated episodes.

Large variants increase extraction history, source depletion, and spoil complexity rather than becoming formal mines.

## Architectural / Behavioral Program

The program is an extraction landscape rather than rooms:

1. Approach / carry-out path.
2. Source exposure or geological lens.
3. Overburden-removal zone.
4. Primary procurement pit.
5. Secondary/legacy pits for M/L variants.
6. Working face or extraction edge.
7. Spoil apron.
8. Rejected nodule field.
9. Testing patch for limited source-side percussion.
10. Selected-material staging patch.
11. Safe circulation lane between pits.
12. Exhausted/depleted source scar.
13. Weathered or partly infilled legacy pit.
14. Optional child knapping patch only through explicit compatible-family composition.

## Required Components

Hero admission requires a source exposure, at least one shallow excavation, spoil directly associated with excavation, rejected/tested stone, a carry-out route, a selected-material staging relationship, surface openness, and an extraction-first qualification score.

M/L variants additionally require multiple extraction scars or chronology phases, explicit circulation avoiding open pits, source-depletion state, and at least one older infilled/weathered extraction scar.

## Procedural Generation Logic

1. **Source candidate selection:** require a plausible near-surface knappable-stone source; reject deep-only geology.
2. **Surface fitness:** favor slopes, gravel cuts, stream terraces, weathered exposures, and stable shallow soil; reject deep water, severe cliffs, and destructive conflicts.
3. **Source-lens generation:** establish one or more deterministic source bands or nodule concentrations before excavation.
4. **Pit solver:** place irregular shallow scoops centered on high-value source cells. Pits may overlap through chronology but remain open to sky.
5. **Depth control:** cap depth by scale; any shaft-like geometry fails validation.
6. **Spoil projection:** move overburden and low-value source stone to the downslope/lateral edge of each pit rather than distributing uniformly.
7. **Testing/rejection:** add limited tested/rejected nodules adjacent to pits. Debris density must remain below knapping-ground thresholds.
8. **Selected-material staging:** place a small clean concentration on the carry-out side of the site.
9. **Circulation:** route access among pits and staging while avoiding pit interiors and dense spoil.
10. **Chronology:** repeated-use variants add older partially infilled pits, source depletion, shifted spoil, and new extraction on remaining productive lenses.
11. **Family reservation:** unrelated structures obey the 500-block minimum exclusion. Same-parent compatible lithic-source compositions may share the reservation without destructive replacement.

## Seed Determinism

Recommended named substreams: `source_candidate`, `source_lenses`, `pit_layout`, `pit_depth`, `spoil_projection`, `testing`, `selected_material`, `circulation`, `chronology`, `condition`, `culture_hook`.

Primary extraction geometry must remain stable if later decorative passes are added.

## Biome / Environment Adaptations

Temperate and boreal sites favor weathered slopes, gravel lenses, and forest-edge exposures. Tundra/alpine variants expose more stone and need less overburden. Savanna/arid variants use stronger sediment and weathered-bedrock contrast and must avoid flash-flood channels. Tropical variants emphasize rapid vegetation recolonization and soil infill. Coastal/riverine variants may use gravel-terrace or eroded-bank procurement but must remain above active destructive flow.

## Culture-Variant Hooks

Culture configuration may alter preferred source quality, willingness to transport material, pit spacing, reuse frequency, degree of testing at source, cache/staging behavior, and attachment to camps or travel routes. It may not introduce later mining technology or unsupported modern ethnic coding.

## Material Palette Logic

Terrain remains overwhelmingly local soil, gravel, stone, sand, and vegetation. Toolstone proxies must contrast enough to read as the selected source while remaining geologically coherent. Spoil uses displaced local substrate and rejected source stone. Organic digging-tool traces may be represented indirectly but must remain minor. Forbidden base materials include masonry, planks as formal structures, rails, metal fixtures, mine supports, chests/barrels as default storage, powered blocks, lamps, cranes, or machines.

## Condition Variants

- **Active:** open fresh pits, exposed source, selected-material staging, clean carry-out route.
- **Recently vacated:** fresh extraction remains but selected material is mostly removed.
- **Repeated-use:** overlapping pits, older infill, source depletion, multiple spoil phases.
- **Abandoned:** weathering, vegetation, partial pit infill, depleted staging.
- **Partially infilled:** sediment/litter obscures older scars while pit topology remains recoverable.
- **Eroded/disturbed:** runoff, frost, animals, or slope movement modify spoil and margins without erasing the extraction relationship.
- **Source depleted:** remaining exposed source is poor or sparse; extraction shifts laterally.
- **Later repurposed:** later paths/camps may overlay only additively; earlier extraction scars remain recoverable.

## Jigsaw / Family Relationships

Default behavior is standalone with minimum 500-block exclusion against unrelated independent structures. Compatible same-parent relationships include E01-009 Stone Tool Knapping Ground, early-human camps, travel stops, and later resource-processing children where chronologically valid. Family compatibility never grants blanket overlap; shared placement requires one parent reservation/assembly.

## Infrastructure Dependencies

No built infrastructure is required. Environmental dependencies are a plausible near-surface source, stable access, surface drainage adequate to preserve an open shallow pit, and a carry-out direction. Optional parent infrastructure is limited to primitive paths/activity areas.

## Loot / Occupancy Hooks

Loot is sparse and distributed: rejected nodules, hammerstone proxies, limited reusable source pieces, and rare cached high-quality raw material. Finished tools should be uncommon because selected material is transported away. Occupancy is temporary and task-specific; no permanent inhabitants or storage economy is implied.

## Validation Criteria

Validation must confirm: extraction primacy; explicit source; at least one shallow open pit; depth within scale cap; spoil-source relationship; selected-material staging; carry-out route; safe circulation; procurement debris below knapping-ground dominance; no shaft/galleries; no later-era infrastructure; deterministic replay; biome/material coherence; 500-block unrelated-structure exclusion; additive same-parent compatibility only.

## Production-Readiness Requirements

Production admission requires committed generator/template source, deterministic tests, worldgen placement/protection integration, valid Minecraft block IDs, target NBT/template-pool materialization, fresh-world load evidence, visual review proving procurement readability, deterministic replay evidence, exclusion/conflict tests, and confirmation that the structure is distinguishable from E01-009 and E01-011 at normal exploration distance.

## Hero Acceptance Checklist

A reviewer must be able to answer yes to all of these: Is a specific source visible? Are shallow extraction scars obvious? Is spoil connected to those scars? Can I tell where selected stone left the site? Is testing subordinate to extraction? Is the site open to the sky? Does it avoid mine/quarry-industrial language? Does the 500-block unrelated exclusion remain intact? If any answer is no, the structure is not hero-ready.
