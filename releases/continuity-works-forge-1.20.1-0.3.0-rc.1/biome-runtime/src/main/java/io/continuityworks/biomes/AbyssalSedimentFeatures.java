package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** Abyssal depositional and sediment-morphology generator family. */
public final class AbyssalSedimentFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SHELF_SAND_WAVE_FIELD = FEATURES.register(
        "shelf_sand_wave_field",
        ShelfSandWaveFeature::new
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> NODULE_FIELD = FEATURES.register(
        "nodule_field",
        NoduleFieldFeature::new
    );

    private AbyssalSedimentFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }
}
