# Continuity Works Forge 1.20.1 — 0.3.0-rc.2 build target

The installable release artifact is a **JAR**, not a ZIP.

Authoritative unified Forge project: `modules/continuityworks_runtime/forge-1.20.1/`

Build input commit: `02031f70537b2c4340ad1866418a0750e2770518`

JitPack build log:
https://jitpack.io/com/github/mrcalzon02/Continuity-Works/02031f7/build.log

JitPack Maven artifact request (also triggers an on-demand build):
https://jitpack.io/com/github/mrcalzon02/Continuity-Works/02031f7/Continuity-Works-02031f7.jar

Expected local Forge build filename before JitPack publication:
`ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar`

The unified JAR contains both `continuityworks_biomes` and `continuityworks_spawn_protection`. It compiles the authoritative 128-biome runtime sources, copies the existing biome worldgen resources including materialized NBT structure templates, copies SSPS resources, and embeds TerraBlender using ForgeGradle Jar-in-Jar. The SSPS implementation retains its hard minimum 500-block structure exclusion contract.

No GitHub Actions are used by this build path.
