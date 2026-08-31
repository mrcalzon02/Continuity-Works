package io.continuityworks.spawnprotection.runtime;

import io.continuityworks.spawnprotection.ContinuityWorksSpawnProtection;
import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import io.continuityworks.spawnprotection.data.ResolvedProtection;
import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiece;
import net.minecraft.world.phys.AABB;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** One structure-generation transaction. Kept thread-local while vanilla computes the start. */
public final class GenerationAttempt {
    private final SpawnProtectionService.LevelState state;
    private final ResourceLocation structureId;
    private final String assemblyId;
    private final ResolvedProtection protection;
    private final boolean jigsaw;
    private final List<BlockBox> acceptedJigsawBoxes = new ArrayList<>();
    private boolean invalidStart;

    GenerationAttempt(
        SpawnProtectionService.LevelState state,
        ResourceLocation structureId,
        String assemblyId,
        ResolvedProtection protection,
        boolean jigsaw
    ) {
        this.state = state;
        this.structureId = structureId;
        this.assemblyId = assemblyId;
        this.protection = protection;
        this.jigsaw = jigsaw;
    }

    public ResourceLocation structureId() {
        return structureId;
    }

    public String assemblyId() {
        return assemblyId;
    }

    public boolean invalidStart() {
        return invalidStart;
    }

    /** Observe an already-accepted/source jigsaw piece at the start of vanilla child expansion. */
    public void observeAcceptedPiece(net.minecraft.world.level.levelgen.structure.BoundingBox vanillaBox) {
        BlockBox box = BlockBox.from(vanillaBox);
        if (containsExact(box)) return;
        ReservationConflict local = selfConflict(box);
        if (local != null) {
            invalidStart = true;
            logConflict(local, box, "existing-jigsaw-piece");
            return;
        }
        ReservationConflict external = reserveProbe(box, "piece:" + box.compactKey());
        if (external != null) {
            invalidStart = true;
            logConflict(external, box, "existing-jigsaw-piece");
            return;
        }
        acceptedJigsawBoxes.add(box);
    }

    /** Called from the redirected vanilla voxel-fit check before a candidate piece is accepted. */
    public boolean allowCandidate(AABB candidateBounds) {
        if (invalidStart) return false;
        BlockBox box = BlockBox.from(candidateBounds);
        if (containsExact(box)) return true;
        ReservationConflict local = selfConflict(box);
        if (local != null) {
            logConflict(local, box, "candidate-jigsaw-piece");
            return false;
        }
        ReservationConflict external = reserveProbe(box, "piece:" + box.compactKey());
        if (external != null) {
            logConflict(external, box, "candidate-jigsaw-piece");
            return false;
        }
        acceptedJigsawBoxes.add(box);
        return true;
    }

    /** Reconcile speculative piece probes with vanilla's final StructureStart and atomically commit/release. */
    boolean finish(StructureStart start) {
        if (invalidStart || start == null || !start.isValid()) return false;

        List<StructurePiece> pieces = start.getPieces();
        if (jigsaw && !pieces.isEmpty()) {
            List<BlockBox> actual = pieces.stream().map(piece -> BlockBox.from(piece.getBoundingBox())).toList();
            if (hasSelfOverlap(actual)) {
                ContinuityWorksSpawnProtection.LOGGER.warn(
                    "Rejected {} assembly {} because final jigsaw pieces overlap each other",
                    structureId, assemblyId
                );
                return false;
            }
            Set<String> actualKeys = new HashSet<>();
            for (int i = 0; i < actual.size(); i++) {
                BlockBox box = actual.get(i);
                actualKeys.add(box.compactKey());
                ReservationConflict conflict = reserveProbe(box, "piece:" + i + ":" + box.compactKey());
                if (conflict != null) {
                    logConflict(conflict, box, "final-jigsaw-piece");
                    return false;
                }
            }
            state.index().reconcileProvisionalAssembly(assemblyId, actualKeys);
        } else {
            BlockBox box = BlockBox.from(start.getBoundingBox());
            ReservationConflict conflict = reserveProbe(box, "start:" + box.compactKey());
            if (conflict != null) {
                logConflict(conflict, box, "final-structure");
                return false;
            }
        }

        if (protection.emitsReservations()) {
            int changed = state.index().commitAssembly(assemblyId);
            if (changed > 0) state.markDirty();
        } else {
            state.index().releaseProvisionalAssembly(assemblyId);
        }
        return true;
    }

    void rollback() {
        state.index().releaseProvisionalAssembly(assemblyId);
    }

    private ReservationConflict reserveProbe(BlockBox box, String pieceId) {
        int radius = protection.emitsReservations()
            ? (jigsaw ? protection.jigsawPieceExclusionRadius() : protection.exclusionRadius())
            : 0;
        String reservationId = assemblyId + "|" + box.compactKey();
        Reservation reservation = new Reservation(
            reservationId,
            structureId,
            assemblyId,
            protection.familyId(),
            box,
            radius,
            pieceId,
            true
        );
        return state.index().tryReserve(reservation, SpawnProtectionConfig.SELF_COLLISION_PADDING.get());
    }

    private ReservationConflict selfConflict(BlockBox candidate) {
        int padding = SpawnProtectionConfig.SELF_COLLISION_PADDING.get();
        for (BlockBox existing : acceptedJigsawBoxes) {
            if (candidate.overlapsVolume(existing, padding)) {
                Reservation fake = new Reservation(
                    assemblyId + "|local|" + existing.compactKey(), structureId, assemblyId,
                    protection.familyId(), existing, 0, "local", true
                );
                return new ReservationConflict("SELF_JIGSAW_COLLISION", fake, 0.0, 0);
            }
        }
        return null;
    }

    private boolean hasSelfOverlap(List<BlockBox> boxes) {
        int padding = SpawnProtectionConfig.SELF_COLLISION_PADDING.get();
        for (int i = 0; i < boxes.size(); i++) {
            for (int j = i + 1; j < boxes.size(); j++) {
                if (boxes.get(i).overlapsVolume(boxes.get(j), padding)) return true;
            }
        }
        return false;
    }

    private boolean containsExact(BlockBox box) {
        return acceptedJigsawBoxes.stream().anyMatch(existing -> existing.equals(box));
    }

    private void logConflict(ReservationConflict conflict, BlockBox candidate, String phase) {
        ContinuityWorksSpawnProtection.LOGGER.debug(
            "Rejected {} {} for {}: {} against {} gap={} required={}",
            structureId,
            phase,
            candidate.compactKey(),
            conflict.code(),
            conflict.existing().reservationId(),
            conflict.horizontalGap(),
            conflict.requiredGap()
        );
    }
}
