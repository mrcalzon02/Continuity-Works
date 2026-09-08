package io.continuityworks.api.blueprint;

import java.util.Objects;

/**
 * Fully resolved semantic edit request. It contains only bounded plan-level transforms;
 * raw block placement and raw primitive geometry are intentionally not representable.
 */
public record CompactEditIntent(
    Action action,
    BlockPosition offset,
    CompactBlueprintModifier.Rotation rotation,
    CompactBlueprintModifier.MirrorAxis mirrorAxis,
    String fromPaletteKey,
    String toPaletteKey,
    String moduleId,
    int repeatCount,
    BlockPosition step
) {
    public enum Action { TRANSLATE, ROTATE, MIRROR, PALETTE_REMAP, COMPOSE, REPEAT }

    private static final BlockPosition ZERO = new BlockPosition(0, 0, 0);

    public CompactEditIntent {
        Objects.requireNonNull(action, "action");
        offset = offset == null ? ZERO : offset;
        step = step == null ? ZERO : step;
        fromPaletteKey = fromPaletteKey == null ? "" : fromPaletteKey.trim();
        toPaletteKey = toPaletteKey == null ? "" : toPaletteKey.trim();
        moduleId = moduleId == null ? "" : moduleId.trim();

        switch (action) {
            case TRANSLATE -> {
                requireNull(rotation, "rotation");
                requireNull(mirrorAxis, "mirrorAxis");
                requireBlank(fromPaletteKey, "fromPaletteKey");
                requireBlank(toPaletteKey, "toPaletteKey");
                requireBlank(moduleId, "moduleId");
                requireZero(repeatCount, "repeatCount");
                requireZero(step, "step");
            }
            case ROTATE -> {
                Objects.requireNonNull(rotation, "rotation");
                if (rotation == CompactBlueprintModifier.Rotation.NONE) {
                    throw new IllegalArgumentException("ROTATE intent must change orientation");
                }
                requireNull(mirrorAxis, "mirrorAxis");
                requireBlank(fromPaletteKey, "fromPaletteKey");
                requireBlank(toPaletteKey, "toPaletteKey");
                requireBlank(moduleId, "moduleId");
                requireZero(repeatCount, "repeatCount");
                requireZero(offset, "offset");
                requireZero(step, "step");
            }
            case MIRROR -> {
                requireNull(rotation, "rotation");
                Objects.requireNonNull(mirrorAxis, "mirrorAxis");
                requireBlank(fromPaletteKey, "fromPaletteKey");
                requireBlank(toPaletteKey, "toPaletteKey");
                requireBlank(moduleId, "moduleId");
                requireZero(repeatCount, "repeatCount");
                requireZero(offset, "offset");
                requireZero(step, "step");
            }
            case PALETTE_REMAP -> {
                requireNull(rotation, "rotation");
                requireNull(mirrorAxis, "mirrorAxis");
                if (fromPaletteKey.isBlank() || toPaletteKey.isBlank()) {
                    throw new IllegalArgumentException("PALETTE_REMAP requires FROM and TO palette keys");
                }
                if (fromPaletteKey.equalsIgnoreCase(toPaletteKey)) {
                    throw new IllegalArgumentException("PALETTE_REMAP FROM and TO must differ");
                }
                requireBlank(moduleId, "moduleId");
                requireZero(repeatCount, "repeatCount");
                requireZero(offset, "offset");
                requireZero(step, "step");
            }
            case COMPOSE -> {
                requireNull(rotation, "rotation");
                requireNull(mirrorAxis, "mirrorAxis");
                requireBlank(fromPaletteKey, "fromPaletteKey");
                requireBlank(toPaletteKey, "toPaletteKey");
                if (moduleId.isBlank()) throw new IllegalArgumentException("COMPOSE requires MODULE");
                requireZero(repeatCount, "repeatCount");
                requireZero(step, "step");
            }
            case REPEAT -> {
                requireNull(rotation, "rotation");
                requireNull(mirrorAxis, "mirrorAxis");
                requireBlank(fromPaletteKey, "fromPaletteKey");
                requireBlank(toPaletteKey, "toPaletteKey");
                if (moduleId.isBlank()) throw new IllegalArgumentException("REPEAT requires MODULE");
                if (repeatCount < 1 || repeatCount > CompactBlueprintModifier.MAX_REPEAT_COPIES) {
                    throw new IllegalArgumentException("REPEAT count must be between 1 and " + CompactBlueprintModifier.MAX_REPEAT_COPIES);
                }
                if (repeatCount > 1 && isZero(step)) {
                    throw new IllegalArgumentException("REPEAT with multiple copies requires a non-zero STEP vector");
                }
            }
        }
    }

    public static CompactEditIntent translate(BlockPosition delta) {
        return new CompactEditIntent(Action.TRANSLATE, delta, null, null, "", "", "", 0, ZERO);
    }

    public static CompactEditIntent rotate(CompactBlueprintModifier.Rotation rotation) {
        return new CompactEditIntent(Action.ROTATE, ZERO, rotation, null, "", "", "", 0, ZERO);
    }

    public static CompactEditIntent mirror(CompactBlueprintModifier.MirrorAxis axis) {
        return new CompactEditIntent(Action.MIRROR, ZERO, null, axis, "", "", "", 0, ZERO);
    }

    public static CompactEditIntent paletteRemap(String from, String to) {
        return new CompactEditIntent(Action.PALETTE_REMAP, ZERO, null, null, from, to, "", 0, ZERO);
    }

    public static CompactEditIntent compose(String moduleId, BlockPosition offset) {
        return new CompactEditIntent(Action.COMPOSE, offset, null, null, "", "", moduleId, 0, ZERO);
    }

    public static CompactEditIntent repeat(String moduleId, int count, BlockPosition firstOffset, BlockPosition step) {
        return new CompactEditIntent(Action.REPEAT, firstOffset, null, null, "", "", moduleId, count, step);
    }

    private static void requireNull(Object value, String name) {
        if (value != null) throw new IllegalArgumentException(name + " is not valid for this edit action");
    }

    private static void requireBlank(String value, String name) {
        if (!value.isBlank()) throw new IllegalArgumentException(name + " is not valid for this edit action");
    }

    private static void requireZero(int value, String name) {
        if (value != 0) throw new IllegalArgumentException(name + " is not valid for this edit action");
    }

    private static void requireZero(BlockPosition value, String name) {
        if (!isZero(value)) throw new IllegalArgumentException(name + " is not valid for this edit action");
    }

    private static boolean isZero(BlockPosition value) {
        return value.x() == 0 && value.y() == 0 && value.z() == 0;
    }
}
