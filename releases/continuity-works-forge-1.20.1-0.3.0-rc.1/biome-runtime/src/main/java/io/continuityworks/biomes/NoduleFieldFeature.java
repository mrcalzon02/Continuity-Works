package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** OSF-037 Manganese / Polymetallic Nodule-field Analogues. */
final class NoduleFieldFeature extends Feature<NoneFeatureConfiguration> {
    private static final int CENTER = 20;
    private static final int[][] PROVINCES = new int[][] {
        {9,10,7}, {29,9,6}, {15,29,8}, {31,30,7}, {21,20,5}
    };

    NoduleFieldFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        Transform transform = new Transform(random.nextInt(4), random.nextBoolean());
        int changed = 0;

        for (int province = 0; province < PROVINCES.length; province++) {
            int cx = PROVINCES[province][0];
            int cz = PROVINCES[province][1];
            int radius = PROVINCES[province][2];

            for (int x = Math.max(1, cx - radius); x <= Math.min(39, cx + radius); x++) {
                for (int z = Math.max(1, cz - radius); z <= Math.min(39, cz + radius); z++) {
                    if (inScourCorridor(x, z)) {
                        continue;
                    }

                    int dx = x - cx;
                    int dz = z - cz;
                    double roughRadius = radius * radius
                        + 2.5 * Math.sin((x + province * 7) * 0.63)
                        + 2.0 * Math.cos((z - province * 5) * 0.51);
                    if (dx * dx * 1.15 + dz * dz * 0.85 > roughRadius) {
                        continue;
                    }

                    int matrix = Math.floorMod(x * 31 + z * 17 + province * 43, 23);
                    if (matrix <= 4) {
                        changed += replaceFloor(level, origin, x, z, Blocks.GRAVEL, transform);
                    }

                    int clastSelector = Math.floorMod(x * 13 + z * 29 + province * 11, 17);
                    if (clastSelector == 0 || clastSelector == 1) {
                        Block clast = Math.floorMod(x + z + province, 3) == 0
                            ? Blocks.COBBLED_DEEPSLATE
                            : Blocks.BLACKSTONE;
                        changed += replaceFloor(level, origin, x, z, clast, transform);

                        if (Math.floorMod(x * 7 + z * 5 + province, 11) == 0) {
                            changed += placeNodule(level, origin, x, z, transform);
                        }
                    }
                }
            }
        }

        return changed > 0;
    }

    private int replaceFloor(
        WorldGenLevel level,
        BlockPos origin,
        int sourceX,
        int sourceZ,
        Block block,
        Transform transform
    ) {
        int[] transformed = transform.apply(sourceX - CENTER, sourceZ - CENTER);
        int worldX = origin.getX() + transformed[0];
        int worldZ = origin.getZ() + transformed[1];
        int waterY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, worldX, worldZ);
        BlockPos water = new BlockPos(worldX, waterY, worldZ);
        BlockPos floor = water.below();

        if (!level.getFluidState(water).is(FluidTags.WATER)
            || !level.ensureCanWrite(floor)
            || !isNeutralSeabed(level.getBlockState(floor))) {
            return 0;
        }

        setBlock(level, floor, block.defaultBlockState());
        return 1;
    }

    private int placeNodule(
        WorldGenLevel level,
        BlockPos origin,
        int sourceX,
        int sourceZ,
        Transform transform
    ) {
        int[] transformed = transform.apply(sourceX - CENTER, sourceZ - CENTER);
        int worldX = origin.getX() + transformed[0];
        int worldZ = origin.getZ() + transformed[1];
        int waterY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, worldX, worldZ);
        BlockPos target = new BlockPos(worldX, waterY, worldZ);

        if (!level.ensureCanWrite(target) || !level.getFluidState(target).is(FluidTags.WATER)) {
            return 0;
        }

        BlockState nodule = Blocks.POLISHED_BLACKSTONE_BUTTON.defaultBlockState()
            .setValue(BlockStateProperties.ATTACH_FACE, AttachFace.FLOOR)
            .setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)
            .setValue(BlockStateProperties.POWERED, false);
        setBlock(level, target, nodule);
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
            || state.is(Blocks.CALCITE);
    }

    private static boolean inScourCorridor(int x, int z) {
        if (x < 4 || x >= 37) {
            return false;
        }
        int centerZ = 20 + (int) Math.round(2.2 * Math.sin(x * 0.28));
        return Math.abs(z - centerZ) <= 1;
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
