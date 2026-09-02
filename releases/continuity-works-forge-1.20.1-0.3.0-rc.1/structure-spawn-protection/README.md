# Continuity Works Structure Spawn Protection — Forge 1.20.1

This directory is a standalone Forge mod project. Its output JAR is intentionally independent of Biome Expander, TerraBlender, and any particular modpack so the same protection layer can later be copied into projects such as Infinite Domain without moving the protected structures themselves.

## Guarantees

- **500 blocks is a hard minimum**, measured horizontally from the actual X/Z footprint edge of a structure or jigsaw piece. A profile may request more, never less.
- The active structure registry is scanned automatically. With the default configuration, every registered structure is enrolled unless it is in `#continuityworks_spawn_protection:ignored`.
- Every candidate structure respects all active reservations. The reservation check and provisional insertion are synchronized so parallel worldgen workers cannot both observe the same protected space as free.
- Jigsaw structures reserve **each accepted piece** while the assembly is still being solved. Pieces in the same assembly are exempt from each other's 500+ block external radius so valid connectors can remain close, but their occupied three-dimensional block volumes may not overlap.
- A rejected jigsaw candidate is intercepted at vanilla's voxel-fit branch, before piece-list insertion, child queuing, and free-space mutation.
- Provisional reservations are reconciled against the final `StructureStart`; speculative pieces that vanilla did not keep are removed. Failed starts roll back. Successful starts commit.
- Committed reservations are persisted per dimension with `SavedData`. Valid starts found in already-generated chunks are indexed on chunk load, making adoption additive rather than destructive.
- Existing structure JSON, structure sets, pools, NBT, and placement rules remain authoritative. This module is an additional gate, not a replacement generator.

## Build

Open this directory as a Gradle project with Java 17 and run `gradle build`. The normal artifact is:

`build/libs/ContinuityWorks-StructureSpawnProtection-Forge-1.20.1-0.1.0.jar`

No GitHub Actions are required by this module.

## Inclusion protocols

### Automatic registry scan

`autoIncludeRegisteredStructures=true` is the default. Every active `Registries.STRUCTURE` entry emits reservations. This is the mode that implements the global Continuity Works rule.

### Explicit structure tag

Other mods or datapacks can contribute values to:

`data/continuityworks_spawn_protection/tags/worldgen/structure/protected.json`

This remains useful if automatic inclusion is deliberately disabled.

### Explicit jigsaw tag

`#continuityworks_spawn_protection:jigsaw_piece_protected` also enrolls a structure. Once a jigsaw structure is enrolled, per-piece protection is mandatory and cannot be disabled by profile metadata.

### Ignored tag

`#continuityworks_spawn_protection:ignored` is the explicit compatibility escape hatch. It wins over automatic scanning and protection tags. Ignored structures do not emit reservations, but their generation attempts still respect reservations emitted by protected structures.

### Sidecar profiles

Profiles are loaded from:

`data/<namespace>/continuityworks_spawn_protection/profiles/*.json`

Example:

```json
{
  "selectors": {
    "structures": ["examplemod:research_complex"],
    "tags": ["examplemod:major_structures"],
    "namespaces": ["another_mod"]
  },
  "family": "examplemod:research_sites",
  "exclusion_radius": 800,
  "jigsaw_piece_exclusion_radius": 650,
  "protect_jigsaw_pieces": true,
  "priority": 100
}
```

At least one selector is required. Both radius fields must be `>= 500`. `protect_jigsaw_pieces:false` is rejected; a malformed/unsafe profile never lowers protection and the automatic/tag fallback remains available.

`family` is metadata and grouping information only. **Family equality does not grant a collision exemption.** Only the exact same active `assemblyId` may bypass the external radius, and even then physical piece overlap is prohibited.

## Compatibility model

The module discovers normal Minecraft structures through the live registry and tags instead of maintaining a hard-coded list of mods. That means newly installed registry-based structure mods are discovered without code changes. Their own structure definitions, salts, spacing, biome selectors, processors, templates, and loot remain untouched.

Worldgen systems that place facility-scale content through custom features/events rather than `Registries.STRUCTURE` cannot be safely inferred from registry metadata. For those systems the JAR exposes `io.continuityworks.spawnprotection.api.SpawnProtectionApi`: reserve each accepted custom/jigsaw piece with a shared assembly id, then `commit(...)` after success or `rollback(...)` after failure. The API enforces the same 500-block minimum and same-assembly physical-overlap rule.

The two Mixin hooks are deliberately narrow:

1. `ChunkGenerator.tryGenerateStructure` opens/closes the reservation transaction and can invalidate a conflicting final start.
2. `JigsawPlacement$Placer.tryPlacingChildren` extends the existing vanilla candidate-fit decision with reservation/self-collision checks.

The jigsaw redirect is `require=1`; if a future Minecraft/Forge mapping changes the expected acceptance path, the module fails loudly instead of silently claiming protection that is no longer active.
