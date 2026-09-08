package io.continuityworks.api.blueprint;

import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Resolves pre-authored compact modules by semantic identifier; never synthesizes raw geometry from model text. */
@FunctionalInterface
public interface CompactBlueprintModuleResolver {
    Optional<CompactBlueprintModule> resolve(String moduleId);

    static CompactBlueprintModuleResolver none() {
        return moduleId -> Optional.empty();
    }

    static CompactBlueprintModuleResolver fromMap(Map<String, CompactBlueprintModule> modules) {
        Map<String, CompactBlueprintModule> snapshot = Map.copyOf(Objects.requireNonNull(modules, "modules"));
        return moduleId -> {
            Objects.requireNonNull(moduleId, "moduleId");
            CompactBlueprintModule exact = snapshot.get(moduleId);
            if (exact != null) return Optional.of(exact);
            CompactBlueprintModule match = null;
            for (Map.Entry<String, CompactBlueprintModule> entry : snapshot.entrySet()) {
                if (!entry.getKey().equalsIgnoreCase(moduleId) && !entry.getValue().moduleId().equalsIgnoreCase(moduleId)) continue;
                if (match != null && match != entry.getValue()) {
                    throw new IllegalArgumentException("Ambiguous compact module identifier: " + moduleId);
                }
                match = entry.getValue();
            }
            return Optional.ofNullable(match);
        };
    }
}
