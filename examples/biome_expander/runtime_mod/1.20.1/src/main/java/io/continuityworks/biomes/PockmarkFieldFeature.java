package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * OSF-019 Pockmark Fields.
 *
 * <p>This is a terrain-deformation feature, not a decorative structure. It lowers
 * eligible seabed columns into irregular connected depressions, preserves the water
 * column, and relines the new floor with neutral sediment. Ore blocks and arbitrary
 * modded blocks are never selected as excavation material.</p>
 */
final class PockmarkFieldFeature extends Feature<NoneFeatureConfiguration> {
    PockmarkFieldFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        int basinCount = 5 + random.nextInt(5);
        int changed = 0;

        for (int basin = 0; basin < basinCount; basin++) {
            int centerX = origin.getX() + random.nextInt(41) - 20;
            int centerZ = origin.getZ() + random.nextInt(41) - 20;
            int radiusX = 4 + random.nextInt(6);
            int radiusZ = 4 + random.nextInt(6);
            int maxDepth = 1 + random.nextInt(5);
            long shapeSalt = random.nextLong();

            for (int dx = -radiusX - 1; dx <= radiusX + 1; dx++) {
                for (int dz = -radiusZ - 1; dz <= radiusZ + 1; dz++) {
                    double nx = dx / (double) radiusX;
                    double nz = dz / (double) radiusZ;
                    double normalized = Math.sqrt(nx * nx + nz * nz);
                    double jitter = edgeJitter(centerX + dx, centerZ + dz, shapeSalt);
                    if (normalized > 1.0 + jitter) {
                        continue;
                    }

                    double centerWeight = Math.max(0.0, 1.0 - normalized);
                    int depth = Math.max(1, (int) Math.ceil(maxDepth * centerWeight));
                    changed += depressColumn(level, centerX + dx, centerZ + dz, depth, shapeSalt);
                }
            }
        }

        return changed > 0;
    }

    private int depressColumn(WorldGenLevel level, int x, int z, int requestedDepth, long salt) {
        int waterY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, x, z);
        BlockPos water = new BlockPos(x, waterY, z);
        if (!level.getFluidState(water).is(FluidTags.WATER)) {
            return 0;
        }

        int topSolidY = waterY - 1;
        int carved = 0;
        for (int layer = 0; layer < requestedDepth; layer++) {
            BlockPos target = new BlockPos(x, topSolidY - layer, z);
            if (!level.ensureCanWrite(target)) {
                break;
            }

            BlockState state = level.getBlockState(target);
            if (!isNeutralSeabed(state)) {
                break;
            }

            setBlock(level, target, Blocks.WATER.defaultBlockState());
            carved++;
        }

        if (carved == 0) {
            return 0;
        }

        BlockPos newFloor = new BlockPos(x, topSolidY - carved, z);
        if (level.ensureCanWrite(newFloor) && isNeutralSeabed(level.getBlockState(newFloor))) {
            setBlock(level, newFloor, sedimentFor(x, z, salt).defaultBlockState());
        }

        return carved;
    }

    private static boolean isNeutralSeabed(BlockState state) {
        return state.is(BlockTags.BASE_STONE_OVERWORLD)
            || state.is(Blocks.GRAVEL)
            || state.is(Blocks.SAND)
            || state.is(Blocks.RED_SAND)
            || state.is(Blocks.CLAY)
            || state.is(Blocks.MUD)
            || state.is(Blocks.TUFF)
            || state.is(Blocks.CALCITE);
    }

    private static Block sedimentFor(int x, int z, long salt) {
        long hash = mix(x, z, salt);
        int selector = (int) Math.floorMod(hash, 10L);
        if (selector < 5) {
            return Blocks.CLAY;
        }
        if (selector < 8) {
            return Blocks.MUD;
        }
        return Blocks.GRAVEL;
    }

    private static double edgeJitter(int x, int z, long salt) {
        long hash = mix(x, z, salt);
        double unit = ((hash >>> 24) & 0xFFFFL) / 65535.0;
        return (unit - 0.5) * 0.24;
    }

    private static long mix(int x, int z, long salt) {
        long value = salt;
        value ^= (long) x * 0x9E3779B97F4A7C15L;
        value ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        value ^= value >>> 33;
        value *= 0xFF51AFD7ED558CCDL;
        value ^= value >>> 33;
        value *= 0xC4CEB9FE1A85EC53L;
        return value ^ (value >>> 33);
    }
}
