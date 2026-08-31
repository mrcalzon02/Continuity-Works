package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/** Shared underwater placement rules for neutral Abyssal ecology features. */
final class AbyssalEcologyPlacement {
    private AbyssalEcologyPlacement() { }

    static Transform randomTransform(RandomSource random) {
        return new Transform(random.nextInt(4), random.nextBoolean());
    }

    static int place(
        WorldGenLevel level,
        BlockPos origin,
        int centerX,
        int centerZ,
        int sourceX,
        int sourceY,
        int sourceZ,
        BlockState state,
        Transform transform
    ) {
        int[] transformed = transform.apply(sourceX - centerX, sourceZ - centerZ);
        int worldX = origin.getX() + transformed[0];
        int worldZ = origin.getZ() + transformed[1];
        int waterY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, worldX, worldZ);
        BlockPos water = new BlockPos(worldX, waterY, worldZ);

        if (!level.getFluidState(water).is(FluidTags.WATER)) {
            return 0;
        }

        if (sourceY <= 0) {
            BlockPos floor = water.below();
            if (!level.ensureCanWrite(floor) || !isNeutralSeabed(level.getBlockState(floor))) {
                return 0;
            }
            level.setBlock(floor, state, 2);
            return 1;
        }

        BlockPos target = water.above(sourceY - 1);
        if (!level.ensureCanWrite(target) || !level.getFluidState(target).is(FluidTags.WATER)) {
            return 0;
        }
        level.setBlock(target, state, 2);
        return 1;
    }

    private static boolean isNeutralSeabed(BlockState state) {
        return state.is(BlockTags.BASE_STONE_OVERWORLD)
            || state.is(Blocks.GRAVEL)
            || state.is(Blocks.SAND)
            || state.is(Blocks.RED_SAND)
            || state.is(Blocks.CLAY)
            || state.is(Blocks.MUD)
            || state.is(Blocks.TUFF)
            || state.is(Blocks.CALCITE)
            || state.is(Blocks.BLACKSTONE)
            || state.is(Blocks.SMOOTH_BASALT)
            || state.is(Blocks.BASALT);
    }

    record Transform(int rotation, boolean mirror) {
        int[] apply(int x, int z) {
            int transformedX = mirror ? -x : x;
            return switch (rotation) {
                case 1 -> new int[] {-z, transformedX};
                case 2 -> new int[] {-transformedX, -z};
                case 3 -> new int[] {z, -transformedX};
                default -> new int[] {transformedX, z};
            };
        }
    }
}
