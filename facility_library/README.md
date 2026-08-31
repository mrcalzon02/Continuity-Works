# Continuity Works Facility Semantic Library

This library adds architectural meaning above the generic structural library. It does not replace layouts or modules and does not hard-code a facility type into the base geometry system.

## Layers

A **corporate language** defines a synthetic operator identity: vanilla material palette, massing bias, signage geometry, facade rhythm, lighting, maintenance character, and recurring silhouette tokens.

A **facility archetype** defines function: required structural modules, site zones, circulation, recognizable visual signatures, allowed corporate languages, and explicit distinction rules against similar facility types.

A **facility reference** combines one archetype with one corporate language and an architectural blueprint. The blueprint is intentionally a game-building reference, not an engineering specification. `FacilityLibrary.compile_reference()` resolves its semantic material roles into vanilla `minecraft:` blocks and returns the existing Continuity Works `{size, blocks, metadata}` physical structure shape.

## Fuel and petroleum baseline

The original semantic family covers rural gas stations, highway travel stops, crude-oil well pads, bulk tank farms, compact diesel refineries, and truck fuel terminals. The original concrete references include two gas stations built from the same functional archetype but different corporate languages so brand identity can be tested independently from facility recognizability.

## Aerospace and orbital baseline

Facility Library 0.2 adds a complete `aerospace_orbital` family with six synthetic aerospace operator languages, twelve distinct facility archetypes, and twelve actual vanilla materializable reference structures.

The aerospace corpus has six authoritative scale tiers: `micro`, `light`, `standard`, `heavy`, `superheavy`, and `megastructure`. Every tier must contain at least two different facility archetypes and two complete references. Different seeds or corporate skins of one archetype do not satisfy that requirement.

The machine-readable scale matrix is `aerospace_orbital/corpus.json`. The architecture relationship language is `aerospace_orbital/design_language.json`. The full human contract and itemized facility list are documented in `docs/AEROSPACE_ORBITAL_CORPUS.md`.

Aerospace design separates operator style from system architecture. Asterion, Helium, Black Glass, Atlas Heavy, Pel Roma, and VCF can alter materials, massing, signage, lighting, and recurring geometry while the underlying facility remains functionally recognizable.

Scale is compositional rather than a simple multiplier. Superheavy and megastructure facilities add integration systems, transporter networks, expanded utilities, multiple operational anchors, or deep underground service layers rather than merely increasing dimensions.

## Recognition and distinction

Archetypes declare `required_signatures` such as `fuel_canopy`, `pumpjack`, `launch_mount`, `crawlerway`, `integration_building`, `superheavy_tower`, or `deep_launch_shaft`. References declare the signatures they visibly implement. `FacilityLibrary.evaluate_reference()` reports missing signatures and a recognizability gate.

Archetypes also declare `not_confusable_with` relationships and human-readable distinction rules. These rules establish category boundaries before decorative variation is applied.

## Vanilla blueprint primitives

Reference blueprints use a small deterministic vocabulary: `block`, `fill_box`, `hollow_box`, `line`, and `cylinder`. Later primitives may overwrite earlier placements so glazing, branding bands, equipment, pipework, lighting, and other details can be layered over basic masses.

Corporate palette roles resolve only to `minecraft:` block IDs in the baseline. This keeps references usable as default generation examples even when no mods are available.

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
9. run structural validation, recognizability, distinction, corpus, and project-specific runtime review.

Corporate style never substitutes for facility function. A generated facility with the correct colors but missing its defining operational systems is invalid.
