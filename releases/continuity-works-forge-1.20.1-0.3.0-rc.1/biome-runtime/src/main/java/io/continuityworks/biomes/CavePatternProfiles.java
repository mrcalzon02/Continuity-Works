package io.continuityworks.biomes;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;

import java.util.LinkedHashMap;
import java.util.Map;

/** Assigns a unique literal-grid composition to all 144 primary biomes. */
public final class CavePatternProfiles {
    private static final CaveMaskMode[] MODES = CaveMaskMode.values();
    private static final Map<ResourceKey<Biome>, CavePatternProfile> PROFILES = buildProfiles();

    private CavePatternProfiles() { }

    public static CavePatternProfile resolve(ResourceKey<Biome> biome) {
        return PROFILES.get(biome);
    }

    public static int profileCount() {
        return PROFILES.size();
    }

    private static Map<ResourceKey<Biome>, CavePatternProfile> buildProfiles() {
        Map<ResourceKey<Biome>, CavePatternProfile> profiles = new LinkedHashMap<>();
        int ordinal = 0;

        ordinal = put(profiles, BiomeTemplateKeys.TEMPERATE_GROVE, "temperate_grove", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.FLOWERING_MEADOW, "flowering_meadow", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.MISTY_HIGHLANDS, "misty_highlands", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.MARSHLAND, "marshland", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.FROSTED_TAIGA, "frosted_taiga", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.DRY_SCRUBLAND, "dry_scrubland", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.ROCKY_BADLANDS, "rocky_badlands", "foundation", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.ASH_WASTES, "ash_wastes", "foundation", ordinal);

        ordinal = put(profiles, BiomeTemplateKeys.WESTERN_CONTINENTAL_SLOPE, "western_continental_slope", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.WESTERN_ABYSSAL_PLAIN, "western_abyssal_plain", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.WESTERN_FRACTURE_FIELD, "western_fracture_field", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.WESTERN_HADAL_TRENCH, "western_hadal_trench", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.EASTERN_CONTINENTAL_SLOPE, "eastern_continental_slope", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.EASTERN_ABYSSAL_PLAIN, "eastern_abyssal_plain", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.EASTERN_FRACTURE_FIELD, "eastern_fracture_field", "abyssal", ordinal);
        ordinal = put(profiles, BiomeTemplateKeys.EASTERN_HADAL_TRENCH, "eastern_hadal_trench", "abyssal", ordinal);

        for (AnthologyBiomeCatalog.Entry entry : AnthologyBiomeCatalog.ENTRIES) {
            profiles.put(entry.key(), create(entry.id(), entry.family().configKey(), ordinal++));
        }

        return Map.copyOf(profiles);
    }

    private static int put(
        Map<ResourceKey<Biome>, CavePatternProfile> profiles,
        ResourceKey<Biome> key,
        String id,
        String family,
        int ordinal
    ) {
        profiles.put(key, create(id, family, ordinal));
        return ordinal + 1;
    }

    private static CavePatternProfile create(String id, String family, int ordinal) {
        long hash = mix(stableSalt(id) ^ stableSalt(family) ^ ((long) ordinal * 0x9E3779B97F4A7C15L));

        CaveMaskMode primary = MODES[Math.floorMod(ordinal, MODES.length)];
        CaveMaskMode secondary = MODES[Math.floorMod(ordinal * 7 + 11, MODES.length)];
        CaveMaskMode tertiary = MODES[Math.floorMod(ordinal * 13 + 17, MODES.length)];

        double primaryWeight = 0.48 + unit(hash ^ 0xA24BAED4963EE407L) * 0.12;
        double secondaryWeight = 0.26 + unit(hash ^ 0x9FB21C651E98DF25L) * 0.08;
        double tertiaryWeight = Math.max(0.12, 1.0 - primaryWeight - secondaryWeight);
        double total = primaryWeight + secondaryWeight + tertiaryWeight;
        primaryWeight /= total;
        secondaryWeight /= total;
        tertiaryWeight /= total;

        double maskScale = 28.0 + unit(hash ^ 0xD1B54A32D192ED03L) * 64.0;
        double hexRadius = 10.0 + unit(hash ^ 0x94D049BB133111EBL) * 22.0;
        double corridorWidth = 1.15 + unit(hash ^ 0x369DEA0F31A53F85L) * 2.45;
        double layerSpacing = 14.0 + unit(hash ^ 0xDB4F0B9175AE2165L) * 24.0;
        double layerThickness = 2.0 + unit(hash ^ 0xBBE0563303A4615FL) * 3.8;
        double maskThreshold = 0.31 + unit(hash ^ 0xA0F2EC75A1FE1575L) * 0.24;
        int radialSectors = 4 + (int) Math.floorMod(hash >>> 17, 9L);

        if (family.equals("neon_virtual")) {
            hexRadius *= 0.78;
            corridorWidth *= 1.18;
            maskThreshold -= 0.05;
        } else if (family.equals("industrial") || family.equals("renaissance_clockwork")) {
            corridorWidth *= 1.08;
        } else if (family.equals("atomic_post_collapse")) {
            maskScale *= 1.18;
            maskThreshold += 0.03;
        } else if (family.equals("abyssal")) {
            layerThickness *= 1.22;
            maskThreshold -= 0.04;
        }

        if (containsAny(id, "grid", "circuit", "pulseway", "vector", "recursive", "null_sector")) {
            corridorWidth *= 1.22;
            hexRadius *= 0.84;
        }
        if (containsAny(id, "karst", "cave", "fracture", "trench", "geode")) {
            layerThickness *= 1.18;
            maskThreshold -= 0.04;
        }
        if (containsAny(id, "glassed", "blast_crater", "radstorm", "ash_wastes", "badlands")) {
            maskScale *= 1.16;
        }

        return new CavePatternProfile(
            primary,
            secondary,
            tertiary,
            primaryWeight,
            secondaryWeight,
            tertiaryWeight,
            maskScale,
            hexRadius,
            corridorWidth,
            layerSpacing,
            layerThickness,
            clamp(maskThreshold, 0.20, 0.68),
            radialSectors,
            mix(hash ^ 0xC13FA9A902A6328FL)
        );
    }

    private static boolean containsAny(String value, String... needles) {
        for (String needle : needles) {
            if (value.contains(needle)) {
                return true;
            }
        }
        return false;
    }

    private static double clamp(double value, double min, double max) {
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
