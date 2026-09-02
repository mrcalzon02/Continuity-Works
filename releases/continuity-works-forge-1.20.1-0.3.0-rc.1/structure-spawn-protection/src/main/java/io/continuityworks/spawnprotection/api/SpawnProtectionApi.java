package io.continuityworks.spawnprotection.api;

import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;
import io.continuityworks.spawnprotection.runtime.SpawnProtectionService;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/**
 * Public adaptation surface for worldgen systems that do not use Registries.STRUCTURE.
 * Callers should reserve every independently accepted jigsaw/custom piece with the same
 * assembly id, then commit after the complete assembly succeeds or roll back on failure.
 */
public final class SpawnProtectionApi {
    public static ExternalReservationResult tryReserve(
        ServerLevel level,
        ResourceLocation structureId,
        ResourceLocation familyId,
        String assemblyId,
        BoundingBox footprint,
        int exclusionRadius,
        String pieceId
    ) {
        if (exclusionRadius < SpawnProtectionConfig.HARD_MINIMUM_RADIUS) {
            throw new IllegalArgumentException("External structure exclusion radius must be >= 500");
        }
        SpawnProtectionService.LevelState state = SpawnProtectionService.attachLevel(level);
        BlockBox box = BlockBox.from(footprint);
        String id = "external:" + assemblyId + "|" + box.compactKey();
        Reservation reservation = new Reservation(
            id, structureId, assemblyId,
            familyId == null ? structureId : familyId,
            box, exclusionRadius, pieceId, true
        );
        ReservationConflict conflict = state.index().tryReserve(
            reservation, SpawnProtectionConfig.SELF_COLLISION_PADDING.get()
        );
        return conflict == null
            ? new ExternalReservationResult(true, null, 0.0, 0)
            : new ExternalReservationResult(false, conflict.code(), conflict.horizontalGap(), conflict.requiredGap());
    }

    public static void commit(ServerLevel level, String assemblyId) {
        SpawnProtectionService.LevelState state = SpawnProtectionService.attachLevel(level);
        if (state.index().commitAssembly(assemblyId) > 0) state.markDirty();
    }

    public static void rollback(ServerLevel level, String assemblyId) {
        SpawnProtectionService.attachLevel(level).index().releaseProvisionalAssembly(assemblyId);
    }

    public record ExternalReservationResult(
        boolean accepted,
        String conflictCode,
        double horizontalGap,
        int requiredGap
    ) { }

    private SpawnProtectionApi() { }
}
