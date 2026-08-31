package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * OSF-006 Cooled Lava / Magma-tube Systems with the correlated OSF-007
 * skylight-and-collapse variant.
 *
 * <p>The feature preserves Infinite Domain's flooded open-water conduit contract:
 * it builds only the tube floor, shell, sediment drapes, pressure ridges, and
 * optional collapse rubble. Interior water is never replaced with air.</p>
 */
final class CooledLavaTubeFeature extends Feature<NoneFeatureConfiguration> {
    private static final int SOURCE_CENTER_X = 24;
    private static final int SOURCE_CENTER_Z = 20;

    private static final int[][] DRAPES = new int[][] {
        {7,13}, {9,13}, {11,13}, {18,19}, {20,19}, {22,19},
        {34,18}, {36,18}, {38,18}, {24,25}, {30,25}, {24,32}, {30,32}
    };

    private static final int[][] FLOW_FRONTS = new int[][] {
        {1,0,12}, {1,1,13}, {2,0,19}, {46,0,14}, {47,0,17}, {46,1,20},
        {24,0,38}, {25,1,38}, {29,0,38}, {30,1,37}, {31,0,38}
    };

    private static final int[][] SKYLIGHT_RIM = new int[][] {
        {17,5,13}, {17,6,14}, {17,6,15}, {17,5,16}, {18,6,12},
        {19,7,12}, {20,6,12}, {22,5,13}, {23,6,14}, {23,6,15},
        {23,5,17}, {22,6,18}, {21,7,18}, {20,6,18}, {18,5,18}
    };

    private static final int[][] SKYLIGHT_RUBBLE = new int[][] {
        {18,1,13}, {18,2,13}, {19,1,13}, {19,1,14}, {20,1,13},
        {21,1,17}, {21,2,17}, {22,1,17}, {22,1,16}, {20,1,17},
        {17,0,14}, {23,0,16}, {19,0,18}, {22,0,12}
    };

    private static final int[][] SKYLIGHT_SEDIMENT = new int[][] {
        {16,11}, {17,11}, {18,11}, {21,19}, {22,19}, {23,19}, {24,18}, {16,18}
    };

    CooledLavaTubeFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();

