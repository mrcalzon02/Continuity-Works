package io.continuityworks.biomes;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Authoritative topology assignment for the eight foundation biomes and all 128
 * anthology biomes.
 *
 * <p>The Abyssal work proved four especially useful morphology ideas: connected
 * depressions, chunk-continuous channels, current/ripple ridges and clustered
 * seabed relief. This catalog translates those ideas into terrestrial analogues
 * while keeping every biome's geometry distinct.</p>
 */
public final class LandTopologyProfiles {
    public record Resolved(
        ResourceKey<Biome> biome,
        LandTopologyProfile topology,
        Block top,
        Block under
    ) { }

    private static final Map<ResourceKey<Biome>, Resolved> PROFILES = buildProfiles();

    private LandTopologyProfiles() { }

    public static Resolved resolve(ResourceKey<Biome> biome) {
        return PROFILES.get(biome);
    }

    public static int profileCount() {
        return PROFILES.size();
    }

    private static Map<ResourceKey<Biome>, Resolved> buildProfiles() {
        Map<ResourceKey<Biome>, Resolved> profiles = new LinkedHashMap<>();

        // Foundation eight: explicit signatures matching the original terrain matrix.
        put(profiles, BiomeTemplateKeys.TEMPERATE_GROVE,
            profile(LandTopologyMode.KNOLLS, LandTopologyMode.CHANNELS, 2, 44, 0.30, false, 1101L),
            Blocks.GRASS_BLOCK, Blocks.DIRT);
        put(profiles, BiomeTemplateKeys.FLOWERING_MEADOW,
            profile(LandTopologyMode.KNOLLS, LandTopologyMode.RIDGES, 2, 58, 0.24, false, 1102L),
            Blocks.GRASS_BLOCK, Blocks.DIRT);
        put(profiles, BiomeTemplateKeys.MISTY_HIGHLANDS,
            profile(LandTopologyMode.RIDGES, LandTopologyMode.SCARPS, 6, 48, 0.44, false, 1103L),
            Blocks.COARSE_DIRT, Blocks.STONE);
        put(profiles, BiomeTemplateKeys.MARSHLAND,
            profile(LandTopologyMode.HUMMOCKS, LandTopologyMode.CHANNELS, 2, 32, 0.48, true, 1104L),
            Blocks.MUD, Blocks.DIRT);
        put(profiles, BiomeTemplateKeys.FROSTED_TAIGA,
            profile(LandTopologyMode.MORAINE, LandTopologyMode.BASINS, 4, 46, 0.36, false, 1105L),
            Blocks.PODZOL, Blocks.DIRT);
        put(profiles, BiomeTemplateKeys.DRY_SCRUBLAND,
            profile(LandTopologyMode.CHANNELS, LandTopologyMode.DUNES, 4, 52, 0.34, false, 1106L),
            Blocks.COARSE_DIRT, Blocks.DIRT);
        put(profiles, BiomeTemplateKeys.ROCKY_BADLANDS,
            profile(LandTopologyMode.SCARPS, LandTopologyMode.RIDGES, 7, 38, 0.46, false, 1107L),
            Blocks.RED_SAND, Blocks.TERRACOTTA);
        put(profiles, BiomeTemplateKeys.ASH_WASTES,
            profile(LandTopologyMode.RIFTS, LandTopologyMode.DUNES, 6, 42, 0.38, false, 1108L),
            Blocks.TUFF, Blocks.BASALT);

        // The anthology remains data-authored for identity and build generation. Its
        // topology is derived from each exact biome ID, then frozen into this map at
        // class initialization. Every entry receives its own scale/relief/strength/salt.
        for (AnthologyBiomeCatalog.Entry entry : AnthologyBiomeCatalog.ENTRIES) {
            LandTopologyProfile topology = anthologyProfile(entry.family(), entry.id());
            profiles.put(entry.key(), new Resolved(entry.key(), topology, entry.top(), entry.under()));
        }

        return Map.copyOf(profiles);
    }

    private static void put(
        Map<ResourceKey<Biome>, Resolved> profiles,
        ResourceKey<Biome> biome,
        LandTopologyProfile topology,
        Block top,
        Block under
    ) {
        profiles.put(biome, new Resolved(biome, topology, top, under));
    }

