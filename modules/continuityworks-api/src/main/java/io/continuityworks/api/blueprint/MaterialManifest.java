package io.continuityworks.api.blueprint;

import java.util.Map;
import java.util.UUID;

public record MaterialManifest(UUID blueprintId, Map<String, Long> required, Map<String, Long> available, Map<String, Long> missing) {
    public MaterialManifest {
        if (blueprintId == null) throw new NullPointerException("blueprintId");
        required = normalized(required);
        available = normalized(available);
        missing = normalized(missing);
    }

    private static Map<String, Long> normalized(Map<String, Long> source) {
        Map<String, Long> value = Map.copyOf(source == null ? Map.of() : source);
        if (value.values().stream().anyMatch(count -> count == null || count < 0)) {
            throw new IllegalArgumentException("Material counts must be non-negative");
        }
        return value;
    }
}
