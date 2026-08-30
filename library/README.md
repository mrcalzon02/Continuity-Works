# Continuity Works Structural Library

This directory is the baseline reusable structure corpus for Continuity Works.

The library deliberately separates **layout templates** from **physical test structures**. Layouts describe footprint, zones, connectors, modular dimensions, and material roles without committing to a specific architectural theme. Test structures are small vanilla-only block fixtures used to verify import, bounds, orientation, circulation, verticality, palette handling, and deterministic processing.

## Stability rules

- Library IDs are stable API-facing identifiers. Move files only by preserving their IDs in the manifest.
- Existing library entries are never silently repurposed. Create a new version or a new ID when semantics change.
- Compatibility additions are additive and non-destructive.
- Default fixtures use only `minecraft:` block IDs so a clean vanilla registry can exercise the library.
- Abstract layouts do not prescribe decorative style. Theme, culture, era, faction, biome, and mod palettes are provider concerns.
- Test structures are not shipping showcase builds. They exist to make failures small, obvious, deterministic, and reproducible.

## Baseline layout set

The first baseline contains compact room, linear corridor, cross hub, courtyard, tower core, and 3×3 modular-grid layouts. Their connectors are intentionally centered and use predictable odd widths where practical.

## Baseline test set

The first physical fixtures cover orientation, enclosed rooms, corridors, four-way hubs, courtyards/open space, and vertical towers. Each JSON file uses the existing Continuity Works `size` + `blocks` representation and carries metadata identifying the library entry and targeted checks.

`manifest.json` is the authoritative index. `StructureLibrary` in `structure_capability.structure_library` provides programmatic discovery and validation.
