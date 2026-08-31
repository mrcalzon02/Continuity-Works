package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** Registry for the biome-aware volumetric cave network system. */
public final class BiomeCaveFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> BIOME_CAVE_NETWORK = FEATURES.register(
        "biome_cave_network",
        BiomeCaveNetworkFeature::new
    );

    private BiomeCaveFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }
}
