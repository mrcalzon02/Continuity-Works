# Biome Expander Template Runtime Export — Minecraft 1.20.1

## Export contract

The authoritative Forge template export is a normal JavaFML runtime mod. Drop the single distributable JAR into a Minecraft Forge 1.20.1 `mods/` directory and start the game/server. No Continuity Works validator, preflight command, registry probe, or configuration verification step is required at runtime.

The mod registers eight custom biome definitions, inserts enabled templates directly into natural Overworld world generation through an additive TerraBlender region, embeds TerraBlender using Forge Jar-in-Jar so the user installs one JAR, and automatically creates a Forge COMMON config. All template biomes are enabled by default.

## Config

Forge creates `config/continuityworks-biomes-common.toml` automatically.

```toml
[biomes]
    temperateGrove = true
    floweringMeadow = true
    mistyHighlands = true
    marshland = true
    frostedTaiga = true
    dryScrubland = true
    rockyBadlands = true
    ashWastes = true

[worldgen]
    regionWeight = 3
```

Changing a biome toggle requires a restart. A disabled biome stops being selected for newly generated natural terrain; already-generated chunks and existing biome registry references remain intact. `regionWeight` accepts values from `1` to `20`.

## Template biome IDs

- `continuityworks_biomes:temperate_grove`
- `continuityworks_biomes:flowering_meadow`
- `continuityworks_biomes:misty_highlands`
- `continuityworks_biomes:marshland`
- `continuityworks_biomes:frosted_taiga`
- `continuityworks_biomes:dry_scrubland`
- `continuityworks_biomes:rocky_badlands`
- `continuityworks_biomes:ash_wastes`

## World-generation behavior

The runtime mod uses TerraBlender's `Region` and `VanillaParameterOverlayBuilder` APIs. Each enabled biome contributes climate parameter points for temperature, humidity, continentalness, erosion, depth, and weirdness. TerraBlender blends those entries into Overworld biome selection without replacing the vanilla Overworld biome source.

Biome-specific surface rules provide vanilla-material ground palettes, including podzol for Frosted Taiga, mud for Marshland, red sand/terracotta for Rocky Badlands, and tuff/basalt for Ash Wastes.

## Compatibility behavior

The runtime JAR carries vanilla-compatible dynamic biome definitions plus additive Minecraft and Forge biome tags. It does not replace `minecraft:overworld`, vanilla biome JSON, vanilla noise settings, or the vanilla biome source.

A separate pure-data vanilla compatibility ZIP may be exported for tooling/datapack reuse, but normal Forge runtime insertion is handled by the JavaFML mod itself.

## Source

The reusable runtime template project is stored at `examples/biome_expander/runtime_mod/1.20.1/` and is intended to be copied or generated as the baseline Forge 1.20.1 Biome Expander target.
