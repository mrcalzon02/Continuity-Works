package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * Runtime seafloor generators adapted from Infinite Domain's Abyssal feature library.
 *
 * <p>These are ordinary Forge features. They are registered when the mod JAR is loaded and
 * are attached to owned biome tags through data-driven biome modifiers. No external
 * generator, installer, or validation step is required at runtime.</p>
 */
public final class AbyssalSeafloorFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(
        Registries.FEATURE,
        ContinuityWorksBiomeTemplates.MOD_ID
    );

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> PILLOW_LAVA_FIELD = FEATURES.register(
        "pillow_lava_field",
        PillowLavaFieldFeature::new
    );

    private AbyssalSeafloorFeatures() { }

    public static void register(IEventBus modBus) {
        FEATURES.register(modBus);
    }

    /**
     * OSF-005 Pillow-lava Fields.
     *
     * <p>The source geometry is the Infinite Domain 33x6x33 pillow-lava template, translated
     * into a procedural feature so Continuity Works can reuse it across any compatible
     * underwater biome. Each placement conforms to the local ocean floor and may rotate or
     * mirror the source field, preserving open water gaps and avoiding a repeated stamp.</p>
     */
    private static final class PillowLavaFieldFeature extends Feature<NoneFeatureConfiguration> {
        private static final Lobe[] LOBES = new Lobe[] {
            new Lobe(6, 7, 3.8, 2, Blocks.BASALT),
            new Lobe(10, 6, 3.2, 2, Blocks.SMOOTH_BASALT),
            new Lobe(14, 8, 4.4, 3, Blocks.BASALT),
            new Lobe(19, 6, 3.6, 2, Blocks.BLACKSTONE),
            new Lobe(24, 8, 4.2, 3, Blocks.BASALT),
            new Lobe(27, 12, 3.0, 2, Blocks.SMOOTH_BASALT),
            new Lobe(21, 13, 4.8, 3, Blocks.BASALT),
            new Lobe(15, 14, 3.5, 2, Blocks.BLACKSTONE),
            new Lobe(9, 13, 4.1, 3, Blocks.BASALT),
            new Lobe(5, 17, 3.0, 2, Blocks.SMOOTH_BASALT),
            new Lobe(11, 19, 4.5, 3, Blocks.BASALT),
            new Lobe(17, 20, 3.8, 2, Blocks.BLACKSTONE),
            new Lobe(23, 19, 4.4, 3, Blocks.BASALT),
            new Lobe(28, 19, 2.8, 2, Blocks.SMOOTH_BASALT),
            new Lobe(26, 25, 3.9, 2, Blocks.BASALT),
            new Lobe(20, 26, 4.2, 3, Blocks.BLACKSTONE),
            new Lobe(14, 26, 3.4, 2, Blocks.SMOOTH_BASALT),
            new Lobe(8, 25, 4.0, 3, Blocks.BASALT)
        };

        private static final int[][] PRESSURE_FRONTS = new int[][] {
            {4,10}, {5,10}, {6,10}, {17,10}, {18,10}, {19,10},
            {24,15}, {25,15}, {26,15}, {12,23}, {13,23}, {14,23},
            {21,29}, {22,29}, {23,29}
        };

        private static final int[][] HARDGROUND = new int[][] {
            {3,6}, {4,6}, {29,9}, {30,9}, {16,4},
            {17,4}, {6,29}, {7,29}, {28,25}, {29,25}
        };

        private PillowLavaFieldFeature() {
            super(NoneFeatureConfiguration.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
            WorldGenLevel level = context.level();
            BlockPos origin = context.origin();
            RandomSource random = context.random();
            int rotation = random.nextInt(4);
            boolean mirror = random.nextBoolean();
            int placed = 0;

            for (int index = 0; index < LOBES.length; index++) {
                Lobe lobe = LOBES[index];
                int minX = Math.max(1, (int) (lobe.x - lobe.radius - 1));
                int maxX = Math.min(31, (int) (lobe.x + lobe.radius + 1));
                int minZ = Math.max(1, (int) (lobe.z - lobe.radius - 1));
                int maxZ = Math.min(31, (int) (lobe.z + lobe.radius + 1));

                for (int x = minX; x <= maxX; x++) {
                    for (int z = minZ; z <= maxZ; z++) {
                        double distance = Math.sqrt(square(x - lobe.x) + square(z - lobe.z));
                        double edgeJitter = (((x * 13 + z * 17 + index * 7) % 9) - 4) * 0.08;
                        if (distance > lobe.radius + edgeJitter) {
                            continue;
                        }

                        double relative = Math.max(0.0, 1.0 - distance / Math.max(lobe.radius, 0.1));
                        int top = 1 + (int) (relative * lobe.height * 0.9);
                        for (int y = 0; y <= Math.min(4, top); y++) {
                            if (y > 0 && ((x * 19 + z * 23 + y + index) % 17 == 0)) {
                                continue;
                            }

                            Block block = lobe.block;
                            if (y == top && (x + z + index) % 5 == 0) {
                                block = Blocks.SMOOTH_BASALT;
                            } else if (y == 0 && (x * 3 + z + index) % 7 == 0) {
                                block = Blocks.BLACKSTONE;
                            }

                            if (placeAtLocalFloor(level, origin, x, z, y, block, rotation, mirror)) {
                                placed++;
                            }
                        }
                    }
                }
            }

            for (int[] point : PRESSURE_FRONTS) {
                if (placeAtLocalFloor(level, origin, point[0], point[1], 1, Blocks.BLACKSTONE, rotation, mirror)) {
                    placed++;
                }
                if ((point[0] + point[1]) % 3 == 0
                    && placeAtLocalFloor(level, origin, point[0], point[1], 2, Blocks.BASALT, rotation, mirror)) {
                    placed++;
                }
            }

            for (int[] point : HARDGROUND) {
                if (placeAtLocalFloor(level, origin, point[0], point[1], 0, Blocks.SMOOTH_BASALT, rotation, mirror)) {
                    placed++;
                }
            }

            return placed > 0;
        }

        private boolean placeAtLocalFloor(
            WorldGenLevel level,
            BlockPos origin,
            int sourceX,
            int sourceZ,
            int verticalOffset,
            Block block,
            int rotation,
            boolean mirror
        ) {
            int localX = sourceX - 16;
            int localZ = sourceZ - 16;
            if (mirror) {
                localX = -localX;
            }

            int rotatedX;
            int rotatedZ;
            switch (rotation) {
                case 1 -> {
                    rotatedX = -localZ;
                    rotatedZ = localX;
                }
                case 2 -> {
                    rotatedX = -localX;
                    rotatedZ = -localZ;
                }
                case 3 -> {
                    rotatedX = localZ;
                    rotatedZ = -localX;
                }
                default -> {
                    rotatedX = localX;
                    rotatedZ = localZ;
                }
            }

            int worldX = origin.getX() + rotatedX;
            int worldZ = origin.getZ() + rotatedZ;
            int floorY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, worldX, worldZ);
            BlockPos base = new BlockPos(worldX, floorY, worldZ);

            if (!level.getFluidState(base).is(FluidTags.WATER)) {
                return false;
            }

            BlockPos target = base.above(verticalOffset);
            if (!level.ensureCanWrite(target)) {
                return false;
            }

            setBlock(level, target, block.defaultBlockState());
            return true;
        }

        private static double square(double value) {
            return value * value;
        }

        private record Lobe(int x, int z, double radius, int height, Block block) { }
    }
}
