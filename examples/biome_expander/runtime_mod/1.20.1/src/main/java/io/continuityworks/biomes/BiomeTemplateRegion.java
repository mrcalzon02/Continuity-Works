package io.continuityworks.biomes;

import com.mojang.datafixers.util.Pair;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Climate;
import terrablender.api.Region;
import terrablender.api.RegionType;
import terrablender.api.VanillaParameterOverlayBuilder;

import java.util.function.Consumer;

import static terrablender.api.ParameterUtils.*;

public final class BiomeTemplateRegion extends Region {
    public BiomeTemplateRegion(ResourceLocation name, int weight) {
        super(name, RegionType.OVERWORLD, weight);
    }

    @Override
    public void addBiomes(
        Registry<Biome> registry,
        Consumer<Pair<Climate.ParameterPoint, ResourceKey<Biome>>> mapper
    ) {
        VanillaParameterOverlayBuilder overlay = new VanillaParameterOverlayBuilder();

        if (BiomeTemplateConfig.ENABLE_TEMPERATE_GROVE.get()) {
            add(overlay, BiomeTemplateKeys.TEMPERATE_GROVE,
                new ParameterPointListBuilder()
                    .temperature(Temperature.NEUTRAL, Temperature.WARM)
                    .humidity(Humidity.WET, Humidity.HUMID)
                    .continentalness(Continentalness.MID_INLAND, Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_2, Erosion.EROSION_3, Erosion.EROSION_4)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.MID_SLICE_NORMAL_DESCENDING, Weirdness.MID_SLICE_VARIANT_ASCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_FLOWERING_MEADOW.get()) {
            add(overlay, BiomeTemplateKeys.FLOWERING_MEADOW,
                new ParameterPointListBuilder()
                    .temperature(Temperature.COOL, Temperature.NEUTRAL)
                    .humidity(Humidity.NEUTRAL, Humidity.WET)
                    .continentalness(Continentalness.MID_INLAND, Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_4, Erosion.EROSION_5, Erosion.EROSION_6)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.VALLEY, Weirdness.LOW_SLICE_VARIANT_ASCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_MISTY_HIGHLANDS.get()) {
            add(overlay, BiomeTemplateKeys.MISTY_HIGHLANDS,
                new ParameterPointListBuilder()
                    .temperature(Temperature.COOL, Temperature.NEUTRAL)
                    .humidity(Humidity.WET, Humidity.HUMID)
                    .continentalness(Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_0, Erosion.EROSION_1)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.PEAK_NORMAL, Weirdness.PEAK_VARIANT,
                        Weirdness.HIGH_SLICE_NORMAL_ASCENDING, Weirdness.HIGH_SLICE_VARIANT_DESCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_MARSHLAND.get()) {
            add(overlay, BiomeTemplateKeys.MARSHLAND,
                new ParameterPointListBuilder()
                    .temperature(Temperature.NEUTRAL, Temperature.WARM)
                    .humidity(Humidity.HUMID)
                    .continentalness(Continentalness.COAST, Continentalness.NEAR_INLAND)
                    .erosion(Erosion.EROSION_5, Erosion.EROSION_6)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.VALLEY, Weirdness.LOW_SLICE_NORMAL_DESCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_FROSTED_TAIGA.get()) {
            add(overlay, BiomeTemplateKeys.FROSTED_TAIGA,
                new ParameterPointListBuilder()
                    .temperature(Temperature.ICY, Temperature.COOL)
                    .humidity(Humidity.NEUTRAL, Humidity.WET)
                    .continentalness(Continentalness.MID_INLAND, Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_2, Erosion.EROSION_3)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.MID_SLICE_NORMAL_ASCENDING, Weirdness.MID_SLICE_VARIANT_DESCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_DRY_SCRUBLAND.get()) {
            add(overlay, BiomeTemplateKeys.DRY_SCRUBLAND,
                new ParameterPointListBuilder()
                    .temperature(Temperature.WARM, Temperature.HOT)
                    .humidity(Humidity.ARID, Humidity.DRY)
                    .continentalness(Continentalness.NEAR_INLAND, Continentalness.MID_INLAND)
                    .erosion(Erosion.EROSION_3, Erosion.EROSION_4, Erosion.EROSION_5)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.LOW_SLICE_NORMAL_DESCENDING, Weirdness.LOW_SLICE_VARIANT_ASCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_ROCKY_BADLANDS.get()) {
            add(overlay, BiomeTemplateKeys.ROCKY_BADLANDS,
                new ParameterPointListBuilder()
                    .temperature(Temperature.HOT)
                    .humidity(Humidity.ARID, Humidity.DRY)
                    .continentalness(Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_0, Erosion.EROSION_1, Erosion.EROSION_2)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.PEAK_NORMAL, Weirdness.HIGH_SLICE_NORMAL_DESCENDING));
        }

        if (BiomeTemplateConfig.ENABLE_ASH_WASTES.get()) {
            add(overlay, BiomeTemplateKeys.ASH_WASTES,
                new ParameterPointListBuilder()
                    .temperature(Temperature.HOT)
                    .humidity(Humidity.ARID)
                    .continentalness(Continentalness.FAR_INLAND)
                    .erosion(Erosion.EROSION_0)
                    .depth(Depth.SURFACE)
                    .weirdness(Weirdness.PEAK_VARIANT, Weirdness.MID_SLICE_VARIANT_DESCENDING));
        }

        overlay.build().forEach(mapper::accept);
    }

    private static void add(
        VanillaParameterOverlayBuilder overlay,
        ResourceKey<Biome> biome,
        ParameterPointListBuilder points
    ) {
        points.build().forEach(point -> overlay.add(point, biome));
    }
}
