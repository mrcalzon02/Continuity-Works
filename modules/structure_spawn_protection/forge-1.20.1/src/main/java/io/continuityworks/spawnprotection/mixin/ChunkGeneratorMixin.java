package io.continuityworks.spawnprotection.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import io.continuityworks.spawnprotection.runtime.GenerationAttempt;
import io.continuityworks.spawnprotection.runtime.GenerationAttemptContext;
import io.continuityworks.spawnprotection.runtime.SpawnProtectionService;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureManager;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import org.spongepowered.asm.mixin.Mixin;

@Mixin(ChunkGenerator.class)
public abstract class ChunkGeneratorMixin {
    @WrapMethod(method = "tryGenerateStructure")
    private boolean continuityworks$wrapTryGenerateStructure(
        StructureSet.StructureSelectionEntry selectionEntry,
        StructureManager structureManager,
        RegistryAccess registryAccess,
        RandomState randomState,
        StructureTemplateManager structureTemplateManager,
        long seed,
        ChunkAccess chunk,
        ChunkPos chunkPos,
        SectionPos sectionPos,
        Operation<Boolean> original
    ) {
        ServerLevel level = null;
        if (structureManager.level() instanceof ServerLevel serverLevel) {
            level = serverLevel;
        }

        GenerationAttempt attempt = null;
        if (level != null) {
            String structureId = registryAccess.registryOrThrow(Registries.STRUCTURE)
                .getKey(selectionEntry.structure().value()).toString();
            attempt = SpawnProtectionService.beginAttempt(
                level,
                structureId,
                chunkPos.getMiddleBlockX(),
                chunkPos.getMiddleBlockZ()
            );
        }

        GenerationAttemptContext.begin(attempt);
        boolean terminalHandled = attempt == null;
        try {
            if (attempt != null && !attempt.permitted()) {
                return false;
            }

            boolean generated = original.call(
                selectionEntry,
                structureManager,
                registryAccess,
                randomState,
                structureTemplateManager,
                seed,
                chunk,
                chunkPos,
                sectionPos
            );

            if (attempt == null) {
                return generated;
            }
            if (!generated) {
                return false;
            }

            Structure structure = selectionEntry.structure().value();
            StructureStart start = chunk.getStartForStructure(structure);
            terminalHandled = true;
            if (!SpawnProtectionService.finishAttempt(attempt, start)) {
                chunk.setStartForStructure(structure, StructureStart.INVALID_START);
                return false;
            }
            return true;
        } finally {
            if (!terminalHandled && attempt != null) {
                SpawnProtectionService.rollbackAttempt(attempt);
            }
            GenerationAttemptContext.end(attempt);
        }
    }
}