package io.continuityworks.biomes;

/**
 * Reusable land-shaping modes adapted from the proven Abyssal morphology systems.
 *
 * <p>The modes describe geometry rather than biome identity. Individual biomes combine
 * two modes with their own relief, scale and deterministic salt so a single safe
 * generator can produce many distinct terrain signatures.</p>
 */
public enum LandTopologyMode {
    KNOLLS,
    BASINS,
    CHANNELS,
    RIDGES,
    TERRACES,
    DUNES,
    MORAINE,
    KARST,
    SCARPS,
    CRATERS,
    RIFTS,
    HUMMOCKS,
    SPOIL,
    GRID,
    SPIRES,
    RUBBLE
}
