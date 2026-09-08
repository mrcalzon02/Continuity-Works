package io.continuityworks.api.blueprint;

import java.util.Objects;

public record ProtectedBlockConflict(BlockPosition relativePosition, String observedBlockId, String reason) {
    public ProtectedBlockConflict {
        Objects.requireNonNull(relativePosition, "relativePosition");
        Objects.requireNonNull(observedBlockId, "observedBlockId");
        reason = reason == null ? "protected" : reason;
    }
}
