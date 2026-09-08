package io.continuityworks.api.blueprint;

import java.util.Objects;

/** Compact geometric instruction. Coordinates are relative to the plan anchor. */
public record CompactBlueprintPrimitive(
    int sequence,
    Kind kind,
    BlockPosition from,
    BlockPosition to,
    int radius,
    int flags,
    String paletteKey
) {
    public static final int FLAG_SOLID = 1;
    public static final int FLAG_CAPS = 1 << 1;
    private static final int KNOWN_FLAGS = FLAG_SOLID | FLAG_CAPS;

    public enum Kind { BLOCK, LINE, FILL_BOX, HOLLOW_BOX, CYLINDER }

    public CompactBlueprintPrimitive {
        if (sequence < 0) throw new IllegalArgumentException("sequence must be non-negative");
        Objects.requireNonNull(kind, "kind");
        Objects.requireNonNull(from, "from");
        Objects.requireNonNull(to, "to");
        Objects.requireNonNull(paletteKey, "paletteKey");
        if (paletteKey.isBlank()) throw new IllegalArgumentException("paletteKey must not be blank");
        if ((flags & ~KNOWN_FLAGS) != 0) throw new IllegalArgumentException("unknown primitive flags: " + flags);

        switch (kind) {
            case BLOCK -> {
                if (!from.equals(to)) throw new IllegalArgumentException("BLOCK primitive requires from == to");
                if (radius != 0 || flags != 0) throw new IllegalArgumentException("BLOCK primitive does not use radius or flags");
            }
            case LINE -> {
                if (radius != 0 || flags != 0) throw new IllegalArgumentException("LINE primitive does not use radius or flags");
            }
            case FILL_BOX, HOLLOW_BOX -> {
                requireOrdered(from, to, kind.name());
                if (radius != 0 || flags != 0) throw new IllegalArgumentException(kind + " primitive does not use radius or flags");
            }
            case CYLINDER -> {
                if (radius < 1) throw new IllegalArgumentException("CYLINDER radius must be positive");
                if (from.x() != to.x() || from.z() != to.z() || from.y() > to.y()) {
                    throw new IllegalArgumentException("CYLINDER uses from/to as one vertical center axis");
                }
            }
        }
    }

    public static CompactBlueprintPrimitive block(int sequence, BlockPosition position, String paletteKey) {
        return new CompactBlueprintPrimitive(sequence, Kind.BLOCK, position, position, 0, 0, paletteKey);
    }

    public static CompactBlueprintPrimitive line(int sequence, BlockPosition from, BlockPosition to, String paletteKey) {
        return new CompactBlueprintPrimitive(sequence, Kind.LINE, from, to, 0, 0, paletteKey);
    }

    public static CompactBlueprintPrimitive fillBox(int sequence, BlockPosition min, BlockPosition max, String paletteKey) {
        return new CompactBlueprintPrimitive(sequence, Kind.FILL_BOX, min, max, 0, 0, paletteKey);
    }

    public static CompactBlueprintPrimitive hollowBox(int sequence, BlockPosition min, BlockPosition max, String paletteKey) {
        return new CompactBlueprintPrimitive(sequence, Kind.HOLLOW_BOX, min, max, 0, 0, paletteKey);
    }

    public static CompactBlueprintPrimitive cylinder(
        int sequence,
        BlockPosition centerMinY,
        BlockPosition centerMaxY,
        int radius,
        boolean solid,
        boolean caps,
        String paletteKey
    ) {
        int primitiveFlags = (solid ? FLAG_SOLID : 0) | (caps ? FLAG_CAPS : 0);
        return new CompactBlueprintPrimitive(sequence, Kind.CYLINDER, centerMinY, centerMaxY, radius, primitiveFlags, paletteKey);
    }

    public boolean solid() { return (flags & FLAG_SOLID) != 0; }
    public boolean caps() { return (flags & FLAG_CAPS) != 0; }

    public Bounds localBounds() {
        return switch (kind) {
            case BLOCK, FILL_BOX, HOLLOW_BOX -> new Bounds(from, to);
            case LINE -> new Bounds(
                new BlockPosition(Math.min(from.x(), to.x()), Math.min(from.y(), to.y()), Math.min(from.z(), to.z())),
                new BlockPosition(Math.max(from.x(), to.x()), Math.max(from.y(), to.y()), Math.max(from.z(), to.z()))
            );
            case CYLINDER -> new Bounds(
                new BlockPosition(Math.subtractExact(from.x(), radius), from.y(), Math.subtractExact(from.z(), radius)),
                new BlockPosition(Math.addExact(from.x(), radius), to.y(), Math.addExact(from.z(), radius))
            );
        };
    }

    /** Conservative count before overlap/overwrite resolution. */
    public long rawPlacementUpperBound() {
        return switch (kind) {
            case BLOCK -> 1L;
            case LINE -> Math.max(Math.abs((long)to.x() - from.x()),
                Math.max(Math.abs((long)to.y() - from.y()), Math.abs((long)to.z() - from.z()))) + 1L;
            case FILL_BOX -> volume(from, to);
            case HOLLOW_BOX -> hollowVolume(from, to);
            case CYLINDER -> saturatedMultiply(saturatedMultiply(radius * 2L + 1L, radius * 2L + 1L), (long)to.y() - from.y() + 1L);
        };
    }

    private static void requireOrdered(BlockPosition min, BlockPosition max, String label) {
        if (min.x() > max.x() || min.y() > max.y() || min.z() > max.z()) {
            throw new IllegalArgumentException(label + " requires ordered min/max coordinates");
        }
    }

    private static long volume(BlockPosition min, BlockPosition max) {
        long w = (long)max.x() - min.x() + 1L;
        long h = (long)max.y() - min.y() + 1L;
        long d = (long)max.z() - min.z() + 1L;
        return saturatedMultiply(saturatedMultiply(w, h), d);
    }

    private static long hollowVolume(BlockPosition min, BlockPosition max) {
        long outer = volume(min, max);
        long w = (long)max.x() - min.x() + 1L;
        long h = (long)max.y() - min.y() + 1L;
        long d = (long)max.z() - min.z() + 1L;
        if (w <= 2L || h <= 2L || d <= 2L) return outer;
        long inner = saturatedMultiply(saturatedMultiply(w - 2L, h - 2L), d - 2L);
        return outer - inner;
    }

    private static long saturatedMultiply(long a, long b) {
        if (a == 0L || b == 0L) return 0L;
        if (a > Long.MAX_VALUE / b) return Long.MAX_VALUE;
        return a * b;
    }
}
