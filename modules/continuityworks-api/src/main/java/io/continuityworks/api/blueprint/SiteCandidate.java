package io.continuityworks.api.blueprint;

import java.util.Map;
import java.util.Objects;

public record SiteCandidate(
    String siteId,
    BlockPosition origin,
    Facing facing,
    Bounds usableBounds,
    double suitability,
    Map<String, String> attributes
) {
    public SiteCandidate {
        Objects.requireNonNull(siteId, "siteId");
        Objects.requireNonNull(origin, "origin");
        Objects.requireNonNull(facing, "facing");
        Objects.requireNonNull(usableBounds, "usableBounds");
        if (siteId.isBlank()) throw new IllegalArgumentException("siteId must not be blank");
        if (!Double.isFinite(suitability) || suitability < 0.0 || suitability > 1.0) {
            throw new IllegalArgumentException("suitability must be between 0 and 1");
        }
        attributes = Map.copyOf(attributes == null ? Map.of() : attributes);
    }
}
