package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** OSF-049 neutral natural wood-fall site family. */
final class WoodFallFeature extends Feature<NoneFeatureConfiguration> {
    private static final int CENTER_X = 17;
    private static final int CENTER_Z = 12;

    WoodFallFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        AbyssalEcologyPlacement.Transform transform = AbyssalEcologyPlacement.randomTransform(random);
        int roll = random.nextInt(8);
        int changed = sedimentApron(level, origin, transform, roll >= 6);

        if (roll < 3) {
            changed += rooted(level, origin, transform);
        } else if (roll < 6) {
            changed += fragmented(level, origin, transform);
        } else {
            changed += buried(level, origin, transform);
        }
        return changed > 0;
    }

    private int sedimentApron(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform,
        boolean old
    ) {
        int changed = 0;
        for (int x = 2; x < 33; x++) {
            for (int z = 3; z < 22; z++) {
                double dx = (x - 17) / 15.0;
                double dz = (z - 12) / 9.0;
                if (dx * dx + dz * dz > 1.0) {
                    continue;
                }
                int h = Math.floorMod(x * 23 + z * 13 + (old ? 11 : 0), 31);
                Block block = null;
                if (h == 0 || h == 1) {
                    block = Blocks.MUD;
                } else if (h == 2) {
                    block = Blocks.CLAY;
                } else if (h == 3) {
                    block = Blocks.GRAVEL;
                }
                if (block != null) {
                    changed += put(level, origin, x, 0, z, block.defaultBlockState(), transform);
                }
            }
        }
        return changed;
    }

    private int rooted(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        int[][] segments = new int[][] {
            {6,2,12},{7,2,12},{8,2,12},{9,2,12},{10,2,12},{11,2,12},
            {12,2,13},{13,2,13},{14,2,13},{15,2,13},{16,2,13},{17,2,13},
            {18,3,13},{19,3,13},{20,3,13},{21,3,13},{22,3,13},{23,3,13},
            {24,2,13},{25,2,13},{26,2,13}
        };
        for (int i = 0; i < segments.length; i++) {
            int[] p = segments[i];
            Block material = i % 5 == 0 ? Blocks.STRIPPED_OAK_LOG : Blocks.DARK_OAK_LOG;
            changed += put(level, origin, p[0], p[1], p[2], axis(material, Direction.Axis.X), transform);
        }

        int[][][] roots = new int[][][] {
            {{6,2,12},{5,2,11},{4,1,10},{3,1,9}},
            {{6,2,12},{5,2,13},{4,1,15},{3,1,17}},
            {{7,2,12},{6,2,10},{6,1,8},{5,1,6}},
            {{7,2,13},{6,2,15},{6,1,18},{7,1,20}}
        };
        for (int root = 0; root < roots.length; root++) {
            for (int j = 1; j < roots[root].length; j++) {
                int[] p = roots[root][j];
                Block material = Math.floorMod(root + j - 1, 2) == 0 ? Blocks.DARK_OAK_LOG : Blocks.OAK_LOG;
                changed += put(level, origin, p[0], p[1], p[2], axis(material, Direction.Axis.Z), transform);
            }
        }

        int[][] branches = new int[][] {{12,-1,4},{16,1,5},{21,-1,3},{24,1,4}};
        for (int[] branch : branches) {
            int x = branch[0];
            int side = branch[1];
            int length = branch[2];
            for (int d = 1; d <= length; d++) {
                int y = d < 3 ? 2 : 1;
                changed += put(level, origin, x, y, 13 + side * d, axis(Blocks.OAK_LOG, Direction.Axis.Z), transform);
            }
        }
        return changed;
    }

    private int fragmented(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        Object[][] pieces = new Object[][] {
            {4,1,7,10,Blocks.OAK_LOG},
            {15,2,10,8,Blocks.DARK_OAK_LOG},
            {24,1,17,7,Blocks.STRIPPED_OAK_LOG}
        };
        for (Object[] piece : pieces) {
            int x = (Integer) piece[0];
            int y = (Integer) piece[1];
            int z = (Integer) piece[2];
            int length = (Integer) piece[3];
            Block material = (Block) piece[4];
            for (int i = 0; i < length; i++) {
                if (i != 3) {
                    changed += put(level, origin, x + i, y, z, axis(material, Direction.Axis.X), transform);
                }
            }
        }
        for (int z = 5; z < 11; z++) {
            if (z != 8) {
                changed += put(level, origin, 12, 1, z, axis(Blocks.OAK_LOG, Direction.Axis.Z), transform);
            }
        }
        for (int z = 13; z < 20; z++) {
            if (z != 15) {
                changed += put(level, origin, 29, 1, z, axis(Blocks.DARK_OAK_LOG, Direction.Axis.Z), transform);
            }
        }
        for (int[] p : new int[][] {{8,0,16},{11,0,18},{18,0,6},{22,0,8},{28,0,11}}) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.GRAVEL.defaultBlockState(), transform);
        }
        return changed;
    }

    private int buried(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        for (int x = 5; x < 30; x++) {
            if (x % 5 == 0 || x % 5 == 1 || x % 5 == 2) {
                int y = x % 7 == 0 ? 2 : 1;
                int z = 12 + (x > 18 ? 1 : 0);
                Block material = x % 4 == 0 ? Blocks.STRIPPED_OAK_LOG : Blocks.DARK_OAK_LOG;
                changed += put(level, origin, x, y, z, axis(material, Direction.Axis.X), transform);
            }
        }

        int[][][] roots = new int[][][] {
            {{5,1,12},{4,1,10},{3,0,8}},
            {{6,1,12},{5,1,14},{4,0,17}},
            {{7,1,12},{7,0,16},{8,0,19}}
        };
        for (int[][] path : roots) {
            for (int[] p : path) {
                changed += put(level, origin, p[0], p[1], p[2], axis(Blocks.OAK_LOG, Direction.Axis.Z), transform);
            }
        }

        for (int x = 7; x < 29; x++) {
            int z = 12 + (x > 18 ? 1 : 0);
            if (x % 3 == 0) {
                changed += put(level, origin, x, 2, z, Blocks.MUD.defaultBlockState(), transform);
            }
            if (x % 4 == 0) {
                changed += put(level, origin, x, 1, 11, Blocks.CLAY.defaultBlockState(), transform);
            }
        }
        for (int[] p : new int[][] {{10,1,8},{13,1,16},{19,1,9},{25,1,16},{30,1,12}}) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.GRAVEL.defaultBlockState(), transform);
        }
        return changed;
    }

    private static int put(
        WorldGenLevel level,
        BlockPos origin,
        int x,
        int y,
        int z,
        BlockState state,
        AbyssalEcologyPlacement.Transform transform
    ) {
        return AbyssalEcologyPlacement.place(level, origin, CENTER_X, CENTER_Z, x, y, z, state, transform);
    }

    private static BlockState axis(Block block, Direction.Axis axis) {
        return block.defaultBlockState().setValue(BlockStateProperties.AXIS, axis);
    }
}
