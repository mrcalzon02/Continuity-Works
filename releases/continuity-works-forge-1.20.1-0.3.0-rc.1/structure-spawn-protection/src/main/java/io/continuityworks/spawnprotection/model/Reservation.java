package io.continuityworks.spawnprotection.model;

import net.minecraft.resources.ResourceLocation;

public record Reservation(
    String reservationId,
    ResourceLocation structureId,
    String assemblyId,
    ResourceLocation familyId,
    BlockBox box,
    int exclusionRadius,
    String pieceId,
    boolean provisional
) {
    public Reservation {
        if (reservationId == null || reservationId.isBlank()) throw new IllegalArgumentException("reservationId");
        if (structureId == null) throw new IllegalArgumentException("structureId");
        if (assemblyId == null || assemblyId.isBlank()) throw new IllegalArgumentException("assemblyId");
        if (familyId == null) throw new IllegalArgumentException("familyId");
        if (box == null) throw new IllegalArgumentException("box");
        if (exclusionRadius != 0 && exclusionRadius < 500) {
            throw new IllegalArgumentException("persistent exclusionRadius must be 0 (transient probe) or >= 500");
        }
    }

    public Reservation committed() {
        return provisional ? new Reservation(
            reservationId, structureId, assemblyId, familyId, box, exclusionRadius, pieceId, false
        ) : this;
    }
}
