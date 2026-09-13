package io.continuityworks.spawnprotection.runtime;

import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Thread-safe spatial reservation index used by parallel worldgen workers. */
public final class ReservationIndex {
    private static final int CELL_SIZE = 512;

    private final Map<String, Reservation> reservations = new LinkedHashMap<>();
    private final Map<Long, Set<String>> cells = new HashMap<>();

    public ReservationIndex(Collection<Reservation> initial) {
        for (Reservation reservation : initial) {
            if (reservations.containsKey(reservation.reservationId())) {
                throw new IllegalArgumentException("Duplicate restored reservation id: " + reservation.reservationId());
            }
            putUnchecked(reservation);
        }
    }

    public synchronized ReservationConflict conflictFor(
        BlockBox candidate,
        int candidateRadius,
        String assemblyId,
        int selfCollisionPadding
    ) {
        for (Reservation existing : candidates(candidate, candidateRadius)) {
            if (existing.assemblyId().equals(assemblyId)) {
                if (candidate.overlapsVolume(existing.box(), selfCollisionPadding)) {
                    return new ReservationConflict("SELF_JIGSAW_COLLISION", existing, 0.0, 0);
                }
                continue;
            }
            double gap = candidate.horizontalGap(existing.box());
            int required = Math.max(candidateRadius, existing.exclusionRadius());
            if (gap < required) {
                return new ReservationConflict("STRUCTURE_EXCLUSION_CONFLICT", existing, gap, required);
            }
        }
        return null;
    }

    /** Atomic check + insert. Null means the reservation was accepted. */
    public synchronized ReservationConflict tryReserve(Reservation reservation, int selfCollisionPadding) {
        Reservation current = reservations.get(reservation.reservationId());
        if (current != null) {
            if (current.committed().equals(reservation.committed())) return null;
            return new ReservationConflict("RESERVATION_ID_CONFLICT", current, 0.0, 0);
        }
        ReservationConflict conflict = conflictFor(
            reservation.box(), reservation.exclusionRadius(), reservation.assemblyId(), selfCollisionPadding
        );
        if (conflict != null) return conflict;
        putUnchecked(reservation);
        return null;
    }

    /**
     * Idempotently import committed saved/existing world state. Equivalent imports may strengthen
     * their exclusion radius, but never weaken an already stronger persisted reservation.
     */
    public synchronized boolean importCommitted(Reservation reservation) {
        Reservation committed = reservation.committed();
        Reservation current = reservations.get(committed.reservationId());
        if (current != null) {
            Reservation currentCommitted = current.committed();
            if (currentCommitted.equals(committed)) return false;
            if (sameCommittedIdentity(currentCommitted, committed)) {
                if (currentCommitted.exclusionRadius() >= committed.exclusionRadius()) return false;
                removeUnchecked(currentCommitted.reservationId());
                putUnchecked(committed);
                return true;
            }
            throw new IllegalArgumentException(
                "Reservation id already identifies a different committed reservation: " + committed.reservationId()
            );
        }
        putUnchecked(committed);
        return true;
    }

    public synchronized int releaseProvisionalAssembly(String assemblyId) {
        List<String> remove = reservations.values().stream()
            .filter(r -> r.provisional() && r.assemblyId().equals(assemblyId))
            .map(Reservation::reservationId)
            .toList();
        remove.forEach(this::removeUnchecked);
        return remove.size();
    }

    public synchronized int reconcileProvisionalAssembly(String assemblyId, Set<String> actualBoxKeys) {
        List<String> remove = reservations.values().stream()
            .filter(r -> r.provisional() && r.assemblyId().equals(assemblyId) && !actualBoxKeys.contains(r.box().compactKey()))
            .map(Reservation::reservationId)
            .toList();
        remove.forEach(this::removeUnchecked);
        return remove.size();
    }

    public synchronized int commitAssembly(String assemblyId) {
        int changed = 0;
        for (Map.Entry<String, Reservation> entry : new ArrayList<>(reservations.entrySet())) {
            Reservation reservation = entry.getValue();
            if (reservation.provisional() && reservation.assemblyId().equals(assemblyId)) {
                reservations.put(entry.getKey(), reservation.committed());
                changed++;
            }
        }
        return changed;
    }

