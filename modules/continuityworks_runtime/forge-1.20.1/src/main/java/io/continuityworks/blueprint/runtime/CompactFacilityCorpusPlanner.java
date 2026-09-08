package io.continuityworks.blueprint.runtime;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import io.continuityworks.api.blueprint.*;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/**
 * Lazy primitive-preserving adapter for the bundled Continuity Works facility corpus.
 * It opens only the manifest, up to MAX_CANDIDATES reference files, and one selected
 * corporate palette. Fixed references are rotated and anchored but never block-expanded.
 */
final class CompactFacilityCorpusPlanner {
    static final int MAX_CANDIDATES = 8;
    private static final String ROOT = "continuityworks/facility_library/";
    private volatile Index index;

    Optional<CompactBlueprintPlan> plan(BlueprintRequest request) {
        Map<String, BlueprintSpecification> specs = first(request.specifications());
        boolean explicitSelector = specs.containsKey("REFERENCE") || specs.containsKey("ARCHETYPE") || specs.containsKey("CATEGORY");
        if (!explicitSelector) return Optional.empty();

        List<Scored> ranked = rank(specs);
        if (ranked.isEmpty()) throw new IllegalArgumentException("No Continuity Works facility reference matches the requested selector.");

        Candidate best = null;
        int opened = 0;
        for (Scored scored : ranked) {
            if (opened++ >= MAX_CANDIDATES) break;
            Candidate candidate = load(scored, request, specs);
            if (candidate == null) continue;
            if (best == null || candidate.score() > best.score()) best = candidate;
        }
        if (best == null) throw new IllegalArgumentException("No matching Continuity Works facility reference fits the selected construction volume within the bounded candidate window.");
        return Optional.of(compile(best, request, specs));
    }

    private Candidate load(Scored scored, BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        JsonObject ref = json(scored.entry().path());
        String refId = text(ref, "reference_id");
        String archetype = text(ref, "archetype_id");
        String corporate = text(ref, "corporate_language_id");
        if (specs.containsKey("REFERENCE") && !idMatches(specs.get("REFERENCE").value(), refId)) return null;
        if (specs.containsKey("ARCHETYPE") && !idMatches(specs.get("ARCHETYPE").value(), archetype)) return null;

        JsonArray size = ref.getAsJsonArray("size");
        int sw = size.get(0).getAsInt(), sh = size.get(1).getAsInt(), sd = size.get(2).getAsInt();
        Dims dims = rotateDims(sw, sh, sd, request.preferredFacing());
        Bounds volume = request.constructionVolume().bounds();
        if (dims.width() > volume.width() || dims.height() > volume.height() || dims.depth() > volume.depth()) return null;

        int score = scored.score();
        String sizeClass = sizeClass(dims, volume);
        BlueprintSpecification requestedSize = specs.get("SIZE");
        if (requestedSize != null) score += normalize(requestedSize.value()).equals(sizeClass) ? 80 : -20;
        return new Candidate(scored.entry(), ref, refId, archetype, corporate, dims, sizeClass, score, sw, sd);
    }

