package io.continuityworks.spawnprotection.model;

import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.AABB;

/** Inclusive block-space bounding box used by the reservation gate. */
public record BlockBox(int minX, int minY, int minZ, int maxX, int maxY, int maxZ) {
    public BlockBox {
        if (minX > maxX || minY > maxY || minZ > maxZ) {
            throw new IllegalArgumentException("Invalid block box");
        }
    }

    public static BlockBox from(BoundingBox box) {
        return new BlockBox(box.minX(), box.minY(), box.minZ(), box.maxX(), box.maxY(), box.maxZ());
    }

    public static BlockBox from(AABB box) {
        return new BlockBox(
            (int) Math.floor(box.minX),
            (int) Math.floor(box.minY),
            (int) Math.floor(box.minZ),
            (int) Math.ceil(box.maxX) - 1,
            (int) Math.ceil(box.maxY) - 1,
            (int) Math.ceil(box.maxZ) - 1
        );
    }

    /** True for occupied-volume overlap. Ordinary face adjacency is allowed. */
    public boolean overlapsVolume(BlockBox other, int padding) {
        if (padding < 0) {
            throw new IllegalArgumentException("padding must be non-negative");
        }
        return (long) minX - padding < (long) other.maxX + 1L
            && (long) maxX + 1L + padding > other.minX
            && (long) minY - padding < (long) other.maxY + 1L
            && (long) maxY + 1L + padding > other.minY
            && (long) minZ - padding < (long) other.maxZ + 1L
            && (long) maxZ + 1L + padding > other.minZ;
    }

    /** Euclidean edge-to-edge X/Z distance between half-open horizontal footprints. */
    public double horizontalGap(BlockBox other) {
        long dx = Math.max(0L, Math.max(
            (long) other.minX - ((long) maxX + 1L),
            (long) minX - ((long) other.maxX + 1L)
        ));
        long dz = Math.max(0L, Math.max(
            (long) other.minZ - ((long) maxZ + 1L),
            (long) minZ - ((long) other.maxZ + 1L)
        ));
        return Math.hypot((double) dx, (double) dz);
    }

    public String compactKey() {
        return minX + "," + minY + "," + minZ + ":" + maxX + "," + maxY + "," + maxZ;
    }
}
