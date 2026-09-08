package io.continuityworks.api.blueprint;

import java.util.Objects;

public record MaterialIssue(String materialId, Kind kind, long required, long available, String detail) {
    public enum Kind { MISSING, UNSUPPORTED, SUBSTITUTED }

    public MaterialIssue {
        Objects.requireNonNull(materialId, "materialId");
        Objects.requireNonNull(kind, "kind");
        detail = detail == null ? "" : detail;
        if (required < 0 || available < 0) throw new IllegalArgumentException("Material counts must be non-negative");
    }
}
