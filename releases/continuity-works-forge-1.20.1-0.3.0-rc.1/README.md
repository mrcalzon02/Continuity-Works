# Continuity Works Forge 1.20.1 — 0.3.0-rc.1

This directory is the repository-backed Continuity Works release candidate package for Minecraft 1.20.1 Forge. It freezes the current authoritative biome, structure-generation, and structure-exclusion work into one self-contained package tree on `main`.

## Included

- `biome-runtime/` — the complete Forge 1.20.1 Biome Expander runtime source snapshot. The current anthology contains 128 generated biomes and the two currently materialized abyssal NBT structure templates, together with their worldgen registrations and supporting terrain/cave feature code.
- `structure-spawn-protection/` — the complete Forge 1.20.1 Structure Spawn Protection System. Its spatial contract reserves each enrolled structure's horizontal footprint plus a minimum 500-block exclusion radius, preserves larger requested radii, persists committed reservations, automatically enrolls registered structures by default, and handles same-assembly jigsaw pieces without allowing self-overlap.
- `structure-capability/` — the authoritative Continuity Works structure capability implementation, generators, schemas, and worldgen contracts.
- `era-structure-specs/` — the hero-development records and ledger for the era structure line. Stage 2 source and Stage 3 worldgen integration currently extend through E01-015.
- `RELEASE_MANIFEST.json` — machine-readable composition, provenance, and readiness gates.
- `build_release_package.py` — deterministic binary-package builder. It refuses to report success unless both Forge JARs exist after build.

## Release-candidate boundary

This is deliberately marked `0.3.0-rc.1`, not production-final. The biome anthology is wired into the Forge project but still requires local Gradle compilation and Minecraft runtime/worldgen validation. The E01-001 through E01-015 era structures have generator/worldgen contracts, but their final NBT/template-pool materialization and Minecraft load validation remain pending. Those structure contracts are included in this package so the release snapshot is complete, but they are not misrepresented as finished playable NBT assets.

The two abyssal vent structures already materialized in the biome runtime are included as actual NBT resources.

## Build the binary distribution

From this directory, with Java 17 and network access for ForgeGradle dependencies:

```bash
python build_release_package.py
```

The builder compiles both Forge projects, requires a usable JAR from each project, stages the two mods plus the structure source/contracts, writes SHA-256 checksums, and creates:

`dist/continuity-works-forge-1.20.1-0.3.0-rc.1.zip`

If either Forge build fails or a binary JAR cannot be found, the command exits non-zero and no successful binary release is claimed.

Use `--skip-build` only when both projects were already built in their respective `build/libs` directories.

## Runtime validation required before production promotion

Production promotion requires successful Forge compilation for both modules, a clean Minecraft 1.20.1 server/client load as appropriate, fresh-world biome/worldgen verification, confirmation that the materialized NBT structures place correctly, and end-to-end SSPS collision tests including the 500-block independent-structure exclusion rule and same-assembly jigsaw behavior. The remaining era structures additionally require NBT/template-pool materialization and Minecraft load validation before they can be described as production runtime assets.

This package does not add or depend on GitHub Actions.
