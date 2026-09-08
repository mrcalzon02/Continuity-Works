package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.*;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.*;

/**
 * Low-overhead primitive planner. Geometry stays compressed until a caller streams it.
 * This provider intentionally owns no inference model, world object, or persistent block cache.
 */
public final class CompactBlueprintProvider implements ContinuityWorksCompactBlueprintApi {
    static final int MAX_ACTIVE_REQUESTS = 3;
    static final int MAX_PRIMITIVES = 128;
    static final long MAX_RAW_PLACEMENTS = 131_072L;
    static final int MAX_RETAINED_MANIFESTS = 16;
    private static final int MAX_WIDTH = 48;
    private static final int MAX_HEIGHT = 24;
    private static final int MAX_DEPTH = 48;
    private static final String VERSION = "compact-generic/v1";

    private final ThreadPoolExecutor executor = new ThreadPoolExecutor(
        1, 1, 0L, TimeUnit.MILLISECONDS,
        new ArrayBlockingQueue<>(MAX_ACTIVE_REQUESTS - 1),
        runnable -> {
            Thread thread = new Thread(runnable, "continuityworks-compact-blueprint");
            thread.setDaemon(true);
            thread.setPriority(Thread.NORM_PRIORITY - 1);
            return thread;
        },
        new ThreadPoolExecutor.AbortPolicy()
    );
    private final Semaphore requestPermits = new Semaphore(MAX_ACTIVE_REQUESTS, true);
    private final ConcurrentMap<UUID, CompletableFuture<CompactBlueprintPlan>> activeRequests = new ConcurrentHashMap<>();
    private final ConcurrentMap<UUID, UUID> activeByCompanion = new ConcurrentHashMap<>();
    private final Map<UUID, MaterialManifest> manifests = Collections.synchronizedMap(
        new LinkedHashMap<>(MAX_RETAINED_MANIFESTS + 1, 0.75f, true) {
            @Override protected boolean removeEldestEntry(Map.Entry<UUID, MaterialManifest> eldest) {
                return size() > MAX_RETAINED_MANIFESTS;
            }
        }
    );

    @Override
    public BlueprintApiVersion apiVersion() { return BlueprintApiVersion.CURRENT; }

    @Override
    public BlueprintVocabulary vocabulary() {
        return new BlueprintVocabulary("compact/1", List.of(
            new SpecificationDescriptor("STYLE", Set.of("SIMPLE_HALL", "RECTILINEAR_WORKSHOP", "HOLLOW_COURT"), false, "SIMPLE_HALL", "Compact structural massing grammar."),
            new SpecificationDescriptor("SIZE", Set.of("TINY", "COMPACT", "STANDARD", "LARGE", "FILL"), false, "COMPACT", "Fraction of the selected build volume, bounded by the compact kernel caps."),
            new SpecificationDescriptor("FLOORS", Set.of("1", "2", "3"), false, "1", "Usable floor count."),
            new SpecificationDescriptor("ROOF", Set.of("FLAT", "OPEN"), false, "FLAT", "Roof treatment."),
            new SpecificationDescriptor("ENTRANCE", Set.of("NORTH", "SOUTH", "EAST", "WEST"), false, "", "Primary opening direction."),
            new SpecificationDescriptor("PURPOSE_DETAIL", Set.of(), true, "", "Open semantic refinement; never interpreted as raw placement instructions.")
        ));
    }

    @Override
    public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        validateRequestBudget(request);
        if (!requestPermits.tryAcquire()) {
            return CompletableFuture.failedFuture(new RejectedExecutionException("Continuity Works compact planner is saturated"));
        }
        UUID prior = activeByCompanion.putIfAbsent(request.companionUuid(), request.requestId());
        if (prior != null) {
            requestPermits.release();
            return CompletableFuture.failedFuture(new IllegalStateException("Companion already has active compact blueprint request " + prior));
        }

