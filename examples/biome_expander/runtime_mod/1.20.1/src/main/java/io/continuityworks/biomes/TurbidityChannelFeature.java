package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * OSF-027 Turbidity-current Channels.
 *
 * <p>The field is evaluated from absolute world coordinates and the world seed, so
 * neighboring chunks independently reconstruct the same connected sinuous channel
 * network. Narrow thalwegs erode the seabed while wider shoulders deposit levees.</p>
 */
final class TurbidityChannelFeature extends Feature<NoneFeatureConfiguration> {
    private static final long SALT = 0x4F53463032374C4CL;
    private static final double CHANNEL_SPACING = 176.0;
    private static final double CHANNEL_HALF_WIDTH = 4.25;
    private static final double LEVEE_OUTER_WIDTH = 10.5;

    TurbidityChannelFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        long seed = level.getSeed() ^ SALT;
        int chunkMinX = (origin.getX() >> 4) << 4;
        int chunkMinZ = (origin.getZ() >> 4) << 4;
        int changed = 0;

        for (int localX = 0; localX < 16; localX++) {
            for (int localZ = 0; localZ < 16; localZ++) {
                int x = chunkMinX + localX;
                int z = chunkMinZ + localZ;
                ChannelSample sample = sample(x, z, seed);

                if (sample.distance <= CHANNEL_HALF_WIDTH) {
                    double centerWeight = 1.0 - sample.distance / CHANNEL_HALF_WIDTH;
                    int depth = 3 + (int) Math.round(centerWeight * (7.0 + sample.roughness * 3.0));
                    changed += erode(level, x, z, Math.min(14, depth), seed);
                } else if (sample.distance <= LEVEE_OUTER_WIDTH) {
                    double leveeWeight = 1.0 - ((sample.distance - CHANNEL_HALF_WIDTH)
                        / (LEVEE_OUTER_WIDTH - CHANNEL_HALF_WIDTH));
                    int height = leveeWeight > 0.58 ? 2 : 1;
                    changed += deposit(level, x, z, height, seed);
                }
            }
        }

        return changed > 0;
    }

    private static ChannelSample sample(int x, int z, long seed) {
        double phaseA = unit(seed ^ 0x3C79AC492BA7B653L) * Math.PI * 2.0;
        double phaseB = unit(seed ^ 0x1C69B3F74AC4AE35L) * Math.PI * 2.0;

        double eastWestMeander = Math.sin(x * 0.012 + phaseA) * 24.0
            + Math.sin(x * 0.0045 + phaseB) * 13.0;
        double northSouthMeander = Math.sin(z * 0.0105 + phaseB) * 21.0
            + Math.sin(z * 0.0040 + phaseA) * 11.0;

        double eastWestDistance = wrappedDistance(z - eastWestMeander, CHANNEL_SPACING);
        double northSouthDistance = wrappedDistance(x - northSouthMeander, CHANNEL_SPACING * 1.35);

        // The secondary orientation is deliberately less dominant; it creates branching
        // and occasional confluences without turning the seabed into a grid.
        double distance = Math.min(eastWestDistance, northSouthDistance * 1.28);
        double roughness = 0.5 + 0.5 * Math.sin((x + z) * 0.037 + phaseA - phaseB);
        return new ChannelSample(distance, roughness);
    }

    private static int erode(WorldGenLevel level, int x, int z, int requestedDepth, long seed) {
        int waterY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, x, z);
        BlockPos water = new BlockPos(x, waterY, z);
        if (!level.getFluidState(water).is(FluidTags.WATER)) {
            return 0;
        }

        int topSolidY = waterY - 1;
        int carved = 0;
        for (int layer = 0; layer < requestedDepth; layer++) {
            BlockPos target = new BlockPos(x, topSolidY - layer, z);
            if (!level.ensureCanWrite(target) || !isNeutralSeabed(level.getBlockState(target))) {
                break;
            }
            level.setBlock(target, Blocks.WATER.defaultBlockState(), 2);
            carved++;
        }

        if (carved > 0) {
            BlockPos newFloor = new BlockPos(x, topSolidY - carved, z);
            if (level.ensureCanWrite(newFloor) && isNeutralSeabed(level.getBlockState(newFloor))) {
                level.setBlock(newFloor, sediment(x, z, seed).defaultBlockState(), 2);
            }
        }
        return carved;
    }

    private static int deposit(WorldGenLevel level, int x, int z, int height, long seed) {
        int floorY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, x, z);
        int placed = 0;
        for (int y = 0; y < height; y++) {
            BlockPos target = new BlockPos(x, floorY + y, z);
            if (!level.ensureCanWrite(target) || !level.getFluidState(target).is(FluidTags.WATER)) {
                break;
            }
            Block block = y == 0 ? sediment(x, z, seed) : Blocks.GRAVEL;
            level.setBlock(target, block.defaultBlockState(), 2);
            placed++;
        }
        return placed;
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

    private static Block sediment(int x, int z, long seed) {
        long h = mix(seed ^ ((long) x * 341873128712L) ^ ((long) z * 132897987541L));
        int selector = (int) Math.floorMod(h, 12L);
        if (selector < 5) {
            return Blocks.GRAVEL;
        }
        if (selector < 9) {
            return Blocks.CLAY;
        }
        return Blocks.SAND;
    }

    private static double wrappedDistance(double value, double period) {
        double wrapped = value - Math.floor(value / period + 0.5) * period;
        return Math.abs(wrapped);
    }

    private static double unit(long value) {
        long mixed = mix(value);
        return ((mixed >>> 11) & ((1L << 53) - 1)) / (double) (1L << 53);
    }

    private static long mix(long value) {
        value ^= value >>> 33;
        value *= 0xFF51AFD7ED558CCDL;
        value ^= value >>> 33;
        value *= 0xC4CEB9FE1A85EC53L;
        return value ^ (value >>> 33);
    }

    private record ChannelSample(double distance, double roughness) { }
}
