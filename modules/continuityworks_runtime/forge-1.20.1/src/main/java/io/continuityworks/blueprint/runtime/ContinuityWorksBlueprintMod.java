package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.ContinuityWorksBlueprintServices;
import io.continuityworks.api.blueprint.ContinuityWorksCompactBlueprintServices;
import io.continuityworks.api.blueprint.ContinuityWorksSelectionServices;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(ContinuityWorksBlueprintMod.MOD_ID)
public final class ContinuityWorksBlueprintMod {
    public static final String MOD_ID = "continuityworks_blueprint";

    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MOD_ID);
    public static final RegistryObject<Item> BUILD_AREA_SELECTOR = ITEMS.register(
        "build_area_selector",
        () -> new BuildAreaSelectorItem(new Item.Properties().stacksTo(1))
    );

    public ContinuityWorksBlueprintMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(modBus);
        modBus.addListener(this::buildCreativeContents);
        ContinuityWorksSelectionNetwork.register();
        ContinuityWorksBlueprintServices.install(new ResourceBudgetedBlueprintApi());
        ContinuityWorksCompactBlueprintServices.install(new CorpusAwareCompactBlueprintProvider());
        ContinuityWorksSelectionServices.install(ContinuityWorksSelectionStore.INSTANCE);
    }

    private void buildCreativeContents(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            event.accept(BUILD_AREA_SELECTOR);
        }
    }
}
