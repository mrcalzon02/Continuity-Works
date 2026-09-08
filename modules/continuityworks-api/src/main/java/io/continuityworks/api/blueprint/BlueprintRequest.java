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
    ConstructionVolume constructionVolume,
    BlockPosition preferredOrigin,
    Facing preferredFacing,
    List<BlueprintSpecification> specifications,
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
        Objects.requireNonNull(constructionVolume, "constructionVolume");
        Objects.requireNonNull(preferredOrigin, "preferredOrigin");
        Objects.requireNonNull(preferredFacing, "preferredFacing");
        if (dimensionId.isBlank()) throw new IllegalArgumentException("dimensionId must not be blank");
        if (buildPurpose.isBlank()) throw new IllegalArgumentException("buildPurpose must not be blank");
        if (!constructionVolume.contains(preferredOrigin)) {
            throw new IllegalArgumentException("preferredOrigin must be inside constructionVolume");
        }
        specifications = List.copyOf(specifications == null ? List.of() : specifications);
        availableMaterials = List.copyOf(availableMaterials == null ? List.of() : availableMaterials);
        candidateSites = List.copyOf(candidateSites == null ? List.of() : candidateSites);
        permittedStyles = Set.copyOf(permittedStyles == null ? Set.of() : permittedStyles);
    }
}
