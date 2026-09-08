package io.continuityworks.api.blueprint;

import java.util.Objects;
import java.util.Optional;

public final class ContinuityWorksSelectionServices {
    private static volatile ContinuityWorksSelectionApi provider;

    private ContinuityWorksSelectionServices() {}

    public static Optional<ContinuityWorksSelectionApi> find() {
        return Optional.ofNullable(provider);
    }

    public static ContinuityWorksSelectionApi require() {
        return find().orElseThrow(() -> new IllegalStateException("Continuity Works selection provider is not installed"));
    }

    public static synchronized void install(ContinuityWorksSelectionApi api) {
        Objects.requireNonNull(api, "api");
        if (provider != null && provider != api) {
            throw new IllegalStateException("Continuity Works selection provider already installed");
        }
        provider = api;
    }
}
