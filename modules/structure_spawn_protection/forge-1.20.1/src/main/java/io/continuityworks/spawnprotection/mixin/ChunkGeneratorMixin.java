package io.continuityworks.spawnprotection.mixin;

import io.continuityworks.spawnprotection.runtime.GenerationAttempt;
import io.continuityworks.spawnprotection.runtime.GenerationAttemptContext;
import io.continuityworks.spawnprotection.runtime.LevelResolver;
import io.continuityworks.spawnprotection.runtime.SpawnProtectionService;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(ChunkGenerator.class)
public abstract class ChunkGeneratorMixin {
    @Inject(method = "tryGenerateStructure", at = @At("HEAD"))
    private void continuityworks$beginStructureAttempt(
        StructureSet.StructureSelectionEntry entry,
        StructureManager structureManager,
        RegistryAccess registryAccess,
        RandomState randomState,
        StructureTemplateManager templateManager,
        long seed,
        ChunkAccess chunk,
        ChunkPos chunkPos,
        SectionPos sectionPos,
        CallbackInfoReturnable<Boolean> cir
    ) {
        ServerLevel level = LevelResolver.serverLevel(chunk.getWorldForge());
        GenerationAttempt attempt = null;
        if (level != null) {
            Structure structure = entry.structure().value();
            attempt = SpawnProtectionService.beginAttempt(level, registryAccess, structure, chunkPos);
        }
        GenerationAttemptContext.begin(attempt);
    }

    @Inject(method = "tryGenerateStructure", at = @At("RETURN"), cancellable = true)
    private void continuityworks$finishStructureAttempt(
        StructureSet.StructureSelectionEntry entry,
        StructureManager structureManager,
        RegistryAccess registryAccess,
        RandomState randomState,
        StructureTemplateManager templateManager,
        long seed,
        ChunkAccess chunk,
        ChunkPos chunkPos,
        SectionPos sectionPos,
        CallbackInfoReturnable<Boolean> cir
    ) {
        GenerationAttempt attempt = GenerationAttemptContext.current();
        try {
            if (attempt == null) return;
            if (!Boolean.TRUE.equals(cir.getReturnValue())) {
                SpawnProtectionService.rollbackAttempt(attempt);
                return;
            }
            Structure structure = entry.structure().value();
            StructureStart start = chunk.getStartForStructure(structure);
            if (!SpawnProtectionService.finishAttempt(attempt, start)) {
                chunk.setStartForStructure(structure, StructureStartAccessor.continuityworks$getInvalidStart());
                cir.setReturnValue(false);
            }
        } finally {
            GenerationAttemptContext.end(attempt);
        }
    }
}