    private CompactBlueprintPlan compile(Candidate c, BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        Entry corporateEntry = index().byId().get(c.corporateId());
        if (corporateEntry == null) throw new IllegalStateException("Missing corporate palette " + c.corporateId());
        JsonObject paletteJson = json(corporateEntry.path()).getAsJsonObject("palette");
        Map<String, String> roles = new HashMap<>();
        for (Map.Entry<String, JsonElement> entry : paletteJson.entrySet()) roles.put(entry.getKey(), entry.getValue().getAsString());

        List<SourcePrimitive> source = new ArrayList<>();
        SortedSet<String> blocks = new TreeSet<>();
        for (JsonElement element : c.ref().getAsJsonArray("blueprint")) {
            JsonObject primitive = element.getAsJsonObject();
            String block = primitive.has("block") ? primitive.get("block").getAsString() : roles.get(text(primitive, "role"));
            if (block == null || !block.startsWith("minecraft:")) throw new IllegalStateException("Invalid corpus block " + block);
            blocks.add(block);
            source.add(new SourcePrimitive(primitive, block));
        }

        Map<String, String> paletteKeyByBlock = new LinkedHashMap<>();
        List<PaletteEntry> palette = new ArrayList<>(blocks.size());
        int paletteIndex = 0;
        for (String block : blocks) {
            String key = "p" + paletteIndex++;
            paletteKeyByBlock.put(block, key);
            palette.add(new PaletteEntry(key, block, block, Map.of("source", "facility_corpus_compact")));
        }

        ArrayList<CompactBlueprintPrimitive> primitives = new ArrayList<>(source.size());
        int sequence = 0;
        for (SourcePrimitive sourcePrimitive : source) {
            JsonObject p = sourcePrimitive.json();
            String paletteKey = paletteKeyByBlock.get(sourcePrimitive.block());
            String op = text(p, "op");
            switch (op) {
                case "block" -> {
                    BlockPosition pos = rotate(position(p.getAsJsonArray("pos")), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    primitives.add(CompactBlueprintPrimitive.block(sequence++, pos, paletteKey));
                }
                case "fill_box", "hollow_box" -> {
                    BlockPosition a = rotate(position(p.getAsJsonArray("min")), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    BlockPosition b = rotate(position(p.getAsJsonArray("max")), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    BlockPosition min = min(a, b), max = max(a, b);
                    primitives.add("fill_box".equals(op)
                        ? CompactBlueprintPrimitive.fillBox(sequence++, min, max, paletteKey)
                        : CompactBlueprintPrimitive.hollowBox(sequence++, min, max, paletteKey));
                }
                case "line" -> {
                    BlockPosition a = rotate(position(p.getAsJsonArray("start")), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    BlockPosition b = rotate(position(p.getAsJsonArray("end")), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    primitives.add(CompactBlueprintPrimitive.line(sequence++, a, b, paletteKey));
                }
                case "cylinder" -> {
                    JsonArray center = p.getAsJsonArray("center");
                    int cx = center.get(0).getAsInt(), cz = center.get(1).getAsInt();
                    int y0 = p.get("y_min").getAsInt(), y1 = p.get("y_max").getAsInt();
                    BlockPosition rotatedCenter = rotate(new BlockPosition(cx, y0, cz), c.sourceWidth(), c.sourceDepth(), request.preferredFacing());
                    int radius = p.get("radius").getAsInt();
                    boolean solid = p.has("mode") && "solid".equals(p.get("mode").getAsString());
                    boolean caps = p.has("caps") && p.get("caps").getAsBoolean();
                    primitives.add(CompactBlueprintPrimitive.cylinder(sequence++, rotatedCenter,
                        new BlockPosition(rotatedCenter.x(), y1, rotatedCenter.z()), radius, solid, caps, paletteKey));
                }
                default -> throw new IllegalStateException("Unsupported compact corpus primitive " + op);
            }
        }
        if (primitives.size() > CompactBlueprintProvider.MAX_PRIMITIVES) {
            throw new IllegalArgumentException("Facility reference exceeds compact primitive budget " + CompactBlueprintProvider.MAX_PRIMITIVES);
        }
        OperationCounts operationCounts = operationCounts(primitives);

        BlockPosition anchor = anchor(request.preferredOrigin(), request.constructionVolume().bounds(), c.dims());
        Bounds localBounds = new Bounds(new BlockPosition(0, 0, 0),
            new BlockPosition(c.dims().width() - 1, c.dims().height() - 1, c.dims().depth() - 1));
        String version = "facility-corpus-compact/" + index().version() + "/v" + c.ref().get("version").getAsInt();
        String hash = sha256(canonical(c, request, anchor, palette, primitives));
        UUID blueprintId = UUID.nameUUIDFromBytes((version + ":" + hash).getBytes(StandardCharsets.UTF_8));
        MaterialManifest manifest = manifest(blueprintId, palette, primitives, request.availableMaterials());
        List<MaterialIssue> materialIssues = issues(manifest);
        List<SpecificationResolution> ledger = ledger(c, request, specs);
        List<BlueprintWarning> warnings = warnings(ledger, specs);
        if (!materialIssues.isEmpty()) warnings.add(new BlueprintWarning("MATERIALS_INCOMPLETE", BlueprintWarning.Severity.WARNING,
            "Current material snapshot cannot satisfy all ordered primitive placements."));

        double confidence = warnings.stream().anyMatch(w -> w.severity() == BlueprintWarning.Severity.ERROR) ? 0.45 : 0.99;
        Map<String, String> metadata = Map.of(
            "reference", c.refId(),
            "archetype", c.archetypeId(),
            "category", c.entry().category(),
            "corporate_language", c.corporateId(),
            "size_class", c.sizeClass(),
            "planner", "compact_lazy_facility_corpus",
            "primitive_count", Integer.toString(primitives.size())
        );

        CompactBlueprintPlan plan = new CompactBlueprintPlan(
            blueprintId, version, "SHA-256", hash, request.dimensionId(), request.constructionVolume(), localBounds,
            anchor, request.preferredFacing(), ledger, palette, manifest, primitives, materialIssues,
            new WorkloadEstimate(operationCounts.placements(), operationCounts.clears(), 0, operationCounts.total()),
            new PreviewMetadata(request.buildPurpose(), c.ref().has("description") ? c.ref().get("description").getAsString() : c.refId(),
                c.entry().category(), metadata),
            confidence, warnings
        );
        if (!plan.allPrimitiveBoundsInsideConstructionVolume()) throw new IllegalStateException("Compact corpus plan escaped construction volume");
        return plan;
    }

    private List<Scored> rank(Map<String, BlueprintSpecification> specs) {
        List<Scored> ranked = new ArrayList<>();
        for (Entry entry : index().references()) {
            int score = "baseline".equalsIgnoreCase(entry.status()) ? 5 : 0;
            BlueprintSpecification ref = specs.get("REFERENCE");
            BlueprintSpecification category = specs.get("CATEGORY");
            BlueprintSpecification archetype = specs.get("ARCHETYPE");
            if (ref != null) {
                if (!idMatches(ref.value(), entry.id())) continue;
                score += 10_000;
            }
            if (category != null) {
                if (!normalize(category.value()).equals(normalize(entry.category()))) continue;
                score += 1_000;
            }
            if (archetype != null) {
                String wanted = slug(archetype.value());
                String hay = slug(entry.id()) + " " + normalize(entry.path());
                score += tokenScore(wanted, hay);
            }
            ranked.add(new Scored(entry, score));
        }
        ranked.sort(Comparator.comparingInt(Scored::score).reversed().thenComparing(scored -> scored.entry().id()));
        return ranked;
    }

    private List<SpecificationResolution> ledger(Candidate c, BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        ArrayList<SpecificationResolution> ledger = new ArrayList<>();
        applySelector(ledger, specs.get("REFERENCE"), "REFERENCE", c.refId());
        applySelector(ledger, specs.get("ARCHETYPE"), "ARCHETYPE", c.archetypeId());
        applySelector(ledger, specs.get("CATEGORY"), "CATEGORY", normalize(c.entry().category()));

        BlueprintSpecification size = specs.get("SIZE");
        if (size == null) {
            ledger.add(new SpecificationResolution("SIZE", "", c.sizeClass(), SpecificationResolution.Status.DEFAULTED,
                "Fixed reference size class resolved against the selected construction volume."));
        } else if (normalize(size.value()).equals(c.sizeClass())) {
            ledger.add(new SpecificationResolution("SIZE", size.value(), c.sizeClass(), SpecificationResolution.Status.APPLIED,
                "Fixed reference already matches the requested size class."));
        } else {
            ledger.add(new SpecificationResolution("SIZE", size.value(), c.sizeClass(), SpecificationResolution.Status.UNSUPPORTED,
                "Fixed facility references are not rescaled; the closest fitting reference was retained."));
        }

        BlueprintSpecification detail = specs.get("PURPOSE_DETAIL");
        if (detail != null) ledger.add(new SpecificationResolution("PURPOSE_DETAIL", detail.value(), detail.value(),
            SpecificationResolution.Status.APPLIED, "Preserved as semantic metadata."));

        Set<String> fixedGeometry = Set.of("STYLE", "ROOF", "FLOORS", "ENTRANCE");
        for (String key : fixedGeometry) {
            BlueprintSpecification spec = specs.get(key);
            if (spec != null) ledger.add(new SpecificationResolution(key, spec.value(), "", SpecificationResolution.Status.UNSUPPORTED,
                "Bundled facility references preserve authored geometry; this specification would mutate fixed geometry."));
        }
        Set<String> known = new HashSet<>(Set.of("REFERENCE", "ARCHETYPE", "CATEGORY", "SIZE", "PURPOSE_DETAIL", "STYLE", "ROOF", "FLOORS", "ENTRANCE"));
        for (BlueprintSpecification spec : request.specifications()) {
            if (!known.contains(spec.key())) ledger.add(new SpecificationResolution(spec.key(), spec.value(), "", SpecificationResolution.Status.UNSUPPORTED,
                "Compact facility corpus planner does not interpret this key."));
        }
        return List.copyOf(ledger);
    }

    private static void applySelector(List<SpecificationResolution> ledger, BlueprintSpecification spec, String key, String resolved) {
        if (spec != null) ledger.add(new SpecificationResolution(key, spec.value(), resolved, SpecificationResolution.Status.APPLIED,
            "Matched bundled facility corpus reference."));
    }

    private static List<BlueprintWarning> warnings(List<SpecificationResolution> ledger, Map<String, BlueprintSpecification> specs) {
        ArrayList<BlueprintWarning> warnings = new ArrayList<>();
        for (SpecificationResolution resolution : ledger) {
            if (resolution.status() != SpecificationResolution.Status.UNSUPPORTED && resolution.status() != SpecificationResolution.Status.CONFLICT) continue;
            BlueprintSpecification requested = specs.get(resolution.key());
            BlueprintWarning.Severity severity = requested != null && requested.requirement() == BlueprintSpecification.Requirement.REQUIRED
                ? BlueprintWarning.Severity.ERROR : BlueprintWarning.Severity.WARNING;
            warnings.add(new BlueprintWarning("SPECIFICATION_UNSUPPORTED", severity,
                resolution.key() + ": " + resolution.detail()));
        }
        return warnings;
    }

    private Index index() {
        Index current = index;
        if (current != null) return current;
        synchronized (this) {
            if (index != null) return index;
            JsonObject manifest = json("manifest.json");
            List<Entry> references = new ArrayList<>();
            Map<String, Entry> byId = new HashMap<>();
            for (JsonElement element : manifest.getAsJsonArray("entries")) {
                JsonObject object = element.getAsJsonObject();
                Entry entry = new Entry(text(object, "id"), text(object, "kind"), text(object, "category"), text(object, "path"),
                    object.has("status") ? object.get("status").getAsString() : "");
                byId.put(entry.id(), entry);
                if ("facility_reference".equals(entry.kind())) references.add(entry);
            }
            references.sort(Comparator.comparing(Entry::id));
            return index = new Index(manifest.get("library_version").getAsString(), List.copyOf(references), Map.copyOf(byId));
        }
    }

    private static MaterialManifest manifest(UUID id, List<PaletteEntry> palette, List<CompactBlueprintPrimitive> primitives,
                                             List<MaterialAvailability> availableRows) {
        Map<String, String> materialByKey = new HashMap<>();
        for (PaletteEntry entry : palette) materialByKey.put(entry.key(), entry.materialId());
        Map<String, Long> required = new HashMap<>();
        CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            if (kind != PlacementOperation.Kind.CLEAR) {
                String material = materialByKey.get(paletteKey);
                if (material == null) throw new IllegalStateException("Unknown compact corpus palette key " + paletteKey);
                required.merge(material, 1L, Long::sum);
            }
            return true;
        }, CompactBlueprintProvider.MAX_RAW_PLACEMENTS);
        Map<String, Long> available = new HashMap<>();
        for (MaterialAvailability row : availableRows) available.merge(row.materialId(), row.availableCount(), Long::sum);
        Map<String, Long> missing = new HashMap<>();
        for (Map.Entry<String, Long> entry : required.entrySet()) {
            long have = available.getOrDefault(entry.getKey(), 0L);
            if (have < entry.getValue()) missing.put(entry.getKey(), entry.getValue() - have);
        }
        return new MaterialManifest(id, required, available, missing);
    }

    private static List<MaterialIssue> issues(MaterialManifest manifest) {
        ArrayList<MaterialIssue> out = new ArrayList<>();
        for (Map.Entry<String, Long> missing : manifest.missing().entrySet()) {
            out.add(new MaterialIssue(missing.getKey(), MaterialIssue.Kind.MISSING,
                manifest.required().getOrDefault(missing.getKey(), 0L), manifest.available().getOrDefault(missing.getKey(), 0L),
                "Material is not currently available in sufficient quantity."));
        }
        return List.copyOf(out);
    }

    private static OperationCounts operationCounts(List<CompactBlueprintPrimitive> primitives) {
        final long[] placements = {0L};
        final long[] clears = {0L};
        long total = CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            if (kind == PlacementOperation.Kind.CLEAR) clears[0]++;
            else placements[0]++;
            return true;
        }, CompactBlueprintProvider.MAX_RAW_PLACEMENTS);
        return new OperationCounts(placements[0], clears[0], total);
    }

    private static int tokenScore(String wanted, String hay) {
        if (hay.contains(wanted)) return 800;
        int score = 0;
        for (String token : wanted.split("_")) {
            if (token.length() > 2 && hay.contains(token)) score += 80;
        }
        return score;
    }

    private static String canonical(Candidate c, BlueprintRequest request, BlockPosition anchor,
                                    List<PaletteEntry> palette, List<CompactBlueprintPrimitive> primitives) {
        StringBuilder out = new StringBuilder(1024);
        out.append(c.refId()).append('|').append(c.archetypeId()).append('|').append(c.corporateId()).append('|')
            .append(request.dimensionId()).append('|').append(request.constructionVolume().volumeId()).append('|')
            .append(request.constructionVolume().snapshotEpoch()).append('|').append(request.constructionVolume().bounds()).append('|')
            .append(anchor).append('|').append(request.preferredFacing());
        for (PaletteEntry p : palette) out.append("|P:").append(p.key()).append('=').append(p.blockState()).append(':').append(p.materialId());
        for (CompactBlueprintPrimitive p : primitives) out.append("|G:").append(p.sequence()).append(':').append(p.kind()).append(':')
            .append(p.operationKind()).append(':').append(p.from()).append(':').append(p.to()).append(':').append(p.radius()).append(':')
            .append(p.flags()).append(':').append(p.paletteKey());
        return out.toString();
    }

    private static JsonObject json(String path) {
        try (InputStream in = CompactFacilityCorpusPlanner.class.getClassLoader().getResourceAsStream(ROOT + path)) {
            if (in == null) throw new IllegalStateException("Missing bundled corpus resource " + ROOT + path);
            return JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (IOException error) {
            throw new IllegalStateException("Failed reading bundled corpus resource " + path, error);
        }
    }

    private static BlockPosition position(JsonArray array) {
        return new BlockPosition(array.get(0).getAsInt(), array.get(1).getAsInt(), array.get(2).getAsInt());
    }

    private static BlockPosition rotate(BlockPosition p, int width, int depth, Facing facing) {
        return switch (facing) {
            case SOUTH -> new BlockPosition(width - 1 - p.x(), p.y(), depth - 1 - p.z());
            case EAST -> new BlockPosition(depth - 1 - p.z(), p.y(), p.x());
            case WEST -> new BlockPosition(p.z(), p.y(), width - 1 - p.x());
            default -> p;
        };
    }

    private static Dims rotateDims(int width, int height, int depth, Facing facing) {
        return switch (facing) {
            case EAST, WEST -> new Dims(depth, height, width);
            default -> new Dims(width, height, depth);
        };
    }

    private static BlockPosition anchor(BlockPosition preferred, Bounds bounds, Dims dims) {
        return new BlockPosition(
            clamp(preferred.x() - dims.width() / 2, bounds.min().x(), bounds.max().x() - dims.width() + 1),
            clamp(preferred.y(), bounds.min().y(), bounds.max().y() - dims.height() + 1),
            clamp(preferred.z() - dims.depth() / 2, bounds.min().z(), bounds.max().z() - dims.depth() + 1)
        );
    }

    private static int clamp(int value, int min, int max) { return max < min ? min : Math.max(min, Math.min(max, value)); }
    private static BlockPosition min(BlockPosition a, BlockPosition b) { return new BlockPosition(Math.min(a.x(), b.x()), Math.min(a.y(), b.y()), Math.min(a.z(), b.z())); }
    private static BlockPosition max(BlockPosition a, BlockPosition b) { return new BlockPosition(Math.max(a.x(), b.x()), Math.max(a.y(), b.y()), Math.max(a.z(), b.z())); }

    private static String sizeClass(Dims dims, Bounds volume) {
        double ratio = Math.max((double)dims.width() / volume.width(),
            Math.max((double)dims.height() / volume.height(), (double)dims.depth() / volume.depth()));
        return ratio <= .30 ? "TINY" : ratio <= .50 ? "COMPACT" : ratio <= .70 ? "STANDARD" : ratio <= .90 ? "LARGE" : "FILL";
    }

    private static Map<String, BlueprintSpecification> first(List<BlueprintSpecification> specifications) {
        LinkedHashMap<String, BlueprintSpecification> result = new LinkedHashMap<>();
        for (BlueprintSpecification specification : specifications) result.putIfAbsent(specification.key(), specification);
        return result;
    }

    private static boolean idMatches(String requested, String actual) {
        String req = slug(requested), act = slug(actual);
        return req.equals(act) || normalize(requested).equals(normalize(actual));
    }

    private static String slug(String value) {
        String trimmed = value.trim();
        int slash = trimmed.lastIndexOf('/');
        if (slash >= 0) trimmed = trimmed.substring(slash + 1);
        int colon = trimmed.lastIndexOf(':');
        if (colon >= 0) trimmed = trimmed.substring(colon + 1);
        return normalize(trimmed);
    }

    private static String normalize(String value) { return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_'); }
    private static String text(JsonObject object, String key) { return object.get(key).getAsString(); }

    private static String sha256(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("SHA-256 unavailable", impossible);
        }
    }

    private record Entry(String id, String kind, String category, String path, String status) {}
    private record Index(String version, List<Entry> references, Map<String, Entry> byId) {}
    private record Scored(Entry entry, int score) {}
    private record Dims(int width, int height, int depth) {}
    private record Candidate(Entry entry, JsonObject ref, String refId, String archetypeId, String corporateId,
                             Dims dims, String sizeClass, int score, int sourceWidth, int sourceDepth) {}
    private record SourcePrimitive(JsonObject json, String block) {}
    private record OperationCounts(long placements, long clears, long total) {}
}
