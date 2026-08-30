package io.continuityworks.biomes;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.SurfaceRules;

public final class BiomeTemplateSurfaceRules {
    private BiomeTemplateSurfaceRules() { }

    public static SurfaceRules.RuleSource makeRules() {
        return SurfaceRules.sequence(
            biomeSurface(BiomeTemplateKeys.TEMPERATE_GROVE, Blocks.GRASS_BLOCK, Blocks.DIRT),
            biomeSurface(BiomeTemplateKeys.FLOWERING_MEADOW, Blocks.GRASS_BLOCK, Blocks.DIRT),
            biomeSurface(BiomeTemplateKeys.MISTY_HIGHLANDS, Blocks.COARSE_DIRT, Blocks.STONE),
            biomeSurface(BiomeTemplateKeys.MARSHLAND, Blocks.MUD, Blocks.DIRT),
            biomeSurface(BiomeTemplateKeys.FROSTED_TAIGA, Blocks.PODZOL, Blocks.DIRT),
            biomeSurface(BiomeTemplateKeys.DRY_SCRUBLAND, Blocks.COARSE_DIRT, Blocks.DIRT),
            biomeSurface(BiomeTemplateKeys.ROCKY_BADLANDS, Blocks.RED_SAND, Blocks.TERRACOTTA),
            biomeSurface(BiomeTemplateKeys.ASH_WASTES, Blocks.TUFF, Blocks.BASALT)
        );
    }

    private static SurfaceRules.RuleSource biomeSurface(
        ResourceKey<Biome> biome,
        Block top,
        Block under
    ) {
        return SurfaceRules.ifTrue(
            SurfaceRules.isBiome(biome),
            SurfaceRules.sequence(
                SurfaceRules.ifTrue(SurfaceRules.ON_FLOOR, state(top)),
                SurfaceRules.ifTrue(SurfaceRules.UNDER_FLOOR, state(under))
            )
        );
    }

    private static SurfaceRules.RuleSource state(Block block) {
        return SurfaceRules.state(block.defaultBlockState());
    }
}
