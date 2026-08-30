package io.continuityworks.biomes;

import net.minecraftforge.common.ForgeConfigSpec;

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

        builder.push("worldgen");
        REGION_WEIGHT = builder
            .comment("Relative TerraBlender region weight. Higher values make the template region more common.")
            .defineInRange("regionWeight", 3, 1, 20);
        builder.pop();

        SPEC = builder.build();
    }

    private BiomeTemplateConfig() { }

    public static boolean anyEnabled() {
        return ENABLE_TEMPERATE_GROVE.get()
            || ENABLE_FLOWERING_MEADOW.get()
            || ENABLE_MISTY_HIGHLANDS.get()
            || ENABLE_MARSHLAND.get()
            || ENABLE_FROSTED_TAIGA.get()
            || ENABLE_DRY_SCRUBLAND.get()
            || ENABLE_ROCKY_BADLANDS.get()
            || ENABLE_ASH_WASTES.get();
    }
}
