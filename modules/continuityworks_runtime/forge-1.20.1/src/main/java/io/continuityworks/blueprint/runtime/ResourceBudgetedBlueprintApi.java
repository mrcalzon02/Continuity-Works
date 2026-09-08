package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Low-overhead public provider. Continuity Works deliberately contains no neural
 * inference runtime; semantic inference stays with the optional consuming mod.
 */
public final class ResourceBudgetedBlueprintApi implements ContinuityWorksBlueprintApi {
    public static final int MAX_ACTIVE_REQUESTS = 3;
    public static final int MAX_COMPLETED_REQUESTS_PER_RUNTIME = 4_096;
    public static final int MAX_SPECIFICATIONS = 32;
    public static final int MAX_AVAILABLE_MATERIAL_ROWS = 512;
    public static final int MAX_SITE_CANDIDATES = 32;
    public static final int MAX_PERMITTED_STYLES = 32;
    public static final int MAX_RECENT_CORPUS_MANIFESTS = 16;
    public static final int MAX_CORPUS_CANDIDATES = FacilityCorpusPlanner.MAX_CANDIDATES;
    public static final int MAX_CORPUS_OPERATIONS = FacilityCorpusPlanner.MAX_OPERATIONS;

    private final DeterministicBlueprintApi fallback = new DeterministicBlueprintApi();
    private final FacilityCorpusPlanner corpus = new FacilityCorpusPlanner();
    private final FacilityCorpusVocabulary corpusVocabulary = new FacilityCorpusVocabulary();
    private final ThreadPoolExecutor plannerExecutor = new ThreadPoolExecutor(
        1, 1, 0L, TimeUnit.MILLISECONDS,
        new ArrayBlockingQueue<>(MAX_ACTIVE_REQUESTS - 1),
        runnable -> {
            Thread thread = new Thread(runnable, "continuityworks-blueprint-budgeted");
            thread.setDaemon(true);
            thread.setPriority(Thread.NORM_PRIORITY - 1);
            return thread;
        },
        new ThreadPoolExecutor.AbortPolicy()
    );
    private final Semaphore globalRequestPermits = new Semaphore(MAX_ACTIVE_REQUESTS, true);
    private final ConcurrentMap<UUID, CompletableFuture<BlueprintProposal>> activeRequests = new ConcurrentHashMap<>();
    private final ConcurrentMap<UUID, UUID> activeByCompanion = new ConcurrentHashMap<>();
    private final Map<UUID, MaterialManifest> corpusManifests = Collections.synchronizedMap(
        new LinkedHashMap<>(MAX_RECENT_CORPUS_MANIFESTS + 1, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<UUID, MaterialManifest> eldest) {
                return size() > MAX_RECENT_CORPUS_MANIFESTS;
            }
        }
    );
    private final AtomicInteger completedRequests = new AtomicInteger();

    @Override
    public BlueprintApiVersion apiVersion() {
        return fallback.apiVersion();
    }

    @Override
    public BlueprintVocabulary vocabulary() {
        BlueprintVocabulary base = fallback.vocabulary();
        FacilityCorpusVocabulary.Snapshot manifest = corpusVocabulary.snapshot();
        List<SpecificationDescriptor> specs = new ArrayList<>(base.specifications());
        specs.add(new SpecificationDescriptor("REFERENCE", manifest.references(), true, "",
            "Optional bundled facility reference slug. Values are manifest-derived; openValue preserves forward compatibility."));
        specs.add(new SpecificationDescriptor("ARCHETYPE", manifest.archetypes(), true, "",
            "Bundled facility archetype slug. Prefer one of the manifest-derived values for tiny-model reliability."));
        specs.add(new SpecificationDescriptor("CATEGORY", manifest.categories(), true, "",
            "Bundled facility category. Prefer one of the manifest-derived values for tiny-model reliability."));
        return new BlueprintVocabulary("3:" + manifest.libraryVersion(), specs);
    }

    @Override
    public CompletableFuture<BlueprintProposal> generate(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        validateInputBudget(request);

        if (completedRequests.get() >= MAX_COMPLETED_REQUESTS_PER_RUNTIME) {
            return CompletableFuture.failedFuture(new RejectedExecutionException(
                "Continuity Works blueprint session budget reached " + MAX_COMPLETED_REQUESTS_PER_RUNTIME
                    + " completed requests; restart the runtime before generating additional blueprints."));
        }
        if (!globalRequestPermits.tryAcquire()) {
            return CompletableFuture.failedFuture(new RejectedExecutionException(
                "Continuity Works blueprint budget is saturated; at most " + MAX_ACTIVE_REQUESTS
                    + " requests may be active or queued."));
        }
        UUID prior = activeByCompanion.putIfAbsent(request.companionUuid(), request.requestId());
        if (prior != null) {
            globalRequestPermits.release();
            return CompletableFuture.failedFuture(new IllegalStateException(
                "Companion already has active blueprint request " + prior));
        }

        final CompletableFuture<BlueprintProposal> future;
        try {
            future = CompletableFuture.supplyAsync(
                () -> corpus.plan(request).orElseGet(() -> fallback.generate(request).join()),
                plannerExecutor
            );
        } catch (RejectedExecutionException error) {
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            globalRequestPermits.release();
            return CompletableFuture.failedFuture(error);
        }

        activeRequests.put(request.requestId(), future);
        future.whenComplete((proposal, error) -> {
            activeRequests.remove(request.requestId(), future);
            activeByCompanion.remove(request.companionUuid(), request.requestId());
            if (future.isCancelled()) fallback.cancel(request.requestId());
            if (proposal != null) {
                if (proposal.blueprintVersion().startsWith("facility-corpus/")) {
                    corpusManifests.put(proposal.blueprintId(), proposal.materials());
                }
                completedRequests.incrementAndGet();
            }
            globalRequestPermits.release();
        });
        return future;
    }

    @Override
    public ValidationResult validate(BlueprintProposal proposal, BlueprintContext context) {
        return fallback.validate(proposal, context);
    }

    @Override
    public MaterialManifest getMaterials(UUID blueprintId) {
        Objects.requireNonNull(blueprintId, "blueprintId");
        MaterialManifest manifest = corpusManifests.get(blueprintId);
        if (manifest != null) return manifest;
        return fallback.getMaterials(blueprintId);
    }

    @Override
    public void cancel(UUID requestId) {
        Objects.requireNonNull(requestId, "requestId");
        CompletableFuture<BlueprintProposal> future = activeRequests.get(requestId);
        if (future != null) future.cancel(true);
        fallback.cancel(requestId);
    }

    public RuntimeBudgetSnapshot budgetSnapshot() {
        return new RuntimeBudgetSnapshot(
            MAX_ACTIVE_REQUESTS,
            globalRequestPermits.availablePermits(),
            plannerExecutor.getQueue().size(),
            completedRequests.get(),
            corpusManifests.size(),
            MAX_CORPUS_CANDIDATES,
            MAX_CORPUS_OPERATIONS
        );
    }

    private static void validateInputBudget(BlueprintRequest request) {
        if (request.specifications().size() > MAX_SPECIFICATIONS)
            throw new IllegalArgumentException("Too many blueprint specifications: " + request.specifications().size());
        if (request.availableMaterials().size() > MAX_AVAILABLE_MATERIAL_ROWS)
            throw new IllegalArgumentException("Too many material availability rows: " + request.availableMaterials().size());
        if (request.candidateSites().size() > MAX_SITE_CANDIDATES)
            throw new IllegalArgumentException("Too many site candidates: " + request.candidateSites().size());
        if (request.permittedStyles().size() > MAX_PERMITTED_STYLES)
            throw new IllegalArgumentException("Too many permitted styles: " + request.permittedStyles().size());
    }

    public record RuntimeBudgetSnapshot(
        int maxActiveRequests,
        int availableRequestPermits,
        int queuedRequests,
        int completedRequestCount,
        int retainedCorpusManifestCount,
        int maxCorpusCandidates,
        int maxCorpusOperations
    ) {}
}
