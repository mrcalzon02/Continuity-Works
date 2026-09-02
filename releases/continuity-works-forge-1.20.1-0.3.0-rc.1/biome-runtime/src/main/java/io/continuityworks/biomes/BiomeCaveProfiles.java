package io.continuityworks.biomes;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Authoritative per-biome cave-network profiles for all 144 primary Continuity Works
 * biomes: eight foundation land biomes, eight Abyssal primary biomes and the complete
 * 128-biome anthology.
 */
public final class BiomeCaveProfiles {
    private static final Map<ResourceKey<Biome>, BiomeCaveProfile> PROFILES = buildProfiles();

    private BiomeCaveProfiles() { }

    public static BiomeCaveProfile resolve(ResourceKey<Biome> biome) {
        return PROFILES.get(biome);
    }

    public static int profileCount() {
        return PROFILES.size();
    }

    private static Map<ResourceKey<Biome>, BiomeCaveProfile> buildProfiles() {
        Map<ResourceKey<Biome>, BiomeCaveProfile> profiles = new LinkedHashMap<>();

        put(profiles, BiomeTemplateKeys.TEMPERATE_GROVE, "temperate_grove", "foundation");
        put(profiles, BiomeTemplateKeys.FLOWERING_MEADOW, "flowering_meadow", "foundation");
        put(profiles, BiomeTemplateKeys.MISTY_HIGHLANDS, "misty_highlands", "foundation");
        put(profiles, BiomeTemplateKeys.MARSHLAND, "marshland", "foundation");
        put(profiles, BiomeTemplateKeys.FROSTED_TAIGA, "frosted_taiga", "foundation");
        put(profiles, BiomeTemplateKeys.DRY_SCRUBLAND, "dry_scrubland", "foundation");
        put(profiles, BiomeTemplateKeys.ROCKY_BADLANDS, "rocky_badlands", "foundation");
        put(profiles, BiomeTemplateKeys.ASH_WASTES, "ash_wastes", "foundation");

        put(profiles, BiomeTemplateKeys.WESTERN_CONTINENTAL_SLOPE, "western_continental_slope", "abyssal");
        put(profiles, BiomeTemplateKeys.WESTERN_ABYSSAL_PLAIN, "western_abyssal_plain", "abyssal");
        put(profiles, BiomeTemplateKeys.WESTERN_FRACTURE_FIELD, "western_fracture_field", "abyssal");
        put(profiles, BiomeTemplateKeys.WESTERN_HADAL_TRENCH, "western_hadal_trench", "abyssal");
        put(profiles, BiomeTemplateKeys.EASTERN_CONTINENTAL_SLOPE, "eastern_continental_slope", "abyssal");
        put(profiles, BiomeTemplateKeys.EASTERN_ABYSSAL_PLAIN, "eastern_abyssal_plain", "abyssal");
        put(profiles, BiomeTemplateKeys.EASTERN_FRACTURE_FIELD, "eastern_fracture_field", "abyssal");
        put(profiles, BiomeTemplateKeys.EASTERN_HADAL_TRENCH, "eastern_hadal_trench", "abyssal");

        for (AnthologyBiomeCatalog.Entry entry : AnthologyBiomeCatalog.ENTRIES) {
            profiles.put(entry.key(), create(entry.id(), entry.family().configKey()));
        }

        return Map.copyOf(profiles);
    }

    private static void put(
        Map<ResourceKey<Biome>, BiomeCaveProfile> profiles,
        ResourceKey<Biome> key,
        String id,
        String family
    ) {
        profiles.put(key, create(id, family));
    }

