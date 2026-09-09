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

    /** Discover the tiny-inference decision protocol, token ceiling, mutator graph and fixed vocabularies. */
    default BlueprintDecisionChain.Profile decisionProfile() {
        return BlueprintDecisionChain.profile();
    }

    /** Start a deterministic decision state. Rich state is carried outside the model output budget. */
    default BlueprintDecisionChain.State beginDecision(BlueprintRequest request) {
        return BlueprintDecisionChain.begin(request);
    }

    /** Return only currently dependency-valid semantic mutators for the next bounded inference. */
    default BlueprintDecisionChain.Step nextDecision(BlueprintDecisionChain.State state) {
        return BlueprintDecisionChain.next(state);
    }

    /** Apply a compact mutator response such as A=E01-017 or Z=M;B=RIVERBANK. */
    default BlueprintDecisionChain.State applyDecision(
        BlueprintDecisionChain.State state,
        String encodedMutations
    ) {
        return BlueprintDecisionChain.apply(state, encodedMutations);
    }

    /** Build a state-bound compact choice dictionary from fixed or authoritative dynamic candidates. */
    default BlueprintDecisionCandidates.Dictionary decisionCandidates(
        BlueprintRequest request,
        BlueprintDecisionChain.State state,
        String mutatorCode,
        BlueprintDecisionCandidateSource source
    ) {
        return BlueprintDecisionCandidates.create(request, state, mutatorCode, source);
    }

    /** Resolve one compact dictionary code back to its semantic value and apply it authoritatively. */
    default BlueprintDecisionChain.State applyCandidateDecision(
        BlueprintDecisionChain.State state,
        BlueprintDecisionCandidates.Dictionary dictionary,
        String localChoiceCode
    ) {
        return BlueprintDecisionCandidates.apply(state, dictionary, localChoiceCode);
    }

    /** Validate accumulated semantic decisions without generating or mutating world geometry. */
    default BlueprintDecisionChain.Validation validateDecision(BlueprintDecisionChain.State state) {
        return BlueprintDecisionChain.validate(state);
    }

    /** Freeze a valid decision state into semantic BlueprintSpecifications for deterministic generation. */
    default BlueprintDecisionChain.FinalizedDecision finalizeDecision(BlueprintDecisionChain.State state) {
        return BlueprintDecisionChain.finalizeDecision(state);
    }

    default long streamPlacements(CompactBlueprintPlan plan, CompactPlacementSink sink) {
        return CompactBlueprintMaterializer.forEachPlacement(plan, sink);
    }

    /** Apply a non-module semantic edit such as translate, rotate, mirror, or palette remap. */
    default CompactBlueprintPlan applyEdit(CompactBlueprintPlan plan, String encodedIntent) {
        return CompactBlueprintEditExecutor.parseAndApply(plan, encodedIntent);
    }

    /** Apply any semantic edit, resolving COMPOSE/REPEAT only from trusted pre-authored modules. */
    default CompactBlueprintPlan applyEdit(
        CompactBlueprintPlan plan,
        String encodedIntent,
        CompactBlueprintModuleResolver modules
    ) {
        return CompactBlueprintEditExecutor.parseAndApply(plan, encodedIntent, modules);
    }
}
