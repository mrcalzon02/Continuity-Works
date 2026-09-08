package io.continuityworks.api.blueprint;

import java.util.Map;
import java.util.Objects;

public record PaletteEntry(String key, String blockState, String materialId, Map<String, String> metadata) {
    public PaletteEntry {
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(blockState, "blockState");
        Objects.requireNonNull(materialId, "materialId");
        if (key.isBlank() || blockState.isBlank() || materialId.isBlank()) {
            throw new IllegalArgumentException("Palette key, blockState and materialId must not be blank");
        }
        metadata = Map.copyOf(metadata == null ? Map.of() : metadata);
    }
}
