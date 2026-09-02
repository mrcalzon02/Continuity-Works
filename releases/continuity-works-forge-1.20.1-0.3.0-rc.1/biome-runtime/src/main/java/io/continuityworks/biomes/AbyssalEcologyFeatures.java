package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** Neutral Abyssal ecological-site generator family. */
public final class AbyssalEcologyFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> WHALE_FALL = FEATURES.register(
        "whale_fall",
        WhaleFallFeature::new
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> WOOD_FALL = FEATURES.register(
        "wood_fall",
        WoodFallFeature::new
    );

    private AbyssalEcologyFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }
}
