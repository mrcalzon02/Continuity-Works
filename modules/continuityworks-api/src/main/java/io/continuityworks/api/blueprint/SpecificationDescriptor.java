package io.continuityworks.api.blueprint;

import java.util.Set;

public record SpecificationDescriptor(
    String key,
    Set<String> allowedValues,
    boolean openValue,
    String defaultValue,
    String description
) {
    public SpecificationDescriptor {
        if (key == null || key.isBlank()) throw new IllegalArgumentException("key must not be blank");
        allowedValues = Set.copyOf(allowedValues == null ? Set.of() : allowedValues);
        defaultValue = defaultValue == null ? "" : defaultValue;
        description = description == null ? "" : description;
    }
}
