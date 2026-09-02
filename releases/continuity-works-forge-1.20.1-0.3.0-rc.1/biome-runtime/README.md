# Continuity Works Biome Templates — Runtime Mod

Minecraft Java 1.20.1 / Forge runtime template mod.

## Install

1. Install Forge 47.4.10 or later for Minecraft 1.20.1.
2. Drop `ContinuityWorks-BiomeTemplates-Forge-1.20.1-0.2.0.jar` in `mods/`.
3. Start Minecraft or the server and generate a world normally.

The distributable embeds TerraBlender as a Forge Jar-in-Jar dependency, so the user installs one mod JAR. All eight template biomes are enabled by default and participate in natural Overworld generation.

## Config

Forge automatically creates `config/continuityworks-biomes-common.toml`.

Each template biome has a true/false toggle. `false` removes that biome from newly generated natural terrain after restart while keeping its registry definition available for existing worlds. `worldgen.regionWeight` defaults to `3` and controls relative frequency.

## Template biomes

- `continuityworks_biomes:temperate_grove`
- `continuityworks_biomes:flowering_meadow`
- `continuityworks_biomes:misty_highlands`
- `continuityworks_biomes:marshland`
- `continuityworks_biomes:frosted_taiga`
- `continuityworks_biomes:dry_scrubland`
- `continuityworks_biomes:rocky_badlands`
- `continuityworks_biomes:ash_wastes`

## Compatibility model

The mod adds a TerraBlender Overworld region and additive biome tags. It does not replace `minecraft:overworld`, vanilla biome JSON, vanilla noise settings, or the vanilla biome source. All biome content uses vanilla blocks, placed/configured features, carvers, sounds, and mobs.

## Building

Requires Java 17 and Gradle. Run `gradle clean jarJar reobfJarJar`. The Jar-in-Jar output is the distributable mod.

Biome registry definitions and additive classification tags live directly under `src/main/resources/data/`, so a normal Gradle build needs no generator, resource-unpacking step, validator, or preflight command.
