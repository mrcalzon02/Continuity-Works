package io.continuityworks.biomes;

/**
 * Named visibility fields used to expose/occlude literal hex cave geometry.
 * These are not aliases: every enum value has its own compositing rule.
 */
public final class CaveMaskField {
    private static final double TWO_PI = Math.PI * 2.0;

    private CaveMaskField() { }

    public static double sample(
        CaveMaskMode mode,
        double x,
        double y,
        double z,
        long salt,
        int radialSectors
    ) {
        return clamp01(switch (mode) {
            case MIRRORED_WORLEY_HEX_FIELD -> {
                double a = worleyCenter(Math.abs(x), y, z, salt);
                double b = worleyBoundary(Math.abs(x), y, z, salt ^ 0x9E3779B97F4A7C15L);
                yield a * 0.58 + b * 0.42;
            }
            case KALEIDOSCOPIC_CELLULAR_GRID -> {
                Polar p = radialFold(x, z, Math.max(3, radialSectors));
                yield worleyCenter(p.x(), y, p.z(), salt) * 0.62
                    + worleyBoundary(p.x() * 1.7, y, p.z() * 1.7, salt ^ 0xA24BAED4963EE407L) * 0.38;
            }
            case RECURSIVE_MIRROR_GRID -> {
                double rx = recursiveMirror(x, 2.0);
                double rz = recursiveMirror(z, 2.0);
                double coarse = worleyCenter(rx, y, rz, salt);
                double fine = worleyBoundary(recursiveMirror(x * 2.7, 1.0), y, recursiveMirror(z * 2.7, 1.0), salt ^ 0x9FB21C651E98DF25L);
                yield coarse * 0.62 + fine * 0.38;
            }
            case WORLEY_VORONOI_OCCLUSION_MAP -> worleyCenter(x, y, z, salt);
            case DUAL_WORLEY_LAYER_MAP -> worleyCenter(x * 0.63, y * 0.72, z * 0.63, salt) * 0.58
                + worleyBoundary(x * 1.86, y * 1.22, z * 1.86, salt ^ 0xD1B54A32D192ED03L) * 0.42;
            case INVERTED_CELLULAR_GRID -> {
                double a = worleyCenter(x, y, z, salt);
                double b = 1.0 - worleyCenter(-x, y, z, salt ^ 0x94D049BB133111EBL);
                yield Math.abs(a - b);
            }
            case MIRROR_SEAM_FRACTAL_MAP -> {
                double mirrored = fractal(Math.abs(x), y, z, salt);
                double disrupt = plasma(x, y, z, salt ^ 0x369DEA0F31A53F85L);
                yield mirrored * 0.78 + disrupt * 0.22;
            }
            case FOUR_WAY_SYMMETRIC_CELLULAR_MAP -> worleyCenter(Math.abs(x), y, Math.abs(z), salt);
            case RADIALLY_MIRRORED_WORLEY_MAP -> {
                Polar p = radialFold(x, z, Math.max(3, radialSectors));
                yield worleyCenter(p.x(), y, p.z(), salt);
            }
            case CELL_BOUNDARY_GRID_MASK -> worleyBoundary(x, y, z, salt);
            case CELL_CENTER_GRID_MASK -> worleyCenter(x, y, z, salt);
            case NESTED_CELLULAR_MAP -> {
                Worley coarse = worley(x * 0.52, y * 0.62, z * 0.52, salt);
                long nestedSalt = salt ^ mix((long) Math.floor(coarse.f1() * 8192.0));
                double inner = worleyCenter(x * 2.15, y * 1.45, z * 2.15, nestedSalt);
                yield (1.0 - smooth01(coarse.f1())) * 0.55 + inner * 0.45;
            }
            case FRACTAL_WORLEY_HYBRID -> worleyCenter(x, y, z, salt) * 0.60
                + fractal(x * 1.12, y, z * 1.12, salt ^ 0xDB4F0B9175AE2165L) * 0.40;
            case DOMAIN_WARPED_CELLULAR_GRID -> {
                Warp w = warp(x, y, z, salt, 0.72);
                yield worleyCenter(w.x(), w.y(), w.z(), salt ^ 0xBBE0563303A4615FL);
            }
            case MIRRORED_DOMAIN_WARP_MAP -> {
                Warp w = warp(Math.abs(x), y, z, salt, 0.70);
                double symmetric = worleyCenter(w.x(), w.y(), w.z(), salt);
                double breakNoise = plasma(x * 1.4, y, z * 1.4, salt ^ 0xA0F2EC75A1FE1575L);
                yield symmetric * 0.84 + breakNoise * 0.16;
            }
            case CELLULAR_RIDGE_MAP -> worleyBoundary(x, y, z, salt);
            case CELLULAR_BASIN_MAP -> {
                Worley w = worley(x, y, z, salt);
                yield 1.0 - smooth01(w.f1() / 0.85);
            }
            case INTERFERENCE_MIRROR_MAP -> {
                double a = worleyCenter(x, y, z, salt);
                double b = worleyCenter(-x, y, z, salt ^ 0xC13FA9A902A6328FL);
                yield clamp01(Math.abs(a - b) * 0.72 + Math.min(a, b) * 0.48);
            }
            case MULTI_AXIS_REFLECTION_FIELD -> {
                double a = worleyCenter(Math.abs(x), y, Math.abs(z), salt);
                double b = worleyCenter(Math.abs(z), y, Math.abs(x), salt ^ 0x91E10DA5C79E7B1DL);
                double c = worleyBoundary(Math.abs(x + z) * 0.707, y, Math.abs(x - z) * 0.707, salt ^ 0xC2B2AE3D27D4EB4FL);
                yield (a + b + c) / 3.0;
            }
            case OCTAVE_CELLULAR_MAP -> octaveWorley(x, y, z, salt);
            case THRESHOLDED_CELLULAR_ARCHIPELAGO -> {
                double v = worleyCenter(x, y, z, salt) * 0.68
                    + fractal(x, y, z, salt ^ 0x165667B19E3779F9L) * 0.32;
                yield v > 0.57 ? 1.0 : 0.0;
            }
            case SOFT_CELLULAR_FOG_MAP -> smooth01((worleyCenter(x, y, z, salt) - 0.18) / 0.68);
            case CELLULAR_CRACK_NETWORK -> {
                double b = worleyBoundary(x, y, z, salt);
                yield smooth01((b - 0.60) / 0.32);
            }
            case MIRRORED_CRACK_NETWORK -> {
                double b = worleyBoundary(Math.abs(x), y, z, salt);
                yield smooth01((b - 0.56) / 0.36);
            }
            case PLASMA_WORLEY_COMPOSITE -> plasma(x, y, z, salt) * 0.56
                + worleyCenter(x, y, z, salt ^ 0x85EBCA77C2B2AE63L) * 0.44;
            case FRACTAL_MIRROR_PLASMA_MAP -> {
                double f = fractal(recursiveMirror(x, 3.0), y, recursiveMirror(z, 3.0), salt);
                double p = plasma(Math.abs(x), y, Math.abs(z), salt ^ 0x27D4EB2F165667C5L);
                yield Math.rint((f * 0.62 + p * 0.38) * 4.0) / 4.0;
            }
            case CELLULAR_XOR_MAP -> {
                boolean a = worleyCenter(x, y, z, salt) > 0.52;
                boolean b = worleyCenter(-x, y, z, salt ^ 0x94D049BB133111EBL) > 0.52;
                yield a ^ b ? 1.0 : 0.0;
            }
            case CELLULAR_BOOLEAN_MAP -> {
                double a = worleyCenter(x, y, z, salt);
                double b = worleyBoundary(x * 1.73, y, z * 1.73, salt ^ 0x2545F4914F6CDD1DL);
                double c = fractal(x * 0.78, y, z * 0.78, salt ^ 0xBF58476D1CE4E5B9L);
                yield clamp01(Math.max(Math.min(a, c), b * 0.72) - Math.max(0.0, 0.45 - a) * 0.35);
            }
            case CONCENTRIC_CELLULAR_MIRROR -> {
                double radius = Math.hypot(x, z);
                double angle = Math.atan2(z, x);
                double mirroredRadius = recursiveMirror(radius, 2.2);
                yield worleyCenter(mirroredRadius, y, angle * Math.max(2, radialSectors) / TWO_PI, salt);
            }
            case SYMMETRY_BROKEN_MIRROR_MAP -> {
                double symmetric = worleyCenter(Math.abs(x), y, Math.abs(z), salt);
                double asymmetric = plasma(x * 1.51, y * 1.17, z * 1.43, salt ^ 0x4F74430C22A54005L);
                yield symmetric * 0.86 + asymmetric * 0.14;
            }
        });
    }

