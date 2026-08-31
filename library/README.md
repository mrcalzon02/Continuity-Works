# Continuity Works Structural Library

This directory is the reusable structural corpus for Continuity Works.

The library separates **layout templates**, **functional modules**, and **physical test structures**. Layouts describe large-scale spatial patterns. Modules describe reusable construction functions with standardized connection interfaces. Test structures are small vanilla-only block fixtures used to verify import, bounds, orientation, circulation, verticality, palette handling, and deterministic processing.

## Stability rules

- Library IDs are stable API-facing identifiers.
- Existing entries are never silently repurposed; create a new ID/version for semantic breaks.
- Compatibility additions are additive and non-destructive.
- Abstract layouts/modules do not prescribe corporate, cultural, biome, era, or mod style.
- Module connectors must use profiles from `contracts/connector_profiles.json`.
- Physical baseline fixtures use only `minecraft:` block IDs.

## Structural Library 0.4

The library now contains six layouts, forty-three reusable modules, and six diagnostic test structures. The original general-purpose and fuel/petroleum vocabularies remain intact.

Version 0.4 adds twenty-one aerospace/orbital modules under `modules/aerospace_orbital/` covering landing surfaces, launch mounts, gantries and towers, integration/recovery buildings, crawlerways and causeways, mission operations, launch-exhaust visual language, and deep-silo systems.

Connector contract v3 retains all previous interfaces and adds dedicated heavy crawler, launch-mount, heavy/superheavy hangar, superheavy crawler, and deep-silo vertical interfaces. This prevents person-scale circulation, ordinary vehicle routing, heavy launch transport, and underground launch shafts from being treated as interchangeable connectors.

The structural library itself remains style-neutral. Facility function, corporate language, recognizability, scale semantics, and complete architectural references live in the additive sibling `facility_library/` and are exposed through `FacilityLibrary`.

`manifest.json` remains the authoritative structural index. `StructureLibrary` provides discovery, filtering, connector compatibility, loading, and static validation.
