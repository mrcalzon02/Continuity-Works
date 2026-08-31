# Facility Archetypes and Corporate Language

## Objective

Continuity Works must generate structures that occupy recognizable architectural roles rather than merely receiving semantic labels. A gas station, crude-oil extraction pad, bulk tank farm, fuel terminal, and diesel refinery therefore have separate functional contracts even when they share individual modules such as tanks, utility rooms, or pipe racks.

The facility system also separates **what a place does** from **who operates it**. This lets two facilities share an archetype while remaining visually distinguishable through synthetic corporate language.

## Architectural model

`StructureLibrary` remains the source of generic geometry and functional modules. `FacilityLibrary` is an additive semantic layer above it.

A facility archetype supplies purpose, scale tiers, required and optional modules, site zoning, circulation, recognition signatures, allowed corporate languages, and distinction rules. A corporate language supplies visual grammar: vanilla palette, silhouette preferences, facade rhythm, signage geometry, lighting behavior, maintenance character, and recurring identity motifs. A facility reference combines the two and supplies a deterministic vanilla-block blueprint suitable for testing and generation guidance.

This split prevents palette changes from silently redefining facility function and prevents functional archetypes from becoming copies of one brand.

## Baseline structural vocabulary

Structural Library 0.3 adds nine fuel/petroleum primitives: fuel canopy, pump island, roadside pylon, pumpjack, storage tank, pipe rack, process column, flare stack, and loading gantry. Connector contract v2 adds vehicle lanes, controlled vehicle gates, and process-pipe transfer interfaces.

These modules remain abstract. A `storage_tank_9x7x9` is not owned by a refinery, tank farm, or extraction pad; those archetypes decide how many tanks are used, where they sit, and what they mean in the site composition.

## Baseline archetypes

### Rural gas station

Road-facing public fueling. Mandatory visual read: customer canopy, pump islands, storefront, and pylon/sign identity. Bulk industrial equipment must remain subordinate.

### Highway travel stop

A larger customer/fleet environment with expanded fueling capacity, heavy-vehicle circulation, and substantial public frontage. It must read larger and more circulation-intensive than a rural station while remaining retail-forward.

### Crude-oil well pad

Extraction-equipment-dominant site. The pumpjack/well equipment is the principal silhouette, with limited crude storage, visible collection piping, a control/service shed, and maintenance access.

### Bulk tank farm

Storage-dominant compound. Repeated tanks, containment, pipe headers, and controlled loading are the primary visual grammar. Dense vertical process equipment is deliberately absent.

### Compact diesel refinery

Process-dominant industrial campus. Vertical process columns, dense connecting pipework, product tanks, flare system, utility/control zone, and loading interface are mandatory signatures.

### Truck fuel terminal

Distribution-dominant facility. Bulk storage supports multiple loading bays and heavy-vehicle throughput; public pump islands/storefronts are excluded and process towers remain subordinate or absent.

## Corporate languages

The initial synthetic operators are intentionally different rather than simple recolors.

**Northstar Fuel** is clean, bright, horizontal, highly maintained, and retail-facing, using a thin canopy, tall pylon, glazed frontage, white/light-gray massing, and red/blue bands.

**Frontier Cooperative** is rural, practical, and heavier, with sandstone/wood character, green/yellow identity, gable preference, gravel service areas, shorter signage, and less rigid symmetry.

**Iron Mesa Energy** is equipment-first and industrial, emphasizing dark structural frames, gray/deepslate masses, orange/yellow hazard accents, visible piping, and task-focused lighting.

**Atlas Basin Refining** is an orderly legacy industrial language: pale tanks, repeated structural bays, oxidized-copper-like process piping, blue/orange identity, stone/brick service buildings, and process-campus hierarchy.

These identities are fictional and are not intended to reproduce trademarked real-world stations or industrial operators.

## Reference compiler

A facility reference uses five architectural primitives: block, filled box, hollow box, line, and cylinder. The blueprint stores semantic roles rather than fixed materials. The selected corporate palette resolves those roles to vanilla blocks at compile time.

This has two useful consequences. First, an architectural reference can be materialized directly as a concrete Continuity Works structure for audits/export. Second, an archetype-compatible corporate override can reuse reference geometry while changing the material language, making corporate coherence independently testable.

The compiler guarantees the baseline output remains in the `minecraft:` namespace and rejects out-of-bounds placements or unresolved palette roles.

## Validation gates

Facility validation is layered. The structural dependency must pass first. Corporate profiles must have valid synthetic IDs, design-language tokens, and vanilla palettes. Archetypes must resolve every required module and allowed corporate identity. References must contain every required archetype module, fit their module placements inside the declared site bounds, satisfy the archetype's required visual signatures, and compile successfully to vanilla blocks.

`evaluate_reference()` is the first recognizability gate. It is deliberately explicit rather than pretending visual understanding can be inferred from a filename. Future stages can add richer silhouette metrics, zone-adjacency scoring, visual renders, and runtime placement tests without changing these stable semantic IDs.

## Non-destructive extension

Mod compatibility, alternative palettes, cultural themes, biome adaptations, damaged/abandoned variants, and project-specific corporate profiles must be additive. They may map or extend a base archetype/reference but must not mutate the authoritative baseline in place.
