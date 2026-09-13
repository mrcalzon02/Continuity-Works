package io.continuityworks.spawnprotection.model;

import net.minecraft.world.phys.AABB;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

final class BlockBoxTest {
    @Test
    void aabbExclusiveMaximumCanRepresentIntegerMaxValueBlock() {
        AABB box = new AABB(
            Integer.MAX_VALUE, 64.0D, 0.0D,
            (double) Integer.MAX_VALUE + 1.0D, 65.0D, 1.0D
        );

        BlockBox blockBox = BlockBox.from(box);

        assertEquals(Integer.MAX_VALUE, blockBox.minX());
        assertEquals(Integer.MAX_VALUE, blockBox.maxX());
    }

    @Test
    void nonFiniteAabbCoordinatesFailClosed() {
        AABB box = new AABB(0.0D, 0.0D, 0.0D, Double.POSITIVE_INFINITY, 1.0D, 1.0D);

        assertThrows(IllegalArgumentException.class, () -> BlockBox.from(box));
    }

    @Test
    void outOfRangeAabbCoordinatesFailClosedInsteadOfSaturating() {
        double firstUnsupportedBlock = (double) Integer.MAX_VALUE + 1.0D;
        AABB box = new AABB(
            firstUnsupportedBlock, 0.0D, 0.0D,
            firstUnsupportedBlock + 1.0D, 1.0D, 1.0D
        );

        assertThrows(IllegalArgumentException.class, () -> BlockBox.from(box));
    }
}
