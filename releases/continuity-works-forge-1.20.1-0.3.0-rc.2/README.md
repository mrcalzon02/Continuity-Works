# Continuity Works Forge 1.20.1 — 0.3.0-rc.2

This release-candidate process produces a **single installable Forge JAR**. It supersedes the rc.1 outer-ZIP packaging approach.

## Target artifact

`ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar`

The JAR is built from the authoritative unified project at:

`modules/continuityworks_runtime/forge-1.20.1/`

It deliberately retains two Forge mod IDs inside the same archive:

- `continuityworks_biomes`
- `continuityworks_spawn_protection`

This lets the existing biome and structure-protection entry points remain authoritative while giving users one file to place in `mods/`.

## Included runtime systems

The unified build compiles the current Forge 1.20.1 biome runtime, including the authoritative 128-biome anthology and its generated biome resources, terrain/cave systems, TerraBlender natural-placement integration, and currently materialized worldgen resources.

It also compiles Structure Spawn Protection into the same JAR. The protection system retains the project invariant of a hard minimum 500-block horizontal exclusion zone, footprint-aware reservations, persistent reservation state, automatic registry/profile enrollment, and per-piece jigsaw collision handling. Family proximity remains opt-in only for explicitly compatible families.

## Structure-content boundary

The current runtime resource tree contains two materialized NBT templates:

- `fracture_vent_field.nbt`
- `hadal_vent_complex.nbt`

The E01 era structure line has been developed through E01-015 at specification/source level, but those structures are not all yet materialized as Minecraft NBT/template-pool worldgen assets. This release process does not rename specifications into `.nbt` files or claim them as playable structures before materialization and runtime validation.

## Build

From the repository root, with Java 17 and a ForgeGradle-compatible Gradle installed:

```text
python releases/continuity-works-forge-1.20.1-0.3.0-rc.2/build_release_jar.py
```

The builder invokes the unified Forge project, selects the runtime JAR, inspects the archive, and only then copies it to:

`releases/continuity-works-forge-1.20.1-0.3.0-rc.2/dist/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar`

The builder fails if either compiled mod entry point is missing, if fewer than 128 generated biome definitions are present, if the Structure Spawn Protection mixins are missing, if the existing NBT templates are missing, or if Jar-in-Jar metadata for the embedded TerraBlender dependency is absent.

## External build path

The repository root includes `jitpack.yml` so the same authoritative project can be built on JitPack without adding or relying on GitHub Actions. JitPack is a compiler/distribution build environment only; repository `main` remains authoritative.

## Readiness boundary

A successful compile and archive inspection establish that the JAR was materially built. They do not by themselves prove Minecraft runtime correctness. Fresh Forge 1.20.1 launch/worldgen verification is still required before promoting rc.2 to a production-final runtime release.
