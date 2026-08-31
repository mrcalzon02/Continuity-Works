package io.continuityworks.spawnprotection.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class SpawnProtectionConfig {
    public static final int HARD_MINIMUM_RADIUS = 500;

    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.IntValue DEFAULT_EXCLUSION_RADIUS;
    public static final ForgeConfigSpec.IntValue DEFAULT_JIGSAW_PIECE_RADIUS;
    public static final ForgeConfigSpec.BooleanValue AUTO_INCLUDE_REGISTERED_STRUCTURES;
    public static final ForgeConfigSpec.BooleanValue INDEX_EXISTING_CHUNK_STARTS;
    public static final ForgeConfigSpec.IntValue SELF_COLLISION_PADDING;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
        builder.comment(
            "Continuity Works Structure Spawn Protection.",
            "The 500-block minimum is intentionally not configurable downward."
        ).push("protection");

        DEFAULT_EXCLUSION_RADIUS = builder
            .comment("Default horizontal exclusion radius for enrolled structures.")
            .defineInRange("defaultExclusionRadius", HARD_MINIMUM_RADIUS, HARD_MINIMUM_RADIUS, 32768);

        DEFAULT_JIGSAW_PIECE_RADIUS = builder
            .comment("Default horizontal exclusion radius emitted by every accepted jigsaw piece.")
            .defineInRange("defaultJigsawPieceRadius", HARD_MINIMUM_RADIUS, HARD_MINIMUM_RADIUS, 32768);

        AUTO_INCLUDE_REGISTERED_STRUCTURES = builder
            .comment(
                "Automatically enroll every active structure registry entry unless explicitly ignored.",
                "Disable only when intentionally operating in tag/profile-only mode."
            )
            .define("autoIncludeRegisteredStructures", true);

        INDEX_EXISTING_CHUNK_STARTS = builder
            .comment("Index valid structure starts when already-generated chunks are loaded.")
            .define("indexExistingChunkStarts", true);

        SELF_COLLISION_PADDING = builder
            .comment(
                "Optional extra block padding used only for same-assembly jigsaw self-collision tests.",
                "0 permits normal face-adjacent connected pieces."
            )
            .defineInRange("selfCollisionPadding", 0, 0, 64);

        builder.pop();
        SPEC = builder.build();
    }

    private SpawnProtectionConfig() { }
}
