package io.continuityworks.api.blueprint;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.function.UnaryOperator;

/**
 * Pure compact-IR modification and composition utilities.
 * No method expands a blueprint into a retained per-block list or touches live world state.
 */
public final class CompactBlueprintModifier {
    public static final String MODIFIER_VERSION = "compact-modifier/v1";
    public static final int MAX_MODIFIED_PRIMITIVES = 4096;
    public static final int MAX_REPEAT_COPIES = 64;
    public static final long MAX_MODIFIED_OPERATIONS = CompactBlueprintMaterializer.MAX_STREAM_OPERATIONS;

    public enum Rotation { NONE, CLOCKWISE_90, CLOCKWISE_180, CLOCKWISE_270 }
    public enum MirrorAxis { X, Z }

    private CompactBlueprintModifier() {}

    public static CompactBlueprintPlan translate(CompactBlueprintPlan source, BlockPosition delta) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(delta, "delta");
        BlockPosition anchor = offsetExact(source.anchor(), delta);
        return rebuild(source, source.primitives(), source.palette(), anchor, source.facing(),
            "translate:" + delta.x() + "," + delta.y() + "," + delta.z());
    }

    public static CompactBlueprintPlan rotate(CompactBlueprintPlan source, Rotation rotation) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(rotation, "rotation");
        if (rotation == Rotation.NONE) {
            return rebuild(source, source.primitives(), source.palette(), source.anchor(), source.facing(), "rotate:none");
        }
        Bounds envelope = geometryBounds(source);
        int width = envelope.width();
        int depth = envelope.depth();
        UnaryOperator<BlockPosition> mapper = position -> rotatePoint(position, envelope, width, depth, rotation);
        List<CompactBlueprintPrimitive> primitives = transform(source.primitives(), mapper);
        Facing facing = rotateFacing(source.facing(), rotation);
        return rebuild(source, primitives, source.palette(), source.anchor(), facing, "rotate:" + rotation.name());
    }

    public static CompactBlueprintPlan mirror(CompactBlueprintPlan source, MirrorAxis axis) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(axis, "axis");
        Bounds envelope = geometryBounds(source);
        UnaryOperator<BlockPosition> mapper = position -> switch (axis) {
            case X -> new BlockPosition(
                toIntExact((long)envelope.max().x() - ((long)position.x() - envelope.min().x())),
                position.y(), position.z());
            case Z -> new BlockPosition(
                position.x(), position.y(),
                toIntExact((long)envelope.max().z() - ((long)position.z() - envelope.min().z())));
        };
        List<CompactBlueprintPrimitive> primitives = transform(source.primitives(), mapper);
        return rebuild(source, primitives, source.palette(), source.anchor(), mirrorFacing(source.facing(), axis),
            "mirror:" + axis.name());
    }

    /** Remap primitive palette references to other existing palette keys. */
    public static CompactBlueprintPlan remapPalette(CompactBlueprintPlan source, Map<String, String> remap) {
        Objects.requireNonNull(source, "source");
        Map<String, String> requested = Map.copyOf(Objects.requireNonNull(remap, "remap"));
        Set<String> keys = paletteKeys(source.palette());
        for (Map.Entry<String, String> entry : requested.entrySet()) {
            if (entry.getKey() == null || entry.getValue() == null || entry.getKey().isBlank() || entry.getValue().isBlank()) {
                throw new IllegalArgumentException("palette remap keys and values must not be blank");
            }
            if (!keys.contains(entry.getKey())) throw new IllegalArgumentException("Unknown source palette key " + entry.getKey());
            if (!keys.contains(entry.getValue())) throw new IllegalArgumentException("Unknown target palette key " + entry.getValue());
        }
        ArrayList<CompactBlueprintPrimitive> primitives = new ArrayList<>(source.primitives().size());
        for (CompactBlueprintPrimitive primitive : source.primitives()) {
            String paletteKey = primitive.paletteKey();
            if (paletteKey != null) paletteKey = requested.getOrDefault(paletteKey, paletteKey);
            primitives.add(copy(primitive, primitive.sequence(), primitive.from(), primitive.to(), paletteKey));
        }
        return rebuild(source, primitives, source.palette(), source.anchor(), source.facing(), "palette-remap:" + canonicalMap(requested));
    }

    /** Replace one palette definition without changing primitive keys. */
    public static CompactBlueprintPlan replacePaletteEntry(CompactBlueprintPlan source, String key, PaletteEntry replacement) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(replacement, "replacement");
        if (!key.equals(replacement.key())) throw new IllegalArgumentException("replacement palette key must remain " + key);
        ArrayList<PaletteEntry> palette = new ArrayList<>(source.palette());
        boolean replaced = false;
        for (int i = 0; i < palette.size(); i++) {
            if (palette.get(i).key().equals(key)) {
                palette.set(i, replacement);
                replaced = true;
                break;
            }
        }
        if (!replaced) throw new IllegalArgumentException("Unknown palette key " + key);
        return rebuild(source, source.primitives(), palette, source.anchor(), source.facing(),
            "palette-entry:" + key + "=" + replacement.blockState() + ":" + replacement.materialId());
    }

    public static CompactBlueprintPlan replacePrimitive(CompactBlueprintPlan source, int sequence, CompactBlueprintPrimitive replacement) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(replacement, "replacement");
        if (sequence < 0 || sequence >= source.primitives().size()) throw new IndexOutOfBoundsException("primitive sequence " + sequence);
        if (replacement.sequence() != sequence) throw new IllegalArgumentException("replacement primitive sequence must equal target sequence");
        validatePaletteReferences(List.of(replacement), source.palette());
        ArrayList<CompactBlueprintPrimitive> primitives = new ArrayList<>(source.primitives());
        primitives.set(sequence, replacement);
        return rebuild(source, primitives, source.palette(), source.anchor(), source.facing(), "replace-primitive:" + sequence);
    }

    /** Append one reusable module at a local compact-plan offset. */
    public static CompactBlueprintPlan compose(CompactBlueprintPlan source, CompactBlueprintModule module, BlockPosition offset) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(module, "module");
        Objects.requireNonNull(offset, "offset");
        validatePaletteReferences(module.primitives(), source.palette());
        ArrayList<CompactBlueprintPrimitive> primitives = new ArrayList<>(source.primitives().size() + module.primitives().size());
        primitives.addAll(source.primitives());
        for (CompactBlueprintPrimitive primitive : module.primitives()) {
            primitives.add(shiftPrimitive(primitive, offset));
        }
        return rebuild(source, primitives, source.palette(), source.anchor(), source.facing(),
            "compose:" + module.moduleId() + "@" + offset.x() + "," + offset.y() + "," + offset.z());
    }

    /** Append count copies of a module beginning at firstOffset and advancing by step. */
    public static CompactBlueprintPlan repeat(
        CompactBlueprintPlan source,
        CompactBlueprintModule module,
        int count,
        BlockPosition firstOffset,
        BlockPosition step
    ) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(module, "module");
        Objects.requireNonNull(firstOffset, "firstOffset");
        Objects.requireNonNull(step, "step");
        if (count < 1 || count > MAX_REPEAT_COPIES) {
            throw new IllegalArgumentException("repeat count must be between 1 and " + MAX_REPEAT_COPIES);
        }
        validatePaletteReferences(module.primitives(), source.palette());
        long projected = (long)source.primitives().size() + (long)module.primitives().size() * count;
        if (projected > MAX_MODIFIED_PRIMITIVES) {
            throw new IllegalArgumentException("repeat would exceed compact primitive budget " + MAX_MODIFIED_PRIMITIVES);
        }
        ArrayList<CompactBlueprintPrimitive> primitives = new ArrayList<>((int)projected);
        primitives.addAll(source.primitives());
        for (int copy = 0; copy < count; copy++) {
            BlockPosition offset = new BlockPosition(
                toIntExact((long)firstOffset.x() + (long)step.x() * copy),
                toIntExact((long)firstOffset.y() + (long)step.y() * copy),
                toIntExact((long)firstOffset.z() + (long)step.z() * copy)
            );
            for (CompactBlueprintPrimitive primitive : module.primitives()) {
                primitives.add(shiftPrimitive(primitive, offset));
            }
        }
        return rebuild(source, primitives, source.palette(), source.anchor(), source.facing(),
            "repeat:" + module.moduleId() + ":" + count + ":first=" + firstOffset + ":step=" + step);
    }

    private static CompactBlueprintPlan rebuild(
        CompactBlueprintPlan source,
        List<CompactBlueprintPrimitive> inputPrimitives,
        List<PaletteEntry> inputPalette,
        BlockPosition requestedAnchor,
        Facing facing,
        String editTag
    ) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(requestedAnchor, "requestedAnchor");
        Objects.requireNonNull(facing, "facing");
        Objects.requireNonNull(editTag, "editTag");
        List<PaletteEntry> palette = List.copyOf(inputPalette);
        List<CompactBlueprintPrimitive> resequenced = resequence(List.copyOf(inputPrimitives));
        if (resequenced.size() > MAX_MODIFIED_PRIMITIVES) {
            throw new IllegalArgumentException("modified compact plan exceeds primitive budget " + MAX_MODIFIED_PRIMITIVES);
        }
        validatePaletteReferences(resequenced, palette);

        NormalizedGeometry normalized = normalizeGeometry(resequenced, requestedAnchor, source.dimensions());
        if (!containsBounds(source.constructionVolume(), normalized.anchor(), normalized.dimensions())) {
            throw new IllegalArgumentException("modified compact plan leaves the selected construction volume");
        }

        Metrics metrics = metrics(normalized.primitives(), palette);
        Map<String, Long> available = source.materials().available();
        Map<String, Long> missing = missing(metrics.required(), available);
        String hash = sha256(canonical(source, normalized, palette, facing, editTag));
        UUID blueprintId = UUID.nameUUIDFromBytes((MODIFIER_VERSION + ":" + hash).getBytes(StandardCharsets.UTF_8));
        MaterialManifest manifest = new MaterialManifest(blueprintId, metrics.required(), available, missing);

        ArrayList<MaterialIssue> materialIssues = new ArrayList<>();
        for (Map.Entry<String, Long> entry : missing.entrySet()) {
            materialIssues.add(new MaterialIssue(entry.getKey(), MaterialIssue.Kind.MISSING,
                metrics.required().getOrDefault(entry.getKey(), 0L), available.getOrDefault(entry.getKey(), 0L),
                "Modified compact plan requires more material than the retained availability snapshot provides."));
        }

        ArrayList<BlueprintWarning> warnings = new ArrayList<>();
        for (BlueprintWarning warning : source.warnings()) {
            if (!"REVALIDATION_REQUIRED".equals(warning.code())) warnings.add(warning);
        }
        warnings.add(new BlueprintWarning("REVALIDATION_REQUIRED", BlueprintWarning.Severity.WARNING,
            "Modified compact blueprint must be validated against a fresh live-world context before execution."));

        Map<String, String> attributes = new HashMap<>(source.preview().attributes());
        attributes.put("modified", "true");
        attributes.put("modifier_version", MODIFIER_VERSION);
        attributes.put("modification", editTag);
        attributes.put("source_blueprint_id", source.blueprintId().toString());
        attributes.put("source_blueprint_version", source.blueprintVersion());
        attributes.put("requires_revalidation", "true");
        attributes.put("primitive_count", Integer.toString(normalized.primitives().size()));

        return new CompactBlueprintPlan(
            blueprintId,
            MODIFIER_VERSION,
            "SHA-256",
            hash,
            source.dimensionId(),
            source.constructionVolume(),
            normalized.dimensions(),
            normalized.anchor(),
            facing,
            source.specificationResolutions(),
            palette,
            manifest,
            normalized.primitives(),
            materialIssues,
            new WorkloadEstimate(metrics.placements(), metrics.removals(), 0L, metrics.operations()),
            new PreviewMetadata(source.preview().title(), source.preview().description(), source.preview().styleId(), attributes),
            source.confidence(),
            warnings
        );
    }

    private static Metrics metrics(List<CompactBlueprintPrimitive> primitives, List<PaletteEntry> palette) {
        Map<String, String> materialByKey = new HashMap<>();
        for (PaletteEntry entry : palette) materialByKey.put(entry.key(), entry.materialId());
        Map<String, Long> required = new HashMap<>();
        long[] placements = {0L};
        long[] removals = {0L};
        long operations = CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            if (kind == PlacementOperation.Kind.CLEAR) {
                removals[0]++;
            } else {
                placements[0]++;
                if (kind == PlacementOperation.Kind.REPLACE) removals[0]++;
                String material = materialByKey.get(paletteKey);
                if (material == null) throw new IllegalArgumentException("Unknown palette key " + paletteKey);
                required.merge(material, 1L, Long::sum);
            }
            return true;
        }, MAX_MODIFIED_OPERATIONS);
        return new Metrics(Map.copyOf(required), placements[0], removals[0], operations);
    }

    private static Map<String, Long> missing(Map<String, Long> required, Map<String, Long> available) {
        HashMap<String, Long> missing = new HashMap<>();
        for (Map.Entry<String, Long> entry : required.entrySet()) {
            long have = available.getOrDefault(entry.getKey(), 0L);
            if (have < entry.getValue()) missing.put(entry.getKey(), entry.getValue() - have);
        }
        return Map.copyOf(missing);
    }

    private static NormalizedGeometry normalizeGeometry(
        List<CompactBlueprintPrimitive> primitives,
        BlockPosition requestedAnchor,
        Bounds fallbackDimensions
    ) {
        if (primitives.isEmpty()) {
            return new NormalizedGeometry(primitives, requestedAnchor, fallbackDimensions);
        }
        Bounds envelope = geometryBounds(primitives);
        BlockPosition shift = new BlockPosition(
            toIntExact(-(long)envelope.min().x()),
            toIntExact(-(long)envelope.min().y()),
            toIntExact(-(long)envelope.min().z())
        );
        ArrayList<CompactBlueprintPrimitive> normalized = new ArrayList<>(primitives.size());
        for (CompactBlueprintPrimitive primitive : primitives) normalized.add(shiftPrimitive(primitive, shift));
        BlockPosition anchor = offsetExact(requestedAnchor, envelope.min());
        Bounds dimensions = new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(
            toIntExact((long)envelope.max().x() - envelope.min().x()),
            toIntExact((long)envelope.max().y() - envelope.min().y()),
            toIntExact((long)envelope.max().z() - envelope.min().z())
        ));
        return new NormalizedGeometry(resequence(normalized), anchor, dimensions);
    }

    private static Bounds geometryBounds(CompactBlueprintPlan plan) {
        return plan.primitives().isEmpty() ? plan.dimensions() : geometryBounds(plan.primitives());
    }

    private static Bounds geometryBounds(List<CompactBlueprintPrimitive> primitives) {
        if (primitives.isEmpty()) throw new IllegalArgumentException("geometry has no primitives");
        Bounds first = primitives.get(0).localBounds();
        int minX = first.min().x(), minY = first.min().y(), minZ = first.min().z();
        int maxX = first.max().x(), maxY = first.max().y(), maxZ = first.max().z();
        for (int i = 1; i < primitives.size(); i++) {
            Bounds bounds = primitives.get(i).localBounds();
            minX = Math.min(minX, bounds.min().x()); minY = Math.min(minY, bounds.min().y()); minZ = Math.min(minZ, bounds.min().z());
            maxX = Math.max(maxX, bounds.max().x()); maxY = Math.max(maxY, bounds.max().y()); maxZ = Math.max(maxZ, bounds.max().z());
        }
        return new Bounds(new BlockPosition(minX, minY, minZ), new BlockPosition(maxX, maxY, maxZ));
    }

    private static List<CompactBlueprintPrimitive> transform(List<CompactBlueprintPrimitive> primitives, UnaryOperator<BlockPosition> mapper) {
        ArrayList<CompactBlueprintPrimitive> transformed = new ArrayList<>(primitives.size());
        for (CompactBlueprintPrimitive primitive : primitives) {
            BlockPosition from = mapper.apply(primitive.from());
            BlockPosition to = mapper.apply(primitive.to());
            if (primitive.kind() == CompactBlueprintPrimitive.Kind.FILL_BOX || primitive.kind() == CompactBlueprintPrimitive.Kind.HOLLOW_BOX) {
                BlockPosition min = min(from, to), max = max(from, to);
                from = min; to = max;
            }
            if (primitive.kind() == CompactBlueprintPrimitive.Kind.CYLINDER) {
                int minY = Math.min(from.y(), to.y()), maxY = Math.max(from.y(), to.y());
                from = new BlockPosition(from.x(), minY, from.z());
                to = new BlockPosition(from.x(), maxY, from.z());
            }
            transformed.add(copy(primitive, primitive.sequence(), from, to, primitive.paletteKey()));
        }
        return List.copyOf(transformed);
    }

    private static CompactBlueprintPrimitive shiftPrimitive(CompactBlueprintPrimitive primitive, BlockPosition offset) {
        return copy(primitive, primitive.sequence(), offsetExact(primitive.from(), offset), offsetExact(primitive.to(), offset), primitive.paletteKey());
    }

    private static CompactBlueprintPrimitive copy(
        CompactBlueprintPrimitive source,
        int sequence,
        BlockPosition from,
        BlockPosition to,
        String paletteKey
    ) {
        return new CompactBlueprintPrimitive(sequence, source.kind(), source.operationKind(), from, to,
            source.radius(), source.flags(), paletteKey);
    }

    private static List<CompactBlueprintPrimitive> resequence(List<CompactBlueprintPrimitive> primitives) {
        ArrayList<CompactBlueprintPrimitive> result = new ArrayList<>(primitives.size());
        for (int i = 0; i < primitives.size(); i++) {
            CompactBlueprintPrimitive primitive = Objects.requireNonNull(primitives.get(i), "primitive");
            result.add(copy(primitive, i, primitive.from(), primitive.to(), primitive.paletteKey()));
        }
        return List.copyOf(result);
    }

    private static void validatePaletteReferences(List<CompactBlueprintPrimitive> primitives, List<PaletteEntry> palette) {
        Set<String> keys = paletteKeys(palette);
        for (CompactBlueprintPrimitive primitive : primitives) {
            if (primitive.operationKind() != PlacementOperation.Kind.CLEAR && !keys.contains(primitive.paletteKey())) {
                throw new IllegalArgumentException("Primitive references unknown palette key " + primitive.paletteKey());
            }
        }
    }

    private static Set<String> paletteKeys(List<PaletteEntry> palette) {
        HashSet<String> keys = new HashSet<>();
        for (PaletteEntry entry : palette) {
            if (!keys.add(entry.key())) throw new IllegalArgumentException("Duplicate palette key " + entry.key());
        }
        return Set.copyOf(keys);
    }

    private static boolean containsBounds(ConstructionVolume volume, BlockPosition anchor, Bounds dimensions) {
        return volume.contains(anchor.offset(dimensions.min())) && volume.contains(anchor.offset(dimensions.max()));
    }

    private static BlockPosition rotatePoint(BlockPosition point, Bounds envelope, int width, int depth, Rotation rotation) {
        long x = (long)point.x() - envelope.min().x();
        long z = (long)point.z() - envelope.min().z();
        return switch (rotation) {
            case CLOCKWISE_90 -> new BlockPosition(toIntExact((long)depth - 1L - z), point.y(), toIntExact(x));
            case CLOCKWISE_180 -> new BlockPosition(toIntExact((long)width - 1L - x), point.y(), toIntExact((long)depth - 1L - z));
            case CLOCKWISE_270 -> new BlockPosition(toIntExact(z), point.y(), toIntExact((long)width - 1L - x));
            case NONE -> point;
        };
    }

    private static Facing rotateFacing(Facing facing, Rotation rotation) {
        if (facing == Facing.UP || facing == Facing.DOWN || rotation == Rotation.NONE) return facing;
        return switch (rotation) {
            case CLOCKWISE_90 -> switch (facing) { case NORTH -> Facing.EAST; case EAST -> Facing.SOUTH; case SOUTH -> Facing.WEST; case WEST -> Facing.NORTH; default -> facing; };
            case CLOCKWISE_180 -> switch (facing) { case NORTH -> Facing.SOUTH; case SOUTH -> Facing.NORTH; case EAST -> Facing.WEST; case WEST -> Facing.EAST; default -> facing; };
            case CLOCKWISE_270 -> switch (facing) { case NORTH -> Facing.WEST; case WEST -> Facing.SOUTH; case SOUTH -> Facing.EAST; case EAST -> Facing.NORTH; default -> facing; };
            case NONE -> facing;
        };
    }

    private static Facing mirrorFacing(Facing facing, MirrorAxis axis) {
        return switch (axis) {
            case X -> switch (facing) { case EAST -> Facing.WEST; case WEST -> Facing.EAST; default -> facing; };
            case Z -> switch (facing) { case NORTH -> Facing.SOUTH; case SOUTH -> Facing.NORTH; default -> facing; };
        };
    }

    private static BlockPosition offsetExact(BlockPosition position, BlockPosition delta) {
        return new BlockPosition(
            Math.addExact(position.x(), delta.x()),
            Math.addExact(position.y(), delta.y()),
            Math.addExact(position.z(), delta.z())
        );
    }

    private static BlockPosition min(BlockPosition a, BlockPosition b) {
        return new BlockPosition(Math.min(a.x(), b.x()), Math.min(a.y(), b.y()), Math.min(a.z(), b.z()));
    }

    private static BlockPosition max(BlockPosition a, BlockPosition b) {
        return new BlockPosition(Math.max(a.x(), b.x()), Math.max(a.y(), b.y()), Math.max(a.z(), b.z()));
    }

    private static int toIntExact(long value) { return Math.toIntExact(value); }

    private static String canonicalMap(Map<String, String> values) {
        TreeMap<String, String> sorted = new TreeMap<>(values);
        StringBuilder out = new StringBuilder();
        for (Map.Entry<String, String> entry : sorted.entrySet()) {
            if (out.length() > 0) out.append(',');
            out.append(entry.getKey()).append("->").append(entry.getValue());
        }
        return out.toString();
    }

    private static String canonical(
        CompactBlueprintPlan source,
        NormalizedGeometry geometry,
        List<PaletteEntry> palette,
        Facing facing,
        String editTag
    ) {
        StringBuilder out = new StringBuilder(2048);
        out.append(MODIFIER_VERSION).append('|').append(source.integrityHash()).append('|').append(editTag).append('|')
            .append(source.dimensionId()).append('|').append(source.constructionVolume().volumeId()).append('|')
            .append(source.constructionVolume().snapshotEpoch()).append('|').append(source.constructionVolume().bounds()).append('|')
            .append(geometry.anchor()).append('|').append(geometry.dimensions()).append('|').append(facing);
        for (PaletteEntry entry : palette) {
            out.append("|P:").append(entry.key()).append('=').append(entry.blockState()).append(':').append(entry.materialId());
            TreeMap<String, String> metadata = new TreeMap<>(entry.metadata());
            for (Map.Entry<String, String> item : metadata.entrySet()) out.append(':').append(item.getKey()).append('=').append(item.getValue());
        }
        for (CompactBlueprintPrimitive primitive : geometry.primitives()) {
            out.append("|G:").append(primitive.sequence()).append(':').append(primitive.kind()).append(':').append(primitive.operationKind())
                .append(':').append(primitive.from()).append(':').append(primitive.to()).append(':').append(primitive.radius())
                .append(':').append(primitive.flags()).append(':').append(primitive.paletteKey());
        }
        return out.toString();
    }

    private static String sha256(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("SHA-256 unavailable", impossible);
        }
    }

    private record NormalizedGeometry(List<CompactBlueprintPrimitive> primitives, BlockPosition anchor, Bounds dimensions) {}
    private record Metrics(Map<String, Long> required, long placements, long removals, long operations) {}
}
