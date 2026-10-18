package io.continuityworks.spawnprotection.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import io.continuityworks.spawnprotection.runtime.GenerationAttempt;
import io.continuityworks.spawnprotection.runtime.GenerationAttemptContext;
import io.continuityworks.spawnprotection.runtime.LevelResolver;
import io.continuityworks.spawnprotection.runtime.SpawnProtectionService;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.StructureManager;
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
        // StructureManager has no public level() getter in Forge 1.20.1.
        // The backing LevelAccessor can be a WorldGenRegion; resolve it to
        // its actual ServerLevel so reservations remain dimension-local.
        ServerLevel level = LevelResolver.serverLevel(
            ((StructureManagerLevelAccessor) (Object) structureManager)
                .continuityworks$getLevel()
        );

        GenerationAttempt attempt = null;
        if (level != null) {
            // The service resolves the actual registered structure ID and
            // computes a unique generation transaction from this same chunk.
            // Do not duplicate outdated service parameters in the mixin.
            attempt = SpawnProtectionService.beginAttempt(
                level,
                registryAccess,
                selectionEntry.structure().value(),
                chunkPos
            );
        }

        GenerationAttemptContext.begin(attempt);
        boolean terminalHandled = attempt == null;
        try {
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