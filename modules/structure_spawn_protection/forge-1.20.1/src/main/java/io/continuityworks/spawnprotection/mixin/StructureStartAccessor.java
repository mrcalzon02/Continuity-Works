package io.continuityworks.spawnprotection.mixin;

import net.minecraft.world.level.levelgen.structure.StructureStart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(StructureStart.class)
public interface StructureStartAccessor {
    @Accessor("INVALID_START")
    static StructureStart continuityworks$getInvalidStart() {
        throw new AssertionError();
    }
}
