package io.continuityworks.blueprint.runtime;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

final class ContinuityWorksSelectionNetwork {
    private static final String PROTOCOL = "1";
    private static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
        new ResourceLocation(ContinuityWorksBlueprintMod.MOD_ID, "selection"),
        () -> PROTOCOL,
        PROTOCOL::equals,
        PROTOCOL::equals
    );
    private static boolean registered;

    private ContinuityWorksSelectionNetwork() {}

    static synchronized void register() {
        if (registered) return;
        CHANNEL.messageBuilder(SelectionSyncPacket.class, 0, NetworkDirection.PLAY_TO_CLIENT)
            .encoder(SelectionSyncPacket::encode)
            .decoder(SelectionSyncPacket::decode)
            .consumerMainThread(SelectionSyncPacket::handle)
            .add();
        registered = true;
    }

    static void sync(ServerPlayer player) {
        SelectionSyncPacket packet = ContinuityWorksSelectionStore.INSTANCE.selectedArea(player.getUUID())
            .map(SelectionSyncPacket::from)
            .orElseGet(SelectionSyncPacket::empty);
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }
}
