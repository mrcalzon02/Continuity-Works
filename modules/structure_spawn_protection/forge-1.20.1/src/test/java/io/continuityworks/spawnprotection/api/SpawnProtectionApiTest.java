package io.continuityworks.spawnprotection.api;

import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class SpawnProtectionApiTest {
    @Test
    void acceptsSupportedBoundaryRadii() {
        assertDoesNotThrow(() -> SpawnProtectionApi.validateExclusionRadius(
            SpawnProtectionConfig.HARD_MINIMUM_RADIUS
        ));
        assertDoesNotThrow(() -> SpawnProtectionApi.validateExclusionRadius(
            SpawnProtectionConfig.HARD_MAXIMUM_RADIUS
        ));
    }

    @Test
    void rejectsRadiusBelowHardMinimum() {
        assertThrows(IllegalArgumentException.class, () -> SpawnProtectionApi.validateExclusionRadius(
            SpawnProtectionConfig.HARD_MINIMUM_RADIUS - 1
        ));
    }

    @Test
    void rejectsRadiusAboveHardMaximum() {
        assertThrows(IllegalArgumentException.class, () -> SpawnProtectionApi.validateExclusionRadius(
            SpawnProtectionConfig.HARD_MAXIMUM_RADIUS + 1
        ));
    }
}
