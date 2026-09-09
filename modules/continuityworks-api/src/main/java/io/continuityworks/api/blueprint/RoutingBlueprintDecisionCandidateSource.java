package io.continuityworks.api.blueprint;

import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

/**
 * Routes dynamic candidate requests by mutator code without teaching transport or inference
 * orchestration about catalog/profile storage. New authoritative profile sources can be added
 * to this routing table without changing the decision chain or HTTP authority.
 */
public final class RoutingBlueprintDecisionCandidateSource implements BlueprintDecisionCandidateSource {
    private final Map<String, BlueprintDecisionCandidateSource> routes;

    public RoutingBlueprintDecisionCandidateSource(Map<String, BlueprintDecisionCandidateSource> routes) {
        Objects.requireNonNull(routes, "routes");
        LinkedHashMap<String, BlueprintDecisionCandidateSource> copy = new LinkedHashMap<>();
        for (Map.Entry<String, BlueprintDecisionCandidateSource> entry : routes.entrySet()) {
            String code = normalizeCode(entry.getKey());
            BlueprintDecisionCandidateSource source = Objects.requireNonNull(entry.getValue(), "candidate source for " + code);
            if (copy.put(code, source) != null) {
                throw new IllegalArgumentException("duplicate candidate-source route: " + code);
            }
        }
        if (copy.isEmpty()) throw new IllegalArgumentException("candidate-source routing table must not be empty");
        this.routes = Map.copyOf(copy);
    }

    public static RoutingBlueprintDecisionCandidateSource of(
        String firstCode,
        BlueprintDecisionCandidateSource firstSource,
        String secondCode,
        BlueprintDecisionCandidateSource secondSource
    ) {
        LinkedHashMap<String, BlueprintDecisionCandidateSource> routes = new LinkedHashMap<>();
        routes.put(firstCode, firstSource);
        routes.put(secondCode, secondSource);
        return new RoutingBlueprintDecisionCandidateSource(routes);
    }

    public static RoutingBlueprintDecisionCandidateSource of(
        String firstCode,
        BlueprintDecisionCandidateSource firstSource,
        String secondCode,
        BlueprintDecisionCandidateSource secondSource,
        String thirdCode,
        BlueprintDecisionCandidateSource thirdSource
    ) {
        LinkedHashMap<String, BlueprintDecisionCandidateSource> routes = new LinkedHashMap<>();
        routes.put(firstCode, firstSource);
        routes.put(secondCode, secondSource);
        routes.put(thirdCode, thirdSource);
        return new RoutingBlueprintDecisionCandidateSource(routes);
    }

    @Override
    public CandidateSet candidates(
        BlueprintRequest request,
        BlueprintDecisionChain.State state,
        BlueprintDecisionChain.Mutator mutator
    ) {
        Objects.requireNonNull(mutator, "mutator");
        BlueprintDecisionCandidateSource source = routes.get(normalizeCode(mutator.code()));
        if (source == null) {
            throw new IllegalArgumentException("no authoritative candidate source configured for mutator " + mutator.code());
        }
        return source.candidates(request, state, mutator);
    }

    public Map<String, BlueprintDecisionCandidateSource> routes() {
        return routes;
    }

    private static String normalizeCode(String code) {
        Objects.requireNonNull(code, "mutator code");
        String normalized = code.trim().toUpperCase(Locale.ROOT);
        if (normalized.length() != 1) throw new IllegalArgumentException("candidate-source mutator code must be one character");
        return normalized;
    }
}