    private static LandTopologyProfile profile(
        LandTopologyMode primary,
        LandTopologyMode secondary,
        int relief,
        double scale,
        double secondaryStrength,
        boolean waterFill,
        long salt
    ) {
        return new LandTopologyProfile(primary, secondary, relief, scale, secondaryStrength, waterFill, salt);
    }

    private static LandTopologyProfile anthologyProfile(AnthologyBiomeCatalog.Family family, String id) {
        LandTopologyMode primary;
        LandTopologyMode secondary;

        if (containsAny(id, "karst", "cave")) {
            primary = LandTopologyMode.KARST;
            secondary = LandTopologyMode.SPIRES;
        } else if (id.contains("crater")) {
            primary = LandTopologyMode.CRATERS;
            secondary = LandTopologyMode.RIFTS;
        } else if (containsAny(id, "glacial", "tundra", "alpine")) {
            primary = LandTopologyMode.MORAINE;
            secondary = LandTopologyMode.BASINS;
        } else if (containsAny(id, "marsh", "wetlands", "floodplain", "delta", "polders")) {
            primary = LandTopologyMode.HUMMOCKS;
            secondary = LandTopologyMode.CHANNELS;
        } else if (containsAny(id, "canal", "river", "wadi", "causeways", "harbor")) {
            primary = LandTopologyMode.CHANNELS;
            secondary = switch (family) {
                case ANCIENT, RENAISSANCE_CLOCKWORK, INDUSTRIAL, NEON_VIRTUAL -> LandTopologyMode.TERRACES;
                default -> LandTopologyMode.HUMMOCKS;
            };
        } else if (containsAny(id, "desert", "dunes")) {
            primary = LandTopologyMode.DUNES;
            secondary = LandTopologyMode.RIDGES;
        } else if (containsAny(id, "quarry", "mine")) {
            primary = LandTopologyMode.TERRACES;
            secondary = LandTopologyMode.SCARPS;
        } else if (containsAny(id, "volcanic", "obsidian", "fusion")) {
            primary = LandTopologyMode.RIFTS;
            secondary = LandTopologyMode.RIDGES;
        } else if (containsAny(id, "slag", "cinder", "rustbelt", "wreckage", "ruins", "suburbs")) {
            primary = LandTopologyMode.SPOIL;
            secondary = LandTopologyMode.RUBBLE;
        } else if (family == AnthologyBiomeCatalog.Family.NEON_VIRTUAL
            && containsAny(id, "grid", "metropolis", "pulseway", "district")) {
            primary = LandTopologyMode.GRID;
            secondary = LandTopologyMode.TERRACES;
        } else if (containsAny(id, "arcology", "spaceport", "habitat", "megafarm", "exclusion_zone")) {
            primary = LandTopologyMode.TERRACES;
            secondary = LandTopologyMode.GRID;
        } else if (containsAny(id, "highlands", "ridge", "plateau", "uplands", "hills", "mesa", "badlands", "slopes")) {
            primary = LandTopologyMode.RIDGES;
            secondary = LandTopologyMode.SCARPS;
        } else if (containsAny(id, "spire", "citadel", "observatory", "shrine")) {
            primary = LandTopologyMode.SPIRES;
            secondary = LandTopologyMode.RIDGES;
        } else if (containsAny(id, "forest", "grove", "redwood", "orchard", "gardens", "garden")) {
            primary = LandTopologyMode.KNOLLS;
            secondary = switch (family) {
                case PRIMORDIAL, ADVANCED_SCIFI, NEON_VIRTUAL -> LandTopologyMode.SPIRES;
                default -> LandTopologyMode.CHANNELS;
            };
        } else if (containsAny(id, "basin", "vale", "valley")) {
            primary = LandTopologyMode.BASINS;
            secondary = LandTopologyMode.CHANNELS;
        } else if (containsAny(id, "flats", "steppe", "prairie", "plains", "farmlands", "downs", "heath", "moor", "commons")) {
            primary = LandTopologyMode.KNOLLS;
            secondary = LandTopologyMode.CHANNELS;
        } else if (containsAny(id, "city", "market", "estates", "moorings", "mechanist", "factory", "workers_row")) {
            primary = LandTopologyMode.TERRACES;
            secondary = switch (family) {
                case INDUSTRIAL, RENAISSANCE_CLOCKWORK -> LandTopologyMode.GRID;
                default -> LandTopologyMode.RIDGES;
            };
        } else if (containsAny(id, "coast", "shires")) {
            primary = LandTopologyMode.RIDGES;
            secondary = LandTopologyMode.CHANNELS;
        } else {
            LandTopologyMode[] pair = familyDefault(family);
            primary = pair[0];
            secondary = pair[1];
        }

        long hash = stableSalt(id);
        int relief = clamp(baseRelief(primary) + (int) Math.floorMod(hash >>> 7, 3L) - 1, 2, 7);
        double scale = 24.0 + Math.floorMod(hash >>> 13, 41L);
        double secondaryStrength = (25.0 + Math.floorMod(hash >>> 21, 26L)) / 100.0;
        boolean waterFill = containsAny(id,
            "marsh", "wetlands", "floodplain", "delta", "polders", "canal", "river", "wadi", "harbor", "basin")
            && (primary == LandTopologyMode.HUMMOCKS
                || primary == LandTopologyMode.CHANNELS
                || primary == LandTopologyMode.BASINS);

        // Family ordinal is mixed in so similarly named concepts in different eras still
        // reconstruct different absolute-coordinate fields.
        long salt = mix(hash ^ ((long) family.ordinal() * 0x9E3779B97F4A7C15L));
        return profile(primary, secondary, relief, scale, secondaryStrength, waterFill, salt);
    }

