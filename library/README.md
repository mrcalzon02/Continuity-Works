# Continuity Works Structural Library

This directory is the reusable structural corpus for Continuity Works.

The library deliberately separates **layout templates**, **functional modules**, and **physical test structures**. Layouts describe large-scale spatial patterns. Modules describe reusable construction functions with standardized connection interfaces. Test structures are small vanilla-only block fixtures used to verify import, bounds, orientation, circulation, verticality, palette handling, and deterministic processing.

## Stability rules

- Library IDs are stable API-facing identifiers. Move files only by preserving their IDs in the manifest.
- Existing library entries are never silently repurposed. Create a new version or a new ID when semantics change.
- Compatibility additions are additive and non-destructive.
- Default fixtures use only `minecraft:` block IDs so a clean vanilla registry can exercise the library.
- Abstract layouts and modules do not prescribe decorative style. Theme, culture, era, faction, biome, and mod palettes are provider concerns.
- Test structures are not shipping showcase builds. They exist to make failures small, obvious, deterministic, and reproducible.
- Module connectors must use profiles from `contracts/connector_profiles.json`.

## Baseline layout set

The baseline contains compact room, linear corridor, cross hub, courtyard, tower core, and 3×3 modular-grid layouts.

## Baseline module set

The first module layer contains entrance, stairs, lift shaft, T-intersection, standard room, foundation, flat roof, gable roof, tower transition, bridge span, wall segment, gatehouse, and utility/service modules.

These modules use eight standardized connector profiles covering person-scale passages, gates, service access, vertical shafts, bridge decks, fortification joins, foundation anchors, and roof supports.

## Baseline test set

The physical fixtures cover orientation, enclosed rooms, corridors, four-way hubs, courtyards/open space, and vertical towers. Each JSON file uses the existing Continuity Works `size` + `blocks` representation and carries metadata identifying the library entry and targeted checks.

`manifest.json` is the authoritative index. `StructureLibrary` in `structure_capability.structure_library` provides discovery, filtering, connector-profile compatibility checks, loading, and static validation.
