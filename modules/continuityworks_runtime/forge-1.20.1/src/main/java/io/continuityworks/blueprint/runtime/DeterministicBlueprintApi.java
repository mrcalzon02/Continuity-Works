package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.*;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class DeterministicBlueprintApi implements ContinuityWorksBlueprintApi {
    private static final String BLUEPRINT_VERSION = "bounded-generic/v1";
    private static final int MAX_WIDTH = 48;
    private static final int MAX_HEIGHT = 24;
    private static final int MAX_DEPTH = 48;

    private final ExecutorService executor = Executors.newSingleThreadExecutor(r -> {
        Thread thread = new Thread(r, "continuityworks-blueprint");
        thread.setDaemon(true);
        return thread;
    });
    private final ConcurrentMap<UUID, CompletableFuture<BlueprintProposal>> activeRequests = new ConcurrentHashMap<>();
    private final ConcurrentMap<UUID, UUID> activeByCompanion = new ConcurrentHashMap<>();
    private final ConcurrentMap<UUID, MaterialManifest> manifests = new ConcurrentHashMap<>();

    @Override
    public BlueprintApiVersion apiVersion() { return BlueprintApiVersion.CURRENT; }

    @Override
    public BlueprintVocabulary vocabulary() {
        return new BlueprintVocabulary("1", List.of(
            new SpecificationDescriptor("STYLE", Set.of("SIMPLE_HALL", "RECTILINEAR_WORKSHOP", "HOLLOW_COURT"), false, "SIMPLE_HALL", "High-level massing grammar."),
            new SpecificationDescriptor("SIZE", Set.of("TINY", "COMPACT", "STANDARD", "LARGE", "FILL"), false, "COMPACT", "Fraction of the selected construction volume, subject to safety caps."),
            new SpecificationDescriptor("FLOORS", Set.of("1", "2", "3"), false, "1", "Number of usable floors."),
            new SpecificationDescriptor("ROOF", Set.of("FLAT", "OPEN"), false, "FLAT", "Roof treatment."),
            new SpecificationDescriptor("ENTRANCE", Set.of("NORTH", "SOUTH", "EAST", "WEST"), false, "", "Primary opening direction; when omitted it follows preferredFacing."),
            new SpecificationDescriptor("PURPOSE_DETAIL", Set.of(), true, "", "Open semantic refinement of buildPurpose; never interpreted as raw placement instructions.")
        ));
    }

    @Override
    public CompletableFuture<BlueprintProposal> generate(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        UUID prior = activeByCompanion.putIfAbsent(request.companionUuid(), request.requestId());
        if (prior != null) return CompletableFuture.failedFuture(new IllegalStateException("Companion already has active blueprint request " + prior));
        CompletableFuture<BlueprintProposal> future = CompletableFuture.supplyAsync(() -> plan(request), executor);
        activeRequests.put(request.requestId(), future);
        future.whenComplete((ignored, error) -> {
            activeRequests.remove(request.requestId(), future);
            activeByCompanion.remove(request.companionUuid(), request.requestId());
        });
        return future;
    }

    @Override
    public ValidationResult validate(BlueprintProposal proposal, BlueprintContext context) {
        Objects.requireNonNull(proposal, "proposal");
        Objects.requireNonNull(context, "context");
        List<ProtectedBlockConflict> conflicts = new ArrayList<>();
        List<MaterialIssue> materialIssues = new ArrayList<>();
        List<BlueprintWarning> warnings = new ArrayList<>();
        for (BlueprintWarning warning : proposal.warnings()) {
            if (warning.severity() == BlueprintWarning.Severity.ERROR) warnings.add(warning);
        }

        if (!proposal.dimensionId().equals(context.dimensionId())
            || !proposal.constructionVolume().volumeId().equals(context.constructionVolume().volumeId())
            || proposal.constructionVolume().snapshotEpoch() != context.constructionVolume().snapshotEpoch()
            || !proposal.constructionVolume().bounds().equals(context.constructionVolume().bounds())) {
            warnings.add(new BlueprintWarning("STALE_CONSTRUCTION_VOLUME", BlueprintWarning.Severity.ERROR,
                "Validation context does not match the proposal construction-volume snapshot."));
            return new ValidationResult(proposal.blueprintId(), context.validationId(), ValidationResult.Status.STALE_CONTEXT, List.of(), List.of(), warnings);
        }
        if (!proposal.allOperationsInsideConstructionVolume()) {
            warnings.add(new BlueprintWarning("OPERATION_OUTSIDE_VOLUME", BlueprintWarning.Severity.ERROR,
                "At least one proposed operation leaves the selected construction volume."));
        }

        Map<BlockPosition, ObservedBlock> observed = new HashMap<>();
        for (ObservedBlock block : context.observedBlocks()) observed.put(block.position(), block);
        Set<ChunkPosition> requiredChunks = new HashSet<>();
        for (PlacementOperation operation : proposal.operations()) {
            BlockPosition world = proposal.anchor().offset(operation.relativePosition());
            requiredChunks.add(new ChunkPosition(Math.floorDiv(world.x(), 16), Math.floorDiv(world.z(), 16)));
            ObservedBlock block = observed.get(world);
            if (block != null && block.protectedBlock()) {
                conflicts.add(new ProtectedBlockConflict(operation.relativePosition(), block.blockState(), "protected_block"));
            }
            for (ClaimConstraint claim : context.claimConstraints()) {
                if (claim.access() == ClaimConstraint.Access.BUILD_DENIED && claim.bounds().contains(world)) {
                    conflicts.add(new ProtectedBlockConflict(operation.relativePosition(), "claim:" + claim.source(), "claim_denied"));
                }
            }
        }
        for (ChunkPosition chunk : requiredChunks) {
            if (!context.loadedChunks().contains(chunk)) {
                warnings.add(new BlueprintWarning("CHUNK_NOT_LOADED", BlueprintWarning.Severity.ERROR,
                    "Required chunk is not loaded: " + chunk.x() + "," + chunk.z()));
            }
        }
        for (Map.Entry<String, Long> required : proposal.materials().required().entrySet()) {
            long available = context.inventoryCounts().getOrDefault(required.getKey(), 0L);
            if (available < required.getValue()) {
                materialIssues.add(new MaterialIssue(required.getKey(), MaterialIssue.Kind.MISSING, required.getValue(), available,
                    "Insufficient material in validation inventory snapshot."));
            }
        }
        boolean invalid = !conflicts.isEmpty() || !materialIssues.isEmpty()
            || warnings.stream().anyMatch(w -> w.severity() == BlueprintWarning.Severity.ERROR);
        return new ValidationResult(proposal.blueprintId(), context.validationId(),
            invalid ? ValidationResult.Status.INVALID : ValidationResult.Status.VALID, conflicts, materialIssues, warnings);
    }

    @Override
    public MaterialManifest getMaterials(UUID blueprintId) {
        MaterialManifest manifest = manifests.get(Objects.requireNonNull(blueprintId, "blueprintId"));
        if (manifest == null) throw new NoSuchElementException("Unknown blueprint: " + blueprintId);
        return manifest;
    }

    @Override
    public void cancel(UUID requestId) {
        CompletableFuture<BlueprintProposal> future = activeRequests.get(Objects.requireNonNull(requestId, "requestId"));
        if (future != null) future.cancel(true);
    }

    private BlueprintProposal plan(BlueprintRequest request) {
        Resolution resolution = interpret(request);
        Dimensions size = chooseSize(request.constructionVolume().bounds(), resolution.size());
        if (resolution.style().equals("HOLLOW_COURT") && (size.width() < 11 || size.depth() < 11)) {
            throw new IllegalArgumentException("HOLLOW_COURT requires at least 11x11 horizontal blueprint dimensions inside the selected construction volume");
        }
        int maximumFloors = Math.max(1, (size.height() - 1) / 3);
        if (resolution.floors() > maximumFloors) {
            throw new IllegalArgumentException("Selected construction volume height supports at most " + maximumFloors + " floor(s) at the resolved size");
        }
        BlockPosition anchor = chooseAnchor(request.preferredOrigin(), request.constructionVolume().bounds(), size);
        List<PaletteEntry> palette = paletteFor(request.buildPurpose());
        List<PlacementOperation> operations = buildOperations(size, resolution);
        String hash = sha256(canonicalPlan(request, resolution, anchor, size, palette, operations));
        UUID blueprintId = UUID.nameUUIDFromBytes((BLUEPRINT_VERSION + ":" + hash).getBytes(StandardCharsets.UTF_8));
        MaterialManifest manifest = materialManifest(blueprintId, palette, operations, request.availableMaterials());
        manifests.put(blueprintId, manifest);

        List<MaterialIssue> materialIssues = new ArrayList<>();
        for (Map.Entry<String, Long> missing : manifest.missing().entrySet()) {
            materialIssues.add(new MaterialIssue(missing.getKey(), MaterialIssue.Kind.MISSING,
                manifest.required().getOrDefault(missing.getKey(), 0L), manifest.available().getOrDefault(missing.getKey(), 0L),
                "Material is not currently available in sufficient quantity."));
        }
        List<BlueprintWarning> warnings = new ArrayList<>(resolution.warnings());
        if (!materialIssues.isEmpty()) warnings.add(new BlueprintWarning("MATERIALS_INCOMPLETE", BlueprintWarning.Severity.WARNING,
            "Blueprint is valid as a proposal but current material availability is incomplete."));

        long placements = operations.stream().filter(op -> op.kind() != PlacementOperation.Kind.CLEAR).count();
        long removals = operations.stream().filter(op -> op.kind() == PlacementOperation.Kind.CLEAR).count();
        Bounds localDimensions = new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(size.width() - 1, size.height() - 1, size.depth() - 1));
        double confidence = Math.max(0.0, 1.0 - 0.12 * resolution.unsupportedCount() - 0.25 * resolution.conflictCount());

        BlueprintProposal proposal = new BlueprintProposal(blueprintId, BLUEPRINT_VERSION, "SHA-256", hash, request.dimensionId(),
            request.constructionVolume(), localDimensions, anchor, request.preferredFacing(), resolution.ledger(), palette, manifest, operations,
            List.of(), materialIssues, new WorkloadEstimate(placements, removals, 0, placements + removals),
            new PreviewMetadata(request.buildPurpose(), "Deterministic bounded-volume proposal", resolution.style(),
                Map.of("size", resolution.size(), "roof", resolution.roof(), "floors", Integer.toString(resolution.floors()))),
            confidence, warnings);
        if (!proposal.allOperationsInsideConstructionVolume()) throw new IllegalStateException("Planner emitted operation outside selected construction volume");
        return proposal;
    }

    private Resolution interpret(BlueprintRequest request) {
        Map<String, BlueprintSpecification> seen = new LinkedHashMap<>();
        List<SpecificationResolution> ledger = new ArrayList<>();
        List<BlueprintWarning> warnings = new ArrayList<>();
        AtomicInteger unsupported = new AtomicInteger();
        AtomicInteger conflicts = new AtomicInteger();
        for (BlueprintSpecification spec : request.specifications()) {
            BlueprintSpecification prior = seen.putIfAbsent(spec.key(), spec);
            if (prior != null && !prior.value().equalsIgnoreCase(spec.value())) {
                ledger.add(new SpecificationResolution(spec.key(), spec.value(), "", SpecificationResolution.Status.CONFLICT,
                    "Conflicts with earlier value " + prior.value()));
                conflicts.incrementAndGet();
                warnings.add(new BlueprintWarning("SPECIFICATION_CONFLICT", BlueprintWarning.Severity.ERROR,
                    spec.key() + " has conflicting requested values."));
            }
        }
        String style = resolveEnum("STYLE", seen.get("STYLE"), Set.of("SIMPLE_HALL", "RECTILINEAR_WORKSHOP", "HOLLOW_COURT"),
            inferDefaultStyle(request.buildPurpose()), request.permittedStyles(), ledger, warnings, unsupported);
        String size = resolveEnum("SIZE", seen.get("SIZE"), Set.of("TINY", "COMPACT", "STANDARD", "LARGE", "FILL"),
            "COMPACT", Set.of(), ledger, warnings, unsupported);
        String roof = resolveEnum("ROOF", seen.get("ROOF"), Set.of("FLAT", "OPEN"),
            style.equals("HOLLOW_COURT") ? "OPEN" : "FLAT", Set.of(), ledger, warnings, unsupported);
        String entrance = resolveEnum("ENTRANCE", seen.get("ENTRANCE"), Set.of("NORTH", "SOUTH", "EAST", "WEST"),
            facingName(request.preferredFacing()), Set.of(), ledger, warnings, unsupported);

        int floors = 1;
        BlueprintSpecification floorSpec = seen.get("FLOORS");
        if (floorSpec == null) ledger.add(new SpecificationResolution("FLOORS", "", "1", SpecificationResolution.Status.DEFAULTED, "Default floor count."));
        else {
            try {
                int value = Integer.parseInt(floorSpec.value());
                if (value < 1 || value > 3) throw new NumberFormatException();
                floors = value;
                ledger.add(new SpecificationResolution("FLOORS", floorSpec.value(), Integer.toString(value), SpecificationResolution.Status.APPLIED, ""));
            } catch (NumberFormatException exc) {
                unsupported.incrementAndGet();
                ledger.add(new SpecificationResolution("FLOORS", floorSpec.value(), "1", SpecificationResolution.Status.UNSUPPORTED, "Allowed values are 1, 2, 3."));
                warnings.add(specWarning(floorSpec, "Unsupported FLOORS value; defaulted to 1."));
            }
        }
        BlueprintSpecification detail = seen.get("PURPOSE_DETAIL");
        if (detail != null) ledger.add(new SpecificationResolution("PURPOSE_DETAIL", detail.value(), detail.value(), SpecificationResolution.Status.APPLIED,
            "Preserved as semantic planning metadata."));

        Set<String> known = Set.of("STYLE", "SIZE", "ROOF", "ENTRANCE", "FLOORS", "PURPOSE_DETAIL");
        for (BlueprintSpecification spec : request.specifications()) {
            if (!known.contains(spec.key())) {
                unsupported.incrementAndGet();
                ledger.add(new SpecificationResolution(spec.key(), spec.value(), "", SpecificationResolution.Status.UNSUPPORTED,
                    "This blueprint kernel does not currently interpret this specification key."));
                warnings.add(specWarning(spec, "Unsupported blueprint specification: " + spec.key()));
            }
        }
        return new Resolution(style, size, roof, entrance, floors, List.copyOf(ledger), List.copyOf(warnings), unsupported.get(), conflicts.get());
    }

    private static BlueprintWarning specWarning(BlueprintSpecification spec, String message) {
        BlueprintWarning.Severity severity = spec.requirement() == BlueprintSpecification.Requirement.REQUIRED
            ? BlueprintWarning.Severity.ERROR : BlueprintWarning.Severity.WARNING;
        return new BlueprintWarning("SPECIFICATION_UNSUPPORTED", severity, message);
    }

    private static String resolveEnum(String key, BlueprintSpecification spec, Set<String> allowed, String defaultValue,
                                      Set<String> callerAllowed, List<SpecificationResolution> ledger,
                                      List<BlueprintWarning> warnings, AtomicInteger unsupported) {
        if (spec == null) {
            ledger.add(new SpecificationResolution(key, "", defaultValue, SpecificationResolution.Status.DEFAULTED, "Deterministic default."));
            return defaultValue;
        }
        String requested = spec.value().trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
        boolean allowedByPlanner = allowed.contains(requested);
        boolean allowedByCaller = callerAllowed == null || callerAllowed.isEmpty()
            || callerAllowed.stream().map(value -> value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_')).anyMatch(requested::equals);
        if (allowedByPlanner && allowedByCaller) {
            ledger.add(new SpecificationResolution(key, spec.value(), requested, SpecificationResolution.Status.APPLIED, ""));
            return requested;
        }
        unsupported.incrementAndGet();
        ledger.add(new SpecificationResolution(key, spec.value(), defaultValue, SpecificationResolution.Status.UNSUPPORTED,
            allowedByCaller ? "Value is not supported by this planner." : "Value is not permitted by the caller."));
        warnings.add(specWarning(spec, "Unsupported or disallowed " + key + " value; defaulted to " + defaultValue + "."));
        return defaultValue;
    }

    private static String inferDefaultStyle(String purpose) {
        String normalized = purpose.toUpperCase(Locale.ROOT);
        if (normalized.contains("COURT") || normalized.contains("RUNE")) return "HOLLOW_COURT";
        if (normalized.contains("WORKSHOP") || normalized.contains("FACTORY") || normalized.contains("FORGE")) return "RECTILINEAR_WORKSHOP";
        return "SIMPLE_HALL";
    }

    private static String facingName(Facing facing) {
        return switch (facing) {
            case SOUTH -> "SOUTH";
            case EAST -> "EAST";
            case WEST -> "WEST";
            default -> "NORTH";
        };
    }

    private static Dimensions chooseSize(Bounds volume, String sizeName) {
        double factor = switch (sizeName) {
            case "TINY" -> 0.25;
            case "COMPACT" -> 0.45;
            case "STANDARD" -> 0.65;
            case "LARGE" -> 0.82;
            case "FILL" -> 1.0;
            default -> 0.45;
        };
        int width = boundedAxis(volume.width(), factor, 7, MAX_WIDTH);
        int depth = boundedAxis(volume.depth(), factor, 7, MAX_DEPTH);
        int height = boundedAxis(volume.height(), Math.min(1.0, 0.35 + factor * 0.35), 5, MAX_HEIGHT);
        if (width < 5 || depth < 5 || height < 4) throw new IllegalArgumentException("Selected construction volume is too small for blueprint generation");
        return new Dimensions(width, height, depth);
    }

    private static int boundedAxis(int available, double factor, int minimumTarget, int safetyCap) {
        if (available <= 0) throw new IllegalArgumentException("Construction volume has invalid axis length");
        int desired = Math.max(minimumTarget, (int)Math.floor(available * factor));
        return Math.min(available, Math.min(safetyCap, desired));
    }

    private static BlockPosition chooseAnchor(BlockPosition preferred, Bounds volume, Dimensions size) {
        int x = clamp(preferred.x() - size.width() / 2, volume.min().x(), volume.max().x() - size.width() + 1);
        int y = clamp(preferred.y(), volume.min().y(), volume.max().y() - size.height() + 1);
        int z = clamp(preferred.z() - size.depth() / 2, volume.min().z(), volume.max().z() - size.depth() + 1);
        return new BlockPosition(x, y, z);
    }

    private static int clamp(int value, int min, int max) {
        if (max < min) return min;
        return Math.max(min, Math.min(max, value));
    }

    private static List<PaletteEntry> paletteFor(String purpose) {
        String normalized = purpose.toUpperCase(Locale.ROOT);
        boolean botanical = normalized.contains("BOTANIA") || normalized.contains("RUNE");
        if (botanical) return List.of(
            new PaletteEntry("foundation", "minecraft:stone_bricks", "minecraft:stone_bricks", Map.of("role", "foundation")),
            new PaletteEntry("wall", "minecraft:mossy_stone_bricks", "minecraft:mossy_stone_bricks", Map.of("role", "wall")),
            new PaletteEntry("trim", "minecraft:stripped_oak_log", "minecraft:stripped_oak_log", Map.of("role", "trim")),
            new PaletteEntry("roof", "minecraft:oak_planks", "minecraft:oak_planks", Map.of("role", "roof")),
            new PaletteEntry("light", "minecraft:lantern", "minecraft:lantern", Map.of("role", "light"))
        );
        return List.of(
            new PaletteEntry("foundation", "minecraft:stone_bricks", "minecraft:stone_bricks", Map.of("role", "foundation")),
            new PaletteEntry("wall", "minecraft:smooth_stone", "minecraft:smooth_stone", Map.of("role", "wall")),
            new PaletteEntry("trim", "minecraft:stripped_spruce_log", "minecraft:stripped_spruce_log", Map.of("role", "trim")),
            new PaletteEntry("roof", "minecraft:spruce_planks", "minecraft:spruce_planks", Map.of("role", "roof")),
            new PaletteEntry("light", "minecraft:lantern", "minecraft:lantern", Map.of("role", "light"))
        );
    }

    private static List<PlacementOperation> buildOperations(Dimensions size, Resolution resolution) {
        List<PlacementOperation> operations = new ArrayList<>();
        int seq = 0, w = size.width(), h = size.height(), d = size.depth();
        for (int x = 0; x < w; x++) for (int z = 0; z < d; z++)
            operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, 0, z), "foundation"));

        int floorHeight = Math.max(3, (h - 1) / Math.max(1, resolution.floors()));
        for (int floor = 0; floor < resolution.floors(); floor++) {
            int baseY = Math.min(h - 2, 1 + floor * floorHeight);
            int topY = Math.min(h - 2, baseY + floorHeight - 1);
            for (int y = baseY; y <= topY; y++) {
                for (int x = 0; x < w; x++) {
                    if (!isEntranceGap(resolution.entrance(), x, y, 0, w, d, baseY)) operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, y, 0), wallKey(x, w)));
                    if (!isEntranceGap(resolution.entrance(), x, y, d - 1, w, d, baseY)) operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, y, d - 1), wallKey(x, w)));
                }
                for (int z = 1; z < d - 1; z++) {
                    if (!isEntranceGap(resolution.entrance(), 0, y, z, w, d, baseY)) operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(0, y, z), wallKey(z, d)));
                    if (!isEntranceGap(resolution.entrance(), w - 1, y, z, w, d, baseY)) operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(w - 1, y, z), wallKey(z, d)));
                }
            }
            if (floor > 0) for (int x = 1; x < w - 1; x++) for (int z = 1; z < d - 1; z++)
                if (!isCourtyard(resolution.style(), x, z, w, d)) operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, baseY - 1, z), "foundation"));
        }

        if (!resolution.roof().equals("OPEN")) {
            int roofY = h - 1;
            for (int x = 0; x < w; x++) for (int z = 0; z < d; z++) {
                if (resolution.style().equals("HOLLOW_COURT") && isCourtyard(resolution.style(), x, z, w, d)) continue;
                operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, roofY, z), "roof"));
            }
        }
        int lightY = Math.min(h - 2, 3);
        for (int x : new int[]{1, w - 2}) for (int z : new int[]{1, d - 2})
            operations.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE, new BlockPosition(x, lightY, z), "light"));
        return List.copyOf(operations);
    }

    private static String wallKey(int coordinate, int axisLength) {
        return coordinate == 0 || coordinate == axisLength - 1 || coordinate % 5 == 0 ? "trim" : "wall";
    }

    private static boolean isCourtyard(String style, int x, int z, int w, int d) {
        if (!style.equals("HOLLOW_COURT") || w < 11 || d < 11) return false;
        int marginX = Math.max(3, w / 4), marginZ = Math.max(3, d / 4);
        return x >= marginX && x < w - marginX && z >= marginZ && z < d - marginZ;
    }

    private static boolean isEntranceGap(String entrance, int x, int y, int z, int w, int d, int baseY) {
        if (y < baseY || y > baseY + 1) return false;
        return switch (entrance) {
            case "SOUTH" -> z == d - 1 && x >= w / 2 - 1 && x <= w / 2 + 1;
            case "EAST" -> x == w - 1 && z >= d / 2 - 1 && z <= d / 2 + 1;
            case "WEST" -> x == 0 && z >= d / 2 - 1 && z <= d / 2 + 1;
            default -> z == 0 && x >= w / 2 - 1 && x <= w / 2 + 1;
        };
    }

    private static MaterialManifest materialManifest(UUID blueprintId, List<PaletteEntry> palette, List<PlacementOperation> operations,
                                                     List<MaterialAvailability> availability) {
        Map<String, String> materialByKey = new HashMap<>();
        for (PaletteEntry entry : palette) materialByKey.put(entry.key(), entry.materialId());
        Map<String, Long> required = new TreeMap<>();
        for (PlacementOperation operation : operations) {
            if (operation.kind() == PlacementOperation.Kind.CLEAR || operation.paletteKey() == null) continue;
            String material = materialByKey.get(operation.paletteKey());
            if (material != null) required.merge(material, 1L, Long::sum);
        }
        Map<String, Long> available = new TreeMap<>();
        for (MaterialAvailability material : availability) available.merge(material.materialId(), material.availableCount(), Long::sum);
        Map<String, Long> missing = new TreeMap<>();
        for (Map.Entry<String, Long> entry : required.entrySet()) {
            long have = available.getOrDefault(entry.getKey(), 0L);
            if (have < entry.getValue()) missing.put(entry.getKey(), entry.getValue() - have);
        }
        return new MaterialManifest(blueprintId, required, available, missing);
    }

    private static String canonicalPlan(BlueprintRequest request, Resolution resolution, BlockPosition anchor, Dimensions size,
                                        List<PaletteEntry> palette, List<PlacementOperation> operations) {
        StringBuilder out = new StringBuilder();
        out.append(BLUEPRINT_VERSION).append('|').append(request.dimensionId()).append('|').append(request.buildPurpose())
            .append('|').append(request.constructionVolume().volumeId()).append('|').append(request.constructionVolume().snapshotEpoch())
            .append('|').append(anchor).append('|').append(size).append('|').append(resolution.style()).append('|').append(resolution.size())
            .append('|').append(resolution.roof()).append('|').append(resolution.entrance()).append('|').append(resolution.floors());
        for (PaletteEntry entry : palette) out.append('|').append(entry.key()).append('=').append(entry.blockState());
        for (PlacementOperation operation : operations) out.append('|').append(operation.sequence()).append(':').append(operation.relativePosition()).append(':').append(operation.paletteKey());
        return out.toString();
    }

    private static String sha256(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder(digest.length * 2);
            for (byte b : digest) hex.append(String.format(Locale.ROOT, "%02x", b & 0xff));
            return hex.toString();
        } catch (NoSuchAlgorithmException exc) {
            throw new IllegalStateException("SHA-256 unavailable", exc);
        }
    }

    private record Dimensions(int width, int height, int depth) {}
    private record Resolution(String style, String size, String roof, String entrance, int floors,
                              List<SpecificationResolution> ledger, List<BlueprintWarning> warnings,
                              int unsupportedCount, int conflictCount) {}
}
