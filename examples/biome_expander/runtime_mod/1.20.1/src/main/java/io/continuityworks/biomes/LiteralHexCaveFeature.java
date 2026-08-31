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
 * First-class literal hex cave geometry.
 *
 * <p>The hex grid is explicitly reconstructed as regular hex-cell edges in world
 * coordinates. Named cellular/fractal/mirror operators only decide where those
 * literal edges remain visible, how thick they become, and which segments are
 * occluded. Existing volumetric cave noise remains a separate additive system.</p>
 */
final class LiteralHexCaveFeature extends Feature<NoneFeatureConfiguration> {
    private static final double SQRT_3 = Math.sqrt(3.0);

    LiteralHexCaveFeature() {
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
                SurfaceProfile surface = resolveSurface(level, x, z);
                if (surface == null) {
                    continue;
                }

                CavePatternProfile pattern = CavePatternProfiles.resolve(surface.biome());
                if (pattern == null) {
                    continue;
                }

                HorizontalSample horizontal = horizontalSample(x, z, pattern);
                if (horizontal.edge() < 0.04 && horizontal.vertex() < 0.12) {
                    continue;
                }

                int minY = Math.max(level.getMinBuildHeight() + 7, -56);
                int maxY = surface.surfaceY() - surface.cave().roofBuffer();
                if (maxY <= minY + 3) {
                    continue;
                }

                for (int y = minY; y <= maxY; y++) {
                    double layer = verticalLayer(x, y, z, worldSeed, pattern);
                    double literalGeometry = Math.max(horizontal.edge() * layer, horizontal.vertex() * 0.72);
                    if (literalGeometry < 0.30) {
                        continue;
                    }

                    double nx = x / pattern.maskScale();
                    double ny = y / Math.max(8.0, pattern.maskScale() * 0.62);
                    double nz = z / pattern.maskScale();
                    long salt = worldSeed ^ pattern.salt();

                    double primary = CaveMaskField.sample(
                        pattern.primary(), nx, ny, nz, salt, pattern.radialSectors()
                    );
                    double secondary = CaveMaskField.sample(
                        pattern.secondary(), nx, ny, nz, salt ^ 0x9E3779B97F4A7C15L, pattern.radialSectors()
                    );
                    double tertiary = CaveMaskField.sample(
                        pattern.tertiary(), nx, ny, nz, salt ^ 0xC2B2AE3D27D4EB4FL, pattern.radialSectors()
                    );

                    double mask = primary * pattern.primaryWeight()
                        + secondary * pattern.secondaryWeight()
                        + tertiary * pattern.tertiaryWeight();

                    double threshold = pattern.maskThreshold();
                    threshold += switch (surface.cave().coverage()) {
                        case COMPLETE -> -0.08;
                        case PARTIAL -> 0.04;
                        case OPAQUE -> 0.01;
                    };

                    if (mask < threshold) {
                        continue;
                    }

                    // Mask intensity thickens/thins edges but never replaces or moves them.
                    double thickness = 0.42 - (mask - 0.5) * 0.30;
                    if (literalGeometry < thickness) {
                        continue;
                    }

                    BlockPos target = new BlockPos(x, y, z);
                    BlockState state = level.getBlockState(target);
                    if (!isCarvable(state) || !level.ensureCanWrite(target)) {
                        continue;
                    }
                    if (surface.cave().floodChance() <= 0.0 && touchesWater(level, target)) {
                        continue;
                    }

                    level.setBlock(
                        target,
                        caveState(x, y, z, worldSeed, surface.cave(), pattern),
                        2
                    );
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
        BiomeCaveProfile cave = BiomeCaveProfiles.resolve(key.get());
        return cave == null ? null : new SurfaceProfile(surfaceY, key.get(), cave);
    }

    private static HorizontalSample horizontalSample(double worldX, double worldZ, CavePatternProfile pattern) {
        long salt = pattern.salt();
        double rotation = unit(salt ^ 0xA24BAED4963EE407L) * Math.PI;
        double cos = Math.cos(rotation);
        double sin = Math.sin(rotation);
        double x = worldX * cos - worldZ * sin;
        double z = worldX * sin + worldZ * cos;

        Axial cell = nearestHex(x, z, pattern.hexRadius());
        double centerX = pattern.hexRadius() * SQRT_3 * (cell.q() + cell.r() * 0.5);
        double centerZ = pattern.hexRadius() * 1.5 * cell.r();
        double localX = x - centerX;
        double localZ = z - centerZ;

        double edgeDistance = distanceToHexEdge(localX, localZ, pattern.hexRadius());
        double vertexDistance = distanceToHexVertex(localX, localZ, pattern.hexRadius());
        double edge = 1.0 - smooth01(edgeDistance / pattern.corridorWidth());
        double vertex = 1.0 - smooth01(vertexDistance / Math.max(1.0, pattern.corridorWidth() * 0.78));
        return new HorizontalSample(edge, vertex);
    }

    private static Axial nearestHex(double x, double z, double size) {
        double fq = (SQRT_3 / 3.0 * x - z / 3.0) / size;
        double fr = (2.0 / 3.0 * z) / size;
        double fs = -fq - fr;

        int rq = (int) Math.round(fq);
        int rr = (int) Math.round(fr);
        int rs = (int) Math.round(fs);

        double qDiff = Math.abs(rq - fq);
        double rDiff = Math.abs(rr - fr);
        double sDiff = Math.abs(rs - fs);
        if (qDiff > rDiff && qDiff > sDiff) {
            rq = -rr - rs;
        } else if (rDiff > sDiff) {
            rr = -rq - rs;
        }
        return new Axial(rq, rr);
    }

    private static double distanceToHexEdge(double x, double z, double radius) {
        double best = Double.MAX_VALUE;
        double firstX = 0.0;
        double firstZ = 0.0;
        double prevX = 0.0;
        double prevZ = 0.0;

        for (int i = 0; i < 6; i++) {
            double angle = Math.toRadians(-30.0 + i * 60.0);
            double vx = Math.cos(angle) * radius;
            double vz = Math.sin(angle) * radius;
            if (i == 0) {
                firstX = vx;
                firstZ = vz;
            } else {
                best = Math.min(best, pointSegmentDistance(x, z, prevX, prevZ, vx, vz));
            }
            prevX = vx;
            prevZ = vz;
        }
        return Math.min(best, pointSegmentDistance(x, z, prevX, prevZ, firstX, firstZ));
    }

    private static double distanceToHexVertex(double x, double z, double radius) {
        double best = Double.MAX_VALUE;
        for (int i = 0; i < 6; i++) {
            double angle = Math.toRadians(-30.0 + i * 60.0);
            best = Math.min(best, Math.hypot(
                x - Math.cos(angle) * radius,
                z - Math.sin(angle) * radius
            ));
        }
        return best;
    }

    private static double pointSegmentDistance(
        double px,
        double pz,
        double ax,
        double az,
        double bx,
        double bz
    ) {
        double dx = bx - ax;
        double dz = bz - az;
        double lengthSq = dx * dx + dz * dz;
        if (lengthSq <= 1.0E-9) {
            return Math.hypot(px - ax, pz - az);
        }
        double t = ((px - ax) * dx + (pz - az) * dz) / lengthSq;
        t = Math.max(0.0, Math.min(1.0, t));
        return Math.hypot(px - (ax + t * dx), pz - (az + t * dz));
    }

    private static double verticalLayer(
        int x,
        int y,
        int z,
        long worldSeed,
        CavePatternProfile pattern
    ) {
        double warp = valueNoise2D(
            x / 96.0,
            z / 96.0,
            worldSeed ^ pattern.salt() ^ 0xDB4F0B9175AE2165L
        ) * 4.5;
        double phase = unit(pattern.salt() ^ 0xBBE0563303A4615FL) * pattern.layerSpacing();
        double distance = wrappedDistance(y + warp + phase, pattern.layerSpacing());
        return 1.0 - smooth01(distance / pattern.layerThickness());
    }

    private static double valueNoise2D(double x, double z, long salt) {
        int x0 = floor(x);
        int z0 = floor(z);
        double tx = smooth01(x - x0);
        double tz = smooth01(z - z0);
        double n00 = signedUnit(hash2(x0, z0, salt));
        double n10 = signedUnit(hash2(x0 + 1, z0, salt));
        double n01 = signedUnit(hash2(x0, z0 + 1, salt));
        double n11 = signedUnit(hash2(x0 + 1, z0 + 1, salt));
        return lerp(lerp(n00, n10, tx), lerp(n01, n11, tx), tz);
    }

    private static BlockState caveState(
        int x,
        int y,
        int z,
        long worldSeed,
        BiomeCaveProfile cave,
        CavePatternProfile pattern
    ) {
        if (cave.floodChance() > 0.0) {
            double selector = unit(hash3(x, y, z, worldSeed ^ pattern.salt()));
            if (selector < cave.floodChance()) {
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

    private static double wrappedDistance(double value, double period) {
        double wrapped = value - Math.floor(value / period + 0.5) * period;
        return Math.abs(wrapped);
    }

    private static int floor(double value) {
        int i = (int) value;
        return value < i ? i - 1 : i;
    }

    private static double smooth01(double value) {
        value = Math.max(0.0, Math.min(1.0, value));
        return value * value * (3.0 - 2.0 * value);
    }

    private static double lerp(double a, double b, double t) {
        return a + (b - a) * t;
    }

    private static long hash2(int x, int z, long salt) {
        long v = salt;
        v ^= (long) x * 0x9E3779B97F4A7C15L;
        v ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        return mix(v);
    }

    private static long hash3(int x, int y, int z, long salt) {
        long v = salt;
        v ^= (long) x * 0x9E3779B97F4A7C15L;
        v ^= (long) y * 0xD1B54A32D192ED03L;
        v ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        return mix(v);
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

    private record Axial(int q, int r) { }
    private record HorizontalSample(double edge, double vertex) { }
    private record SurfaceProfile(int surfaceY, ResourceKey<Biome> biome, BiomeCaveProfile cave) { }
}
