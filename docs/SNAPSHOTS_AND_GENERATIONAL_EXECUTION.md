# Adaptive Incremental Snapshotting and Generational Execution

Long-running structure work must be resumable and auditable.

## Generation cycle

For each target:

1. **Discover** — authoritative source, integration, local mods, validators.
2. **Baseline** — immutable source hash and optional client-side visual baseline.
3. **Contextualize** — location, purpose, theme, clearances, constraints.
4. **Audit** — mechanical + functional + context findings.
5. **Choose grade** — minimum sufficient intervention.
6. **Plan generation** — freeze accepted components and define mutable scope.
7. **Mutate one coherent pass** — avoid many unrelated changes.
8. **Validate** — only claims tested by that validator.
9. **Snapshot** — manifest + artifact hashes + changed scope.
10. **Optional client review** — a consuming client may render and inspect the exact persisted artifact using its own compute.
11. **Promote or revise** according to the consuming project's policy.
12. **Record next action**.

StructureSmith itself does not require step 10 in order to generate, validate, snapshot, or return an artifact.

## Generational scripting

A long job is a chain of immutable generations:

```text
G000 baseline
G010 mechanical stabilization
G020 program/circulation
G030 massing
G040 systems/interiors
G050 culture/site context
G060 history/damage
G070 detail cleanup
G080 mechanical validation
G090 optional client-rendered candidate
G100 promoted by consuming project
```

The exact numbers are not sacred; the principle is. Each generation records:
- parent snapshot;
- input hashes;
- allowed mutation;
- results;
- validators;
- accepted/frozen properties;
- unresolved defects;
- next eligible generation.

## Client-side rendering

A snapshot may contain enough geometry, NBT artifacts, layout metadata, or block operations for a client to construct a 3D view. Rendering those results is the client's responsibility. StructureForge demonstrates this pattern in the browser.

A client that needs fixed-camera comparisons can generate and store them itself. Rendering success proves only that the client's renderer succeeded; it is not part of the StructureSmith server's mechanical validation claim.

## Review ownership

Automated StructureSmith validation and optional client visual review are separate concerns. The client decides whether visual review is unnecessary, advisory, or mandatory for its own downstream workflow. No such client policy causes the StructureSmith API host to perform or fund rendering.
