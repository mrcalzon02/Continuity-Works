package io.continuityworks.spawnprotection.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
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

    @Test
    void missingNumericFieldFailsClosedInsteadOfDefaultingToZero() {
        CompoundTag root = new CompoundTag();
        ListTag reservations = new ListTag();
        CompoundTag corrupt = new CompoundTag();
        corrupt.putString("id", "reservation-a");
        corrupt.putString("structure", "continuity_works:test_structure");
        corrupt.putString("assembly", "assembly-a");
        corrupt.putString("family", "continuity_works:test_family");
        corrupt.putInt("radius", 500);
        corrupt.putInt("minX", 0);
        corrupt.putInt("minY", 64);
        corrupt.putInt("minZ", 0);
        corrupt.putInt("maxX", 15);
        corrupt.putInt("maxY", 79);
        reservations.add(corrupt);
        root.put("reservations", reservations);

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }

    @Test
    void belowMinimumPersistedRadiusFailsClosedInsteadOfBeingClamped() {
        CompoundTag root = new CompoundTag();
        ListTag reservations = new ListTag();
        CompoundTag corrupt = validReservationTag(499);
        reservations.add(corrupt);
        root.put("reservations", reservations);

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }

    @Test
    void aboveMaximumPersistedRadiusFailsClosedBeforeSpatialIndexing() {
        CompoundTag root = new CompoundTag();
        ListTag reservations = new ListTag();
        CompoundTag corrupt = validReservationTag(32769);
        reservations.add(corrupt);
        root.put("reservations", reservations);

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }

    @Test
    void nonListReservationsCollectionFailsClosed() {
        CompoundTag root = new CompoundTag();
        root.putString("reservations", "not-a-list");

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }

    @Test
    void nonCompoundReservationsListFailsClosed() {
        CompoundTag root = new CompoundTag();
        ListTag reservations = new ListTag();
        reservations.add(StringTag.valueOf("not-a-compound"));
        root.put("reservations", reservations);

        assertThrows(IllegalStateException.class, () -> SpawnProtectionSavedData.load(root));
    }

    @Test
    void missingReservationsCollectionRemainsValidForFreshSavedData() {
        assertDoesNotThrow(() -> SpawnProtectionSavedData.load(new CompoundTag()));
    }

    private static CompoundTag validReservationTag(int radius) {
        CompoundTag tag = new CompoundTag();
        tag.putString("id", "reservation-a");
        tag.putString("structure", "continuity_works:test_structure");
        tag.putString("assembly", "assembly-a");
        tag.putString("family", "continuity_works:test_family");
        tag.putInt("radius", radius);
        tag.putInt("minX", 0);
        tag.putInt("minY", 64);
        tag.putInt("minZ", 0);
        tag.putInt("maxX", 15);
        tag.putInt("maxY", 79);
        tag.putInt("maxZ", 15);
        return tag;
    }
}
