package io.continuityworks.spawnprotection.model;

import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import net.minecraft.resources.ResourceLocation;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ReservationTest {
    private static final ResourceLocation STRUCTURE_ID = new ResourceLocation("continuityworks", "reservation_test");
    private static final BlockBox BOX = new BlockBox(0, 0, 0, 1, 1, 1);

    @Test
    void acceptsTransientProbeAndSupportedPersistentBoundaries() {
        assertDoesNotThrow(() -> reservation(0, true));
        assertDoesNotThrow(() -> reservation(SpawnProtectionConfig.HARD_MINIMUM_RADIUS, false));
        assertDoesNotThrow(() -> reservation(SpawnProtectionConfig.HARD_MAXIMUM_RADIUS, false));
    }

    @Test
    void rejectsCommittedTransientProbeRadius() {
        assertThrows(IllegalArgumentException.class, () -> reservation(0, false));
    }

    @Test
    void rejectsPersistentRadiusOutsideSupportedRange() {
        assertThrows(
            IllegalArgumentException.class,
            () -> reservation(SpawnProtectionConfig.HARD_MINIMUM_RADIUS - 1, true)
        );
        assertThrows(
            IllegalArgumentException.class,
            () -> reservation(SpawnProtectionConfig.HARD_MAXIMUM_RADIUS + 1, true)
        );
    }

    private static Reservation reservation(int radius, boolean provisional) {
        return new Reservation(
            "reservation-test-" + radius + "-" + provisional,
            STRUCTURE_ID,
            "assembly-test",
            STRUCTURE_ID,
            BOX,
            radius,
            "piece-test",
            provisional
        );
    }
}
