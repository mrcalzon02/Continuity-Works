from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"

HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.util.*;
import java.util.concurrent.*;

public final class DecisionCandidatesHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID id) {
        return new BlueprintRequest(
            id,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "candidate dictionary verification",
            new ConstructionVolume(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            new BlockPosition(8, 8, 8),
            Facing.NORTH,
            List.of(),
            List.of(),
            List.of(),
            Set.of()
        );
    }

    private static final class FakeApi implements ContinuityWorksCompactBlueprintApi {
        @Override public BlueprintApiVersion apiVersion() { return BlueprintApiVersion.CURRENT; }
        @Override public BlueprintVocabulary vocabulary() { return null; }
        @Override public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
            return CompletableFuture.completedFuture(null);
        }
        @Override public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) { return null; }
        @Override public MaterialManifest getCompactMaterials(UUID blueprintId) { return null; }
        @Override public void cancelCompact(UUID requestId) {}
    }

    public static void main(String[] args) {
        require(BlueprintApiVersion.CURRENT.toString().equals("1.9.0"),
            "candidate dictionaries are an additive 1.9 API capability");

        UUID requestId = UUID.fromString("11111111-1111-1111-1111-111111111111");
        BlueprintRequest request = request(requestId);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.State state = api.beginDecision(request);

        final int[] sourceCalls = {0};
        BlueprintDecisionCandidateSource catalog = (req, current, mutator) -> {
            sourceCalls[0]++;
            require(req.requestId().equals(current.requestId()), "source must receive matching request/state identity");
            require(mutator.code().equals("A"), "first dynamic source call must be for archetype");
            return new BlueprintDecisionCandidateSource.CandidateSet(
                "test-catalog-v1",
                List.of("continuityworks:e01_016_test", "continuityworks:e01_017_test")
            );
        };

        BlueprintDecisionCandidates.Dictionary archetypes = api.decisionCandidates(request, state, "A", catalog);
        require(sourceCalls[0] == 1, "dynamic catalog dictionary must invoke its authoritative source exactly once");
        require(archetypes.revision() == 0 && archetypes.requestId().equals(requestId),
            "dictionary must bind to exact request revision");
        require(archetypes.choices().size() == 2, "catalog dictionary must preserve authoritative candidate count");
        require(archetypes.choices().get(0).localCode().equals("0")
                && archetypes.choices().get(1).localCode().equals("1"),
            "dictionary must expose deterministic compact local codes");

        BlueprintDecisionChain.State selected = api.applyCandidateDecision(state, archetypes, "1");
        require(selected.revision() == 1, "candidate application must advance authoritative decision revision");
        require("continuityworks:e01_017_test".equals(selected.selection("A")),
            "local candidate code must resolve to semantic catalog identity before mutation");

        boolean staleRejected = false;
        try {
            api.applyCandidateDecision(selected, archetypes, "0");
        } catch (IllegalStateException expected) {
            staleRejected = true;
        }
        require(staleRejected, "candidate dictionary must reject reuse after decision revision changes");

        BlueprintDecisionCandidates.Dictionary scales = api.decisionCandidates(request, selected, "Z", null);
        require(scales.sourceVersion().equals("cw-fixed-1"), "fixed vocabularies must not require dynamic candidate providers");
        require(scales.choices().stream().map(BlueprintDecisionCandidates.Choice::semanticValue).toList()
                .equals(List.of("S", "M", "L")),
            "fixed dictionary must derive values from authoritative mutator metadata");
        BlueprintDecisionChain.State scaled = api.applyCandidateDecision(selected, scales, "1");
        require("M".equals(scaled.selection("Z")), "fixed local code must resolve through authoritative mutation parser");

        BlueprintDecisionCandidateSource biomeV1 = (req, current, mutator) ->
            new BlueprintDecisionCandidateSource.CandidateSet("profile-v1", List.of("riverbank", "coastal"));
        BlueprintDecisionCandidateSource biomeV2 = (req, current, mutator) ->
            new BlueprintDecisionCandidateSource.CandidateSet("profile-v2", List.of("riverbank", "coastal"));
        BlueprintDecisionCandidates.Dictionary biomes1 = api.decisionCandidates(request, scaled, "B", biomeV1);
        BlueprintDecisionCandidates.Dictionary biomes2 = api.decisionCandidates(request, scaled, "B", biomeV2);
        require(!biomes1.dictionaryId().equals(biomes2.dictionaryId()),
            "source version changes must change dictionary identity even when values match");

        BlueprintDecisionChain.State biomed = api.applyCandidateDecision(scaled, biomes1, "0");
        BlueprintDecisionCandidates.Dictionary family = api.decisionCandidates(request, biomed, "F", null);
        BlueprintDecisionChain.State required = api.applyCandidateDecision(biomed, family, "0");
        require(BlueprintDecisionChain.validate(required).readyToFinalize(),
            "dictionary-selected semantic values must remain compatible with deterministic finalization");
        BlueprintDecisionChain.FinalizedDecision finalized = api.finalizeDecision(required);
        require(finalized.specifications().stream().anyMatch(spec ->
                spec.key().equals("ARCHETYPE") && spec.value().equals("continuityworks:e01_017_test")),
            "finalized specifications must contain semantic value rather than ephemeral local code");

        BlueprintDecisionCandidateSource correctionSource = (req, current, mutator) ->
            new BlueprintDecisionCandidateSource.CandidateSet("profile-v3", List.of("riverbank", "wooded_bank"));
        BlueprintDecisionCandidates.Dictionary correction = api.decisionCandidates(request, required, "B", correctionSource);
        BlueprintDecisionChain.State corrected = api.applyCandidateDecision(required, correction, "1");
        require("wooded_bank".equals(corrected.selection("B")),
            "state-bound dictionaries must permit authoritative correction of an already-selected mutator");

        boolean requestMismatchRejected = false;
        try {
            api.decisionCandidates(request(UUID.randomUUID()), state, "A", catalog);
        } catch (IllegalArgumentException expected) {
            requestMismatchRejected = true;
        }
        require(requestMismatchRejected, "request/state identity mismatch must fail closed");

        boolean dependencyRejected = false;
        try {
            api.decisionCandidates(request, state, "B", biomeV1);
        } catch (IllegalStateException expected) {
            dependencyRejected = true;
        }
        require(dependencyRejected, "dictionary must not bypass mutator dependencies");

        boolean duplicatesRejected = false;
        try {
            new BlueprintDecisionCandidateSource.CandidateSet("bad", List.of("same", "same"));
        } catch (IllegalArgumentException expected) {
            duplicatesRejected = true;
        }
        require(duplicatesRejected, "candidate provider duplicates must fail closed");

        boolean invalidCandidateRejected = false;
        try {
            BlueprintDecisionCandidateSource bad = (req, current, mutator) ->
                new BlueprintDecisionCandidateSource.CandidateSet("bad-wire", List.of("invalid value with spaces"));
            api.decisionCandidates(request, state, "A", bad);
        } catch (IllegalArgumentException expected) {
            invalidCandidateRejected = true;
        }
        require(invalidCandidateRejected, "dynamic candidates must pass the existing authoritative wire validator");

        boolean tamperRejected = false;
        try {
            new BlueprintDecisionCandidates.Dictionary(
                archetypes.protocolVersion(), archetypes.requestId(), archetypes.revision(), archetypes.mutatorCode(),
                archetypes.sourceVersion(), "0000", archetypes.choices());
        } catch (IllegalArgumentException expected) {
            tamperRejected = true;
        }
        require(tamperRejected, "candidate dictionary fingerprint tampering must fail closed");
    }
}
"""


class BlueprintDecisionCandidatesJavaTests(unittest.TestCase):
    def test_candidate_dictionary_compiles_and_executes_as_java_17(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac, "javac is required to verify the Continuity Works Java API")
        self.assertIsNotNone(java, "java is required to execute the candidate-dictionary harness")
        sources = sorted(API_SRC.rglob("*.java"))

        with tempfile.TemporaryDirectory(prefix="continuityworks-candidates-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compile_api = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            self.assertEqual(0, compile_api.returncode,
                "Continuity Works blueprint API failed Java 17 compilation:\n" + compile_api.stdout + compile_api.stderr)

            harness = temp_path / "DecisionCandidatesHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compile_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(0, compile_harness.returncode,
                "Candidate-dictionary harness failed Java 17 compilation:\n" + compile_harness.stdout + compile_harness.stderr)

            execute = subprocess.run(
                [java, "-cp", str(classes), "DecisionCandidatesHarness"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(0, execute.returncode,
                "Candidate-dictionary Java 17 behavioral harness failed:\n" + execute.stdout + execute.stderr)


if __name__ == "__main__":
    unittest.main()
