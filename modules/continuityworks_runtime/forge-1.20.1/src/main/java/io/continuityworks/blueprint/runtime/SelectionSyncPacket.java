package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.BuildAreaSelection;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.UUID;
import java.util.function.Supplier;

public record SelectionSyncPacket(
    boolean present,
    String dimensionId,
    UUID volumeId,
    long snapshotEpoch,
    int minX,
    int minY,
    int minZ,
    int maxX,
    int maxY,
    int maxZ
) {
    static SelectionSyncPacket empty() {
        return new SelectionSyncPacket(false, "", new UUID(0L, 0L), 0L, 0, 0, 0, 0, 0, 0);
    }

    static SelectionSyncPacket from(BuildAreaSelection selection) {
        var bounds = selection.volume().bounds();
        return new SelectionSyncPacket(
            true,
            selection.dimensionId(),
            selection.volume().volumeId(),
            selection.volume().snapshotEpoch(),
            bounds.min().x(), bounds.min().y(), bounds.min().z(),
            bounds.max().x(), bounds.max().y(), bounds.max().z()
        );
    }

    static void encode(SelectionSyncPacket packet, FriendlyByteBuf buffer) {
        buffer.writeBoolean(packet.present());
        if (!packet.present()) return;
        buffer.writeUtf(packet.dimensionId(), 128);
        buffer.writeUUID(packet.volumeId());
        buffer.writeLong(packet.snapshotEpoch());
        buffer.writeInt(packet.minX()); buffer.writeInt(packet.minY()); buffer.writeInt(packet.minZ());
        buffer.writeInt(packet.maxX()); buffer.writeInt(packet.maxY()); buffer.writeInt(packet.maxZ());
    }

    static SelectionSyncPacket decode(FriendlyByteBuf buffer) {
        if (!buffer.readBoolean()) return empty();
        return new SelectionSyncPacket(
            true,
            buffer.readUtf(128),
            buffer.readUUID(),
            buffer.readLong(),
            buffer.readInt(), buffer.readInt(), buffer.readInt(),
            buffer.readInt(), buffer.readInt(), buffer.readInt()
        );
    }

    static void handle(SelectionSyncPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(
            Dist.CLIENT,
            () -> () -> ClientSelectionState.accept(packet)
        ));
        context.setPacketHandled(true);
    }
}
