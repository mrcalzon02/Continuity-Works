package io.continuityworks.api.blueprint;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Deterministic zero-retention primitive expansion. Ordered overlaps use later-write-wins world semantics. */
public final class CompactBlueprintMaterializer {
    private CompactBlueprintMaterializer() {}

    public static long forEachPlacement(CompactBlueprintPlan plan, CompactPlacementSink sink) {
        Objects.requireNonNull(plan, "plan");
        Objects.requireNonNull(sink, "sink");
        Counter counter = new Counter();
        for (CompactBlueprintPrimitive primitive : plan.primitives()) {
            if (!emit(primitive, sink, counter)) break;
        }
        return counter.value;
    }

    public static List<PlacementOperation> materialize(CompactBlueprintPlan plan, int maxOperations) {
        if (maxOperations < 0) throw new IllegalArgumentException("maxOperations must be non-negative");
        ArrayList<PlacementOperation> operations = new ArrayList<>(Math.min(maxOperations, 8192));
        forEachPlacement(plan, (sequence, kind, position, paletteKey) -> {
            if (operations.size() >= maxOperations) throw new IllegalArgumentException("Compact blueprint exceeds materialization limit of " + maxOperations + " operations");
            operations.add(new PlacementOperation(sequence, kind, position, paletteKey));
            return true;
        });
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
        if (counter.value > Integer.MAX_VALUE) throw new IllegalArgumentException("Placement sequence exceeds integer range");
        boolean keepGoing = sink.accept((int)counter.value, currentKind, position, paletteKey);
        counter.value++;
        return keepGoing;
    }

    private static boolean box(CompactBlueprintPrimitive p, boolean hollow, CompactPlacementSink sink, Counter counter) {
        BlockPosition a = p.from(), b = p.to();
        for (int x = a.x(); x <= b.x(); x++) for (int y = a.y(); y <= b.y(); y++) for (int z = a.z(); z <= b.z(); z++) {
            if (hollow && x != a.x() && x != b.x() && y != a.y() && y != b.y() && z != a.z() && z != b.z()) continue;
            if (!one(new BlockPosition(x, y, z), p.paletteKey(), p.operationKind(), sink, counter)) return false;
        }
        return true;
    }

    private static boolean line(CompactBlueprintPrimitive p, CompactPlacementSink sink, Counter counter) {
        BlockPosition a = p.from(), b = p.to();
        int dx = b.x() - a.x(), dy = b.y() - a.y(), dz = b.z() - a.z();
        int n = Math.max(Math.abs(dx), Math.max(Math.abs(dy), Math.abs(dz)));
        if (n == 0) return one(a, p.paletteKey(), p.operationKind(), sink, counter);
        for (int i = 0; i <= n; i++) {
            double t = (double)i / n;
            BlockPosition pos = new BlockPosition(
                (int)Math.round(a.x() + dx * t),
                (int)Math.round(a.y() + dy * t),
                (int)Math.round(a.z() + dz * t)
            );
            if (!one(pos, p.paletteKey(), p.operationKind(), sink, counter)) return false;
        }
        return true;
    }

    private static boolean cylinder(CompactBlueprintPrimitive p, CompactPlacementSink sink, Counter counter) {
        int cx = p.from().x(), cz = p.from().z(), r = p.radius();
        int y0 = p.from().y(), y1 = p.to().y();
        for (int x = cx - r; x <= cx + r; x++) for (int z = cz - r; z <= cz + r; z++) {
            long dx = (long)x - cx, dz = (long)z - cz;
            if (dx * dx + dz * dz > (long)r * r) continue;
            boolean edge = outside(x + 1, z, cx, cz, r) || outside(x - 1, z, cx, cz, r)
                || outside(x, z + 1, cx, cz, r) || outside(x, z - 1, cx, cz, r);
            for (int y = y0; y <= y1; y++) {
                if (!p.solid() && !edge && !(p.caps() && (y == y0 || y == y1))) continue;
                if (!one(new BlockPosition(x, y, z), p.paletteKey(), p.operationKind(), sink, counter)) return false;
            }
        }
        return true;
    }

    private static boolean outside(int x, int z, int cx, int cz, int r) {
        long dx = (long)x - cx, dz = (long)z - cz;
        return dx * dx + dz * dz > (long)r * r;
    }

    private static final class Counter { long value; }
}