    private static double worleyCenter(double x, double y, double z, long salt) {
        Worley w = worley(x, y, z, salt);
        return 1.0 - smooth01(w.f1() / 0.92);
    }

    private static double worleyBoundary(double x, double y, double z, long salt) {
        Worley w = worley(x, y, z, salt);
        return 1.0 - smooth01((w.f2() - w.f1()) / 0.42);
    }

    private static Worley worley(double x, double y, double z, long salt) {
        int bx = floor(x);
        int by = floor(y);
        int bz = floor(z);
        double f1 = Double.MAX_VALUE;
        double f2 = Double.MAX_VALUE;

        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                for (int dz = -1; dz <= 1; dz++) {
                    int cx = bx + dx;
                    int cy = by + dy;
                    int cz = bz + dz;
                    long h = hash3(cx, cy, cz, salt);
                    double px = cx + 0.12 + unit(h) * 0.76;
                    double py = cy + 0.12 + unit(h ^ 0x9E3779B97F4A7C15L) * 0.76;
                    double pz = cz + 0.12 + unit(h ^ 0xC2B2AE3D27D4EB4FL) * 0.76;
                    double d = Math.sqrt((x - px) * (x - px) + (y - py) * (y - py) + (z - pz) * (z - pz));
                    if (d < f1) {
                        f2 = f1;
                        f1 = d;
                    } else if (d < f2) {
                        f2 = d;
                    }
                }
            }
        }
        return new Worley(f1, f2);
    }

    private static double octaveWorley(double x, double y, double z, long salt) {
        double sum = 0.0;
        double norm = 0.0;
        double amplitude = 0.54;
        double frequency = 0.62;
        for (int i = 0; i < 4; i++) {
            sum += worleyCenter(x * frequency, y * frequency, z * frequency, salt + i * 104729L) * amplitude;
            norm += amplitude;
            frequency *= 1.92;
            amplitude *= 0.52;
        }
        return sum / norm;
    }

    private static double fractal(double x, double y, double z, long salt) {
        double sum = 0.0;
        double norm = 0.0;
        double amplitude = 0.56;
        double frequency = 0.70;
        for (int i = 0; i < 5; i++) {
            double n = valueNoise(x * frequency, y * frequency * 1.19, z * frequency, salt + i * 65537L);
            sum += (n * 0.5 + 0.5) * amplitude;
            norm += amplitude;
            frequency *= 1.93;
            amplitude *= 0.53;
        }
        return clamp01(sum / norm);
    }

    private static double plasma(double x, double y, double z, long salt) {
        double p1 = unit(salt) * TWO_PI;
        double p2 = unit(salt ^ 0x510E527FADE682D1L) * TWO_PI;
        double p3 = unit(salt ^ 0x1F83D9ABFB41BD6BL) * TWO_PI;
        double a = Math.sin(x * 2.13 + Math.sin(z * 1.17 + p2) + p1);
        double b = Math.sin(z * 1.91 + Math.cos(y * 1.41 + p3) - p2);
        double c = Math.sin((x + z) * 0.93 + y * 1.62 + p3);
        return clamp01(((a + b + c) / 3.0) * 0.5 + 0.5);
    }

    private static Warp warp(double x, double y, double z, long salt, double strength) {
        double wx = valueNoise(x * 0.62, y * 0.47, z * 0.62, salt) * strength;
        double wz = valueNoise(x * 0.62, y * 0.47, z * 0.62, salt ^ 0x9E3779B97F4A7C15L) * strength;
        double wy = valueNoise(x * 0.38, y * 0.55, z * 0.38, salt ^ 0xC2B2AE3D27D4EB4FL) * strength * 0.42;
        return new Warp(x + wx, y + wy, z + wz);
    }

    private static Polar radialFold(double x, double z, int sectors) {
        double radius = Math.hypot(x, z);
        double angle = Math.atan2(z, x);
        double sector = TWO_PI / sectors;
        double folded = Math.abs(((angle + sector * 0.5) % sector + sector) % sector - sector * 0.5);
        return new Polar(Math.cos(folded) * radius, Math.sin(folded) * radius);
    }

    private static double recursiveMirror(double value, double scale) {
        double v = Math.abs(value);
        double cell = v / scale;
        double frac = cell - Math.floor(cell);
        double folded = frac <= 0.5 ? frac : 1.0 - frac;
        return Math.floor(cell) * scale + folded * scale;
    }

    private static double valueNoise(double x, double y, double z, long salt) {
        int x0 = floor(x);
        int y0 = floor(y);
        int z0 = floor(z);
        double tx = smooth01(x - x0);
        double ty = smooth01(y - y0);
        double tz = smooth01(z - z0);

        double n000 = signedUnit(hash3(x0, y0, z0, salt));
        double n100 = signedUnit(hash3(x0 + 1, y0, z0, salt));
        double n010 = signedUnit(hash3(x0, y0 + 1, z0, salt));
        double n110 = signedUnit(hash3(x0 + 1, y0 + 1, z0, salt));
        double n001 = signedUnit(hash3(x0, y0, z0 + 1, salt));
        double n101 = signedUnit(hash3(x0 + 1, y0, z0 + 1, salt));
        double n011 = signedUnit(hash3(x0, y0 + 1, z0 + 1, salt));
        double n111 = signedUnit(hash3(x0 + 1, y0 + 1, z0 + 1, salt));

        double a = lerp(n000, n100, tx);
        double b = lerp(n010, n110, tx);
        double c = lerp(n001, n101, tx);
        double d = lerp(n011, n111, tx);
        return lerp(lerp(a, b, ty), lerp(c, d, ty), tz);
    }

    private static long hash3(int x, int y, int z, long salt) {
        long v = salt;
        v ^= (long) x * 0x9E3779B97F4A7C15L;
        v ^= (long) y * 0xD1B54A32D192ED03L;
        v ^= (long) z * 0xC2B2AE3D27D4EB4FL;
        return mix(v);
    }

    private static int floor(double value) {
        int i = (int) value;
        return value < i ? i - 1 : i;
    }

    private static double smooth01(double value) {
        value = clamp01(value);
        return value * value * (3.0 - 2.0 * value);
    }

    private static double lerp(double a, double b, double t) {
        return a + (b - a) * t;
    }

    private static double clamp01(double value) {
        return Math.max(0.0, Math.min(1.0, value));
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

    private record Worley(double f1, double f2) { }
    private record Warp(double x, double y, double z) { }
    private record Polar(double x, double z) { }
}