    private static BiomeCaveProfile create(String id, String family) {
        long hash = mix(stableSalt(id) ^ stableSalt(family));
        CaveCoverage coverage = coverageFor(id, family, hash);

        double[] weights = new double[] {
            component(hash, 1), component(hash, 2), component(hash, 3), component(hash, 4),
            component(hash, 5), component(hash, 6), component(hash, 7)
        };

        if (family.equals("primordial")) {
            weights[0] += 0.18; // gradient / Perlin-like continuity
            weights[1] += 0.22; // cellular chambers
            weights[5] += 0.12; // plasma irregularity
        } else if (family.equals("ancient")) {
            weights[0] += 0.14;
            weights[2] += 0.15; // mosaic quarry/terrace geometry
            weights[6] += 0.12;
        } else if (family.equals("medieval")) {
            weights[0] += 0.16;
            weights[1] += 0.12;
            weights[6] += 0.14;
        } else if (family.equals("renaissance_clockwork")) {
            weights[2] += 0.18;
            weights[3] += 0.20; // tiled/engineered repetition
            weights[4] += 0.10;
        } else if (family.equals("industrial")) {
            weights[2] += 0.18;
            weights[4] += 0.22; // scrambled cuts / workings
            weights[6] += 0.12;
        } else if (family.equals("atomic_post_collapse")) {
            weights[1] += 0.16;
            weights[5] += 0.24; // plasma/radiating breakup
            weights[6] += 0.18;
        } else if (family.equals("advanced_scifi")) {
            weights[0] += 0.12;
            weights[3] += 0.18;
            weights[6] += 0.24;
        } else if (family.equals("neon_virtual")) {
            weights[2] += 0.24;
            weights[3] += 0.25;
            weights[4] += 0.20;
        } else if (family.equals("abyssal")) {
            weights[0] += 0.12;
            weights[1] += 0.24;
            weights[5] += 0.14;
        }

        if (containsAny(id, "karst", "cave", "geode")) {
            weights[1] += 0.28;
            weights[6] += 0.20;
        }
        if (containsAny(id, "grid", "city", "district", "metro", "citadel", "arcology")) {
            weights[2] += 0.24;
            weights[3] += 0.24;
            weights[4] += 0.14;
        }
        if (containsAny(id, "fracture", "trench", "crater", "volcanic", "obsidian", "glassed")) {
            weights[5] += 0.22;
            weights[6] += 0.18;
        }
        normalize(weights);

        double horizontalScale = 22.0 + unit(mix(hash ^ 0xA24BAED4963EE407L)) * 46.0;
        double verticalScale = 9.0 + unit(mix(hash ^ 0x9FB21C651E98DF25L)) * 23.0;
        double threshold = switch (coverage) {
            case COMPLETE -> 0.34 + unit(mix(hash ^ 0xD1B54A32D192ED03L)) * 0.08;
            case PARTIAL -> 0.46 + unit(mix(hash ^ 0x94D049BB133111EBL)) * 0.10;
            case OPAQUE -> 0.51 + unit(mix(hash ^ 0x369DEA0F31A53F85L)) * 0.08;
        };

        double tunnelBias = 0.16 + unit(mix(hash ^ 0xDB4F0B9175AE2165L)) * 0.34;
        double chamberBias = 0.14 + unit(mix(hash ^ 0xBBE0563303A4615FL)) * 0.34;
        double shaftBias = 0.05 + unit(mix(hash ^ 0xA0F2EC75A1FE1575L)) * 0.22;

        if (containsAny(id, "karst", "basin", "geode", "quarry", "crater")) {
            chamberBias += 0.16;
        }
        if (containsAny(id, "river", "canal", "wadi", "railcut", "pulseway", "fracture", "trench")) {
            tunnelBias += 0.16;
        }
        if (containsAny(id, "spire", "elevator", "mine", "shaft", "citadel", "highlands")) {
            shaftBias += 0.12;
        }

        double floodChance = floodChanceFor(id, family, hash);
        int roofBuffer = switch (coverage) {
            case PARTIAL -> 6 + (int) Math.floorMod(hash >>> 9, 5L);
            case COMPLETE -> 10 + (int) Math.floorMod(hash >>> 11, 6L);
            case OPAQUE -> 18 + (int) Math.floorMod(hash >>> 13, 11L);
        };

        return new BiomeCaveProfile(
            coverage,
            horizontalScale,
            verticalScale,
            threshold,
            weights[0], weights[1], weights[2], weights[3], weights[4], weights[5], weights[6],
            Math.min(0.62, tunnelBias),
            Math.min(0.62, chamberBias),
            Math.min(0.38, shaftBias),
            floodChance,
            roofBuffer,
            mix(hash ^ 0xC13FA9A902A6328FL)
        );
    }

    private static CaveCoverage coverageFor(String id, String family, long hash) {
        if (containsAny(id, "bunker", "habitat", "research", "null_sector", "necropolis", "reactor", "underground")) {
            return CaveCoverage.OPAQUE;
        }
        if (containsAny(id, "karst", "cave", "mine", "quarry", "metro", "fracture", "trench", "geode")) {
            return CaveCoverage.COMPLETE;
        }
        if (family.equals("abyssal")) {
            return id.contains("plain") ? CaveCoverage.PARTIAL : CaveCoverage.COMPLETE;
        }
        int selector = (int) Math.floorMod(hash, 9L);
        if (selector <= 2) {
            return CaveCoverage.PARTIAL;
        }
        if (selector <= 6) {
            return CaveCoverage.COMPLETE;
        }
        return CaveCoverage.OPAQUE;
    }

    private static double floodChanceFor(String id, String family, long hash) {
        if (family.equals("abyssal")) {
            return 1.0;
        }
        if (containsAny(id, "flooded", "marsh", "wetlands", "floodplain", "delta", "canal", "river", "harbor", "coast", "polders")) {
            return 0.42 + unit(mix(hash ^ 0x8CB92BA72F3D8DD7L)) * 0.43;
        }
        if (containsAny(id, "desert", "dunes", "badlands", "wastes", "flats")) {
            return 0.0;
        }
        return unit(mix(hash ^ 0x4F1BBCDCBFA54001L)) < 0.20 ? 0.10 : 0.0;
    }

    private static double component(long hash, int ordinal) {
        return 0.08 + unit(mix(hash ^ (0x9E3779B97F4A7C15L * ordinal))) * 0.24;
    }

    private static void normalize(double[] values) {
        double total = 0.0;
        for (double value : values) {
            total += value;
        }
        for (int i = 0; i < values.length; i++) {
            values[i] /= total;
        }
    }

    private static boolean containsAny(String value, String... needles) {
        for (String needle : needles) {
            if (value.contains(needle)) {
                return true;
            }
        }
        return false;
    }

    private static long stableSalt(String value) {
        long hash = 0xCBF29CE484222325L;
        for (int i = 0; i < value.length(); i++) {
            hash ^= value.charAt(i);
            hash *= 0x100000001B3L;
        }
        return hash;
    }

    private static double unit(long value) {
        long mixed = mix(value);
        return ((mixed >>> 11) & ((1L << 53) - 1)) / (double) (1L << 53);
    }

    private static long mix(long value) {
        value ^= value >>> 33;
        value *= 0xFF51AFD7ED558CCDL;
        value ^= value >>> 33;
        value *= 0xC4CEB9FE1A85EC53L;
        return value ^ (value >>> 33);
    }
}
