package io.continuityworks.spawnprotection.data;

import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.List;

/** Per-dimension persistence for committed reservation geometry. */
public final class SpawnProtectionSavedData extends SavedData {
    private static final String DATA_NAME = "continuityworks_structure_spawn_protection";
    private List<Reservation> reservations = new ArrayList<>();

    public static SpawnProtectionSavedData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(
            SpawnProtectionSavedData::load,
            SpawnProtectionSavedData::new,
            DATA_NAME
        );
    }

    public static SpawnProtectionSavedData load(CompoundTag root) {
        SpawnProtectionSavedData data = new SpawnProtectionSavedData();
        ListTag list = root.getList("reservations", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag tag = list.getCompound(i);
            try {
                BlockBox box = new BlockBox(
                    tag.getInt("minX"), tag.getInt("minY"), tag.getInt("minZ"),
                    tag.getInt("maxX"), tag.getInt("maxY"), tag.getInt("maxZ")
                );
                data.reservations.add(new Reservation(
                    tag.getString("id"),
                    new ResourceLocation(tag.getString("structure")),
                    tag.getString("assembly"),
                    new ResourceLocation(tag.getString("family")),
                    box,
                    Math.max(500, tag.getInt("radius")),
                    tag.contains("piece") ? tag.getString("piece") : null,
                    false
                ));
            } catch (RuntimeException ignored) {
                // Corrupt entries are skipped instead of weakening valid reservations.
            }
        }
        return data;
    }

    public List<Reservation> reservations() {
        return List.copyOf(reservations);
    }

    public void replaceReservations(List<Reservation> reservations) {
        this.reservations = new ArrayList<>(reservations);
        setDirty();
    }

    @Override
    public CompoundTag save(CompoundTag root) {
        ListTag list = new ListTag();
        for (Reservation reservation : reservations) {
            CompoundTag tag = new CompoundTag();
            tag.putString("id", reservation.reservationId());
            tag.putString("structure", reservation.structureId().toString());
            tag.putString("assembly", reservation.assemblyId());
            tag.putString("family", reservation.familyId().toString());
            tag.putInt("radius", reservation.exclusionRadius());
            if (reservation.pieceId() != null) tag.putString("piece", reservation.pieceId());
            BlockBox box = reservation.box();
            tag.putInt("minX", box.minX());
            tag.putInt("minY", box.minY());
            tag.putInt("minZ", box.minZ());
            tag.putInt("maxX", box.maxX());
            tag.putInt("maxY", box.maxY());
            tag.putInt("maxZ", box.maxZ());
            list.add(tag);
        }
        root.put("reservations", list);
        return root;
    }
}
