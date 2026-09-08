package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

public record BlueprintContext(
    UUID validationId,
    long snapshotEpoch,
    String dimensionId,
    BlockPosition origin,
    Facing facing,
    Bounds scannedBounds,
    List<ObservedBlock> observedBlocks,
    Set<ChunkPosition> loadedChunks,
    List<ClaimConstraint> claimConstraints,
    Map<String, Long> inventoryCounts,
    Map<String, String> attributes
) {
    public BlueprintContext {
        Objects.requireNonNull(validationId, "validationId");
        Objects.requireNonNull(dimensionId, "dimensionId");
        Objects.requireNonNull(origin, "origin");
        Objects.requireNonNull(facing, "facing");
        Objects.requireNonNull(scannedBounds, "scannedBounds");
        observedBlocks = List.copyOf(observedBlocks == null ? List.of() : observedBlocks);
        loadedChunks = Set.copyOf(loadedChunks == null ? Set.of() : loadedChunks);
        claimConstraints = List.copyOf(claimConstraints == null ? List.of() : claimConstraints);
        inventoryCounts = Map.copyOf(inventoryCounts == null ? Map.of() : inventoryCounts);
        attributes = Map.copyOf(attributes == null ? Map.of() : attributes);
    }
}
