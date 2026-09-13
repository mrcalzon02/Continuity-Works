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
        assertDoesNotThrow(() -> reservation(0));
        assertDoesNotThrow(() -> reservation(SpawnProtectionConfig.HARD_MINIMUM_RADIUS));
        assertDoesNotThrow(() -> reservation(SpawnProtectionConfig.HARD_MAXIMUM_RADIUS));
    }

    @Test
    void rejectsPersistentRadiusOutsideSupportedRange() {
        assertThrows(
            IllegalArgumentException.class,
            () -> reservation(SpawnProtectionConfig.HARD_MINIMUM_RADIUS - 1)
        );
        assertThrows(
            IllegalArgumentException.class,
            () -> reservation(SpawnProtectionConfig.HARD_MAXIMUM_RADIUS + 1)
        );
    }

    private static Reservation reservation(int radius) {
        return new Reservation(
            "reservation-test-" + radius,
            STRUCTURE_ID,
            "assembly-test",
            STRUCTURE_ID,
            BOX,
            radius,
            "piece-test",
            true
        );
    }
}
