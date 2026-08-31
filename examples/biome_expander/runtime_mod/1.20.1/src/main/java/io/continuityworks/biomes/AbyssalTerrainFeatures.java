package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * Abyssal generators that alter generated seabed geometry rather than placing
 * discrete landmark structures or surface decoration.
 */
public final class AbyssalTerrainFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> POCKMARK_FIELD = FEATURES.register(
        "pockmark_field",
        PockmarkFieldFeature::new
    );

    private AbyssalTerrainFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }
}
