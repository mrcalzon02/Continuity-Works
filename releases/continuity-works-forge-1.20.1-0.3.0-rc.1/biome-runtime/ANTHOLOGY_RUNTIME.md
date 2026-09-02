# 128-Biome Anthology Runtime Contract

The anthology source of truth is `src/main/anthology/biomes.json`.

The Gradle build materializes that catalog into the normal Forge runtime artifact. `generateAnthologyBiomes` creates 128 worldgen biome JSON definitions, eight family biome tags plus the aggregate anthology tag, and the generated Java catalog consumed by config, TerraBlender placement, and surface rules. `compileJava` and `processResources` depend on the generator, so no end-user preflight or runtime generator is required.

Every anthology biome has an individual common-config switch and every family has a master switch. Disabling a switch removes that biome from new TerraBlender natural selection while leaving its registry definition in the JAR for existing-world readability.

The generated baseline includes climate/effects, vanilla carvers, standard ore geology, family/profile vegetation, family-specific surface material rules, and one unique TerraBlender parameter point per anthology biome. This establishes all 128 biomes as executable runtime content while later terrain primitives, structures, resource specializations, and settlement/technology layers remain additive enrichments rather than prerequisites for the biome IDs to exist.

Families and counts:

- primordial: 16
- ancient: 16
- medieval: 16
- renaissance_clockwork: 16
- industrial: 16
- atomic_post_collapse: 16
- advanced_scifi: 16
- neon_virtual: 16
- total anthology biomes: 128

No GitHub Actions are used or required for this system.
