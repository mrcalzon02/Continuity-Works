package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.biome.Biome;

public final class BiomeTemplateKeys {
    public static final ResourceKey<Biome> TEMPERATE_GROVE = key("temperate_grove");
    public static final ResourceKey<Biome> FLOWERING_MEADOW = key("flowering_meadow");
    public static final ResourceKey<Biome> MISTY_HIGHLANDS = key("misty_highlands");
    public static final ResourceKey<Biome> MARSHLAND = key("marshland");
    public static final ResourceKey<Biome> FROSTED_TAIGA = key("frosted_taiga");
    public static final ResourceKey<Biome> DRY_SCRUBLAND = key("dry_scrubland");
    public static final ResourceKey<Biome> ROCKY_BADLANDS = key("rocky_badlands");
    public static final ResourceKey<Biome> ASH_WASTES = key("ash_wastes");

    // Infinite Domain Abyssal family, adapted to the Continuity Works namespace.
    public static final ResourceKey<Biome> WESTERN_CONTINENTAL_SLOPE = key("western_continental_slope");
    public static final ResourceKey<Biome> WESTERN_ABYSSAL_PLAIN = key("western_abyssal_plain");
    public static final ResourceKey<Biome> WESTERN_FRACTURE_FIELD = key("western_fracture_field");
    public static final ResourceKey<Biome> WESTERN_HADAL_TRENCH = key("western_hadal_trench");
    public static final ResourceKey<Biome> EASTERN_CONTINENTAL_SLOPE = key("eastern_continental_slope");
    public static final ResourceKey<Biome> EASTERN_ABYSSAL_PLAIN = key("eastern_abyssal_plain");
    public static final ResourceKey<Biome> EASTERN_FRACTURE_FIELD = key("eastern_fracture_field");
    public static final ResourceKey<Biome> EASTERN_HADAL_TRENCH = key("eastern_hadal_trench");

    // Retained compatibility IDs from the Infinite Domain program.
    public static final ResourceKey<Biome> WESTERN_ABYSSAL_OCEAN = key("western_abyssal_ocean");
    public static final ResourceKey<Biome> EASTERN_ABYSSAL_OCEAN = key("eastern_abyssal_ocean");

    private BiomeTemplateKeys() { }

    private static ResourceKey<Biome> key(String path) {
        return ResourceKey.create(
            Registries.BIOME,
            new ResourceLocation(ContinuityWorksBiomeTemplates.MOD_ID, path)
        );
    }
}
