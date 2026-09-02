package io.continuityworks.biomes;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.SurfaceRules;

import java.util.ArrayList;
import java.util.List;

public final class BiomeTemplateSurfaceRules {
    private BiomeTemplateSurfaceRules() { }

    public static SurfaceRules.RuleSource makeRules() {
        List<SurfaceRules.RuleSource> rules = new ArrayList<>();

        rules.add(biomeSurface(BiomeTemplateKeys.TEMPERATE_GROVE, Blocks.GRASS_BLOCK, Blocks.DIRT));
        rules.add(biomeSurface(BiomeTemplateKeys.FLOWERING_MEADOW, Blocks.GRASS_BLOCK, Blocks.DIRT));
        rules.add(biomeSurface(BiomeTemplateKeys.MISTY_HIGHLANDS, Blocks.COARSE_DIRT, Blocks.STONE));
        rules.add(biomeSurface(BiomeTemplateKeys.MARSHLAND, Blocks.MUD, Blocks.DIRT));
        rules.add(biomeSurface(BiomeTemplateKeys.FROSTED_TAIGA, Blocks.PODZOL, Blocks.DIRT));
        rules.add(biomeSurface(BiomeTemplateKeys.DRY_SCRUBLAND, Blocks.COARSE_DIRT, Blocks.DIRT));
        rules.add(biomeSurface(BiomeTemplateKeys.ROCKY_BADLANDS, Blocks.RED_SAND, Blocks.TERRACOTTA));
        rules.add(biomeSurface(BiomeTemplateKeys.ASH_WASTES, Blocks.TUFF, Blocks.BASALT));

        for (AnthologyBiomeCatalog.Entry entry : AnthologyBiomeCatalog.ENTRIES) {
            rules.add(biomeSurface(entry.key(), entry.top(), entry.under()));
        }

        return SurfaceRules.sequence(rules.toArray(SurfaceRules.RuleSource[]::new));
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
