package io.continuityworks.biomes;

import net.minecraftforge.common.ForgeConfigSpec;

import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;

public final class BiomeTemplateConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue ENABLE_TEMPERATE_GROVE;
    public static final ForgeConfigSpec.BooleanValue ENABLE_FLOWERING_MEADOW;
    public static final ForgeConfigSpec.BooleanValue ENABLE_MISTY_HIGHLANDS;
    public static final ForgeConfigSpec.BooleanValue ENABLE_MARSHLAND;
    public static final ForgeConfigSpec.BooleanValue ENABLE_FROSTED_TAIGA;
    public static final ForgeConfigSpec.BooleanValue ENABLE_DRY_SCRUBLAND;
    public static final ForgeConfigSpec.BooleanValue ENABLE_ROCKY_BADLANDS;
    public static final ForgeConfigSpec.BooleanValue ENABLE_ASH_WASTES;

    public static final ForgeConfigSpec.BooleanValue ENABLE_ABYSSAL_FAMILY;
    public static final ForgeConfigSpec.BooleanValue ENABLE_WESTERN_CONTINENTAL_SLOPE;
    public static final ForgeConfigSpec.BooleanValue ENABLE_WESTERN_ABYSSAL_PLAIN;
    public static final ForgeConfigSpec.BooleanValue ENABLE_WESTERN_FRACTURE_FIELD;
    public static final ForgeConfigSpec.BooleanValue ENABLE_WESTERN_HADAL_TRENCH;
    public static final ForgeConfigSpec.BooleanValue ENABLE_EASTERN_CONTINENTAL_SLOPE;
    public static final ForgeConfigSpec.BooleanValue ENABLE_EASTERN_ABYSSAL_PLAIN;
    public static final ForgeConfigSpec.BooleanValue ENABLE_EASTERN_FRACTURE_FIELD;
    public static final ForgeConfigSpec.BooleanValue ENABLE_EASTERN_HADAL_TRENCH;

    public static final Map<AnthologyBiomeCatalog.Family, ForgeConfigSpec.BooleanValue> ANTHOLOGY_FAMILY_ENABLED =
        new EnumMap<>(AnthologyBiomeCatalog.Family.class);
    public static final Map<String, ForgeConfigSpec.BooleanValue> ANTHOLOGY_BIOME_ENABLED =
        new LinkedHashMap<>();

    public static final ForgeConfigSpec.IntValue REGION_WEIGHT;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();

        builder.comment(
            "Continuity Works Biome Templates",
            "All biome templates are enabled by default.",
            "Set a biome to false to remove it from NEW natural Overworld generation.",
            "The biome registry entry remains available so existing worlds stay readable.",
            "Restart Minecraft/server after changing these values."
        );

        builder.push("biomes");
        ENABLE_TEMPERATE_GROVE = builder.define("temperateGrove", true);
        ENABLE_FLOWERING_MEADOW = builder.define("floweringMeadow", true);
        ENABLE_MISTY_HIGHLANDS = builder.define("mistyHighlands", true);
        ENABLE_MARSHLAND = builder.define("marshland", true);
        ENABLE_FROSTED_TAIGA = builder.define("frostedTaiga", true);
        ENABLE_DRY_SCRUBLAND = builder.define("dryScrubland", true);
        ENABLE_ROCKY_BADLANDS = builder.define("rockyBadlands", true);
        ENABLE_ASH_WASTES = builder.define("ashWastes", true);
        builder.pop();

        builder.comment(
            "Infinite Domain Abyssal biome family.",
            "The family switch and each member switch affect natural generation only.",
            "Registry definitions stay loaded so saved chunks remain readable."
        );
        builder.push("abyssal");
        ENABLE_ABYSSAL_FAMILY = builder.define("enabled", true);
        ENABLE_WESTERN_CONTINENTAL_SLOPE = builder.define("westernContinentalSlope", true);
        ENABLE_WESTERN_ABYSSAL_PLAIN = builder.define("westernAbyssalPlain", true);
        ENABLE_WESTERN_FRACTURE_FIELD = builder.define("westernFractureField", true);
        ENABLE_WESTERN_HADAL_TRENCH = builder.define("westernHadalTrench", true);
        ENABLE_EASTERN_CONTINENTAL_SLOPE = builder.define("easternContinentalSlope", true);
        ENABLE_EASTERN_ABYSSAL_PLAIN = builder.define("easternAbyssalPlain", true);
        ENABLE_EASTERN_FRACTURE_FIELD = builder.define("easternFractureField", true);
        ENABLE_EASTERN_HADAL_TRENCH = builder.define("easternHadalTrench", true);
        builder.pop();

        builder.comment(
            "128-biome anthology.",
            "Each family has a master switch and every anthology biome has an individual natural-generation switch.",
            "Definitions remain registered even when natural placement is disabled."
        );
        builder.push("anthology");
        for (AnthologyBiomeCatalog.Family family : AnthologyBiomeCatalog.Family.values()) {
            builder.push(family.configKey());
            ANTHOLOGY_FAMILY_ENABLED.put(family, builder.define("enabled", true));
            for (AnthologyBiomeCatalog.Entry entry : AnthologyBiomeCatalog.ENTRIES) {
                if (entry.family() == family) {
                    ANTHOLOGY_BIOME_ENABLED.put(entry.id(), builder.define(entry.id(), true));
                }
            }
            builder.pop();
        }
        builder.pop();

        builder.push("worldgen");
        REGION_WEIGHT = builder
            .comment("Relative TerraBlender region weight. Higher values make Continuity Works biomes more common.")
            .defineInRange("regionWeight", 3, 1, 20);
        builder.pop();

        SPEC = builder.build();
    }

    private BiomeTemplateConfig() { }

    public static boolean isAnthologyEnabled(AnthologyBiomeCatalog.Entry entry) {
        ForgeConfigSpec.BooleanValue family = ANTHOLOGY_FAMILY_ENABLED.get(entry.family());
        ForgeConfigSpec.BooleanValue biome = ANTHOLOGY_BIOME_ENABLED.get(entry.id());
        return family != null && biome != null && family.get() && biome.get();
    }

    public static boolean anyEnabled() {
        return ENABLE_TEMPERATE_GROVE.get()
            || ENABLE_FLOWERING_MEADOW.get()
            || ENABLE_MISTY_HIGHLANDS.get()
            || ENABLE_MARSHLAND.get()
            || ENABLE_FROSTED_TAIGA.get()
            || ENABLE_DRY_SCRUBLAND.get()
            || ENABLE_ROCKY_BADLANDS.get()
            || ENABLE_ASH_WASTES.get()
            || AnthologyBiomeCatalog.ENTRIES.stream().anyMatch(BiomeTemplateConfig::isAnthologyEnabled)
            || (ENABLE_ABYSSAL_FAMILY.get() && (
                ENABLE_WESTERN_CONTINENTAL_SLOPE.get()
                || ENABLE_WESTERN_ABYSSAL_PLAIN.get()
                || ENABLE_WESTERN_FRACTURE_FIELD.get()
                || ENABLE_WESTERN_HADAL_TRENCH.get()
                || ENABLE_EASTERN_CONTINENTAL_SLOPE.get()
                || ENABLE_EASTERN_ABYSSAL_PLAIN.get()
                || ENABLE_EASTERN_FRACTURE_FIELD.get()
                || ENABLE_EASTERN_HADAL_TRENCH.get()
            ));
    }
}