        final CompletableFuture<CompactBlueprintPlan> future;
        try {
            future = CompletableFuture.supplyAsync(() -> plan(request), executor);
        } catch (RejectedExecutionException error) {
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            requestPermits.release();
            return CompletableFuture.failedFuture(error);
        }
        activeRequests.put(request.requestId(), future);
        future.whenComplete((plan, error) -> {
            activeRequests.remove(request.requestId(), future);
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            if (plan != null) manifests.put(plan.blueprintId(), plan.materials());
            requestPermits.release();
        });
        return future;
    }

    @Override
    public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) {
        Objects.requireNonNull(plan, "plan");
        Objects.requireNonNull(context, "context");
        List<BlueprintWarning> warnings = new ArrayList<>();
        for (BlueprintWarning warning : plan.warnings()) if (warning.severity() == BlueprintWarning.Severity.ERROR) warnings.add(warning);

        if (!plan.dimensionId().equals(context.dimensionId())
            || !plan.constructionVolume().volumeId().equals(context.constructionVolume().volumeId())
            || plan.constructionVolume().snapshotEpoch() != context.constructionVolume().snapshotEpoch()
            || !plan.constructionVolume().bounds().equals(context.constructionVolume().bounds())) {
            warnings.add(new BlueprintWarning("STALE_CONSTRUCTION_VOLUME", BlueprintWarning.Severity.ERROR,
                "Validation context does not match the compact plan construction-volume snapshot."));
            return new ValidationResult(plan.blueprintId(), context.validationId(), ValidationResult.Status.STALE_CONTEXT, List.of(), List.of(), warnings);
        }
        if (!plan.allPrimitiveBoundsInsideConstructionVolume()) {
            warnings.add(new BlueprintWarning("PRIMITIVE_OUTSIDE_VOLUME", BlueprintWarning.Severity.ERROR,
                "At least one compact primitive leaves the selected construction volume."));
        }

        Map<BlockPosition, ObservedBlock> observed = new HashMap<>();
        for (ObservedBlock block : context.observedBlocks()) observed.put(block.position(), block);
        Set<ChunkPosition> requiredChunks = new HashSet<>();
        List<ProtectedBlockConflict> conflicts = new ArrayList<>();
        Set<String> conflictKeys = new HashSet<>();
        CompactBlueprintMaterializer.forEachPlacement(plan, (sequence, kind, relative, paletteKey) -> {
            BlockPosition world = plan.anchor().offset(relative);
            if (!plan.constructionVolume().contains(world)) {
                warnings.add(new BlueprintWarning("STREAM_OUTSIDE_VOLUME", BlueprintWarning.Severity.ERROR,
                    "Streamed compact operation leaves the selected construction volume."));
                return false;
            }
            requiredChunks.add(new ChunkPosition(Math.floorDiv(world.x(), 16), Math.floorDiv(world.z(), 16)));
            ObservedBlock existing = observed.get(world);
            if (existing != null && existing.protectedBlock()) {
                String key = relative + ":protected";
                if (conflictKeys.add(key)) conflicts.add(new ProtectedBlockConflict(relative, existing.blockState(), "protected_block"));
            }
            for (ClaimConstraint claim : context.claimConstraints()) {
                if (claim.access() == ClaimConstraint.Access.BUILD_DENIED && claim.bounds().contains(world)) {
                    String key = relative + ":claim:" + claim.source();
                    if (conflictKeys.add(key)) conflicts.add(new ProtectedBlockConflict(relative, "claim:" + claim.source(), "claim_denied"));
                }
            }
            return true;
        });
        for (ChunkPosition chunk : requiredChunks) {
            if (!context.loadedChunks().contains(chunk)) warnings.add(new BlueprintWarning("CHUNK_NOT_LOADED", BlueprintWarning.Severity.ERROR,
                "Required chunk is not loaded: " + chunk.x() + "," + chunk.z()));
        }

        List<MaterialIssue> materialIssues = new ArrayList<>();
        for (Map.Entry<String, Long> required : plan.materials().required().entrySet()) {
            long available = context.inventoryCounts().getOrDefault(required.getKey(), 0L);
            if (available < required.getValue()) materialIssues.add(new MaterialIssue(required.getKey(), MaterialIssue.Kind.MISSING,
                required.getValue(), available, "Insufficient material in validation inventory snapshot."));
        }
        boolean invalid = !conflicts.isEmpty() || !materialIssues.isEmpty()
            || warnings.stream().anyMatch(w -> w.severity() == BlueprintWarning.Severity.ERROR);
        return new ValidationResult(plan.blueprintId(), context.validationId(), invalid ? ValidationResult.Status.INVALID : ValidationResult.Status.VALID,
            conflicts, materialIssues, warnings);
    }

    @Override
    public MaterialManifest getCompactMaterials(UUID blueprintId) {
        MaterialManifest manifest = manifests.get(Objects.requireNonNull(blueprintId, "blueprintId"));
        if (manifest == null) throw new NoSuchElementException("Unknown compact blueprint: " + blueprintId);
        return manifest;
    }

    @Override
    public void cancelCompact(UUID requestId) {
        CompletableFuture<CompactBlueprintPlan> future = activeRequests.get(Objects.requireNonNull(requestId, "requestId"));
        if (future != null) future.cancel(true);
    }

    private CompactBlueprintPlan plan(BlueprintRequest request) {
        Resolution r = resolve(request);
        Dims dims = chooseSize(request.constructionVolume().bounds(), r.size());
        if (r.style().equals("HOLLOW_COURT") && (dims.width() < 11 || dims.depth() < 11)) {
            throw new IllegalArgumentException("HOLLOW_COURT requires at least 11x11 resolved dimensions");
        }
        int maximumFloors = Math.max(1, (dims.height() - 1) / 3);
        if (r.floors() > maximumFloors) throw new IllegalArgumentException("Resolved height supports at most " + maximumFloors + " floor(s)");
        BlockPosition anchor = chooseAnchor(request.preferredOrigin(), request.constructionVolume().bounds(), dims);
        List<PaletteEntry> palette = paletteFor(request.buildPurpose());
        List<CompactBlueprintPrimitive> primitives = buildPrimitives(dims, r);
        if (primitives.size() > MAX_PRIMITIVES) throw new IllegalArgumentException("Compact plan exceeds primitive budget " + MAX_PRIMITIVES);
        long rawCount = rawCount(primitives);
        if (rawCount > MAX_RAW_PLACEMENTS) throw new IllegalArgumentException("Compact plan exceeds raw placement budget " + MAX_RAW_PLACEMENTS);
        Bounds localBounds = new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(dims.width() - 1, dims.height() - 1, dims.depth() - 1));
        String hash = sha256(canonical(request, r, anchor, palette, primitives));
        UUID blueprintId = UUID.nameUUIDFromBytes((VERSION + ":" + hash).getBytes(StandardCharsets.UTF_8));
        MaterialManifest manifest = materialManifest(blueprintId, palette, primitives, request.availableMaterials());
        List<MaterialIssue> materialIssues = materialIssues(manifest);
        List<BlueprintWarning> warnings = new ArrayList<>(r.warnings());
        if (!materialIssues.isEmpty()) warnings.add(new BlueprintWarning("MATERIALS_INCOMPLETE", BlueprintWarning.Severity.WARNING,
            "Current material snapshot cannot satisfy all raw ordered placement requirements."));
        long clears = countKind(primitives, PlacementOperation.Kind.CLEAR);
        long placements = Math.max(0L, rawCount - clears);
        double confidence = Math.max(0.0, 1.0 - 0.12 * r.unsupported() - 0.25 * r.conflicts());
        CompactBlueprintPlan plan = new CompactBlueprintPlan(
            blueprintId, VERSION, "SHA-256", hash, request.dimensionId(), request.constructionVolume(), localBounds, anchor,
            request.preferredFacing(), r.ledger(), palette, manifest, primitives, materialIssues,
            new WorkloadEstimate(placements, clears, 0, rawCount),
            new PreviewMetadata(request.buildPurpose(), "Compact deterministic primitive proposal", r.style(), Map.of(
                "size", r.size(), "floors", Integer.toString(r.floors()), "roof", r.roof(),
                "primitive_count", Integer.toString(primitives.size()), "placement_semantics", "ordered_stream"
            )),
            confidence, warnings
        );
        if (!plan.allPrimitiveBoundsInsideConstructionVolume()) throw new IllegalStateException("Compact planner emitted primitive outside selected volume");
        return plan;
    }

    private static List<CompactBlueprintPrimitive> buildPrimitives(Dims d, Resolution r) {
        ArrayList<CompactBlueprintPrimitive> out = new ArrayList<>();
        int seq = 0;
        out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(0, 0, 0), new BlockPosition(d.width() - 1, 0, d.depth() - 1), "floor"));
        out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(0, 1, 0), new BlockPosition(d.width() - 1, d.height() - 1, 0), "wall"));
        out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(0, 1, d.depth() - 1), new BlockPosition(d.width() - 1, d.height() - 1, d.depth() - 1), "wall"));
        if (d.depth() > 2) {
            out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(0, 1, 1), new BlockPosition(0, d.height() - 1, d.depth() - 2), "wall"));
            out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(d.width() - 1, 1, 1), new BlockPosition(d.width() - 1, d.height() - 1, d.depth() - 2), "wall"));
        }
        if ("FLAT".equals(r.roof()) && d.width() > 2 && d.depth() > 2) {
            out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(1, d.height() - 1, 1), new BlockPosition(d.width() - 2, d.height() - 1, d.depth() - 2), "roof"));
        }
        for (int floor = 1; floor < r.floors(); floor++) {
            int y = floor * 3;
            if (y < d.height() - 1 && d.width() > 2 && d.depth() > 2) {
                out.add(CompactBlueprintPrimitive.fillBox(seq++, new BlockPosition(1, y, 1), new BlockPosition(d.width() - 2, y, d.depth() - 2), "floor"));
            }
        }
        if ("RECTILINEAR_WORKSHOP".equals(r.style()) && d.width() >= 9 && d.depth() >= 9) {
            out.add(CompactBlueprintPrimitive.line(seq++, new BlockPosition(d.width() / 2, 1, 2), new BlockPosition(d.width() / 2, d.height() - 2, 2), "trim"));
            out.add(CompactBlueprintPrimitive.line(seq++, new BlockPosition(d.width() / 2, 1, d.depth() - 3), new BlockPosition(d.width() / 2, d.height() - 2, d.depth() - 3), "trim"));
        }
        if ("HOLLOW_COURT".equals(r.style())) {
            int x0 = d.width() / 3, x1 = d.width() - 1 - x0;
            int z0 = d.depth() / 3, z1 = d.depth() - 1 - z0;
            out.add(new CompactBlueprintPrimitive(seq++, CompactBlueprintPrimitive.Kind.FILL_BOX, PlacementOperation.Kind.CLEAR,
                new BlockPosition(x0, 1, z0), new BlockPosition(x1, d.height() - 1, z1), 0, 0, null));
        }
        BlockPosition[] doorway = doorway(d, r.entrance());
        out.add(new CompactBlueprintPrimitive(seq, CompactBlueprintPrimitive.Kind.FILL_BOX, PlacementOperation.Kind.CLEAR,
            doorway[0], doorway[1], 0, 0, null));
        return List.copyOf(out);
    }

    private static BlockPosition[] doorway(Dims d, String entrance) {
        int cx = d.width() / 2, cz = d.depth() / 2, top = Math.min(3, d.height() - 1);
        return switch (entrance) {
            case "SOUTH" -> new BlockPosition[]{new BlockPosition(Math.max(0, cx - 1), 1, d.depth() - 1), new BlockPosition(Math.min(d.width() - 1, cx + 1), top, d.depth() - 1)};
            case "EAST" -> new BlockPosition[]{new BlockPosition(d.width() - 1, 1, Math.max(0, cz - 1)), new BlockPosition(d.width() - 1, top, Math.min(d.depth() - 1, cz + 1))};
            case "WEST" -> new BlockPosition[]{new BlockPosition(0, 1, Math.max(0, cz - 1)), new BlockPosition(0, top, Math.min(d.depth() - 1, cz + 1))};
            default -> new BlockPosition[]{new BlockPosition(Math.max(0, cx - 1), 1, 0), new BlockPosition(Math.min(d.width() - 1, cx + 1), top, 0)};
        };
    }

    private static List<PaletteEntry> paletteFor(String purpose) {
        boolean arcane = purpose.toUpperCase(Locale.ROOT).contains("RUNE") || purpose.toUpperCase(Locale.ROOT).contains("MAGIC");
        return List.of(
            new PaletteEntry("wall", arcane ? "minecraft:mossy_stone_bricks" : "minecraft:stone_bricks", arcane ? "minecraft:mossy_stone_bricks" : "minecraft:stone_bricks", Map.of("role", "wall")),
            new PaletteEntry("floor", "minecraft:oak_planks", "minecraft:oak_planks", Map.of("role", "floor")),
            new PaletteEntry("roof", "minecraft:stone_bricks", "minecraft:stone_bricks", Map.of("role", "roof")),
            new PaletteEntry("trim", "minecraft:stripped_oak_log", "minecraft:stripped_oak_log", Map.of("role", "trim"))
        );
    }

    private static MaterialManifest materialManifest(UUID id, List<PaletteEntry> palette, List<CompactBlueprintPrimitive> primitives,
                                                     List<MaterialAvailability> availableRows) {
        Map<String, String> materialByKey = new HashMap<>();
        for (PaletteEntry entry : palette) materialByKey.put(entry.key(), entry.materialId());
        Map<String, Long> required = new HashMap<>();
        CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            if (kind != PlacementOperation.Kind.CLEAR) {
                String material = materialByKey.get(paletteKey);
                if (material == null) throw new IllegalStateException("Unknown compact palette key " + paletteKey);
                required.merge(material, 1L, Long::sum);
            }
            return true;
        });
        Map<String, Long> available = new HashMap<>();
        for (MaterialAvailability row : availableRows) available.merge(row.materialId(), row.availableCount(), Long::sum);
        Map<String, Long> missing = new HashMap<>();
        for (Map.Entry<String, Long> entry : required.entrySet()) {
            long have = available.getOrDefault(entry.getKey(), 0L);
            if (have < entry.getValue()) missing.put(entry.getKey(), entry.getValue() - have);
        }
        return new MaterialManifest(id, required, available, missing);
    }

    private static List<MaterialIssue> materialIssues(MaterialManifest manifest) {
        ArrayList<MaterialIssue> issues = new ArrayList<>();
        for (Map.Entry<String, Long> missing : manifest.missing().entrySet()) {
            issues.add(new MaterialIssue(missing.getKey(), MaterialIssue.Kind.MISSING,
                manifest.required().getOrDefault(missing.getKey(), 0L), manifest.available().getOrDefault(missing.getKey(), 0L),
                "Material is not currently available in sufficient quantity."));
        }
        return List.copyOf(issues);
    }

    private static Resolution resolve(BlueprintRequest request) {
        Map<String, BlueprintSpecification> seen = new LinkedHashMap<>();
        List<SpecificationResolution> ledger = new ArrayList<>();
        List<BlueprintWarning> warnings = new ArrayList<>();
        int conflicts = 0, unsupported = 0;
        for (BlueprintSpecification spec : request.specifications()) {
            BlueprintSpecification prior = seen.putIfAbsent(spec.key(), spec);
            if (prior != null && !prior.value().equalsIgnoreCase(spec.value())) {
                conflicts++;
                ledger.add(new SpecificationResolution(spec.key(), spec.value(), "", SpecificationResolution.Status.CONFLICT,
                    "Conflicts with earlier value " + prior.value()));
                warnings.add(new BlueprintWarning("SPECIFICATION_CONFLICT", BlueprintWarning.Severity.ERROR,
                    spec.key() + " has conflicting requested values."));
            }
        }
        String style = value("STYLE", seen.get("STYLE"), Set.of("SIMPLE_HALL", "RECTILINEAR_WORKSHOP", "HOLLOW_COURT"),
            inferStyle(request.buildPurpose()), ledger, warnings);
        String size = value("SIZE", seen.get("SIZE"), Set.of("TINY", "COMPACT", "STANDARD", "LARGE", "FILL"),
            "COMPACT", ledger, warnings);
        String roof = value("ROOF", seen.get("ROOF"), Set.of("FLAT", "OPEN"), "HOLLOW_COURT".equals(style) ? "OPEN" : "FLAT", ledger, warnings);
        String entrance = value("ENTRANCE", seen.get("ENTRANCE"), Set.of("NORTH", "SOUTH", "EAST", "WEST"), request.preferredFacing().name(), ledger, warnings);
        int floors = 1;
        BlueprintSpecification fs = seen.get("FLOORS");
        if (fs == null) ledger.add(new SpecificationResolution("FLOORS", "", "1", SpecificationResolution.Status.DEFAULTED, "Deterministic default."));
        else try {
            floors = Integer.parseInt(fs.value());
            if (floors < 1 || floors > 3) throw new NumberFormatException();
            ledger.add(new SpecificationResolution("FLOORS", fs.value(), Integer.toString(floors), SpecificationResolution.Status.APPLIED, ""));
        } catch (NumberFormatException error) {
            unsupported++;
            floors = 1;
            ledger.add(new SpecificationResolution("FLOORS", fs.value(), "1", SpecificationResolution.Status.UNSUPPORTED, "Allowed values are 1, 2, 3."));
            warnings.add(specWarning(fs, "Unsupported FLOORS value; defaulted to 1."));
        }
        BlueprintSpecification detail = seen.get("PURPOSE_DETAIL");
        if (detail != null) ledger.add(new SpecificationResolution("PURPOSE_DETAIL", detail.value(), detail.value(), SpecificationResolution.Status.APPLIED, "Preserved as semantic metadata."));
        Set<String> known = Set.of("STYLE", "SIZE", "ROOF", "ENTRANCE", "FLOORS", "PURPOSE_DETAIL");
        for (BlueprintSpecification spec : request.specifications()) if (!known.contains(spec.key())) {
            unsupported++;
            ledger.add(new SpecificationResolution(spec.key(), spec.value(), "", SpecificationResolution.Status.UNSUPPORTED, "Compact generic planner does not interpret this key."));
            warnings.add(specWarning(spec, "Unsupported compact blueprint specification: " + spec.key()));
        }
        return new Resolution(style, size, roof, entrance, floors, List.copyOf(ledger), List.copyOf(warnings), unsupported, conflicts);
    }

    private static String value(String key, BlueprintSpecification spec, Set<String> allowed, String fallback,
                                List<SpecificationResolution> ledger, List<BlueprintWarning> warnings) {
        if (spec == null) {
            ledger.add(new SpecificationResolution(key, "", fallback, SpecificationResolution.Status.DEFAULTED, "Deterministic default."));
            return fallback;
        }
        String normalized = normalize(spec.value());
        if (allowed.contains(normalized)) {
            ledger.add(new SpecificationResolution(key, spec.value(), normalized, SpecificationResolution.Status.APPLIED, ""));
            return normalized;
        }
        ledger.add(new SpecificationResolution(key, spec.value(), fallback, SpecificationResolution.Status.UNSUPPORTED, "Unsupported value."));
        warnings.add(specWarning(spec, "Unsupported " + key + " value; defaulted to " + fallback + "."));
        return fallback;
    }

    private static BlueprintWarning specWarning(BlueprintSpecification spec, String message) {
        return new BlueprintWarning("SPECIFICATION_UNSUPPORTED",
            spec.requirement() == BlueprintSpecification.Requirement.REQUIRED ? BlueprintWarning.Severity.ERROR : BlueprintWarning.Severity.WARNING,
            message);
    }

    private static String inferStyle(String purpose) {
        String value = purpose.toUpperCase(Locale.ROOT);
        if (value.contains("COURT") || value.contains("RUNE")) return "HOLLOW_COURT";
        if (value.contains("WORKSHOP") || value.contains("FACTORY") || value.contains("FORGE")) return "RECTILINEAR_WORKSHOP";
        return "SIMPLE_HALL";
    }

    private static Dims chooseSize(Bounds volume, String size) {
        double factor = switch (size) {
            case "TINY" -> 0.25; case "STANDARD" -> 0.65; case "LARGE" -> 0.82; case "FILL" -> 1.0; default -> 0.45;
        };
        return new Dims(axis(volume.width(), factor, 7, MAX_WIDTH), axis(volume.height(), factor, 5, MAX_HEIGHT), axis(volume.depth(), factor, 7, MAX_DEPTH));
    }

    private static int axis(int available, double factor, int preferredMin, int cap) {
        int scaled = Math.max(1, (int)Math.floor(available * factor));
        int minimum = Math.min(available, preferredMin);
        return Math.min(available, Math.min(cap, Math.max(minimum, scaled)));
    }

    private static BlockPosition chooseAnchor(BlockPosition preferred, Bounds volume, Dims d) {
        return new BlockPosition(
            clamp(preferred.x() - d.width() / 2, volume.min().x(), volume.max().x() - d.width() + 1),
            clamp(preferred.y(), volume.min().y(), volume.max().y() - d.height() + 1),
            clamp(preferred.z() - d.depth() / 2, volume.min().z(), volume.max().z() - d.depth() + 1)
        );
    }

    private static int clamp(int value, int min, int max) { return max < min ? min : Math.max(min, Math.min(max, value)); }
    private static String normalize(String value) { return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_'); }

    private static long rawCount(List<CompactBlueprintPrimitive> primitives) {
        final long[] count = {0L};
        CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            count[0]++;
            if (count[0] > MAX_RAW_PLACEMENTS) return false;
            return true;
        });
        return count[0];
    }

    private static long countKind(List<CompactBlueprintPrimitive> primitives, PlacementOperation.Kind wanted) {
        final long[] count = {0L};
        CompactBlueprintMaterializer.forEachPlacement(primitives, (sequence, kind, relative, paletteKey) -> {
            if (kind == wanted) count[0]++;
            return true;
        });
        return count[0];
    }

    private static String canonical(BlueprintRequest request, Resolution r, BlockPosition anchor,
                                    List<PaletteEntry> palette, List<CompactBlueprintPrimitive> primitives) {
        StringBuilder out = new StringBuilder(1024);
        out.append(VERSION).append('|').append(request.dimensionId()).append('|').append(request.buildPurpose()).append('|')
            .append(request.constructionVolume().volumeId()).append('|').append(request.constructionVolume().snapshotEpoch()).append('|')
            .append(request.constructionVolume().bounds()).append('|').append(anchor).append('|').append(request.preferredFacing()).append('|')
            .append(r.style()).append('|').append(r.size()).append('|').append(r.roof()).append('|').append(r.entrance()).append('|').append(r.floors());
        for (PaletteEntry p : palette) out.append("|P:").append(p.key()).append('=').append(p.blockState()).append(':').append(p.materialId());
        for (CompactBlueprintPrimitive p : primitives) out.append("|G:").append(p.sequence()).append(':').append(p.kind()).append(':').append(p.operationKind())
            .append(':').append(p.from()).append(':').append(p.to()).append(':').append(p.radius()).append(':').append(p.flags()).append(':').append(p.paletteKey());
        return out.toString();
    }

    private static String sha256(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("SHA-256 unavailable", impossible);
        }
    }

    private static void validateRequestBudget(BlueprintRequest request) {
        if (request.specifications().size() > 32) throw new IllegalArgumentException("Too many compact blueprint specifications");
        if (request.availableMaterials().size() > 512) throw new IllegalArgumentException("Too many material availability rows");
        if (request.candidateSites().size() > 32) throw new IllegalArgumentException("Too many candidate sites");
        if (request.permittedStyles().size() > 32) throw new IllegalArgumentException("Too many permitted styles");
    }

    private record Dims(int width, int height, int depth) {}
    private record Resolution(String style, String size, String roof, String entrance, int floors,
                              List<SpecificationResolution> ledger, List<BlueprintWarning> warnings, int unsupported, int conflicts) {}
}
