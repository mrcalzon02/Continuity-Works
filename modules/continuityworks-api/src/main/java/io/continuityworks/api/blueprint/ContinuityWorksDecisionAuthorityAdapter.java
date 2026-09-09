package io.continuityworks.api.blueprint;

import java.util.Objects;

/**
 * Thin transport-facing authority for the compact decision chain.
 *
 * <p>This adapter deliberately delegates every semantic operation through the
 * configured {@link ContinuityWorksCompactBlueprintApi}. It does not reimplement
 * mutator vocabulary, dependency rules, validation, or finalization. A later HTTP,
 * IPC, or companion-mod transport can bind to this class while preserving one
 * authoritative decision implementation.</p>
 */
public final class ContinuityWorksDecisionAuthorityAdapter {
    private final ContinuityWorksCompactBlueprintApi api;

    public ContinuityWorksDecisionAuthorityAdapter(ContinuityWorksCompactBlueprintApi api) {
        this.api = Objects.requireNonNull(api, "api");
    }

    /** API version reported by the configured authoritative provider. */
    public BlueprintApiVersion apiVersion() {
        return api.apiVersion();
    }

    /** Discover the provider's current compact inference contract. */
    public BlueprintDecisionChain.Profile decisionProfile() {
        return api.decisionProfile();
    }

    /** Begin a decision state through the authoritative provider. */
    public BlueprintDecisionChain.State beginDecision(BlueprintRequest request) {
        return api.beginDecision(Objects.requireNonNull(request, "request"));
    }

    /** Return only the next dependency-valid semantic decisions. */
    public BlueprintDecisionChain.Step nextDecision(BlueprintDecisionChain.State state) {
        return api.nextDecision(Objects.requireNonNull(state, "state"));
    }

    /**
     * Apply one compact inference response when the caller's observed revision still
     * matches the authoritative state. This prevents late asynchronous inference
     * output from mutating a newer decision state.
     */
    public BlueprintDecisionChain.State applyDecision(
        BlueprintDecisionChain.State state,
        long expectedRevision,
        String encodedMutations
    ) {
        requireRevision(state, expectedRevision);
        return api.applyDecision(state, Objects.requireNonNull(encodedMutations, "encodedMutations"));
    }

    /** Validate accumulated semantic state without materializing geometry. */
    public BlueprintDecisionChain.Validation validateDecision(BlueprintDecisionChain.State state) {
        return api.validateDecision(Objects.requireNonNull(state, "state"));
    }

    /** Freeze a valid semantic state through the authoritative provider. */
    public BlueprintDecisionChain.FinalizedDecision finalizeDecision(BlueprintDecisionChain.State state) {
        return api.finalizeDecision(Objects.requireNonNull(state, "state"));
    }

    /**
     * Verify a transport/request revision before performing work against a state.
     * The returned state is the same immutable authoritative state instance.
     */
    public BlueprintDecisionChain.State requireRevision(
        BlueprintDecisionChain.State state,
        long expectedRevision
    ) {
        Objects.requireNonNull(state, "state");
        if (expectedRevision < 0) {
            throw new IllegalArgumentException("expectedRevision must be non-negative");
        }
        if (state.revision() != expectedRevision) {
            throw new IllegalStateException(
                "stale decision revision: expected " + expectedRevision + " but state is " + state.revision()
            );
        }
        return state;
    }
}
