package io.continuityworks.spawnprotection.mixin;

import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.StructureManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Forge/Mojang 1.20.1 StructureManager retains the current LevelAccessor in
 * a private field and exposes no level() method. Read the authoritative
 * backing level without substituting a global server or guessing dimension.
 */
@Mixin(StructureManager.class)
public interface StructureManagerLevelAccessor {
    @Accessor("level")
    LevelAccessor continuityworks$getLevel();
}
