# Continuity Works Java Blueprint API

`continuityworks-api` is the loader-neutral Java 17 contract between Continuity Works and optional Minecraft consumers such as Alfheim Companion.

The API is intentionally data-only. It does not scan worlds, mutate blocks, execute placement, hold companion state, or require Forge/Minecraft classes. A Minecraft integration adapter translates `BlockPos`/`Direction` into `BlockPosition`/`Facing` at the boundary.

The intended flow is:

`semantic intent -> consumer planner -> BlueprintRequest -> Continuity Works -> BlueprintProposal -> server snapshot validation -> player preview/approval -> consumer execution`

Tiny inference engines should emit semantic intent only. They must never generate raw block placement operations or registry IDs. Continuity Works owns deterministic blueprint planning, palette selection, operation ordering, material accounting, integrity metadata, and proposal warnings. The consuming mod owns world-thread scanning, player approval, claim/permission/reach/inventory/chunk checks, and execution.

Contract version `1.x` preserves source-level intent and proposal semantics. Consumers should call `ContinuityWorksBlueprintApi.apiVersion()` and reject incompatible major versions.
