package io.continuityworks.biomes;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** Generalized non-Abyssal terrain deformation feature registry. */
public final class LandTerrainFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> LAND_TOPOLOGY = FEATURES.register(
        "land_topology",
        LandTopologyFeature::new
    );

    private LandTerrainFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }
}
