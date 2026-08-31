package io.continuityworks.biomes;

/**
 * Immutable terrain-shaping contract for one biome.
 *
 * @param primary dominant terrain morphology
 * @param secondary lower-amplitude supporting morphology
 * @param relief maximum vertical change in blocks
 * @param scale characteristic horizontal wavelength in blocks
 * @param secondaryStrength contribution of the secondary morphology
 * @param waterFill whether excavated depressions should become pools/channels
 * @param salt biome-specific deterministic world-field salt
 */
public record LandTopologyProfile(
    LandTopologyMode primary,
    LandTopologyMode secondary,
    int relief,
    double scale,
    double secondaryStrength,
    boolean waterFill,
    long salt
) {
    public LandTopologyProfile {
        if (primary == null || secondary == null) {
            throw new IllegalArgumentException("Topology modes must be defined");
        }
        if (relief < 1 || relief > 12) {
            throw new IllegalArgumentException("Topology relief must be between 1 and 12 blocks");
        }
        if (scale < 12.0 || scale > 192.0) {
            throw new IllegalArgumentException("Topology scale must be between 12 and 192 blocks");
        }
        if (secondaryStrength < 0.0 || secondaryStrength > 1.0) {
            throw new IllegalArgumentException("Secondary topology strength must be between 0 and 1");
        }
    }
}
