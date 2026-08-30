# Biome Expander Template Export — 1.20.1 Baseline

## Status

This is the first concrete Biome Expander export fixture for Continuity Works.

- Target: Minecraft Java 1.20.1
- Forge packaging: LowCodeFML data-only mod
- Vanilla packaging: standard datapack ZIP
- Namespace: `continuityworks_biomes`
- Export version: `0.1.0`
- Compatibility mode: `append_only`
- Base authority: preserved
- Static gate: `BIOME_FIRST_EXPORT = PASS`
- Runtime gate: not yet run

## Produced exports

The Forge export is installable as a data-only Forge mod and contains the same core biome registry definitions as the vanilla datapack export. The vanilla export contains no Forge namespace resources. Both use only vanilla Minecraft worldgen resources inside the biome definitions.

The default export intentionally does **not** replace `minecraft:overworld`, any vanilla biome JSON, the vanilla noise settings, or the Overworld biome source. Defining a datapack biome makes the registry entry available, but does not by itself add that biome to natural vanilla Overworld climate selection. Natural placement therefore remains a separate provider operation and must pass fresh-world runtime verification before Continuity Works reports it as supported.

## Template biomes

| Biome ID | Template role | Vanilla analog |
|---|---|---|
| `continuityworks_biomes:temperate_grove` | Temperate forest | `minecraft:forest` |
| `continuityworks_biomes:flowering_meadow` | Open flowering grassland | `minecraft:meadow` |
| `continuityworks_biomes:misty_highlands` | Cool rough highland | `minecraft:windswept_hills` |
| `continuityworks_biomes:marshland` | High-humidity wetland | `minecraft:swamp` |
| `continuityworks_biomes:frosted_taiga` | Cold coniferous forest | `minecraft:snowy_taiga` |
| `continuityworks_biomes:dry_scrubland` | Hot low-density scrub | `minecraft:savanna` |
| `continuityworks_biomes:rocky_badlands` | Hot arid roughland | `minecraft:badlands` |
| `continuityworks_biomes:ash_wastes` | Barren extreme dryland | `minecraft:eroded_badlands` |

Each template includes a Continuity Works metric profile for temperature, humidity, vegetation density, terrain roughness, and water density. These are export metadata and are intentionally separate from Minecraft's native biome codec fields.

## Vanilla compatibility behavior

The vanilla datapack appends the templates to relevant existing Minecraft biome tags using `replace: false`. All eight are added to `minecraft:is_overworld`; forest, mountain, taiga, badlands, and savanna analogs are additionally classified through the corresponding vanilla tags. No file under `data/minecraft/worldgen/biome/` is emitted.

## Forge compatibility behavior

The Forge LowCodeFML JAR includes the same additive Minecraft tags and also appends appropriate Forge biome classification tags such as plains, swamp, mountain, coniferous, snowy, hot, dry, dead, and sandy. It does not use remove/replace biome modifiers.

## Verification results

The static export validator checks:

- exact template count;
- required biome codec keys;
- eleven feature-generation stages per template;
- required visual effect fields;
- JSON readability;
- Forge `mods.toml` TOML parsing and `lowcodefml` loader declaration;
- Minecraft 1.20.1 pack format 15;
- no vanilla biome definition overrides;
- no tag with `replace: true`;
- Forge/vanilla core biome-definition parity;
- ZIP/JAR archive integrity;
- non-destructive manifest invariants;
- explicit `PLACEMENT_PROVIDER_REQUIRED` status for natural Overworld placement.

The current generated bundle passes all 73 static checks. This does not substitute for launching Minecraft. The next runtime stage is to load both exports in controlled 1.20.1 test environments, verify registry load, inspect logs for missing worldgen references, and only then promote the provider tuple to runtime-validated status.

## Artifact hashes

- Forge JAR SHA-256: `78b382133130b11606f7a08dcaf4e26adb3a37b7a9c38ca72b1b7afa7690d957`
- Vanilla datapack SHA-256: `ffda5e2d614964532e3929feb745ed4e50ebc972d48e2b796f8765b8b58506c7`
- Source bundle SHA-256: `664baebdf021064c52a772050a4787092168c4a46fad2f402c710821b42bdd5a`
