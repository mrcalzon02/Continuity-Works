package io.continuityworks.biomes;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

import java.util.Optional;

/**
 * Generalized land-topology engine derived from the successful Abyssal terrain work.
 *
 * <p>Pockmark-style cellular deformation becomes basins, craters and karst. The
 * turbidity-channel absolute-coordinate field becomes gullies, rivers, drainage cuts,
 * canals and rifts. Sand-wave morphology becomes dunes, moraines and ridge trains.
 * Clustered seafloor relief becomes tors, spoil heaps, rubble and synthetic spires.</p>
 *
 * <p>The feature evaluates absolute world coordinates, so neighboring chunks rebuild
 * the same field independently and do not form 16x16 stamp seams. It only mutates
 * known natural blocks or the current biome's owned surface materials; arbitrary
 * modded blocks and later structure materials are not excavation targets.</p>
 */
final class LandTopologyFeature extends Feature<NoneFeatureConfiguration> {
    private static final long SECONDARY_SALT = 0x6A09E667F3BCC909L;
    private static final double TWO_PI = Math.PI * 2.0;

    LandTopologyFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        int chunkMinX = (origin.getX() >> 4) << 4;
        int chunkMinZ = (origin.getZ() >> 4) << 4;
        long worldSeed = level.getSeed();
        int changed = 0;

        for (int localX = 0; localX < 16; localX++) {
            for (int localZ = 0; localZ < 16; localZ++) {
                int x = chunkMinX + localX;
                int z = chunkMinZ + localZ;
                LandTopologyProfiles.Resolved resolved = resolve(level, x, z);
                if (resolved == null) {
                    continue;
                }

                LandTopologyProfile profile = resolved.topology();
                long salt = worldSeed ^ profile.salt();
                double primary = sample(profile.primary(), x, z, profile.scale(), salt);
                double secondary = sample(
                    profile.secondary(),
                    x,
                    z,
                    profile.scale() * 0.72,
                    salt ^ SECONDARY_SALT
                );
                double combined = primary + secondary * profile.secondaryStrength();
                double boundary = boundaryFactor(level, x, z, resolved.biome());
                int delta = clamp(
                    (int) Math.round(combined * profile.relief() * boundary),
                    -profile.relief(),
                    profile.relief()
                );

                if (delta != 0) {
                    changed += reshapeColumn(level, x, z, delta, resolved);
                }
            }
        }

