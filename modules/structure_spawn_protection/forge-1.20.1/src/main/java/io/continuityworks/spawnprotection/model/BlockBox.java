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
        return minX - padding < other.maxX + 1
            && maxX + 1 + padding > other.minX
            && minY - padding < other.maxY + 1
            && maxY + 1 + padding > other.minY
            && minZ - padding < other.maxZ + 1
            && maxZ + 1 + padding > other.minZ;
    }

    /** Euclidean edge-to-edge X/Z distance between half-open horizontal footprints. */
    public double horizontalGap(BlockBox other) {
        int dx = Math.max(0, Math.max(other.minX - (maxX + 1), minX - (other.maxX + 1)));
        int dz = Math.max(0, Math.max(other.minZ - (maxZ + 1), minZ - (other.maxZ + 1)));
        return Math.hypot(dx, dz);
    }

    public String compactKey() {
        return minX + "," + minY + "," + minZ + ":" + maxX + "," + maxY + "," + maxZ;
    }
}
