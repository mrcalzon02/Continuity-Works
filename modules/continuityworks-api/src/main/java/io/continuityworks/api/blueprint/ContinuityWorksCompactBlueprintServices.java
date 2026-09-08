package io.continuityworks.api.blueprint;

import java.util.Objects;
import java.util.Optional;

/** In-JVM optional discovery boundary for the compact primitive planner. */
public final class ContinuityWorksCompactBlueprintServices {
    private static volatile ContinuityWorksCompactBlueprintApi provider;
    private ContinuityWorksCompactBlueprintServices() {}

    public static Optional<ContinuityWorksCompactBlueprintApi> find() { return Optional.ofNullable(provider); }

    public static ContinuityWorksCompactBlueprintApi require() {
        return find().orElseThrow(() -> new IllegalStateException("Continuity Works compact blueprint provider is not installed"));
    }

    public static synchronized void install(ContinuityWorksCompactBlueprintApi api) {
        Objects.requireNonNull(api, "api");
        if (provider != null && provider != api) {
            throw new IllegalStateException("Continuity Works compact blueprint provider already installed");
        }
        provider = api;
    }
}