        int floorY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, origin.getX(), origin.getZ());
        int surfaceY = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, origin.getX(), origin.getZ());
        if (surfaceY - floorY < 10) {
            return false;
        }

        Transform transform = new Transform(random.nextInt(4), random.nextBoolean());
        boolean skylightVariant = random.nextInt(4) == 0;
        int placed = 0;

        // Long flooded primary conduit. The eastern end bends toward +Z.
        for (int x = 3; x <= 45; x++) {
            int bend = x >= 30 ? Math.max(0, Math.min(2, ((x - 30) / 5) + 1)) : 0;
            int centerZ = 15 + bend;

            for (int dz = -3; dz <= 3; dz++) {
                Block floor = ((x + dz) % 4 == 0) ? Blocks.TUFF : Blocks.SMOOTH_BASALT;
                placed += put(level, origin, floorY, x, 0, centerZ + dz, floor, transform, skylightVariant);
            }

            for (int y = 1; y <= 3; y++) {
                Block northWall = ((x + y) % 3 == 0) ? Blocks.BLACKSTONE : Blocks.BASALT;
                Block southWall = ((x + 2 * y) % 3 == 0) ? Blocks.BLACKSTONE : Blocks.BASALT;
                placed += put(level, origin, floorY, x, y, centerZ - 4, northWall, transform, skylightVariant);
                placed += put(level, origin, floorY, x, y, centerZ + 4, southWall, transform, skylightVariant);
            }

            placed += put(level, origin, floorY, x, 4, centerZ - 3, Blocks.BASALT, transform, skylightVariant);
            placed += put(level, origin, floorY, x, 4, centerZ + 3, Blocks.BASALT, transform, skylightVariant);

            if (x != 14 && x != 31 && x != 32) {
                for (int dz = -2; dz <= 2; dz++) {
                    int roofY = Math.abs(dz) == 2 ? 5 : 6;
                    Block roof = ((x + dz) % 5 == 0) ? Blocks.BLACKSTONE : Blocks.SMOOTH_BASALT;
                    placed += put(level, origin, floorY, x, roofY, centerZ + dz, roof, transform, skylightVariant);
                }
            } else {
                placed += put(level, origin, floorY, x, 5, centerZ - 2, Blocks.BASALT, transform, skylightVariant);
                placed += put(level, origin, floorY, x, 5, centerZ + 2, Blocks.BASALT, transform, skylightVariant);
                placed += put(level, origin, floorY, x, 6, centerZ, Blocks.BLACKSTONE, transform, skylightVariant);
            }

            if (x % 6 == 0) {
                placed += put(level, origin, floorY, x, 1, centerZ - 5, Blocks.BLACKSTONE, transform, skylightVariant);
                placed += put(level, origin, floorY, x, 2, centerZ - 5, Blocks.BASALT, transform, skylightVariant);
                placed += put(level, origin, floorY, x, 1, centerZ + 5, Blocks.BLACKSTONE, transform, skylightVariant);
                placed += put(level, origin, floorY, x, 2, centerZ + 5, Blocks.BASALT, transform, skylightVariant);
            }
        }

        // South-turning lateral branch: this makes the formation a network, not a straight tunnel prop.
        final int branchX = 27;
        for (int z = 17; z <= 36; z++) {
            for (int dx = -3; dx <= 3; dx++) {
                Block floor = ((z + dx) % 4 == 0) ? Blocks.TUFF : Blocks.SMOOTH_BASALT;
                placed += put(level, origin, floorY, branchX + dx, 0, z, floor, transform, skylightVariant);
            }

            for (int y = 1; y <= 3; y++) {
                Block westWall = ((z + y) % 3 == 0) ? Blocks.BLACKSTONE : Blocks.BASALT;
                Block eastWall = ((z + 2 * y) % 3 == 0) ? Blocks.BLACKSTONE : Blocks.BASALT;
                placed += put(level, origin, floorY, branchX - 4, y, z, westWall, transform, skylightVariant);
                placed += put(level, origin, floorY, branchX + 4, y, z, eastWall, transform, skylightVariant);
            }

            placed += put(level, origin, floorY, branchX - 3, 4, z, Blocks.BASALT, transform, skylightVariant);
            placed += put(level, origin, floorY, branchX + 3, 4, z, Blocks.BASALT, transform, skylightVariant);

            if (z != 28) {
                for (int dx = -2; dx <= 2; dx++) {
                    int roofY = Math.abs(dx) == 2 ? 5 : 6;
                    Block roof = ((z + dx) % 5 == 0) ? Blocks.BLACKSTONE : Blocks.SMOOTH_BASALT;
                    placed += put(level, origin, floorY, branchX + dx, roofY, z, roof, transform, skylightVariant);
                }
            }

            if (z % 5 == 0) {
                placed += put(level, origin, floorY, branchX - 5, 1, z, Blocks.BLACKSTONE, transform, skylightVariant);
                placed += put(level, origin, floorY, branchX + 5, 1, z, Blocks.BLACKSTONE, transform, skylightVariant);
            }
        }

        for (int[] point : DRAPES) {
            placed += put(level, origin, floorY, point[0], 7, point[1], Blocks.TUFF, transform, skylightVariant);
            if ((point[0] + point[1]) % 3 == 0) {
                placed += put(level, origin, floorY, point[0], 8, point[1], Blocks.GRAVEL, transform, skylightVariant);
            }
        }

        for (int[] point : FLOW_FRONTS) {
            Block block = ((point[0] + point[2]) % 2 == 0) ? Blocks.BASALT : Blocks.BLACKSTONE;
            placed += put(level, origin, floorY, point[0], point[1], point[2], block, transform, skylightVariant);
        }

        if (skylightVariant) {
            placed += addSkylightCollapse(level, origin, floorY, transform);
        }

        return placed > 0;
    }

    private int addSkylightCollapse(WorldGenLevel level, BlockPos origin, int floorY, Transform transform) {
        int placed = 0;

        for (int i = 0; i < SKYLIGHT_RIM.length; i++) {
            int[] point = SKYLIGHT_RIM[i];
            Block block = i % 3 == 0 ? Blocks.BLACKSTONE : Blocks.BASALT;
            placed += putRaw(level, origin, floorY, point[0], point[1], point[2], block, transform);
            if (i == 1 || i == 5 || i == 10 || i == 12) {
                placed += putRaw(level, origin, floorY, point[0], point[1] + 1, point[2], Blocks.TUFF, transform);
            }
        }

        for (int i = 0; i < SKYLIGHT_RUBBLE.length; i++) {
            int[] point = SKYLIGHT_RUBBLE[i];
            Block block = i % 5 == 0 ? Blocks.GRAVEL : (i % 3 == 0 ? Blocks.TUFF : Blocks.BLACKSTONE);
            placed += putRaw(level, origin, floorY, point[0], point[1], point[2], block, transform);
        }

        for (int[] point : SKYLIGHT_SEDIMENT) {
            Block block = (point[0] + point[1]) % 2 == 0 ? Blocks.GRAVEL : Blocks.TUFF;
            placed += putRaw(level, origin, floorY, point[0], 0, point[1], block, transform);
        }

        return placed;
    }

    private int put(
        WorldGenLevel level,
        BlockPos origin,
        int floorY,
        int sourceX,
        int sourceY,
        int sourceZ,
        Block block,
        Transform transform,
        boolean skylightVariant
    ) {
        if (skylightVariant && isSkylightCut(sourceX, sourceY, sourceZ)) {
            return 0;
        }
        return putRaw(level, origin, floorY, sourceX, sourceY, sourceZ, block, transform);
    }

    private int putRaw(
        WorldGenLevel level,
        BlockPos origin,
        int floorY,
        int sourceX,
        int sourceY,
        int sourceZ,
        Block block,
        Transform transform
    ) {
        int localX = sourceX - SOURCE_CENTER_X;
        int localZ = sourceZ - SOURCE_CENTER_Z;
        int[] transformed = transform.apply(localX, localZ);
        BlockPos target = new BlockPos(
            origin.getX() + transformed[0],
            floorY + sourceY,
            origin.getZ() + transformed[1]
        );

        if (!level.ensureCanWrite(target) || !level.getFluidState(target).is(FluidTags.WATER)) {
            return 0;
        }

        setBlock(level, target, block.defaultBlockState());
        return 1;
    }

    private static boolean isSkylightCut(int x, int y, int z) {
        if (x >= 18 && x <= 22 && z >= 13 && z <= 17 && y >= 5 && y <= 8) {
            return true;
        }
        if (y < 4 || y > 6) {
            return false;
        }
        return (x == 19 && z == 12)
            || (x == 20 && z == 12)
            || (x == 21 && z == 12)
            || (x == 18 && z == 18)
            || (x == 19 && z == 18)
            || (x == 22 && z == 18);
    }

    private record Transform(int rotation, boolean mirror) {
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
