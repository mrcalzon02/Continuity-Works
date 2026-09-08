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
                future = generic.generateCompact(request);
            }
        } catch (RuntimeException error) {
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            permits.release();
            return CompletableFuture.failedFuture(error);
        }

        activeRequests.put(request.requestId(), future);
        future.whenComplete((plan, error) -> {
            activeRequests.remove(request.requestId(), future);
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

    private static boolean hasCorpusSelector(BlueprintRequest request) {
        for (BlueprintSpecification specification : request.specifications()) {
            if ("REFERENCE".equals(specification.key()) || "ARCHETYPE".equals(specification.key()) || "CATEGORY".equals(specification.key())) return true;
        }
        return false;
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
