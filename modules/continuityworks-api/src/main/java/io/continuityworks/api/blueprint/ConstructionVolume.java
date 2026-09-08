package io.continuityworks.api.blueprint;

import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/**
 * Exact server-selected world volume offered to Continuity Works for planning.
 * Version 1 uses a hard boundary: every proposed world-space operation must remain inside it.
 */
public record ConstructionVolume(
    UUID volumeId,
    Bounds bounds,
    long snapshotEpoch,
    Map<String, String> attributes
) {
    public ConstructionVolume {
        Objects.requireNonNull(volumeId, "volumeId");
        Objects.requireNonNull(bounds, "bounds");
        attributes = Map.copyOf(attributes == null ? Map.of() : attributes);
    }

    public boolean contains(BlockPosition position) {
        return bounds.contains(position);
    }
}
