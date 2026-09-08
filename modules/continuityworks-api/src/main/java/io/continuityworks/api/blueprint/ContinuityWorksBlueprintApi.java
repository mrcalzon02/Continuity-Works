package io.continuityworks.api.blueprint;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;

public interface ContinuityWorksBlueprintApi {
    BlueprintApiVersion apiVersion();

    BlueprintVocabulary vocabulary();

    CompletableFuture<BlueprintProposal> generate(BlueprintRequest request);

    ValidationResult validate(BlueprintProposal proposal, BlueprintContext context);

    MaterialManifest getMaterials(UUID blueprintId);

    void cancel(UUID requestId);
}
