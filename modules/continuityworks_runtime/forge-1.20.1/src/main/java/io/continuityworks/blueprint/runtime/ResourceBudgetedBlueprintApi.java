package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Low-overhead public provider wrapper.
 *
 * Continuity Works deliberately contains no neural inference runtime. This class
 * bounds request fan-out, input cardinality and retained results so Minecraft
 * remains the dominant memory consumer.
 */
public final class ResourceBudgetedBlueprintApi implements ContinuityWorksBlueprintApi {
    public static final int MAX_ACTIVE_REQUESTS = 3;
    public static final int MAX_COMPLETED_REQUESTS_PER_RUNTIME = 4_096;
    public static final int MAX_SPECIFICATIONS = 32;
    public static final int MAX_AVAILABLE_MATERIAL_ROWS = 512;
    public static final int MAX_SITE_CANDIDATES = 32;
    public static final int MAX_PERMITTED_STYLES = 32;
    public static final int MAX_RECENT_MANIFESTS = 16;

    private final DeterministicBlueprintApi delegate = new DeterministicBlueprintApi();
    private final Semaphore globalRequestPermits = new Semaphore(MAX_ACTIVE_REQUESTS, true);
    private final ConcurrentMap<UUID, CompletableFuture<BlueprintProposal>> activeRequests = new ConcurrentHashMap<>();
    private final Map<UUID, MaterialManifest> recentManifests = Collections.synchronizedMap(
        new LinkedHashMap<>(MAX_RECENT_MANIFESTS + 1, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<UUID, MaterialManifest> eldest) {
                return size() > MAX_RECENT_MANIFESTS;
            }
        }
    );
    private final AtomicInteger completedRequests = new AtomicInteger();

    @Override
    public BlueprintApiVersion apiVersion() {
        return delegate.apiVersion();
    }

    @Override
    public BlueprintVocabulary vocabulary() {
        return delegate.vocabulary();
    }

    @Override
    public CompletableFuture<BlueprintProposal> generate(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        validateInputBudget(request);

        if (completedRequests.get() >= MAX_COMPLETED_REQUESTS_PER_RUNTIME) {
            return CompletableFuture.failedFuture(new RejectedExecutionException(
                "Continuity Works blueprint session budget reached "
                    + MAX_COMPLETED_REQUESTS_PER_RUNTIME
                    + " completed requests; restart the runtime before generating additional blueprints."
            ));
        }
        if (!globalRequestPermits.tryAcquire()) {
            return CompletableFuture.failedFuture(new RejectedExecutionException(
                "Continuity Works lightweight blueprint budget is saturated; at most "
                    + MAX_ACTIVE_REQUESTS + " requests may be active or queued."
            ));
        }

        final CompletableFuture<BlueprintProposal> future;
        try {
            future = delegate.generate(request);
        } catch (Throwable error) {
            globalRequestPermits.release();
            return CompletableFuture.failedFuture(error);
        }

        activeRequests.put(request.requestId(), future);
        future.whenComplete((proposal, error) -> {
            activeRequests.remove(request.requestId(), future);
            if (proposal != null) {
                recentManifests.put(proposal.blueprintId(), proposal.materials());
                completedRequests.incrementAndGet();
            }
            globalRequestPermits.release();
        });
        return future;
    }

    @Override
    public ValidationResult validate(BlueprintProposal proposal, BlueprintContext context) {
        return delegate.validate(proposal, context);
    }

    @Override
    public MaterialManifest getMaterials(UUID blueprintId) {
        Objects.requireNonNull(blueprintId, "blueprintId");
        MaterialManifest recent = recentManifests.get(blueprintId);
        if (recent != null) return recent;
        return delegate.getMaterials(blueprintId);
    }

    @Override
    public void cancel(UUID requestId) {
        Objects.requireNonNull(requestId, "requestId");
        CompletableFuture<BlueprintProposal> future = activeRequests.get(requestId);
        if (future != null) future.cancel(true);
        delegate.cancel(requestId);
    }

    public RuntimeBudgetSnapshot budgetSnapshot() {
        return new RuntimeBudgetSnapshot(
            MAX_ACTIVE_REQUESTS,
            globalRequestPermits.availablePermits(),
            recentManifests.size(),
            completedRequests.get(),
            MAX_COMPLETED_REQUESTS_PER_RUNTIME
        );
    }

    private static void validateInputBudget(BlueprintRequest request) {
        if (request.specifications().size() > MAX_SPECIFICATIONS) {
            throw new IllegalArgumentException("Too many blueprint specifications: " + request.specifications().size()
                + " > " + MAX_SPECIFICATIONS);
        }
        if (request.availableMaterials().size() > MAX_AVAILABLE_MATERIAL_ROWS) {
            throw new IllegalArgumentException("Too many material availability rows: " + request.availableMaterials().size()
                + " > " + MAX_AVAILABLE_MATERIAL_ROWS);
        }
        if (request.candidateSites().size() > MAX_SITE_CANDIDATES) {
            throw new IllegalArgumentException("Too many site candidates: " + request.candidateSites().size()
                + " > " + MAX_SITE_CANDIDATES);
        }
        if (request.permittedStyles().size() > MAX_PERMITTED_STYLES) {
            throw new IllegalArgumentException("Too many permitted styles: " + request.permittedStyles().size()
                + " > " + MAX_PERMITTED_STYLES);
        }
    }

    public record RuntimeBudgetSnapshot(
        int maxActiveRequests,
        int availableRequestPermits,
        int recentManifestCount,
        int completedRequestCount,
        int maxCompletedRequestsPerRuntime
    ) {}
}
