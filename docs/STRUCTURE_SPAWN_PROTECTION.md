# Structure Spawn Protection System

## Purpose

Continuity Works now treats structure placement as a shared spatial resource. The Structure Spawn Protection System (SSPS) is a portable Forge module that prevents independent structures from generating through, into, or unacceptably close to one another while preserving each source mod's existing worldgen definitions.

The authoritative implementation for Minecraft 1.20.1 lives at:

`modules/structure_spawn_protection/forge-1.20.1/`

The module is intentionally separable from the Biome Expander so it can later be consumed by Infinite Domain or another pack as a normal JAR.

## Spatial contract

Every enrolled structure reserves its actual horizontal footprint plus a **minimum 500-block exclusion radius**. Larger requested radii are preserved. When two reservations have different radii, the required edge-to-edge clearance is the larger radius. Vertical separation does not bypass the external structure rule.

This is footprint based, not center based. A very large facility therefore cannot place its center 500 blocks away while its walls overlap another protected region.

Reservations have two states:

- **provisional** — created atomically while a structure or jigsaw assembly is being solved;
- **committed** — retained after a successful `StructureStart` and persisted with dimension `SavedData`.

Failed attempts release provisional entries. Final jigsaw reconciliation removes speculative candidates that were considered but were not retained by vanilla.

## Jigsaw contract

Jigsaw structures use per-piece reservations. The source/start piece is observed when child expansion begins, and every child candidate is checked at the same vanilla voxel-fit decision that determines whether the piece can be accepted.

A piece in assembly `A` may sit within 500 blocks of another piece in assembly `A`, because that clearance would otherwise make connected jigsaws impossible. The exception is deliberately narrow:

- exact same assembly: external radius bypass allowed;
- same assembly + occupied 3D volume overlap: rejected as `SELF_JIGSAW_COLLISION`;
- same family but different assembly: no exception;
- any different assembly: enforce `max(candidateRadius, existingRadius)`.

This prevents a jigsaw from growing backward through its own halls, towers, rooms, or other already accepted components even when the parent and child belong to the same structural family.

## Automatic discovery and inclusion

At tag/registry refresh the module scans `Registries.STRUCTURE`. The default common configuration automatically enrolls every active registry entry. This means adding a third-party structure mod does not require a new Java adapter just to receive baseline protection.

Packs can additionally supply:

- `#continuityworks_spawn_protection:protected` — explicit enrollment;
- `#continuityworks_spawn_protection:jigsaw_piece_protected` — explicit enrollment with documented jigsaw intent;
- `#continuityworks_spawn_protection:ignored` — explicit non-emission escape hatch;
- data-pack sidecar profiles under `continuityworks_spawn_protection/profiles/` for selectors, families, priority, and radii above the hard minimum.

The ignored tag is non-destructive: an ignored structure is not rewritten or disabled. It simply does not emit its own persistent reservation, while still respecting reservations created by other structures during generation.

Registry scanning intentionally does not guess at custom worldgen that bypasses `Registries.STRUCTURE`. Those systems use the public `SpawnProtectionApi` adaptation surface. An adapter reserves each accepted custom or jigsaw piece under one assembly id and then commits or rolls back the transaction. This gives event/feature-driven structure systems the same 500-block minimum, atomic reservation semantics, and same-assembly self-collision checks without forcing their generators into a replacement format.

## Existing-world adaptation

When an already-generated chunk is loaded, valid structure starts are read from the chunk's existing structure-start table. Enrolled starts are converted to committed reservations using their current bounding boxes; jigsaws are indexed piece by piece. Deterministic IDs and equivalent-box checks prevent repeated chunk loads from multiplying the same reservation.

No NBT structure template, datapack structure JSON, structure set, pool, biome selector, or source mod registry object is mutated.

## Configuration

The common config exposes:

- `defaultExclusionRadius` — default 500, minimum 500;
- `defaultJigsawPieceRadius` — default 500, minimum 500;
- `autoIncludeRegisteredStructures` — default `true`;
- `indexExistingChunkStarts` — default `true`;
- `selfCollisionPadding` — default `0`; optional stricter same-assembly physical separation.

There is intentionally no setting that lowers the core exclusion radius below 500 or turns off per-piece protection for a jigsaw that is enrolled.

## Biome Expander integration

The current abyssal vent structures also contribute explicit protection metadata under the protection module's namespace. Their original `minecraft:jigsaw` structure JSON, structure sets, pools, and NBT remain unchanged. This provides a concrete cross-module example and means they remain enrolled if a pack later chooses tag/profile-only mode.

## Infinite Domain adoption later

When this module is ready to move into Infinite Domain, the expected integration is deliberately small:

1. build/copy the SSPS JAR into the pack's mods set;
2. leave Infinite Domain's existing structure generators and datapacks in place;
3. add protection tags/profiles only where the pack wants explicit grouping or radii above 500;
4. allow the registry scanner to discover the remaining active structure systems;
5. test on a fresh world and an existing-world copy to verify both new-generation reservations and old-start indexing.

Infinite Domain-specific adapters are intentionally not implemented here yet; Continuity Works remains the source project until the protection system is finished and validated.

## Failure policy

The module fails closed where silent failure would misrepresent protection. Profile values below 500 are rejected. Attempts that collide are invalidated. The jigsaw Mixin requires its expected vanilla fit call to exist. If Minecraft/Forge changes that internal contract in a future port, the correct response is to port the hook explicitly rather than silently continue without piece-level protection.
