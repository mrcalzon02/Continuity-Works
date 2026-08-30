# Structural Library Contract

## Purpose

The Continuity Works Structural Library provides a deterministic vocabulary of layout primitives, reusable structural modules, and physical diagnostic fixtures for generation providers, external AI clients, editor integrations, automated tests, and future higher-level structure grammars.

The library is not a catalog of finished themed buildings. Its first responsibility is to supply stable, machine-readable geometry contracts that make generation behavior measurable and composable.

## Three-layer model

A **layout** is abstract large-scale geometry. It defines dimensions, zones, coarse connectors, rotation/mirroring allowances, modular scale, and semantic material roles. Layouts answer questions such as “room, corridor, hub, courtyard, tower core, or macro grid?”

A **module** is an abstract reusable construction component. It defines a bounded structural function—entrance, stair, lift shaft, room, intersection, foundation, roof, tower transition, bridge, wall, gatehouse, or utility cell—plus exact connector profiles that govern how modules may mate. Modules contain no fixed block palette and therefore remain theme- and mod-independent.

A **test structure** is concrete. It contains explicit vanilla block positions in the existing lightweight structure JSON format. These fixtures are deliberately simple enough that a failed import, rotation, clipping operation, palette resolution, or circulation check can be diagnosed without visual ambiguity.

## IDs and versioning

Every manifest entry has a stable namespaced ID. File paths are implementation details; IDs are the durable reference. Existing IDs must not be silently redefined. Breaking semantic changes require a new ID or an explicit versioned successor.

The manifest owns the current library version and entry inventory. Consumers should resolve entries through the manifest rather than hard-coding repository paths.

## Baseline layouts

The baseline provides six patterns: `compact_room_7x7`, `linear_corridor_5x13`, `cross_hub_13x13`, `courtyard_17x17`, `tower_core_9x9`, and `modular_grid_3x3`. These are geometry contracts, not aesthetic prescriptions.

## Baseline module families

Library version 0.2 adds thirteen reusable modules:

- entrance threshold;
- stair core;
- elevator/lift core;
- T-intersection;
- standard room;
- foundation pad;
- flat roof;
- gable roof;
- tower transition;
- bridge span;
- wall segment;
- gatehouse;
- utility/service room.

These are base construction vocabulary. A provider may materialize them with vanilla blocks, verified mod assets, cultural/thematic palettes, degradation rules, or project-specific processors without changing their stable IDs.

## Connector contract

`library/contracts/connector_profiles.json` is the authoritative connector vocabulary. Version 1 defines eight profiles: `passage_3x3`, `gate_3x3`, `service_2x2`, `vertical_3x3`, `bridge_5x3`, `wall_join_3x5`, `foundation_anchor_3x1`, and `roof_support_3x1`.

Each module connector declares a profile, face, center point, semantic role, and whether the connection is required. Connector centers must lie on the declared module face. Compatibility is explicit and symmetric through each profile's `mates` list. `StructureLibrary.profiles_compatible()` exposes that contract programmatically.

Connector compatibility only proves interface compatibility. It does not automatically prove terrain fitness, structural plausibility, Minecraft runtime placement, or jigsaw pool correctness.

## Baseline test structures

The concrete set provides one structure for each major geometric behavior: orientation marker, room shell, corridor, cross hub, courtyard, and tower core. All use only `minecraft:` IDs.

## Validation

`StructureLibrary.validate()` checks manifest inventory counts; stable unique IDs; file existence and root containment; JSON readability; module IDs and families; base-layout references; connector profile existence; symmetric connector mating declarations; connector uniqueness, bounds, face placement, and profile assignment; zone bounds; namespaced block IDs; unique block coordinates; and concrete structure bounds.

These checks are static gates. They do not substitute for Minecraft runtime placement, NBT import verification, jigsaw behavior, terrain integration, load-bearing simulation, or client-side visual review.

## Composition rules

Providers should prefer composition before invention:

1. choose a base layout or macro layout;
2. assign functional modules to required zones;
3. mate only compatible connector profiles;
4. resolve material roles through the target registry and theme;
5. apply grade/theme/biome/compatibility transformations;
6. materialize concrete blocks or NBT;
7. run static, runtime, and project-specific validation.

Optional module connectors may remain sealed. Required connectors must either mate to another compatible connector or be deliberately terminated by a provider-defined boundary condition.

## Extension policy

New structures should generally enter the library in one of four layers: base layouts, reusable structural modules, test fixtures, or themed/reference families. New families should compose from existing layouts/modules where practical rather than forking near-duplicate geometry.

Mod compatibility remains additive. A compatibility family may map material roles, IDs, processors, pools, or selectors onto a base entry, but it must not mutate the authoritative base entry in place.
