package io.continuityworks.api.blueprint;

import java.util.Objects;

public record SpecificationResolution(
    String key,
    String requestedValue,
    String resolvedValue,
    Status status,
    String detail
) {
    public enum Status { APPLIED, DEFAULTED, UNSUPPORTED, CONFLICT }

    public SpecificationResolution {
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(requestedValue, "requestedValue");
        Objects.requireNonNull(status, "status");
        resolvedValue = resolvedValue == null ? "" : resolvedValue;
        detail = detail == null ? "" : detail;
    }
}
