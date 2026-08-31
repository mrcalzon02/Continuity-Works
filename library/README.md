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

## Structural Library 0.3

The base set retains six layouts, thirteen general structural modules, and six diagnostic test structures. Version 0.3 adds nine facility-oriented but still reusable structural modules under `modules/fuel_petroleum/`: fuel canopy, pump island, roadside pylon, pumpjack, storage tank, pipe rack, process column, flare stack, and loading gantry.

Connector contract v2 adds three interfaces needed for site-scale industrial composition: `vehicle_lane_5x4`, `vehicle_gate_5x4`, and `process_pipe_1x1`. Existing connector profiles remain unchanged.

These additions do not make the structural library itself brand-aware. Facility function, corporate language, recognizability, and complete architectural references live in the additive sibling `facility_library/` and are exposed through `FacilityLibrary`.

`manifest.json` remains the authoritative structural index. `StructureLibrary` provides discovery, filtering, connector compatibility, loading, and static validation.
