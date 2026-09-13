package io.continuityworks.spawnprotection.runtime;

import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;
import net.minecraft.resources.ResourceLocation;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

final class ReservationIndexTest {
    @Test
    void duplicateIdWithDifferentReservationFailsClosed() {
        Reservation existing = reservation("shared-id", "first", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), true);
        Reservation replacement = reservation("shared-id", "second", "assembly-b", new BlockBox(1000, 64, 1000, 1015, 79, 1015), true);
        ReservationIndex index = new ReservationIndex(List.of(existing));

        ReservationConflict conflict = index.tryReserve(replacement, 0);

        assertEquals("RESERVATION_ID_CONFLICT", conflict.code());
        assertSame(existing, conflict.existing());
        assertEquals(1, index.size());
    }

    @Test
    void exactReservationRetryRemainsIdempotentAcrossLifecycleState() {
        Reservation provisional = reservation("retry-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), true);
        Reservation committed = provisional.committed();
        ReservationIndex index = new ReservationIndex(List.of(committed));

        assertNull(index.tryReserve(provisional, 0));
        assertEquals(1, index.size());
    }

    @Test
    void importCommittedEquivalentRetryIsIdempotentAcrossLifecycleState() {
        Reservation provisional = reservation("import-retry-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), true);
        Reservation committed = provisional.committed();
        ReservationIndex index = new ReservationIndex(List.of(committed));

        assertFalse(index.importCommitted(provisional));
        assertEquals(List.of(committed), index.committedSnapshot());
    }

    @Test
    void importCommittedEquivalentReservationStrengthensRadiusAndSpatialIndex() {
        Reservation existing = reservation("radius-upgrade-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), false, 500);
        Reservation strengthened = reservation("radius-upgrade-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), false, 1500);
        ReservationIndex index = new ReservationIndex(List.of(existing));

        assertEquals(true, index.importCommitted(strengthened));
        assertEquals(List.of(strengthened), index.committedSnapshot());

        ReservationConflict conflict = index.conflictFor(
            new BlockBox(1200, 64, 0, 1215, 79, 15), 0, "other-assembly", 0
        );
        assertEquals("STRUCTURE_EXCLUSION_CONFLICT", conflict.code());
        assertEquals(1500, conflict.requiredGap());
    }

    @Test
    void importCommittedEquivalentReservationNeverWeakensRadius() {
        Reservation existing = reservation("radius-preserve-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), false, 900);
        Reservation weaker = reservation("radius-preserve-id", "same", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), false, 500);
        ReservationIndex index = new ReservationIndex(List.of(existing));

        assertFalse(index.importCommitted(weaker));
        assertEquals(List.of(existing), index.committedSnapshot());
    }

    @Test
    void committedEquivalentRequiresCurrentRadiusOrStronger() {
        BlockBox box = new BlockBox(0, 64, 0, 15, 79, 15);
        Reservation existing = reservation("equivalent-radius-id", "same", "assembly-a", box, false, 500);
        ReservationIndex index = new ReservationIndex(List.of(existing));
        ResourceLocation structureId = new ResourceLocation("continuity_works", "same");

        assertEquals(true, index.containsCommittedEquivalent(structureId, box, 500));
        assertFalse(index.containsCommittedEquivalent(structureId, box, 800));
    }

    @Test
    void importCommittedDuplicateIdWithDifferentReservationFailsClosed() {
        Reservation existing = reservation("import-shared-id", "first", "assembly-a", new BlockBox(0, 64, 0, 15, 79, 15), false);
        Reservation replacement = reservation("import-shared-id", "second", "assembly-b", new BlockBox(1000, 64, 1000, 1015, 79, 1015), false);
        ReservationIndex index = new ReservationIndex(List.of(existing));

        assertThrows(IllegalArgumentException.class, () -> index.importCommitted(replacement));
        assertEquals(List.of(existing), index.committedSnapshot());
    }

    private static Reservation reservation(
        String id,
        String structurePath,
        String assemblyId,
        BlockBox box,
        boolean provisional
    ) {
        return reservation(id, structurePath, assemblyId, box, provisional, 500);
    }

    private static Reservation reservation(
        String id,
        String structurePath,
        String assemblyId,
        BlockBox box,
        boolean provisional,
        int exclusionRadius
    ) {
        return new Reservation(
            id,
            new ResourceLocation("continuity_works", structurePath),
            assemblyId,
            new ResourceLocation("continuity_works", "test_family"),
            box,
            exclusionRadius,
            "piece",
            provisional
        );
    }
}
