# Validation, evidence, and failure reporting

## Separate these gates

1. **Schema and registry:** Exact published route, expected parameter types, target Minecraft version, verified vanilla/mod IDs, known datapack/NBT format.
2. **Generator fitness:** Deterministic layout, required rooms/program, viable circulation/connectors, accepted purpose depth, shape/footprint/height constraints, no fake artifact identifiers.
3. **Compatibility and exclusion:** Additive adapter changes only; no overwritten terrain, structure family/exclusion-zone conflict, invasive replacement, or unsupported mod-version claim.
4. **Packaging and repository:** Generated file content, NBT/JSON validity, manifest/snapshot hashes, target loader packaging, tests; verify writes by read-back and confirmed commit SHA.
5. **Actual execution:** Fresh-world Minecraft structure placement, terrain/height behavior, jigsaw registrations, loot/occupancy, restart and multiplayer/dimension behavior where applicable. Remote API serviceability is verified separately.

A plan or test passed in a local harness is not proof of game runtime placement. An advertised API hostname is not an active endpoint until `/v1/health` returns a correct identity and representative external calls succeed. GitHub Pages is a static client; never use it for `/v1/*` execution.

## Result labels

Use explicit claims, each backed by evidence:
- `PLANNED_ONLY`: requirements or payload exists, no generator invocation.
- `GENERATED_NOT_VALIDATED`: real generator output exists but required checks incomplete.
- `LOCALLY_VALIDATED`: local schema/materialization tests passed, runtime deployment unverified.
- `RUNTIME_TEST_REQUIRED`: geometry/integration is plausible; no observed fresh-world placement.
- `VERIFIED_IN_GAME`: real target-version Minecraft test observed, with test setup/evidence.
- `EXTERNALLY_VERIFIED`: public API discovery and execution passed remote checks.

These are **reporting labels**, not new API status codes. Preserve and report the authoritative API's actual status codes and gate reasons without translating failure into success.

## Repository execution discipline

Follow INTENT → EXECUTE → OBSERVE → VERIFY → CLAIM. Before large file edits, record baseline path, size/hash, and targeted section. Modify only intended sections; verify surrounding content remains intact. For connector timeouts, stale SHAs, or permission failures, diagnose and bounded-retry transient errors with refreshed remote state; never blindly overwrite remote work or claim success after an unverified write. Avoid GitHub Actions unless explicitly authorized.

When claiming completion, provide the exact tool/route or local code path used, seed and Minecraft version, outputs, gate results, unresolved game tests, and, for code changes, the read-back commit and changed file paths.

Further authority: [public serviceability](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/PUBLIC_SERVICEABILITY.md), [API](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/API.md), and [deployment boundary](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/DEPLOYMENT.md).
