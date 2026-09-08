package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Objects;

/** Reusable compact primitive fragment. Palette keys are resolved by the receiving plan. */
public record CompactBlueprintModule(String moduleId, List<CompactBlueprintPrimitive> primitives) {
    public CompactBlueprintModule {
        Objects.requireNonNull(moduleId, "moduleId");
        if (moduleId.isBlank()) throw new IllegalArgumentException("moduleId must not be blank");
        primitives = List.copyOf(primitives == null ? List.of() : primitives);
        if (primitives.isEmpty()) throw new IllegalArgumentException("module must contain at least one primitive");
        for (int i = 0; i < primitives.size(); i++) {
            CompactBlueprintPrimitive primitive = Objects.requireNonNull(primitives.get(i), "primitive");
            if (primitive.sequence() != i) {
                throw new IllegalArgumentException("module primitive sequence must be contiguous from zero");
            }
        }
    }
}
