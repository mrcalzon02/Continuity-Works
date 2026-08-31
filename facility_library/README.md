# Continuity Works Facility Semantic Library

This library adds architectural meaning above the generic structural library. It does not replace layouts or modules and does not hard-code a facility type into the base geometry system.

## Layers

A **corporate language** defines a synthetic operator identity: vanilla material palette, massing bias, signage geometry, facade rhythm, lighting, maintenance character, and recurring silhouette tokens.

A **facility archetype** defines function: required structural modules, site zones, circulation, recognizable visual signatures, allowed corporate languages, and explicit distinction rules against similar facility types.

A **facility reference** combines one archetype with one corporate language and an architectural blueprint. The blueprint is intentionally a game-building reference, not an engineering specification. `FacilityLibrary.compile_reference()` resolves its semantic material roles into vanilla `minecraft:` blocks and returns the existing Continuity Works `{size, blocks, metadata}` physical structure shape.

## Fuel and petroleum baseline

The first semantic family covers rural gas stations, highway travel stops, crude-oil well pads, bulk tank farms, compact diesel refineries, and truck fuel terminals. The first five concrete references deliberately include two gas stations built from the same functional archetype but different corporate languages so brand identity can be tested independently from facility recognizability.

Synthetic corporate profiles are Northstar Fuel, Frontier Cooperative, Iron Mesa Energy, and Atlas Basin Refining. They are fictional design systems rather than copies of real companies.

## Recognition and distinction

Archetypes declare `required_signatures` such as `fuel_canopy`, `pumpjack`, `repeated_storage_tanks`, `process_columns`, or `flare_stack`. References declare the signatures they visibly implement. `FacilityLibrary.evaluate_reference()` reports missing signatures and a recognizability gate.

Archetypes also declare `not_confusable_with` relationships and human-readable distinction rules. These rules establish category boundaries before decorative variation is applied: a tank farm is storage-dominant, a well pad is extraction-equipment-dominant, and a refinery is process-equipment-dominant.

## Vanilla blueprint primitives

Reference blueprints use a small deterministic vocabulary: `block`, `fill_box`, `hollow_box`, `line`, and `cylinder`. Later primitives may overwrite earlier placements so glazing, branding bands, equipment, pipework, lighting, and other details can be layered over basic masses.

Corporate palette roles resolve only to `minecraft:` block IDs in this baseline. This keeps the references usable as default generation examples even when no mods are available.

## Generation order

The intended generation order is:

1. select facility archetype from purpose/context;
2. select scale tier and site constraints;
3. select or infer an allowed corporate language;
4. establish functional site zones and circulation;
5. compose required structural modules;
6. add optional/detail modules;
7. resolve the corporate palette and design-language biases;
8. materialize blocks;
9. run structural validation, recognizability, distinction, and project-specific runtime review.

Corporate style never substitutes for facility function. A generated refinery that has the correct colors but lacks process columns, pipe infrastructure, storage, flare, and loading signatures is not a valid refinery reference.
