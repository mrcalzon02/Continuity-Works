package io.continuityworks.spawnprotection.runtime;

import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;
import net.minecraft.resources.ResourceLocation;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;

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

    private static Reservation reservation(
        String id,
        String structurePath,
        String assemblyId,
        BlockBox box,
        boolean provisional
    ) {
        return new Reservation(
            id,
            new ResourceLocation("continuity_works", structurePath),
            assemblyId,
            new ResourceLocation("continuity_works", "test_family"),
            box,
            500,
            "piece",
            provisional
        );
    }
}
