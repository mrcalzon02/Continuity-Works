package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

public record BlueprintRequest(
    UUID requestId,
    UUID companionUuid,
    UUID ownerUuid,
    String dimensionId,
    String buildPurpose,
    BlockPosition preferredOrigin,
    Facing preferredFacing,
    Bounds maximumBounds,
    List<MaterialAvailability> availableMaterials,
    List<SiteCandidate> candidateSites,
    Set<String> permittedStyles
) {
    public BlueprintRequest {
        Objects.requireNonNull(requestId, "requestId");
        Objects.requireNonNull(companionUuid, "companionUuid");
        Objects.requireNonNull(ownerUuid, "ownerUuid");
        Objects.requireNonNull(dimensionId, "dimensionId");
        Objects.requireNonNull(buildPurpose, "buildPurpose");
        Objects.requireNonNull(preferredOrigin, "preferredOrigin");
        Objects.requireNonNull(preferredFacing, "preferredFacing");
        Objects.requireNonNull(maximumBounds, "maximumBounds");
        if (dimensionId.isBlank()) throw new IllegalArgumentException("dimensionId must not be blank");
        if (buildPurpose.isBlank()) throw new IllegalArgumentException("buildPurpose must not be blank");
        availableMaterials = List.copyOf(availableMaterials == null ? List.of() : availableMaterials);
        candidateSites = List.copyOf(candidateSites == null ? List.of() : candidateSites);
        permittedStyles = Set.copyOf(permittedStyles == null ? Set.of() : permittedStyles);
    }
}