    public synchronized List<Reservation> committedSnapshot() {
        return reservations.values().stream().filter(r -> !r.provisional()).toList();
    }

    public synchronized int size() {
        return reservations.size();
    }

    public synchronized boolean containsCommittedEquivalent(
        net.minecraft.resources.ResourceLocation structureId,
        BlockBox box,
        int requiredExclusionRadius
    ) {
        return reservations.values().stream().anyMatch(r ->
            !r.provisional()
                && r.structureId().equals(structureId)
                && r.box().equals(box)
                && r.exclusionRadius() >= requiredExclusionRadius
        );
    }

    private Set<Reservation> candidates(BlockBox box, int candidateRadius) {
        Set<String> ids = new HashSet<>();
        int radius = Math.max(0, candidateRadius);
        int minCellX = Math.floorDiv(box.minX() - radius, CELL_SIZE);
        int maxCellX = Math.floorDiv(box.maxX() + radius, CELL_SIZE);
        int minCellZ = Math.floorDiv(box.minZ() - radius, CELL_SIZE);
        int maxCellZ = Math.floorDiv(box.maxZ() + radius, CELL_SIZE);
        for (int x = minCellX; x <= maxCellX; x++) {
            for (int z = minCellZ; z <= maxCellZ; z++) {
                Set<String> bucket = cells.get(cellKey(x, z));
                if (bucket != null) ids.addAll(bucket);
            }
        }
        Set<Reservation> out = new HashSet<>();
        for (String id : ids) {
            Reservation reservation = reservations.get(id);
            if (reservation != null) out.add(reservation);
        }
        return out;
    }

    private void putUnchecked(Reservation reservation) {
        reservations.put(reservation.reservationId(), reservation);
        int radius = reservation.exclusionRadius();
        int minCellX = Math.floorDiv(reservation.box().minX() - radius, CELL_SIZE);
        int maxCellX = Math.floorDiv(reservation.box().maxX() + radius, CELL_SIZE);
        int minCellZ = Math.floorDiv(reservation.box().minZ() - radius, CELL_SIZE);
        int maxCellZ = Math.floorDiv(reservation.box().maxZ() + radius, CELL_SIZE);
        for (int x = minCellX; x <= maxCellX; x++) {
            for (int z = minCellZ; z <= maxCellZ; z++) {
                cells.computeIfAbsent(cellKey(x, z), ignored -> new HashSet<>()).add(reservation.reservationId());
            }
        }
    }

    private void removeUnchecked(String reservationId) {
        Reservation reservation = reservations.remove(reservationId);
        if (reservation == null) return;
        int radius = reservation.exclusionRadius();
        int minCellX = Math.floorDiv(reservation.box().minX() - radius, CELL_SIZE);
        int maxCellX = Math.floorDiv(reservation.box().maxX() + radius, CELL_SIZE);
        int minCellZ = Math.floorDiv(reservation.box().minZ() - radius, CELL_SIZE);
        int maxCellZ = Math.floorDiv(reservation.box().maxZ() + radius, CELL_SIZE);
        for (int x = minCellX; x <= maxCellX; x++) {
            for (int z = minCellZ; z <= maxCellZ; z++) {
                long key = cellKey(x, z);
                Set<String> bucket = cells.get(key);
                if (bucket == null) continue;
                bucket.remove(reservationId);
                if (bucket.isEmpty()) cells.remove(key);
            }
        }
    }

    private static boolean sameCommittedIdentity(Reservation left, Reservation right) {
        return left.reservationId().equals(right.reservationId())
            && left.structureId().equals(right.structureId())
            && left.assemblyId().equals(right.assemblyId())
            && Objects.equals(left.familyId(), right.familyId())
            && left.box().equals(right.box())
            && Objects.equals(left.pieceId(), right.pieceId());
    }

    private static long cellKey(int x, int z) {
        return ((long) x << 32) ^ (z & 0xffffffffL);
    }
}
