package io.continuityworks.api.blueprint;

import java.util.List;

public record BlueprintVocabulary(String schemaVersion, List<SpecificationDescriptor> specifications) {
    public BlueprintVocabulary {
        if (schemaVersion == null || schemaVersion.isBlank()) throw new IllegalArgumentException("schemaVersion must not be blank");
        specifications = List.copyOf(specifications == null ? List.of() : specifications);
    }
}
