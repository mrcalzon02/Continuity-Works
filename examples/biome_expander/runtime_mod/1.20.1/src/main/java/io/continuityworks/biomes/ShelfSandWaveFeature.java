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

/** OSF-023 Shelf Sand-wave / Ripple Fields. */
final class ShelfSandWaveFeature extends Feature<NoneFeatureConfiguration> {
    private static final int CENTER = 24;

    ShelfSandWaveFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        Transform transform = new Transform(random.nextInt(4), random.nextBoolean());
        int placed = 0;

        // Primary current patch: broken east-west crests with deterministic meander.
        int band = 0;
        for (int baseZ = 5; baseZ < 45; baseZ += 6, band++) {
            for (int x = 3; x < 46; x++) {
                int curve = (int) Math.round(1.7 * Math.sin((x + band * 5) * 0.22));
                int z = baseZ + curve;
                int breakSelector = Math.floorMod(x * 17 + band * 23, 13);
                if (breakSelector == 0 || breakSelector == 1) {
                    continue;
                }

                Block material = Math.floorMod(x + band, 7) == 0 ? Blocks.GRAVEL : Blocks.SAND;
                placed += put(level, origin, x, z, 0, material, transform);
                if (Math.floorMod(x + 2 * band, 4) != 0) {
                    placed += put(level, origin, x, z, 1, material, transform);
                }
                if (Math.floorMod(x + band, 11) == 0) {
                    placed += put(level, origin, x, z, 2, Blocks.SAND, transform);
                }
                int leeSelector = Math.floorMod(x * 3 + band, 5);
                if (leeSelector == 1 || leeSelector == 2) {
                    Block lee = Math.floorMod(x + band, 3) == 0 ? Blocks.CLAY : Blocks.SAND;
                    placed += put(level, origin, x, z + 1, 0, lee, transform);
                }
            }
        }

        // Second oblique current patch changes flow orientation rather than forming a grid.
        band = 0;
        for (int intercept = -8; intercept < 29; intercept += 7, band++) {
            for (int x = 24; x < 47; x++) {
                int z = intercept + (x - 24) / 2 + (int) Math.round(Math.sin((x + band * 4) * 0.35));
                if (z < 3 || z > 46 || Math.floorMod(x * 11 + band * 19, 12) == 0) {
                    continue;
                }

                Block material = Math.floorMod(x + band, 8) == 0 ? Blocks.GRAVEL : Blocks.SAND;
                placed += put(level, origin, x, z, 0, material, transform);
                if (Math.floorMod(x + band, 3) != 0) {
                    placed += put(level, origin, x, z, 1, material, transform);
                }
                if (Math.floorMod(x + 2 * band, 10) == 0) {
                    placed += put(level, origin, x, z + 1, 0, Blocks.CLAY, transform);
                }
            }
        }

        // Local scour/transition patches interrupt crest trains with mixed sediment.
        int[][] scourCenters = new int[][] {{10,12}, {17,33}, {34,14}, {39,37}};
        int[][] offsets = new int[][] {{0,0}, {1,0}, {-1,0}, {0,1}, {0,-1}, {2,0}, {-2,0}};
        for (int[] center : scourCenters) {
            for (int[] offset : offsets) {
                int x = center[0] + offset[0];
                int z = center[1] + offset[1];
                Block material = Math.floorMod(offset[0] + offset[1], 2) == 0 ? Blocks.GRAVEL : Blocks.CLAY;
                placed += put(level, origin, x, z, 0, material, transform);
            }
        }

        return placed > 0;
    }

    private int put(
        WorldGenLevel level,
        BlockPos origin,
        int sourceX,
        int sourceZ,
        int verticalOffset,
        Block block,
        Transform transform
    ) {
        int[] transformed = transform.apply(sourceX - CENTER, sourceZ - CENTER);
        int worldX = origin.getX() + transformed[0];
        int worldZ = origin.getZ() + transformed[1];
        int floorY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, worldX, worldZ);
        BlockPos target = new BlockPos(worldX, floorY + verticalOffset, worldZ);

        if (!level.ensureCanWrite(target) || !level.getFluidState(target).is(FluidTags.WATER)) {
            return 0;
        }

        setBlock(level, target, block.defaultBlockState());
        return 1;
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
