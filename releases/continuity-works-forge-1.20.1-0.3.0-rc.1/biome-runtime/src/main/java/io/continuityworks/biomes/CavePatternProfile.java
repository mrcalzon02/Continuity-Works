package io.continuityworks.biomes;

/**
 * Per-biome literal-grid composition profile. Every biome keeps a real hex lattice
 * and combines three named visibility/occlusion operators around that geometry.
 */
public record CavePatternProfile(
    CaveMaskMode primary,
    CaveMaskMode secondary,
    CaveMaskMode tertiary,
    double primaryWeight,
    double secondaryWeight,
    double tertiaryWeight,
    double maskScale,
    double hexRadius,
    double corridorWidth,
    double layerSpacing,
    double layerThickness,
    double maskThreshold,
    int radialSectors,
    long salt
) { }
