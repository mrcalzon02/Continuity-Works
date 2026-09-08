package io.continuityworks.api.blueprint;

import java.util.Objects;

public record PlacementOperation(int sequence, Kind kind, BlockPosition relativePosition, String paletteKey) {
    public enum Kind { PLACE, CLEAR, REPLACE }

    public PlacementOperation {
        if (sequence < 0) throw new IllegalArgumentException("sequence must be non-negative");
        Objects.requireNonNull(kind, "kind");
        Objects.requireNonNull(relativePosition, "relativePosition");
        if (kind != Kind.CLEAR) {
            Objects.requireNonNull(paletteKey, "paletteKey");
            if (paletteKey.isBlank()) throw new IllegalArgumentException("paletteKey must not be blank");
        }
    }
}
