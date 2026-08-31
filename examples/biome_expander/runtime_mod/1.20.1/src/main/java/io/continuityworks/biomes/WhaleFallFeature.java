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

/** OSF-045 neutral whale-fall ecological site family. */
final class WhaleFallFeature extends Feature<NoneFeatureConfiguration> {
    private static final int CENTER_X = 19;
    private static final int CENTER_Z = 11;

    WhaleFallFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        AbyssalEcologyPlacement.Transform transform = AbyssalEcologyPlacement.randomTransform(random);
        int roll = random.nextInt(7);
        int changed = sedimentApron(level, origin, transform, roll >= 5);

        if (roll < 3) {
            changed += coherent(level, origin, transform);
        } else if (roll < 5) {
            changed += dispersed(level, origin, transform);
        } else {
            changed += sedimented(level, origin, transform);
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
        for (int x = 1; x < 38; x++) {
            for (int z = 2; z < 21; z++) {
                double dx = (x - 19) / 18.0;
                double dz = (z - 11) / 9.0;
                if (dx * dx + dz * dz > 1.0) {
                    continue;
                }
                int h = Math.floorMod(x * 19 + z * 31 + (old ? 7 : 0), 29);
                Block block = null;
                if (h == 0 || h == 1) {
                    block = Blocks.MUD;
                } else if (h == 2 || h == 3) {
                    block = Blocks.CLAY;
                } else if (h == 4) {
                    block = Blocks.GRAVEL;
                }
                if (block != null) {
                    changed += put(level, origin, x, 0, z, block.defaultBlockState(), transform);
                }
            }
        }
        return changed;
    }

    private int coherent(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        int[][] head = new int[][] {
            {4,2,10},{4,2,11},{4,2,12},{5,2,9},{5,2,10},{5,2,11},{5,2,12},{5,2,13},
            {6,2,9},{6,2,10},{6,2,11},{6,2,12},{6,2,13},{7,2,10},{7,2,11},{7,2,12},
            {5,3,10},{5,3,11},{5,3,12},{6,3,10},{6,3,11},{6,3,12}
        };
        for (int[] p : head) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.BONE_BLOCK.defaultBlockState(), transform);
        }

        for (int x = 4; x < 8; x++) {
            changed += put(level, origin, x, 1, 8, axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
            changed += put(level, origin, x, 1, 14, axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
        }
        for (int x = 8; x < 33; x++) {
            if (x != 17 && x != 28) {
                changed += put(level, origin, x, 2, 11, axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
            }
        }
        int[] ribX = new int[] {10, 13, 16, 19, 22, 25};
        for (int x : ribX) {
            for (int side : new int[] {-1, 1}) {
                for (int d = 1; d <= 5; d++) {
                    int y = 2 + (d <= 2 ? 1 : (d <= 4 ? 2 : 1));
                    changed += put(level, origin, x, y, 11 + side * d, axis(Blocks.BONE_BLOCK, Direction.Axis.Z), transform);
                }
                changed += put(level, origin, x, 5, 11 + side * 3, axis(Blocks.BONE_BLOCK, Direction.Axis.Y), transform);
            }
        }
        for (int x = 33; x < 37; x++) {
            changed += put(level, origin, x, 2, 11, axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
        }
        changed += put(level, origin, 36, 1, 9, axis(Blocks.BONE_BLOCK, Direction.Axis.Z), transform);
        changed += put(level, origin, 36, 1, 13, axis(Blocks.BONE_BLOCK, Direction.Axis.Z), transform);

        int[][] calcite = new int[][] {{9,1,8},{12,1,15},{18,1,6},{23,1,16},{29,1,9},{31,1,14}};
        for (int[] p : calcite) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.CALCITE.defaultBlockState(), transform);
        }
        return changed;
    }

    private int dispersed(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        int[][] spine = new int[][] {
            {8,2,11},{9,2,11},{11,2,12},{12,2,12},{15,2,10},{16,2,10},
            {20,2,12},{21,2,12},{24,2,9},{27,2,13},{30,2,12}
        };
        for (int[] p : spine) {
            changed += put(level, origin, p[0], p[1], p[2], axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
        }

        int[][] ribs = new int[][] {{10,5,1},{13,7,-1},{17,4,1},{20,6,-1},{24,5,1},{28,4,-1}};
        for (int[] rib : ribs) {
            int x = rib[0];
            int length = rib[1];
            int side = rib[2];
            int baseZ = 11 + side * ((x / 3) % 3);
            for (int d = 1; d < length; d++) {
                int y = 1 + (d < 3 ? 1 : 2);
                changed += put(level, origin, x, y, baseZ + side * d, axis(Blocks.BONE_BLOCK, Direction.Axis.Z), transform);
            }
        }

        int[][] head = new int[][] {{5,1,8},{6,1,8},{4,2,9},{7,1,14},{8,2,15},{6,2,15}};
        int[][] scattered = new int[][] {{18,1,17},{22,1,6},{26,1,16},{31,1,7},{34,1,13}};
        int[][] mineral = new int[][] {{6,0,12},{11,0,16},{15,0,7},{19,0,15},{25,0,6},{32,0,15}};
        for (int[] p : head) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.BONE_BLOCK.defaultBlockState(), transform);
        }
        for (int[] p : scattered) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.BONE_BLOCK.defaultBlockState(), transform);
        }
        for (int[] p : mineral) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.CALCITE.defaultBlockState(), transform);
        }
        return changed;
    }

    private int sedimented(
        WorldGenLevel level,
        BlockPos origin,
        AbyssalEcologyPlacement.Transform transform
    ) {
        int changed = 0;
        for (int x = 7; x < 34; x++) {
            if (x % 5 != 0) {
                changed += put(level, origin, x, 1, 11, axis(Blocks.BONE_BLOCK, Direction.Axis.X), transform);
            }
        }
        for (int x : new int[] {10, 14, 18, 22, 26}) {
            for (int side : new int[] {-1, 1}) {
                for (int d = 1; d < 5; d++) {
                    int y = d < 3 ? 1 : 0;
                    changed += put(level, origin, x, y, 11 + side * d, axis(Blocks.BONE_BLOCK, Direction.Axis.Z), transform);
                }
            }
        }
        for (int x = 9; x < 31; x++) {
            if (x % 4 == 0 || x % 4 == 1) {
                changed += put(level, origin, x, 2, 11, Blocks.MUD.defaultBlockState(), transform);
            }
        }
        for (int[] p : new int[][] {{10,1,9},{14,1,14},{18,1,8},{22,1,15},{27,1,9},{30,1,13}}) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.CLAY.defaultBlockState(), transform);
        }
        for (int[] p : new int[][] {
            {4,1,10},{4,1,11},{4,1,12},{5,1,9},{5,1,10},{5,1,11},{5,1,12},{5,1,13},
            {6,1,10},{6,1,11},{6,1,12}
        }) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.BONE_BLOCK.defaultBlockState(), transform);
        }
        for (int[] p : new int[][] {{5,2,10},{5,2,12},{7,1,9},{8,1,13},{16,1,16},{25,1,7},{32,1,12}}) {
            changed += put(level, origin, p[0], p[1], p[2], Blocks.CALCITE.defaultBlockState(), transform);
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
