# Continuity Works Forge 1.20.1 — 0.3.0-rc.2 build target

The installable release artifact is a **JAR**, not a ZIP.

Authoritative unified Forge project:

`modules/continuityworks_runtime/forge-1.20.1/`

Expected local Forge release filename:

`ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar`

The canonical local build/verification entry point is:

`python releases/continuity-works-forge-1.20.1-0.3.0-rc.2/build_release_jar.py`

The repository root `jitpack.yml` supplies an external no-GitHub-Actions build path for environments where Gradle/Forge dependencies are not locally available. For immutable build evidence, request JitPack against the exact final `main` commit rather than relying on a moving `main-SNAPSHOT` coordinate.

The unified JAR contains both `continuityworks_biomes` and `continuityworks_spawn_protection`. It compiles the authoritative 128-biome runtime sources, includes the existing biome worldgen resources and currently materialized NBT structure templates, includes SSPS resources/classes, and embeds TerraBlender through ForgeGradle Jar-in-Jar. The SSPS implementation retains its hard minimum 500-block structure exclusion contract.

The release builder validates the archive before it is copied into `dist/`; an unbuilt or incomplete archive is not accepted as the release artifact.

No GitHub Actions are used by this build path.
