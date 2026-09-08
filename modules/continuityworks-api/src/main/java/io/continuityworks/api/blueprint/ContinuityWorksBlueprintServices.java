package io.continuityworks.api.blueprint;

import java.util.Objects;
import java.util.Optional;

public final class ContinuityWorksBlueprintServices {
    private static volatile ContinuityWorksBlueprintApi provider;

    private ContinuityWorksBlueprintServices() {}

    public static Optional<ContinuityWorksBlueprintApi> find() {
        return Optional.ofNullable(provider);
    }

    public static ContinuityWorksBlueprintApi require() {
        return find().orElseThrow(() -> new IllegalStateException("Continuity Works blueprint provider is not installed"));
    }

    public static synchronized void install(ContinuityWorksBlueprintApi api) {
        Objects.requireNonNull(api, "api");
        if (provider != null && provider != api) {
            throw new IllegalStateException("Continuity Works blueprint provider already installed");
        }
        provider = api;
    }
}
