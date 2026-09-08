package io.continuityworks.api.blueprint;

import java.util.Locale;
import java.util.Objects;

/**
 * Open semantic planning instruction. Keys and values are intentionally not enums so
 * new structure vocabularies can be added without changing the Java ABI.
 */
public record BlueprintSpecification(String key, String value, Requirement requirement) {
    public enum Requirement { REQUIRED, PREFERRED, AVOID }

    public BlueprintSpecification {
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(value, "value");
        requirement = requirement == null ? Requirement.PREFERRED : requirement;
        key = normalize(key);
        value = value.trim();
        if (key.isEmpty()) throw new IllegalArgumentException("specification key must not be blank");
        if (value.isEmpty()) throw new IllegalArgumentException("specification value must not be blank");
    }

    private static String normalize(String value) {
        return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
    }
}
