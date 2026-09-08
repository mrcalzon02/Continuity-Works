package io.continuityworks.api.blueprint;

import java.util.Objects;
import java.util.UUID;

/**
 * Compact player-owned build-area selection shared across Continuity Works consumers.
 * The selected volume is authoritative planning metadata, not a block snapshot.
 */
public record BuildAreaSelection(
    UUID ownerUuid,
    String dimensionId,
    ConstructionVolume volume
) {
    public BuildAreaSelection {
        Objects.requireNonNull(ownerUuid, "ownerUuid");
        Objects.requireNonNull(dimensionId, "dimensionId");
        Objects.requireNonNull(volume, "volume");
        if (dimensionId.isBlank()) throw new IllegalArgumentException("dimensionId must not be blank");
    }
}
