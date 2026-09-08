package io.continuityworks.api.blueprint;

import java.util.Objects;
import java.util.Set;

public record MaterialAvailability(String materialId, long availableCount, Set<String> tags) {
    public MaterialAvailability {
        Objects.requireNonNull(materialId, "materialId");
        if (materialId.isBlank()) throw new IllegalArgumentException("materialId must not be blank");
        if (availableCount < 0) throw new IllegalArgumentException("availableCount must be non-negative");
        tags = Set.copyOf(tags == null ? Set.of() : tags);
    }
}
