package io.continuityworks.biomes;

import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import terrablender.api.Regions;
import terrablender.api.SurfaceRuleManager;

@Mod(ContinuityWorksBiomeTemplates.MOD_ID)
public final class ContinuityWorksBiomeTemplates {
    public static final String MOD_ID = "continuityworks_biomes";

    public ContinuityWorksBiomeTemplates() {
        ModLoadingContext.get().registerConfig(
            ModConfig.Type.COMMON,
            BiomeTemplateConfig.SPEC,
            "continuityworks-biomes-common.toml"
        );

        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        modBus.addListener(this::commonSetup);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            if (!BiomeTemplateConfig.anyEnabled()) {
                return;
            }

            Regions.register(new BiomeTemplateRegion(
                new ResourceLocation(MOD_ID, "overworld_templates"),
                BiomeTemplateConfig.REGION_WEIGHT.get()
            ));

            SurfaceRuleManager.addSurfaceRules(
                SurfaceRuleManager.RuleCategory.OVERWORLD,
                MOD_ID,
                BiomeTemplateSurfaceRules.makeRules()
            );
        });
    }
}
