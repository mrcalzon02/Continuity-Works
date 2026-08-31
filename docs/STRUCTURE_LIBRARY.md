# Structural Library Contract

## Purpose

The Continuity Works Structural Library is the stable geometry layer for layouts, reusable modules, and physical diagnostic fixtures. It is intentionally independent of corporate identity, architectural theme, biome, culture, faction, and mod palette.

A separate additive `FacilityLibrary` consumes this structural vocabulary when generation requires recognizable real-world-inspired facility roles and corporate design languages.

## Three structural layers

A **layout** defines large-scale abstract geometry such as room, corridor, hub, courtyard, tower core, or macro grid.

A **module** defines a bounded reusable construction function plus exact connector contracts. Modules contain semantic material roles rather than a fixed decorative palette.

A **test structure** contains explicit vanilla block placements for deterministic diagnostics.

## Structural Library 0.3

The baseline retains six layouts and the original thirteen general module families. Version 0.3 adds nine reusable site/facility primitives: fuel canopy, pump island, roadside pylon, pumpjack, storage tank, pipe rack, process column, flare stack, and loading gantry. These modules are not facility archetypes; they may be shared across multiple facility types.

## Connector contract v2

`library/contracts/connector_profiles.json` remains authoritative. Version 2 preserves the original eight profiles and adds:

- `vehicle_lane_5x4` for vehicle-scale circulation;
- `vehicle_gate_5x4` for controlled vehicle thresholds;
- `process_pipe_1x1` for abstract process/product transfer.

Compatibility remains explicit and symmetric through `mates`. A process connection cannot be silently treated as a pedestrian doorway, and a truck loading route cannot be reduced to person-scale circulation.

## Facility semantic sidecar

`facility_library/` owns corporate languages, facility archetypes, and complete vanilla architectural references. This is deliberately separate from `library/manifest.json`: generic geometry can evolve without becoming coupled to one industrial/commercial taxonomy.

`FacilityLibrary` depends on a passing `StructureLibrary`, resolves archetype module requirements against structural IDs, compiles reference blueprints to the existing `{size, blocks, metadata}` structure format, and evaluates required recognizability signatures.

See `docs/FACILITY_ARCHETYPES_AND_CORPORATE_LANGUAGE.md` for the semantic contract.

## Validation

`StructureLibrary.validate()` checks inventory counts, unique IDs, file/root integrity, module IDs/families, base-layout references, connector contracts and symmetric mating, connector bounds/face placement, zone bounds, namespaced concrete blocks, coordinate uniqueness, and concrete structure bounds.

Structural validation does not prove facility recognizability. Facility-level recognition, distinction, corporate coherence, and semantic composition belong to `FacilityLibrary`.

## Extension policy

Prefer composition before invention. New facility families should reuse generic layouts and modules wherever practical. Corporate/mod/biome/theme mappings are additive and must not mutate authoritative base entries in place.
