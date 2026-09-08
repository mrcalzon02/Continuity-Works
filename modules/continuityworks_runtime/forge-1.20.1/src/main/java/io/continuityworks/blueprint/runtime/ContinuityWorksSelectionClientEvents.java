package io.continuityworks.blueprint.runtime;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ContinuityWorksBlueprintMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class ContinuityWorksSelectionClientEvents {
    private ContinuityWorksSelectionClientEvents() {}

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        while (ContinuityWorksSelectionClientModEvents.TOGGLE_HIGHLIGHT.consumeClick()) {
            ClientSelectionState.toggleHighlight();
        }
    }

    @SubscribeEvent
    public static void onRenderLevel(RenderLevelStageEvent event) {
        ClientSelectionState.render(event);
    }
}
