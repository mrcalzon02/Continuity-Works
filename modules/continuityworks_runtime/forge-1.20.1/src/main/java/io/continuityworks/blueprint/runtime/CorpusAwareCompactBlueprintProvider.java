package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.*;

import java.util.*;
import java.util.concurrent.*;

/**
 * Single public compact capability router. Explicit corpus selectors stay primitive-based;
 * other requests delegate to the bounded generic compact grammar. A shared permit gate keeps
 * the combined route at three active/queued requests even though each planner is independently usable.
 */
public final class CorpusAwareCompactBlueprintProvider implements ContinuityWorksCompactBlueprintApi {
    private static final int MAX_ACTIVE_REQUESTS = 3;
    private static final int MAX_RETAINED_CORPUS_MANIFESTS = 16;
    private static final Set<String> GENERIC_STYLES = Set.of("SIMPLE_HALL", "RECTILINEAR_WORKSHOP", "HOLLOW_COURT");

    private final CompactBlueprintProvider generic = new CompactBlueprintProvider();
    private final CompactFacilityCorpusPlanner corpus = new CompactFacilityCorpusPlanner();
    private final FacilityCorpusVocabulary corpusVocabulary = new FacilityCorpusVocabulary();
    private final ThreadPoolExecutor corpusExecutor = new ThreadPoolExecutor(
        1, 1, 0L, TimeUnit.MILLISECONDS,
        new ArrayBlockingQueue<>(MAX_ACTIVE_REQUESTS - 1),
        runnable -> {
            Thread thread = new Thread(runnable, "continuityworks-compact-corpus");
            thread.setDaemon(true);
            thread.setPriority(Thread.NORM_PRIORITY - 1);
            return thread;
        },
        new ThreadPoolExecutor.AbortPolicy()
    );
    private final Semaphore permits = new Semaphore(MAX_ACTIVE_REQUESTS, true);
    private final ConcurrentMap<UUID, UUID> activeByCompanion = new ConcurrentHashMap<>();
    private final ConcurrentMap<UUID, CompletableFuture<CompactBlueprintPlan>> activeRequests = new ConcurrentHashMap<>();
    private final Map<UUID, MaterialManifest> corpusManifests = Collections.synchronizedMap(
        new LinkedHashMap<>(MAX_RETAINED_CORPUS_MANIFESTS + 1, 0.75f, true) {
            @Override protected boolean removeEldestEntry(Map.Entry<UUID, MaterialManifest> eldest) {
                return size() > MAX_RETAINED_CORPUS_MANIFESTS;
            }
        }
    );

    @Override
    public BlueprintApiVersion apiVersion() { return generic.apiVersion(); }

    @Override
    public BlueprintVocabulary vocabulary() {
        BlueprintVocabulary base = generic.vocabulary();
        FacilityCorpusVocabulary.Snapshot manifest = corpusVocabulary.snapshot();
        ArrayList<SpecificationDescriptor> specifications = new ArrayList<>(base.specifications());
        specifications.add(new SpecificationDescriptor("REFERENCE", manifest.references(), true, "",
            "Optional bundled facility reference slug. Explicit selection preserves authored primitive geometry."));
        specifications.add(new SpecificationDescriptor("ARCHETYPE", manifest.archetypes(), true, "",
            "Bundled facility archetype slug used to select a pre-solved primitive reference."));
        specifications.add(new SpecificationDescriptor("CATEGORY", manifest.categories(), true, "",
            "Bundled facility category used to constrain pre-solved reference selection."));
        return new BlueprintVocabulary("compact/2:" + manifest.libraryVersion(), specifications);
    }

    @Override
    public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        if (!permits.tryAcquire()) {
            return CompletableFuture.failedFuture(new RejectedExecutionException(
                "Continuity Works compact capability is saturated; at most " + MAX_ACTIVE_REQUESTS + " requests may be active or queued."));
        }
        UUID prior = activeByCompanion.putIfAbsent(request.companionUuid(), request.requestId());
        if (prior != null) {
            permits.release();
            return CompletableFuture.failedFuture(new IllegalStateException("Companion already has active compact blueprint request " + prior));
        }

        CompletableFuture<CompactBlueprintPlan> future;
        try {
            if (hasCorpusSelector(request)) {
                future = CompletableFuture.supplyAsync(
                    () -> corpus.plan(request).orElseThrow(() -> new IllegalArgumentException("No compact facility corpus plan resolved.")),
                    corpusExecutor
                );
            } else {
                BlueprintRequest guarded = enforcePermittedStyle(request);
                future = generic.generateCompact(guarded);
            }
            future = future.thenApply(CorpusAwareCompactBlueprintProvider::correctConfidence);
        } catch (RuntimeException error) {
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            permits.release();
            return CompletableFuture.failedFuture(error);
        }

