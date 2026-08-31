package io.continuityworks.biomes;

/**
 * Controls how much of a biome's cave field is allowed to resolve into traversable
 * volume. PARTIAL produces broken/branching networks, COMPLETE favors connected
 * systems, and OPAQUE keeps the network deep and sealed beneath a thicker roof.
 */
public enum CaveCoverage {
    PARTIAL,
    COMPLETE,
    OPAQUE
}
