package io.continuityworks.spawnprotection.data;

import net.minecraft.resources.ResourceLocation;

public record ResolvedProtection(
    ResourceLocation structureId,
    ResourceLocation familyId,
    boolean emitsReservations,
    boolean protectJigsawPieces,
    int exclusionRadius,
    int jigsawPieceExclusionRadius,
    String source
) {
    public static ResolvedProtection respectOnly(ResourceLocation structureId) {
        return new ResolvedProtection(structureId, structureId, false, false, 0, 0, "respect-only");
    }
}
