# Continuity Works Java Blueprint API

`continuityworks-api` is the loader-neutral Java 17 contract between Continuity Works and optional Minecraft consumers such as Alfheim Companion.

The API is intentionally data-only. It does not scan worlds, mutate blocks, execute placement, hold companion state, or require Forge/Minecraft classes. A Minecraft integration adapter translates `BlockPos`/`Direction` into `BlockPosition`/`Facing` at the boundary.

The intended flow is:

`semantic intent -> consumer planner -> BlueprintRequest -> Continuity Works -> BlueprintProposal -> server snapshot validation -> player preview/approval -> consumer execution`

## Bounded-volume contract

The Minecraft-side consumer selects and scans an exact `ConstructionVolume` on the server thread. That immutable volume is passed into `BlueprintRequest`. Continuity Works must keep the proposal anchor and every world-space placement operation inside that volume. The same volume identity/snapshot epoch is carried into `BlueprintContext` for validation so stale or mismatched snapshots can be rejected.

## Dynamic specifications

Tiny inference engines emit only semantic key/value specifications such as `PURPOSE=BOTANIA_RUNE_WORKSHOP`, `SITE=NORTH_CLEARING`, `STYLE=HOLLOW_COURT`, and `SIZE=COMPACT`. `BlueprintSpecification` deliberately keeps keys and values open-ended so new vocabularies do not require a Java ABI change. `SpecificationResolution` is returned for every interpreted item with `APPLIED`, `DEFAULTED`, `UNSUPPORTED`, or `CONFLICT` status.

The model never emits raw block placements or registry IDs. Continuity Works owns deterministic interpretation, blueprint planning, palette selection, operation ordering, material accounting, volume conformance, integrity metadata, and proposal warnings. The consuming mod owns world-thread scanning, player approval, claim/permission/reach/inventory/chunk checks, and execution.

Contract version `1.x` preserves the blueprint intent/proposal family. Consumers should call `ContinuityWorksBlueprintApi.apiVersion()` and reject incompatible major versions.