        activeRequests.put(request.requestId(), future);
        CompletableFuture<CompactBlueprintPlan> tracked = future;
        future.whenComplete((plan, error) -> {
            activeRequests.remove(request.requestId(), tracked);
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            if (plan != null && plan.blueprintVersion().startsWith("facility-corpus-compact/")) {
                corpusManifests.put(plan.blueprintId(), plan.materials());
            }
            permits.release();
        });
        return future;
    }

    @Override
    public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) {
        return generic.validateCompact(plan, context);
    }

    @Override
    public MaterialManifest getCompactMaterials(UUID blueprintId) {
        Objects.requireNonNull(blueprintId, "blueprintId");
        MaterialManifest manifest = corpusManifests.get(blueprintId);
        if (manifest != null) return manifest;
        return generic.getCompactMaterials(blueprintId);
    }

    @Override
    public void cancelCompact(UUID requestId) {
        Objects.requireNonNull(requestId, "requestId");
        CompletableFuture<CompactBlueprintPlan> future = activeRequests.get(requestId);
        if (future != null) future.cancel(true);
        generic.cancelCompact(requestId);
    }

    RuntimeSnapshot snapshot() {
        return new RuntimeSnapshot(
            MAX_ACTIVE_REQUESTS,
            permits.availablePermits(),
            corpusExecutor.getQueue().size(),
            corpusManifests.size(),
            CompactFacilityCorpusPlanner.MAX_CANDIDATES,
            CompactBlueprintProvider.MAX_PRIMITIVES,
            CompactBlueprintProvider.MAX_RAW_PLACEMENTS
        );
    }

    private static BlueprintRequest enforcePermittedStyle(BlueprintRequest request) {
        if (request.permittedStyles().isEmpty()) return request;
        TreeSet<String> permitted = new TreeSet<>();
        for (String value : request.permittedStyles()) {
            String normalized = normalize(value);
            if (GENERIC_STYLES.contains(normalized)) permitted.add(normalized);
        }
        if (permitted.isEmpty()) throw new IllegalArgumentException("No caller-permitted style is supported by the compact generic planner.");

        BlueprintSpecification explicit = null;
        for (BlueprintSpecification specification : request.specifications()) {
            if ("STYLE".equals(specification.key())) { explicit = specification; break; }
        }
        if (explicit != null) {
            if (!permitted.contains(normalize(explicit.value()))) {
                throw new IllegalArgumentException("Requested STYLE is not permitted by the caller: " + explicit.value());
            }
            return request;
        }

        String inferred = inferGenericStyle(request.buildPurpose());
        String selected = permitted.contains(inferred) ? inferred : permitted.first();
        ArrayList<BlueprintSpecification> specifications = new ArrayList<>(request.specifications());
        specifications.add(new BlueprintSpecification("STYLE", selected, BlueprintSpecification.Requirement.PREFERRED));
        return new BlueprintRequest(
            request.requestId(), request.companionUuid(), request.ownerUuid(), request.dimensionId(), request.buildPurpose(),
            request.constructionVolume(), request.preferredOrigin(), request.preferredFacing(), specifications,
            request.availableMaterials(), request.candidateSites(), request.permittedStyles()
        );
    }

    private static CompactBlueprintPlan correctConfidence(CompactBlueprintPlan plan) {
        int unsupported = 0, conflicts = 0;
        for (SpecificationResolution resolution : plan.specificationResolutions()) {
            if (resolution.status() == SpecificationResolution.Status.UNSUPPORTED) unsupported++;
            else if (resolution.status() == SpecificationResolution.Status.CONFLICT) conflicts++;
        }
        double resolved = Math.max(0.0, 1.0 - 0.12 * unsupported - 0.25 * conflicts);
        double confidence = Math.min(plan.confidence(), resolved);
        if (Double.compare(confidence, plan.confidence()) == 0) return plan;
        return new CompactBlueprintPlan(
            plan.blueprintId(), plan.blueprintVersion(), plan.integrityAlgorithm(), plan.integrityHash(), plan.dimensionId(),
            plan.constructionVolume(), plan.dimensions(), plan.anchor(), plan.facing(), plan.specificationResolutions(), plan.palette(),
            plan.materials(), plan.primitives(), plan.materialIssues(), plan.workload(), plan.preview(), confidence, plan.warnings()
        );
    }

    private static boolean hasCorpusSelector(BlueprintRequest request) {
        for (BlueprintSpecification specification : request.specifications()) {
            if ("REFERENCE".equals(specification.key()) || "ARCHETYPE".equals(specification.key()) || "CATEGORY".equals(specification.key())) return true;
        }
        return false;
    }

    private static String inferGenericStyle(String purpose) {
        String value = purpose.toUpperCase(Locale.ROOT);
        if (value.contains("COURT") || value.contains("RUNE")) return "HOLLOW_COURT";
        if (value.contains("WORKSHOP") || value.contains("FACTORY") || value.contains("FORGE")) return "RECTILINEAR_WORKSHOP";
        return "SIMPLE_HALL";
    }

    private static String normalize(String value) {
        return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
    }

    record RuntimeSnapshot(
        int maxActiveRequests,
        int availablePermits,
        int queuedCorpusRequests,
        int retainedCorpusManifests,
        int maxCorpusCandidates,
        int maxPrimitives,
        long maxRawPlacements
    ) {}
}
