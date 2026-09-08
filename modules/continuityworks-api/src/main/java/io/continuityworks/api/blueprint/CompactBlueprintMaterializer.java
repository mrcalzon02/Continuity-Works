package io.continuityworks.api.blueprint;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Deterministic zero-retention primitive expansion. Ordered overlaps use later-write-wins world semantics. */
public final class CompactBlueprintMaterializer {
    public static final long MAX_STREAM_OPERATIONS = 1_048_576L;

    private CompactBlueprintMaterializer() {}

    public static long forEachPlacement(CompactBlueprintPlan plan, CompactPlacementSink sink) {
        Objects.requireNonNull(plan, "plan");
        return forEachPlacement(plan.primitives(), sink);
    }

    public static long forEachPlacement(List<CompactBlueprintPrimitive> primitives, CompactPlacementSink sink) {
        return forEachPlacement(primitives, sink, MAX_STREAM_OPERATIONS);
    }

    public static long forEachPlacement(List<CompactBlueprintPrimitive> primitives, CompactPlacementSink sink, long maxOperations) {
        Objects.requireNonNull(primitives, "primitives");
        Objects.requireNonNull(sink, "sink");
        if (maxOperations < 0L || maxOperations > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("maxOperations must be between 0 and Integer.MAX_VALUE");
        }
        Counter counter = new Counter(maxOperations);
        for (CompactBlueprintPrimitive primitive : primitives) {
            if (!emit(Objects.requireNonNull(primitive, "primitive"), sink, counter)) break;
        }
        return counter.value;
    }

    public static List<PlacementOperation> materialize(CompactBlueprintPlan plan, int maxOperations) {
        if (maxOperations < 0) throw new IllegalArgumentException("maxOperations must be non-negative");
        ArrayList<PlacementOperation> operations = new ArrayList<>(Math.min(maxOperations, 8192));
        forEachPlacement(plan.primitives(), (sequence, kind, position, paletteKey) -> {
            operations.add(new PlacementOperation(sequence, kind, position, paletteKey));
            return true;
        }, maxOperations);
        return List.copyOf(operations);
    }

    private static boolean emit(CompactBlueprintPrimitive primitive, CompactPlacementSink sink, Counter counter) {
        return switch (primitive.kind()) {
            case BLOCK -> one(primitive.from(), primitive.paletteKey(), primitive.operationKind(), sink, counter);
            case LINE -> line(primitive, sink, counter);
            case FILL_BOX -> box(primitive, false, sink, counter);
            case HOLLOW_BOX -> box(primitive, true, sink, counter);
            case CYLINDER -> cylinder(primitive, sink, counter);
        };
    }

    private static boolean one(BlockPosition position, String paletteKey, PlacementOperation.Kind currentKind, CompactPlacementSink sink, Counter counter) {
        if (counter.value >= counter.limit) {
            throw new IllegalArgumentException("Compact blueprint exceeds streaming limit of " + counter.limit + " operations");
        }
        boolean keepGoing = sink.accept((int)counter.value, currentKind, position, paletteKey);
        counter.value++;
        return keepGoing;
    }

    private static boolean box(CompactBlueprintPrimitive p, boolean hollow, CompactPlacementSink sink, Counter counter) {
        BlockPosition a = p.from(), b = p.to();
        for (long x = a.x(); x <= b.x(); x++) {
            for (long y = a.y(); y <= b.y(); y++) {
                for (long z = a.z(); z <= b.z(); z++) {
                    if (hollow && x != a.x() && x != b.x() && y != a.y() && y != b.y() && z != a.z() && z != b.z()) continue;
                    if (!one(new BlockPosition((int)x, (int)y, (int)z), p.paletteKey(), p.operationKind(), sink, counter)) return false;
                }
            }
        }
        return true;
    }

    private static boolean line(CompactBlueprintPrimitive p, CompactPlacementSink sink, Counter counter) {
        BlockPosition a = p.from(), b = p.to();
        long dx = (long)b.x() - a.x(), dy = (long)b.y() - a.y(), dz = (long)b.z() - a.z();
        long n = Math.max(Math.abs(dx), Math.max(Math.abs(dy), Math.abs(dz)));
        if (n == 0L) return one(a, p.paletteKey(), p.operationKind(), sink, counter);
        if (n + 1L > counter.remaining()) {
            throw new IllegalArgumentException("LINE primitive exceeds remaining compact streaming budget");
        }
        for (long i = 0L; i <= n; i++) {
            double t = (double)i / (double)n;
            BlockPosition pos = new BlockPosition(
                Math.toIntExact(Math.round(a.x() + dx * t)),
                Math.toIntExact(Math.round(a.y() + dy * t)),
                Math.toIntExact(Math.round(a.z() + dz * t))
            );
            if (!one(pos, p.paletteKey(), p.operationKind(), sink, counter)) return false;
        }
        return true;
    }

    private static boolean cylinder(CompactBlueprintPrimitive p, CompactPlacementSink sink, Counter counter) {
        long cx = p.from().x(), cz = p.from().z(), r = p.radius();
        long y0 = p.from().y(), y1 = p.to().y();
        long minX = Math.subtractExact(cx, r), maxX = Math.addExact(cx, r);
        long minZ = Math.subtractExact(cz, r), maxZ = Math.addExact(cz, r);
        if (minX < Integer.MIN_VALUE || maxX > Integer.MAX_VALUE || minZ < Integer.MIN_VALUE || maxZ > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("CYLINDER primitive exceeds integer coordinate range");
        }
        long radiusSquared = r * r;
        for (long x = minX; x <= maxX; x++) {
            for (long z = minZ; z <= maxZ; z++) {
                long dx = x - cx, dz = z - cz;
                if (dx * dx + dz * dz > radiusSquared) continue;
                boolean edge = outside(x + 1L, z, cx, cz, radiusSquared)
                    || outside(x - 1L, z, cx, cz, radiusSquared)
                    || outside(x, z + 1L, cx, cz, radiusSquared)
                    || outside(x, z - 1L, cx, cz, radiusSquared);
                for (long y = y0; y <= y1; y++) {
                    if (!p.solid() && !edge && !(p.caps() && (y == y0 || y == y1))) continue;
                    if (!one(new BlockPosition((int)x, (int)y, (int)z), p.paletteKey(), p.operationKind(), sink, counter)) return false;
                }
            }
        }
        return true;
    }

    private static boolean outside(long x, long z, long cx, long cz, long radiusSquared) {
        long dx = x - cx, dz = z - cz;
        return dx * dx + dz * dz > radiusSquared;
    }

    private static final class Counter {
        private final long limit;
        private long value;
        private Counter(long limit) { this.limit = limit; }
        private long remaining() { return limit - value; }
    }
}
