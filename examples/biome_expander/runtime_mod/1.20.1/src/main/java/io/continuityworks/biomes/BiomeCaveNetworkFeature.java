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
 * Volumetric biome cave-network generator.
 *
 * <p>Each biome combines several deterministic fields: Perlin-style gradient noise,
 * cellular/Worley distance, mosaics, periodic tiles, coordinate scrambling, plasma
 * waves and a ridged fractal mask. Separate warped tunnel, chamber and shaft fields
 * are then blended according to that biome's profile. This produces a cave network,
 * not a single repeated cave stamp.</p>
 *
 * <p>All fields are evaluated from absolute coordinates plus world seed, so cave
 * systems remain continuous across chunk boundaries. Only base geology is carved;
 * ores, arbitrary mod blocks and structure materials are deliberately excluded.</p>
 */
final class BiomeCaveNetworkFeature extends Feature<NoneFeatureConfiguration> {
    private static final int SEA_LEVEL = 63;
    private static final double TWO_PI = Math.PI * 2.0;

    BiomeCaveNetworkFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        int chunkMinX = (origin.getX() >> 4) << 4;
        int chunkMinZ = (origin.getZ() >> 4) << 4;
        int changed = 0;

        for (int localX = 0; localX < 16; localX++) {
            for (int localZ = 0; localZ < 16; localZ++) {
                int x = chunkMinX + localX;
                int z = chunkMinZ + localZ;
                SurfaceProfile surface = resolveSurface(level, x, z);
                if (surface == null) {
                    continue;
                }

                BiomeCaveProfile profile = surface.profile();
                int minY = Math.max(level.getMinBuildHeight() + 7, -56);
                int maxY = surface.surfaceY() - profile.roofBuffer();
                if (maxY <= minY + 3) {
                    continue;
                }

                for (int y = minY; y <= maxY; y++) {
                    BlockPos target = new BlockPos(x, y, z);
                    BlockState state = level.getBlockState(target);
                    if (!isCarvable(state)) {
                        continue;
                    }
                    if (profile.floodChance() <= 0.0 && touchesWater(level, target)) {
                        continue;
                    }

                    double score = caveScore(x, y, z, minY, maxY, level.getSeed(), profile);
                    if (score <= profile.threshold()) {
                        continue;
                    }

                    if (profile.coverage() == CaveCoverage.PARTIAL
                        && scrambleNoise(
                            x / (profile.horizontalScale() * 0.72),
                            y / (profile.verticalScale() * 0.82),
                            z / (profile.horizontalScale() * 0.72),
                            level.getSeed() ^ profile.salt() ^ 0x1D8E4E27C47D124FL
                        ) < -0.22) {
                        continue;
                    }

                    if (!level.ensureCanWrite(target)) {
                        continue;
                    }

                    level.setBlock(target, caveState(x, y, z, level.getSeed(), profile), 2);
                    changed++;
                }
            }
        }

