package io.continuityworks.blueprint.runtime;

import net.minecraft.ChatFormatting;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.function.Supplier;

/** Client request to move one selected-volume face outward (+1) or inward (-1). */
public record SelectionAdjustPacket(SelectionFace face, int outwardDelta) {
    public SelectionAdjustPacket {
        Objects.requireNonNull(face, "face");
        if (outwardDelta != -1 && outwardDelta != 1) {
            throw new IllegalArgumentException("Selection face adjustment must be -1 or +1");
        }
    }

    static void encode(SelectionAdjustPacket packet, FriendlyByteBuf buffer) {
        buffer.writeByte(packet.face().ordinal());
        buffer.writeByte(packet.outwardDelta());
    }

    static SelectionAdjustPacket decode(FriendlyByteBuf buffer) {
        SelectionFace face = SelectionFace.fromOrdinal(buffer.readUnsignedByte());
        int delta = buffer.readByte();
        return new SelectionAdjustPacket(face, delta);
    }

    static void handle(SelectionAdjustPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) return;
            try {
                ContinuityWorksSelectionStore.INSTANCE.adjustFace(player, packet.face(), packet.outwardDelta());
            } catch (IllegalArgumentException error) {
                player.displayClientMessage(Component.literal(error.getMessage()).withStyle(ChatFormatting.RED), true);
            } finally {
                ContinuityWorksSelectionNetwork.sync(player);
            }
        });
        context.setPacketHandled(true);
    }
}
