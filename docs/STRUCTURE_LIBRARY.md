# Structural Library Contract

## Purpose

The Continuity Works Structural Library provides a small, deterministic vocabulary of geometry and layout primitives that can be used by tests, generation providers, external AI clients, editor integrations, and future higher-level structure grammars.

The library is intentionally not a catalog of finished themed buildings. Its first responsibility is to supply stable reference shapes that make generation behavior measurable.

## Two-layer model

A **layout** is abstract. It defines dimensions, zones, connectors, rotation/mirroring allowances, modular scale, and semantic material roles. It should remain useful whether the eventual build is medieval, industrial, ruined, subterranean, modded, or vanilla.

A **test structure** is concrete. It contains explicit vanilla block positions in the existing lightweight structure JSON format. These fixtures are deliberately simple enough that a failed import, rotation, clipping operation, palette resolution, or circulation check can be diagnosed without visual ambiguity.

## IDs and versioning

Every manifest entry has a stable namespaced ID. File paths are implementation details; IDs are the durable reference. Existing IDs must not be silently redefined. Breaking semantic changes require a new ID or an explicit versioned successor.

The manifest owns the current library version and entry inventory. Consumers should resolve entries through the manifest rather than hard-coding repository paths.

## Baseline layouts

The initial baseline provides six patterns: `compact_room_7x7`, `linear_corridor_5x13`, `cross_hub_13x13`, `courtyard_17x17`, `tower_core_9x9`, and `modular_grid_3x3`. These are geometry contracts, not aesthetic prescriptions.

## Baseline test structures

The concrete set provides one structure for each major geometric behavior: orientation marker, room shell, corridor, cross hub, courtyard, and tower core. All use only `minecraft:` IDs.

## Validation

`StructureLibrary.validate()` checks manifest shape, stable unique IDs, file existence, path containment, JSON readability, namespaced block IDs, unique block coordinates, bounds, and basic layout connector/footprint integrity.

These checks are static gates. They do not substitute for Minecraft runtime placement, NBT import verification, jigsaw behavior, terrain integration, or client-side visual review.

## Extension policy

New structures should generally enter the library in one of four layers: base layouts, test fixtures, reusable structural modules, or themed/reference families. New families should compose from existing layouts where practical rather than forking near-duplicate geometry.

Mod compatibility remains additive. A compatibility family may map material roles, IDs, processors, pools, or selectors onto a base layout, but it must not mutate the authoritative base entry in place.