        return changed > 0;
    }

    private static SurfaceProfile resolveSurface(WorldGenLevel level, int x, int z) {
        int surfaceY = level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG, x, z) - 1;
        if (surfaceY <= level.getMinBuildHeight() + 8) {
            return null;
        }
        Optional<ResourceKey<Biome>> key = level.getBiome(new BlockPos(x, surfaceY, z)).unwrapKey();
        if (key.isEmpty()) {
            return null;
        }
        BiomeCaveProfile profile = BiomeCaveProfiles.resolve(key.get());
        return profile == null ? null : new SurfaceProfile(surfaceY, profile);
    }

    private static double caveScore(
        int x,
        int y,
        int z,
        int minY,
        int maxY,
        long worldSeed,
        BiomeCaveProfile profile
    ) {
        long salt = worldSeed ^ profile.salt();
        double nx = x / profile.horizontalScale();
        double ny = y / profile.verticalScale();
        double nz = z / profile.horizontalScale();

        double gradient = gradientNoise3D(nx, ny, nz, salt ^ 0x243F6A8885A308D3L);
        double cellular = cellularNoise(nx * 1.18, ny * 1.05, nz * 1.18, salt ^ 0x13198A2E03707344L);
        double mosaic = mosaicNoise(nx * 1.65, ny * 1.20, nz * 1.65, salt ^ 0xA4093822299F31D0L);
        double tile = tileNoise(nx, ny, nz, salt ^ 0x082EFA98EC4E6C89L);
        double scramble = scrambleNoise(nx, ny, nz, salt ^ 0x452821E638D01377L);
        double plasma = plasmaNoise(nx, ny, nz, salt ^ 0xBE5466CF34E90C6CL);
        double fractal = fractalMask(nx, ny, nz, salt ^ 0xC0AC29B7C97C50DDL) * 2.0 - 1.0;

        double base = gradient * profile.gradientWeight()
            + cellular * profile.cellularWeight()
            + mosaic * profile.mosaicWeight()
            + tile * profile.tileWeight()
            + scramble * profile.scrambleWeight()
            + plasma * profile.plasmaWeight()
            + fractal * profile.fractalWeight();

        double tunnel = warpedTunnelField(nx, ny, nz, salt ^ 0x3F84D5B5B5470917L);
        double chamber = chamberField(nx, ny, nz, salt ^ 0x9216D5D98979FB1BL);
        double shaft = shaftField(nx, ny, nz, salt ^ 0xD1310BA698DFB5ACL);
        double mask = fractalMask(nx * 0.62, ny * 0.72, nz * 0.62, salt ^ 0x2FFD72DBD01ADFB7L);

        double depth = (y - minY) / (double) Math.max(1, maxY - minY);
        double depthEnvelope = 0.38 + 0.62 * Math.sin(Math.PI * clamp01(depth));

        double score = base * 0.72
            + tunnel * profile.tunnelBias()
            + chamber * profile.chamberBias()
            + shaft * profile.shaftBias()
            + (mask - 0.5) * 0.34;

        score *= depthEnvelope;

        if (profile.coverage() == CaveCoverage.COMPLETE) {
            score += 0.07 + tunnel * 0.06;
        } else if (profile.coverage() == CaveCoverage.OPAQUE) {
            // Opaque networks are extensive but stay visually sealed from the surface.
            score += 0.025;
        } else {
            score -= 0.025;
        }

        return score;
    }

    private static BlockState caveState(int x, int y, int z, long seed, BiomeCaveProfile profile) {
        if (y < SEA_LEVEL && profile.floodChance() > 0.0) {
            double selector = unit(hash3(x, y, z, seed ^ profile.salt() ^ 0x6A09E667F3BCC909L));
            if (selector < profile.floodChance()) {
                return Blocks.WATER.defaultBlockState();
            }
        }
        return Blocks.CAVE_AIR.defaultBlockState();
    }

    private static boolean touchesWater(WorldGenLevel level, BlockPos pos) {
        return level.getFluidState(pos.above()).is(FluidTags.WATER)
            || level.getFluidState(pos.below()).is(FluidTags.WATER)
            || level.getFluidState(pos.north()).is(FluidTags.WATER)
            || level.getFluidState(pos.south()).is(FluidTags.WATER)
            || level.getFluidState(pos.east()).is(FluidTags.WATER)
            || level.getFluidState(pos.west()).is(FluidTags.WATER);
    }

    private static boolean isCarvable(BlockState state) {
        return state.is(BlockTags.BASE_STONE_OVERWORLD)
            || state.is(Blocks.DRIPSTONE_BLOCK)
            || state.is(Blocks.TUFF)
            || state.is(Blocks.CALCITE)
            || state.is(Blocks.BASALT)
            || state.is(Blocks.SMOOTH_BASALT)
            || state.is(Blocks.BLACKSTONE)
            || state.is(Blocks.DEEPSLATE)
            || state.is(Blocks.TERRACOTTA)
            || state.is(Blocks.RED_TERRACOTTA)
            || state.is(Blocks.SANDSTONE)
            || state.is(Blocks.RED_SANDSTONE);
    }

    /** Perlin-style gradient interpolation. */
    private static double gradientNoise3D(double x, double y, double z, long salt) {
        int x0 = floor(x);
        int y0 = floor(y);
        int z0 = floor(z);
        double fx = x - x0;
        double fy = y - y0;
        double fz = z - z0;
        double u = fade(fx);
        double v = fade(fy);
        double w = fade(fz);

        double n000 = gradientDot(x0, y0, z0, fx, fy, fz, salt);
        double n100 = gradientDot(x0 + 1, y0, z0, fx - 1.0, fy, fz, salt);
        double n010 = gradientDot(x0, y0 + 1, z0, fx, fy - 1.0, fz, salt);
        double n110 = gradientDot(x0 + 1, y0 + 1, z0, fx - 1.0, fy - 1.0, fz, salt);
        double n001 = gradientDot(x0, y0, z0 + 1, fx, fy, fz - 1.0, salt);
        double n101 = gradientDot(x0 + 1, y0, z0 + 1, fx - 1.0, fy, fz - 1.0, salt);
        double n011 = gradientDot(x0, y0 + 1, z0 + 1, fx, fy - 1.0, fz - 1.0, salt);
        double n111 = gradientDot(x0 + 1, y0 + 1, z0 + 1, fx - 1.0, fy - 1.0, fz - 1.0, salt);

        double x00 = lerp(n000, n100, u);
        double x10 = lerp(n010, n110, u);
        double x01 = lerp(n001, n101, u);
        double x11 = lerp(n011, n111, u);
        return clamp(lerp(lerp(x00, x10, v), lerp(x01, x11, v), w) * 1.45, -1.0, 1.0);
    }

    private static double gradientDot(
        int x,
        int y,
        int z,
        double dx,
        double dy,
        double dz,
        long salt
    ) {
        int selector = (int) Math.floorMod(hash3(x, y, z, salt), 12L);
        return switch (selector) {
            case 0 -> dx + dy;
            case 1 -> -dx + dy;
            case 2 -> dx - dy;
            case 3 -> -dx - dy;
            case 4 -> dx + dz;
            case 5 -> -dx + dz;
            case 6 -> dx - dz;
            case 7 -> -dx - dz;
            case 8 -> dy + dz;
            case 9 -> -dy + dz;
            case 10 -> dy - dz;
            default -> -dy - dz;
        } * 0.70710678118;
    }

    /** Worley/cellular nearest-cell field. */
    private static double cellularNoise(double x, double y, double z, long salt) {
        double distance = cellularDistance3D(x, y, z, salt);
        return clamp((1.0 - distance * 1.22) * 2.0 - 1.0, -1.0, 1.0);
    }

    private static double cellularDistance3D(double x, double y, double z, long salt) {
        int baseX = floor(x);
        int baseY = floor(y);
        int baseZ = floor(z);
        double best = Double.MAX_VALUE;

        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                for (int dz = -1; dz <= 1; dz++) {
                    int cellX = baseX + dx;
                    int cellY = baseY + dy;
                    int cellZ = baseZ + dz;
                    long hash = hash3(cellX, cellY, cellZ, salt);
                    double cx = cellX + 0.14 + unit(hash) * 0.72;
                    double cy = cellY + 0.14 + unit(hash ^ 0x9E3779B97F4A7C15L) * 0.72;
                    double cz = cellZ + 0.14 + unit(hash ^ 0xC2B2AE3D27D4EB4FL) * 0.72;
                    double distance = Math.sqrt(
                        (x - cx) * (x - cx)
                            + (y - cy) * (y - cy)
                            + (z - cz) * (z - cz)
                    );
                    best = Math.min(best, distance);
                }
            }
        }
        return best;
    }

    /** Quantized cellular/value field that creates broken mosaic chambers. */
    private static double mosaicNoise(double x, double y, double z, long salt) {
        int ix = floor(x * 1.7);
        int iy = floor(y * 1.35);
        int iz = floor(z * 1.7);
        double raw = signedUnit(hash3(ix, iy, iz, salt));
        return Math.rint(raw * 4.0) / 4.0;
    }

    /** Periodic tile field with per-biome rotation and phase. */
    private static double tileNoise(double x, double y, double z, long salt) {
        double angle = unit(salt) * Math.PI;
        double rx = x * Math.cos(angle) - z * Math.sin(angle);
        double rz = x * Math.sin(angle) + z * Math.cos(angle);
        double phase = unit(salt ^ 0xA54FF53A5F1D36F1L) * TWO_PI;
        double tiles = Math.sin((rx * 1.55 + y * 0.19) * TWO_PI + phase)
            * Math.cos((rz * 1.47 - y * 0.13) * TWO_PI - phase * 0.71);
        return clamp(tiles, -1.0, 1.0);
    }

    /** Coordinate permutation/scramble field. */
    private static double scrambleNoise(double x, double y, double z, long salt) {
        int ix = floor(x * 2.6);
        int iy = floor(y * 2.2);
        int iz = floor(z * 2.6);
        long selector = mix(salt) & 3L;
        int a = selector == 0 ? ix : selector == 1 ? iz : iy;
        int b = selector == 0 ? iz : selector == 1 ? iy : ix;
        int c = selector == 0 ? iy : selector == 1 ? ix : iz;
        long hash = hash3(a ^ (b << 2), b ^ (c << 1), c ^ (a << 3), salt);
        double cell = signedUnit(hash);
        double local = gradientNoise3D(x * 1.31, y * 1.17, z * 1.29, salt ^ hash);
        return clamp(cell * 0.68 + local * 0.32, -1.0, 1.0);
    }

    /** Plasma-like trigonometric interference field. */
    private static double plasmaNoise(double x, double y, double z, long salt) {
        double p1 = unit(salt) * TWO_PI;
        double p2 = unit(salt ^ 0x510E527FADE682D1L) * TWO_PI;
        double p3 = unit(salt ^ 0x1F83D9ABFB41BD6BL) * TWO_PI;
        double a = Math.sin(x * 2.4 + Math.sin(z * 1.3 + p2) + p1);
        double b = Math.sin(z * 2.0 + Math.cos(y * 1.7 + p3) - p2);
        double c = Math.sin((x + z) * 1.1 + y * 1.8 + p3);
        return clamp((a + b + c) / 3.0, -1.0, 1.0);
    }

    /** Ridged multi-octave mask; returns 0..1. */
    private static double fractalMask(double x, double y, double z, long salt) {
        double amplitude = 0.56;
        double frequency = 0.72;
        double sum = 0.0;
        double norm = 0.0;
        for (int octave = 0; octave < 5; octave++) {
            double noise = gradientNoise3D(
                x * frequency,
                y * frequency,
                z * frequency,
                salt ^ (0x9E3779B97F4A7C15L * (octave + 1))
            );
            double ridge = 1.0 - Math.abs(noise);
            ridge *= ridge;
            sum += ridge * amplitude;
            norm += amplitude;
            frequency *= 1.93;
            amplitude *= 0.53;
        }
        return clamp01(sum / Math.max(0.0001, norm));
    }

    /** Warped 3-D lattice tubes; returns 0..1. */
    private static double warpedTunnelField(double x, double y, double z, long salt) {
        double phase = unit(salt) * TWO_PI;
        double warp = plasmaNoise(x * 0.37, y * 0.41, z * 0.37, salt ^ 0x5BE0CD19137E2179L) * 0.46;
        double a = Math.abs(Math.sin((x + warp) * TWO_PI + phase));
        double b = Math.abs(Math.sin((z - warp * 0.73) * TWO_PI - phase * 0.61));
        double c = Math.abs(Math.sin((y + warp * 0.51) * TWO_PI + phase * 0.37));
        double tubeA = Math.sqrt(a * a + b * b);
        double tubeB = Math.sqrt(b * b + c * c);
        double tubeC = Math.sqrt(a * a + c * c);
        double distance = Math.min(tubeA, Math.min(tubeB, tubeC));
        return 1.0 - smooth01(clamp01(distance / 0.58));
    }

    /** Cellular chamber cores; returns 0..1. */
    private static double chamberField(double x, double y, double z, long salt) {
        double distance = cellularDistance3D(x * 0.74, y * 0.72, z * 0.74, salt);
        if (distance >= 0.62) {
            return 0.0;
        }
        return Math.pow(1.0 - distance / 0.62, 1.55);
    }

    /** Mostly vertical cellular columns with slow lateral wobble; returns 0..1. */
    private static double shaftField(double x, double y, double z, long salt) {
        double wobbleX = Math.sin(y * 0.61 + unit(salt) * TWO_PI) * 0.21;
        double wobbleZ = Math.cos(y * 0.53 + unit(salt ^ 31L) * TWO_PI) * 0.21;
        int cellX = floor((x + wobbleX) * 0.72);
        int cellZ = floor((z + wobbleZ) * 0.72);
        long hash = hash3(cellX, 0, cellZ, salt);
        double centerX = (cellX + 0.18 + unit(hash) * 0.64) / 0.72;
        double centerZ = (cellZ + 0.18 + unit(hash ^ 0xD1B54A32D192ED03L) * 0.64) / 0.72;
        double distance = Math.hypot(x + wobbleX - centerX, z + wobbleZ - centerZ);
        if (distance >= 0.25) {
            return 0.0;
        }
        double core = 1.0 - distance / 0.25;
        return core * (0.78 + 0.22 * Math.sin(y * 1.17 + unit(hash) * TWO_PI));
    }

    private static long hash3(int x, int y, int z, long salt) {
        long value = salt;
        value ^= (long) x * 0x9E3779B97F4A7C15L;
        value ^= (long) y * 0xD1B54A32D192ED03L;
        value ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        return mix(value);
    }

    private static double fade(double t) {
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
    }

    private static double smooth01(double t) {
        t = clamp01(t);
        return t * t * (3.0 - 2.0 * t);
    }

    private static int floor(double value) {
        int integer = (int) value;
        return value < integer ? integer - 1 : integer;
    }

    private static double lerp(double a, double b, double t) {
        return a + (b - a) * t;
    }

    private static double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    private static double clamp01(double value) {
        return clamp(value, 0.0, 1.0);
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

    private record SurfaceProfile(int surfaceY, BiomeCaveProfile profile) { }
}
