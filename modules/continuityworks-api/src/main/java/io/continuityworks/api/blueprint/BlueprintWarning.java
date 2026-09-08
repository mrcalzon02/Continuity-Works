package io.continuityworks.api.blueprint;

import java.util.Objects;

public record BlueprintWarning(String code, Severity severity, String message) {
    public enum Severity { INFO, WARNING, ERROR }

    public BlueprintWarning {
        Objects.requireNonNull(code, "code");
        Objects.requireNonNull(severity, "severity");
        message = message == null ? "" : message;
    }
}
