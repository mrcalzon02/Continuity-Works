package io.continuityworks.spawnprotection.mixin;

import io.continuityworks.spawnprotection.runtime.GenerationAttempt;
import io.continuityworks.spawnprotection.runtime.GenerationAttemptContext;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.apache.commons.lang3.mutable.MutableObject;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Hooks the exact vanilla jigsaw candidate-fit branch. Returning true from the redirect means
 * "occupied" to vanilla, so rejected pieces never reach list insertion, child queuing, or
 * free-space mutation.
 */
@Mixin(targets = "net.minecraft.world.level.levelgen.structure.pools.JigsawPlacement$Placer")
public abstract class JigsawPlacementPlacerMixin {
    @Inject(method = "tryPlacingChildren", at = @At("HEAD"))
    private void continuityworks$observeAcceptedSource(
        PoolElementStructurePiece sourcePiece,
        MutableObject<VoxelShape> contextFree,
        int depth,
        boolean expansionHack,
        LevelHeightAccessor heightAccessor,
        RandomState randomState,
        CallbackInfo ci
    ) {
        GenerationAttempt attempt = GenerationAttemptContext.current();
        if (attempt != null) attempt.observeAcceptedPiece(sourcePiece.getBoundingBox());
    }

    @Redirect(
        method = "tryPlacingChildren",
        at = @At(
            value = "INVOKE",
            target = "Lnet/minecraft/world/phys/shapes/Shapes;joinIsNotEmpty(Lnet/minecraft/world/phys/shapes/VoxelShape;Lnet/minecraft/world/phys/shapes/VoxelShape;Lnet/minecraft/world/phys/shapes/BooleanOp;)Z"
        ),
        require = 1
    )
    private boolean continuityworks$rejectReservedOrSelfConflictingPiece(
        VoxelShape freeSpace,
        VoxelShape candidateShape,
        BooleanOp operator
    ) {
        boolean vanillaOccupied = Shapes.joinIsNotEmpty(freeSpace, candidateShape, operator);
        if (vanillaOccupied) return true;
        GenerationAttempt attempt = GenerationAttemptContext.current();
        return attempt != null && !attempt.allowCandidate(candidateShape.bounds());
    }
}