        return changed > 0;
    }

    private static LandTopologyProfiles.Resolved resolve(WorldGenLevel level, int x, int z) {
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z) - 1;
        y = Math.max(level.getMinBuildHeight() + 1, y);
        Optional<ResourceKey<Biome>> key = level.getBiome(new BlockPos(x, y, z)).unwrapKey();
        return key.map(LandTopologyProfiles::resolve).orElse(null);
    }

    private static double boundaryFactor(
        WorldGenLevel level,
        int x,
        int z,
        ResourceKey<Biome> biome
    ) {
        int matches = 0;
        matches += sameBiome(level, x + 6, z, biome) ? 1 : 0;
        matches += sameBiome(level, x - 6, z, biome) ? 1 : 0;
        matches += sameBiome(level, x, z + 6, biome) ? 1 : 0;
        matches += sameBiome(level, x, z - 6, biome) ? 1 : 0;
        return 0.40 + matches * 0.15;
    }

    private static boolean sameBiome(
        WorldGenLevel level,
        int x,
        int z,
        ResourceKey<Biome> expected
    ) {
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z) - 1;
        y = Math.max(level.getMinBuildHeight() + 1, y);
        return level.getBiome(new BlockPos(x, y, z)).unwrapKey().map(expected::equals).orElse(false);
    }

    private static int reshapeColumn(
        WorldGenLevel level,
        int x,
        int z,
        int delta,
        LandTopologyProfiles.Resolved resolved
    ) {
        int surfaceY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, x, z) - 1;
        if (surfaceY <= level.getMinBuildHeight() + 2) {
            return 0;
        }

        BlockPos surface = new BlockPos(x, surfaceY, z);
        if (!level.ensureCanWrite(surface) || !isMutable(level.getBlockState(surface), resolved)) {
            return 0;
        }

        if (delta > 0) {
            return raise(level, x, z, surfaceY, delta, resolved);
        }
        return lower(level, x, z, surfaceY, -delta, resolved);
    }

    private static int raise(
        WorldGenLevel level,
        int x,
        int z,
        int surfaceY,
        int height,
        LandTopologyProfiles.Resolved resolved
    ) {
        for (int layer = 1; layer <= height; layer++) {
            BlockPos target = new BlockPos(x, surfaceY + layer, z);
            if (!level.ensureCanWrite(target) || !replaceableAbove(level, target)) {
                return 0;
            }
        }

        BlockPos oldSurface = new BlockPos(x, surfaceY, z);
        level.setBlock(oldSurface, resolved.under().defaultBlockState(), 2);
        for (int layer = 1; layer <= height; layer++) {
            BlockPos target = new BlockPos(x, surfaceY + layer, z);
            level.setBlock(
                target,
                (layer == height ? resolved.top() : resolved.under()).defaultBlockState(),
                2
            );
        }
        return height + 1;
    }

    private static int lower(
        WorldGenLevel level,
        int x,
        int z,
        int surfaceY,
        int depth,
        LandTopologyProfiles.Resolved resolved
    ) {
        int actualDepth = Math.min(depth, Math.max(1, surfaceY - level.getMinBuildHeight() - 2));
        BlockPos newFloor = new BlockPos(x, surfaceY - actualDepth, z);
        if (!level.ensureCanWrite(newFloor) || !isMutable(level.getBlockState(newFloor), resolved)) {
            return 0;
        }

        for (int layer = 0; layer < actualDepth; layer++) {
            BlockPos target = new BlockPos(x, surfaceY - layer, z);
            if (!level.ensureCanWrite(target) || !isMutable(level.getBlockState(target), resolved)) {
                return 0;
            }
        }

        boolean submerged = level.getFluidState(new BlockPos(x, surfaceY + 1, z)).is(FluidTags.WATER);
        BlockState replacement = (resolved.topology().waterFill() || submerged)
            ? Blocks.WATER.defaultBlockState()
            : Blocks.AIR.defaultBlockState();

        for (int layer = 0; layer < actualDepth; layer++) {
            level.setBlock(new BlockPos(x, surfaceY - layer, z), replacement, 2);
        }
        level.setBlock(newFloor, resolved.top().defaultBlockState(), 2);
        return actualDepth + 1;
    }

    private static boolean replaceableAbove(WorldGenLevel level, BlockPos target) {
        BlockState state = level.getBlockState(target);
        return state.isAir()
            || state.is(Blocks.SNOW)
            || level.getFluidState(target).is(FluidTags.WATER);
    }

    private static boolean isMutable(BlockState state, LandTopologyProfiles.Resolved resolved) {
        return state.is(resolved.top())
            || state.is(resolved.under())
            || state.is(BlockTags.BASE_STONE_OVERWORLD)
            || state.is(Blocks.GRASS_BLOCK)
            || state.is(Blocks.DIRT)
            || state.is(Blocks.COARSE_DIRT)
            || state.is(Blocks.PODZOL)
            || state.is(Blocks.MYCELIUM)
            || state.is(Blocks.SAND)
            || state.is(Blocks.RED_SAND)
            || state.is(Blocks.GRAVEL)
            || state.is(Blocks.CLAY)
            || state.is(Blocks.MUD)
            || state.is(Blocks.TUFF)
            || state.is(Blocks.CALCITE)
            || state.is(Blocks.TERRACOTTA)
            || state.is(Blocks.RED_TERRACOTTA)
            || state.is(Blocks.BASALT)
            || state.is(Blocks.SMOOTH_BASALT)
            || state.is(Blocks.BLACKSTONE)
            || state.is(Blocks.DEEPSLATE)
            || state.is(Blocks.SNOW_BLOCK);
    }

    private static double sample(
        LandTopologyMode mode,
        double x,
        double z,
        double scale,
        long salt
    ) {
        return switch (mode) {
            case KNOLLS -> fbm(x, z, scale, salt) * 0.72;
            case BASINS -> basinField(x, z, scale, salt, false);
            case CHANNELS -> channelField(x, z, scale, salt, false);
            case RIDGES -> ridgeField(x, z, scale, salt);
            case TERRACES -> {
                double n = fbm(x, z, scale * 1.15, salt);
                yield Math.rint(n * 4.0) / 5.0;
            }
            case DUNES -> duneField(x, z, scale, salt);
            case MORAINE -> ridgeField(x, z, scale * 0.82, salt)
                + basinField(x, z, scale * 1.35, salt ^ 0x51ED2705L, false) * 0.32;
            case KARST -> basinField(x, z, scale * 0.86, salt, false)
                + spireField(x, z, scale * 1.18, salt ^ 0x73A2D5B1L) * 0.55;
            case SCARPS -> scarpField(x, z, scale, salt);
            case CRATERS -> basinField(x, z, scale * 1.25, salt, true);
            case RIFTS -> channelField(x, z, scale * 1.08, salt, true);
            case HUMMOCKS -> fbm(x, z, Math.max(14.0, scale * 0.42), salt) * 0.58
                + basinField(x, z, scale * 0.90, salt ^ 0x2E7D2C03L, false) * 0.28;
            case SPOIL -> spoilField(x, z, scale, salt);
            case GRID -> gridField(x, z, scale, salt);
            case SPIRES -> spireField(x, z, scale, salt);
            case RUBBLE -> rubbleField(x, z, scale, salt);
        };
    }

    private static double basinField(double x, double z, double scale, long salt, boolean crater) {
        CellSample cell = nearestCell(x, z, scale, salt);
        double d = cell.distance();
        if (d < 0.42) {
            double core = 1.0 - d / 0.42;
            return -Math.pow(core, crater ? 1.25 : 1.65);
        }
        if (d < 0.62) {
            double rim = 1.0 - (d - 0.42) / 0.20;
            return rim * (crater ? 0.72 : 0.28);
        }
        return fbm(x, z, scale * 1.7, salt ^ 0x1F123BB5L) * 0.08;
    }

    private static double channelField(double x, double z, double scale, long salt, boolean rift) {
        double spacing = scale * (rift ? 2.8 : 3.5);
        double phaseA = unit(salt ^ 0x3C79AC492BA7B653L) * TWO_PI;
        double phaseB = unit(salt ^ 0x1C69B3F74AC4AE35L) * TWO_PI;
        double meander = Math.sin(x / (scale * 1.6) + phaseA) * scale * 0.42
            + Math.sin(x / (scale * 4.2) + phaseB) * scale * 0.24;
        double distance = wrappedDistance(z - meander, spacing);
        double halfWidth = scale * (rift ? 0.10 : 0.16);
        double leveeWidth = halfWidth * 2.2;

        if (distance <= halfWidth) {
            double center = 1.0 - distance / halfWidth;
            return -(rift ? 1.0 : 0.82) * (0.35 + center * 0.65);
        }
        if (distance <= leveeWidth) {
            double shoulder = 1.0 - (distance - halfWidth) / (leveeWidth - halfWidth);
            return shoulder * (rift ? 0.22 : 0.38);
        }
        return 0.0;
    }

    private static double ridgeField(double x, double z, double scale, long salt) {
        double angle = unit(salt ^ 0xA54FF53A5F1D36F1L) * Math.PI;
        double projected = (x * Math.cos(angle) + z * Math.sin(angle)) / scale;
        double wave = Math.abs(Math.sin(projected * Math.PI + unit(salt) * TWO_PI));
        double ridge = Math.pow(1.0 - wave, 2.6);
        return ridge * 0.92 + fbm(x, z, scale * 1.4, salt ^ 0x510E527FADE682D1L) * 0.16 - 0.12;
    }

    private static double duneField(double x, double z, double scale, long salt) {
        double angle = unit(salt ^ 0x9B05688C2B3E6C1FL) * Math.PI;
        double projected = (x * Math.cos(angle) + z * Math.sin(angle)) / scale;
        double wave = Math.sin(projected * TWO_PI + unit(salt ^ 17L) * TWO_PI);
        double crest = wave > 0.0 ? wave * wave : wave * 0.22;
        return crest * 0.78 + fbm(x, z, scale * 0.70, salt ^ 0x5BE0CD19137E2179L) * 0.18;
    }

    private static double scarpField(double x, double z, double scale, long salt) {
        double angle = unit(salt ^ 0x243F6A8885A308D3L) * Math.PI;
        double projected = (x * Math.cos(angle) + z * Math.sin(angle)) / scale;
        double fraction = projected - Math.floor(projected);
        double step = fraction < 0.18 ? 0.85 : fraction < 0.42 ? 0.35 : fraction < 0.72 ? -0.18 : -0.48;
        return step + fbm(x, z, scale * 0.65, salt ^ 0x13198A2E03707344L) * 0.18;
    }

    private static double spoilField(double x, double z, double scale, long salt) {
        CellSample cell = nearestCell(x, z, scale * 0.72, salt);
        double mound = cell.distance() < 0.52
            ? Math.pow(1.0 - cell.distance() / 0.52, 1.5) * 0.88
            : 0.0;
        double trench = channelField(x, z, scale * 1.25, salt ^ 0xB7E151628AED2A6BL, false) * 0.30;
        return mound + trench - 0.12;
    }

    private static double gridField(double x, double z, double scale, long salt) {
        double offsetX = unit(salt) * scale;
        double offsetZ = unit(salt ^ 0xC6EF372FE94F82BEL) * scale;
        double dx = wrappedDistance(x + offsetX, scale) / scale;
        double dz = wrappedDistance(z + offsetZ, scale) / scale;
        double d = Math.min(dx, dz);
        if (d < 0.055) {
            return 0.92;
        }
        if (d < 0.12) {
            return -0.58;
        }
        return fbm(x, z, scale * 2.2, salt ^ 0x94D049BB133111EBL) * 0.08;
    }

    private static double spireField(double x, double z, double scale, long salt) {
        CellSample cell = nearestCell(x, z, scale, salt);
        if (cell.distance() < 0.22) {
            double core = 1.0 - cell.distance() / 0.22;
            return Math.pow(core, 2.2);
        }
        return fbm(x, z, scale * 1.8, salt ^ 0x2545F4914F6CDD1DL) * 0.08;
    }

    private static double rubbleField(double x, double z, double scale, long salt) {
        double broad = Math.max(0.0, fbm(x, z, scale * 0.70, salt));
        double broken = Math.abs(fbm(x, z, Math.max(12.0, scale * 0.28), salt ^ 0xD1B54A32D192ED03L));
        return broad * 0.52 + broken * 0.42 - 0.18;
    }

    private static double fbm(double x, double z, double scale, long salt) {
        return valueNoise(x, z, scale, salt) * 0.62
            + valueNoise(x, z, Math.max(8.0, scale * 0.52), salt ^ 0x9E3779B97F4A7C15L) * 0.27
            + valueNoise(x, z, Math.max(6.0, scale * 0.26), salt ^ 0xC2B2AE3D27D4EB4FL) * 0.11;
    }

    private static double valueNoise(double x, double z, double scale, long salt) {
        double gx = x / scale;
        double gz = z / scale;
        int x0 = floor(gx);
        int z0 = floor(gz);
        double tx = smooth(gx - x0);
        double tz = smooth(gz - z0);

        double n00 = signedUnit(hashCell(x0, z0, salt));
        double n10 = signedUnit(hashCell(x0 + 1, z0, salt));
        double n01 = signedUnit(hashCell(x0, z0 + 1, salt));
        double n11 = signedUnit(hashCell(x0 + 1, z0 + 1, salt));
        double a = lerp(n00, n10, tx);
        double b = lerp(n01, n11, tx);
        return lerp(a, b, tz);
    }

    private static CellSample nearestCell(double x, double z, double scale, long salt) {
        int baseX = floor(x / scale);
        int baseZ = floor(z / scale);
        double best = Double.MAX_VALUE;
        long bestHash = 0L;

        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                int cellX = baseX + dx;
                int cellZ = baseZ + dz;
                long hash = hashCell(cellX, cellZ, salt);
                double jitterX = 0.18 + unit(hash) * 0.64;
                double jitterZ = 0.18 + unit(hash ^ 0xDB4F0B9175AE2165L) * 0.64;
                double centerX = (cellX + jitterX) * scale;
                double centerZ = (cellZ + jitterZ) * scale;
                double distance = Math.hypot(x - centerX, z - centerZ) / scale;
                if (distance < best) {
                    best = distance;
                    bestHash = hash;
                }
            }
        }
        return new CellSample(best, bestHash);
    }

    private static long hashCell(int x, int z, long salt) {
        long value = salt;
        value ^= (long) x * 0x9E3779B97F4A7C15L;
        value ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        return mix(value);
    }

    private static double wrappedDistance(double value, double period) {
        double wrapped = value - Math.floor(value / period + 0.5) * period;
        return Math.abs(wrapped);
    }

    private static int floor(double value) {
        int integer = (int) value;
        return value < integer ? integer - 1 : integer;
    }

    private static double smooth(double value) {
        return value * value * (3.0 - 2.0 * value);
    }

    private static double lerp(double a, double b, double t) {
        return a + (b - a) * t;
    }

    private static double signedUnit(long value) {
        return unit(value) * 2.0 - 1.0;
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

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private record CellSample(double distance, long hash) { }
}
