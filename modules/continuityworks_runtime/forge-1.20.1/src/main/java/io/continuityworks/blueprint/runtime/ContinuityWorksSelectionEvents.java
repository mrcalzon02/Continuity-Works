package io.continuityworks.blueprint.runtime;

import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ContinuityWorksBlueprintMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ContinuityWorksSelectionEvents {
    private ContinuityWorksSelectionEvents() {}

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        ContinuityWorksSelectionCommands.register(event.getDispatcher());
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) ContinuityWorksSelectionNetwork.sync(player);
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) ContinuityWorksSelectionNetwork.sync(player);
    }

    @SubscribeEvent
    public static void onChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) ContinuityWorksSelectionNetwork.sync(player);
    }

    @SubscribeEvent
    public static void onServerStopped(ServerStoppedEvent event) {
        ContinuityWorksSelectionStore.INSTANCE.clearRuntime();
    }
}
