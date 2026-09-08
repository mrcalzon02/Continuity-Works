package io.continuityworks.api.blueprint;

import java.util.Objects;

public record ClaimConstraint(Bounds bounds, Access access, String source) {
    public enum Access { BUILD_ALLOWED, BUILD_DENIED, OWNER_APPROVAL_REQUIRED }

    public ClaimConstraint {
        Objects.requireNonNull(bounds, "bounds");
        Objects.requireNonNull(access, "access");
        source = source == null ? "unknown" : source;
    }
}
