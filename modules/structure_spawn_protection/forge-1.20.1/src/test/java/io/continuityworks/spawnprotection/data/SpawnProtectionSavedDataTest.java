package io.continuityworks.spawnprotection.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertThrows;

final class SpawnProtectionSavedDataTest {
    @Test
    void malformedPersistedReservationFailsClosedInsteadOfBeingDropped() {
        CompoundTag root = new CompoundTag();
        ListTag reservations = new ListTag();
        CompoundTag corrupt = new CompoundTag();
        corrupt.putString("structure", "continuity_works:test_structure");
        corrupt.putString("assembly", "assembly-a");
        corrupt.putString("family", "continuity_works:test_family");
        corrupt.putInt("radius", 500);
        corrupt.putInt("minX", 0);
        corrupt.putInt("minY", 64);
        corrupt.putInt("minZ", 0);
        corrupt.putInt("maxX", 15);
        corrupt.putInt("maxY", 79);
        corrupt.putInt("maxZ", 15);
        reservations.add(corrupt);
        root.put("reservations", reservations);

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }
}
