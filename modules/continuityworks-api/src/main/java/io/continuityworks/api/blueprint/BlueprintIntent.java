package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

/** Compact semantic output from a tiny inference layer; contains no world mutation instructions. */
public record BlueprintIntent(
    String task,
    String purpose,
    String preferredSiteId,
    List<BlueprintSpecification> specifications
) {
    public BlueprintIntent {
        Objects.requireNonNull(task, "task");
        Objects.requireNonNull(purpose, "purpose");
        if (!"BLUEPRINT".equals(task)) throw new IllegalArgumentException("task must be BLUEPRINT");
        if (purpose.isBlank()) throw new IllegalArgumentException("purpose must not be blank");
        preferredSiteId = preferredSiteId == null ? "" : preferredSiteId;
        specifications = List.copyOf(specifications == null ? List.of() : specifications);
    }

    public Optional<BlueprintSpecification> specification(String key) {
        String normalized = BlueprintIntentCodec.normalizeKey(key);
        return specifications.stream().filter(spec -> spec.key().equals(normalized)).findFirst();
    }
}