    private static LandTopologyMode[] familyDefault(AnthologyBiomeCatalog.Family family) {
        return switch (family) {
            case PRIMORDIAL -> new LandTopologyMode[] {LandTopologyMode.KNOLLS, LandTopologyMode.RIDGES};
            case ANCIENT -> new LandTopologyMode[] {LandTopologyMode.TERRACES, LandTopologyMode.CHANNELS};
            case MEDIEVAL -> new LandTopologyMode[] {LandTopologyMode.KNOLLS, LandTopologyMode.CHANNELS};
            case RENAISSANCE_CLOCKWORK -> new LandTopologyMode[] {LandTopologyMode.TERRACES, LandTopologyMode.CHANNELS};
            case INDUSTRIAL -> new LandTopologyMode[] {LandTopologyMode.SPOIL, LandTopologyMode.TERRACES};
            case ATOMIC_POST_COLLAPSE -> new LandTopologyMode[] {LandTopologyMode.RUBBLE, LandTopologyMode.CRATERS};
            case ADVANCED_SCIFI -> new LandTopologyMode[] {LandTopologyMode.TERRACES, LandTopologyMode.SPIRES};
            case NEON_VIRTUAL -> new LandTopologyMode[] {LandTopologyMode.GRID, LandTopologyMode.SPIRES};
        };
    }

    private static int baseRelief(LandTopologyMode mode) {
        return switch (mode) {
            case KNOLLS, HUMMOCKS -> 2;
            case BASINS, CHANNELS, TERRACES, DUNES, GRID, RUBBLE -> 3;
            case RIDGES, MORAINE, SPOIL -> 4;
            case KARST, SCARPS, RIFTS, SPIRES -> 5;
            case CRATERS -> 6;
        };
    }

    private static boolean containsAny(String value, String... needles) {
        for (String needle : needles) {
            if (value.contains(needle)) {
                return true;
            }
        }
        return false;
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private static long stableSalt(String value) {
        long hash = 0xCBF29CE484222325L;
        for (int i = 0; i < value.length(); i++) {
            hash ^= value.charAt(i);
            hash *= 0x100000001B3L;
        }
        return hash;
    }

    private static long mix(long value) {
        value ^= value >>> 33;
        value *= 0xFF51AFD7ED558CCDL;
        value ^= value >>> 33;
        value *= 0xC4CEB9FE1A85EC53L;
        return value ^ (value >>> 33);
    }
}
