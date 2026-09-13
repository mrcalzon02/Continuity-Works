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
            floorCoordinate(box.minX, "minX"),
            floorCoordinate(box.minY, "minY"),
            floorCoordinate(box.minZ, "minZ"),
            exclusiveMaxCoordinate(box.maxX, "maxX"),
            exclusiveMaxCoordinate(box.maxY, "maxY"),
            exclusiveMaxCoordinate(box.maxZ, "maxZ")
        );
    }

    private static int floorCoordinate(double value, String name) {
        requireFinite(value, name);
        double floored = Math.floor(value);
        if (floored < Integer.MIN_VALUE || floored > Integer.MAX_VALUE) {
            throw new IllegalArgumentException(name + " is outside supported block coordinates: " + value);
        }
        return (int) floored;
    }

    private static int exclusiveMaxCoordinate(double value, String name) {
        requireFinite(value, name);
        double inclusive = Math.ceil(value) - 1.0D;
        if (inclusive < Integer.MIN_VALUE || inclusive > Integer.MAX_VALUE) {
            throw new IllegalArgumentException(name + " is outside supported block coordinates: " + value);
        }
        return (int) inclusive;
    }

    private static void requireFinite(double value, String name) {
        if (!Double.isFinite(value)) {
            throw new IllegalArgumentException(name + " must be finite: " + value);
        }
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
