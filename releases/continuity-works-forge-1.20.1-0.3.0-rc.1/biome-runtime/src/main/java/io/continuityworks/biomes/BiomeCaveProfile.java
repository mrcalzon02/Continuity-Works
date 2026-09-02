package io.continuityworks.biomes;

/**
 * Immutable per-biome cave signature. The seven noise weights are intentionally
 * independent so each biome can combine several generation methods rather than
 * relying on a single global cave function.
 */
public record BiomeCaveProfile(
    CaveCoverage coverage,
    double horizontalScale,
    double verticalScale,
    double threshold,
    double gradientWeight,
    double cellularWeight,
    double mosaicWeight,
    double tileWeight,
    double scrambleWeight,
    double plasmaWeight,
    double fractalWeight,
    double tunnelBias,
    double chamberBias,
    double shaftBias,
    double floodChance,
    int roofBuffer,
    long salt
) { }
