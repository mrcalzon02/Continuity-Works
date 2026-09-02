package io.continuityworks.spawnprotection.runtime;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.LevelAccessor;

public final class LevelResolver {
    public static ServerLevel serverLevel(LevelAccessor accessor) {
        if (accessor instanceof ServerLevel serverLevel) return serverLevel;
        if (accessor instanceof WorldGenRegion region) return region.getLevel();
        return null;
    }

    private LevelResolver() { }
}
