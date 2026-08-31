package io.continuityworks.spawnprotection;

import com.mojang.logging.LogUtils;
import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import org.slf4j.Logger;

@Mod(ContinuityWorksSpawnProtection.MOD_ID)
public final class ContinuityWorksSpawnProtection {
    public static final String MOD_ID = "continuityworks_spawn_protection";
    public static final Logger LOGGER = LogUtils.getLogger();

    public ContinuityWorksSpawnProtection() {
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, SpawnProtectionConfig.SPEC);
        LOGGER.info("Continuity Works Structure Spawn Protection loaded; hard minimum exclusion radius = 500 blocks");
    }
}
