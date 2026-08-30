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

    private BiomeTemplateKeys() { }

    private static ResourceKey<Biome> key(String path) {
        return ResourceKey.create(
            Registries.BIOME,
            new ResourceLocation(ContinuityWorksBiomeTemplates.MOD_ID, path)
        );
    }
}
