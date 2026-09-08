package io.continuityworks.api.blueprint;

import java.util.Objects;

public record Bounds(BlockPosition min, BlockPosition max) {
    public Bounds {
        Objects.requireNonNull(min, "min");
        Objects.requireNonNull(max, "max");
        if (min.x() > max.x() || min.y() > max.y() || min.z() > max.z()) {
            throw new IllegalArgumentException("Bounds min must not exceed max");
        }
    }

    public int width() { return max.x() - min.x() + 1; }
    public int height() { return max.y() - min.y() + 1; }
    public int depth() { return max.z() - min.z() + 1; }

    public boolean contains(BlockPosition pos) {
        return pos.x() >= min.x() && pos.x() <= max.x()
            && pos.y() >= min.y() && pos.y() <= max.y()
            && pos.z() >= min.z() && pos.z() <= max.z();
    }
}
