package io.continuityworks.api.blueprint;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/** Optional compact planning capability for local consumers that want primitive geometry instead of per-block lists. */
public interface ContinuityWorksCompactBlueprintApi {
    BlueprintApiVersion apiVersion();
    BlueprintVocabulary vocabulary();
    CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request);
    ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context);
    MaterialManifest getCompactMaterials(UUID blueprintId);
    void cancelCompact(UUID requestId);

    default long streamPlacements(CompactBlueprintPlan plan, CompactPlacementSink sink) {
        return CompactBlueprintMaterializer.forEachPlacement(plan, sink);
    }
}
