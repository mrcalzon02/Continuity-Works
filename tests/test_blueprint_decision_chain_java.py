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

public final class DecisionChainHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static boolean hasCode(BlueprintDecisionChain.Step step, String code) {
        return step.nextMutators().stream().anyMatch(mutator -> code.equals(mutator.code()));
    }

    private static final class FakeApi implements ContinuityWorksCompactBlueprintApi {
        @Override
        public BlueprintApiVersion apiVersion() {
            return BlueprintApiVersion.CURRENT;
        }

        @Override
        public BlueprintVocabulary vocabulary() {
            return null;
        }

        @Override
        public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
            return CompletableFuture.completedFuture(null);
        }

        @Override
        public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) {
            return null;
        }

        @Override
        public MaterialManifest getCompactMaterials(UUID blueprintId) {
            return null;
        }

        @Override
        public void cancelCompact(UUID requestId) {
        }
    }

    public static void main(String[] args) {
        require(BlueprintDecisionChain.profile().maxOutputTokens() == 64,
            "tiny inference output ceiling must remain 64 tokens");
        require(BlueprintDecisionChain.profile().stateCarriedAcrossInferences(),
            "decision state must persist outside individual inference output");
        require(BlueprintDecisionChain.profile().principles().contains("generator_builds"),
            "protocol must keep construction in deterministic Continuity Works code");

        UUID requestId = UUID.fromString("11111111-1111-1111-1111-111111111111");
        BlueprintDecisionChain.State state = new BlueprintDecisionChain.State(requestId, 0, Map.of(), false);
        BlueprintDecisionChain.Step first = BlueprintDecisionChain.next(state);
        require(first.nextMutators().size() == 1 && "A".equals(first.nextMutators().get(0).code()),
            "archetype must be the first decision-tree selector");

        state = BlueprintDecisionChain.apply(state,
            "A=continuityworks:e01_017_riverbank_foraging_camp");
        require("continuityworks:e01_017_riverbank_foraging_camp".equals(state.selection("A")),
            "catalog/resource identifiers must preserve case-sensitive wire identity rather than being rewritten");
        BlueprintDecisionChain.Step afterArchetype = BlueprintDecisionChain.next(state);
        require(hasCode(afterArchetype, "Z") && hasCode(afterArchetype, "B") && hasCode(afterArchetype, "F"),
            "archetype selection must unlock scale, biome and family decisions");
        require(!hasCode(afterArchetype, "K") && !hasCode(afterArchetype, "D"),
            "dependent palette/detail decisions must remain locked until prerequisites exist");

        state = BlueprintDecisionChain.apply(state, "Z=M;B=riverbank;F=I");
        require(BlueprintDecisionChain.validate(state).readyToFinalize(),
            "required semantic selections should be sufficient for deterministic finalization");

        state = BlueprintDecisionChain.apply(state, "K=river_gravel;O=N");
        require("river_gravel".equals(state.selection("K")) && "N".equals(state.selection("O")),
            "optional legal mutations must accumulate in state");
        state = BlueprintDecisionChain.apply(state, "B=coastal");
        require(state.selection("K") == null && state.selection("O") == null,
            "changing an upstream mutator must invalidate dependent downstream choices");
        require("M".equals(state.selection("Z")) && "I".equals(state.selection("F")),
            "independent decisions must survive unrelated branch mutation");

        BlueprintDecisionChain.FinalizedDecision finalized = BlueprintDecisionChain.finalizeDecision(state);
        require(finalized.state().finalized(), "finalization must freeze the decision state");
        require(finalized.specifications().stream().anyMatch(spec ->
                "ARCHETYPE".equals(spec.key())
                    && "continuityworks:e01_017_riverbank_foraging_camp".equals(spec.value())
                    && spec.requirement() == BlueprintSpecification.Requirement.REQUIRED),
            "finalization must emit semantic archetype specification without geometry");

        boolean rejectedRaw = false;
        try {
            BlueprintDecisionChain.apply(new BlueprintDecisionChain.State(requestId, 0, Map.of(), false),
                "BLOCK=minecraft:stone");
        } catch (IllegalArgumentException expected) {
            rejectedRaw = true;
        }
        require(rejectedRaw, "raw block mutation must fail closed");

        boolean rejectedScale = false;
        try {
            BlueprintDecisionChain.State archetype = BlueprintDecisionChain.apply(
                new BlueprintDecisionChain.State(requestId, 0, Map.of(), false), "A=E01-017");
            BlueprintDecisionChain.apply(archetype, "Z=XL");
        } catch (IllegalArgumentException expected) {
            rejectedScale = true;
        }
        require(rejectedScale, "fixed mutator vocabularies must fail closed");

        ContinuityWorksDecisionAuthorityAdapter authority =
            new ContinuityWorksDecisionAuthorityAdapter(new FakeApi());
        require(authority.apiVersion().equals(BlueprintApiVersion.CURRENT),
            "authority adapter must report its configured provider API version");
        require(authority.decisionProfile().protocolVersion().equals(BlueprintDecisionChain.PROTOCOL_VERSION),
            "authority adapter must delegate protocol discovery to the configured provider");

        BlueprintDecisionChain.State transportState =
            new BlueprintDecisionChain.State(requestId, 0, Map.of(), false);
        transportState = authority.applyDecision(transportState, 0,
            "A=continuityworks:e01_017_riverbank_foraging_camp");
        require(transportState.revision() == 1,
            "authority adapter must return the provider's revised immutable decision state");

        boolean rejectedStale = false;
        try {
            authority.applyDecision(transportState, 0, "Z=M");
        } catch (IllegalStateException expected) {
            rejectedStale = true;
        }
        require(rejectedStale,
            "authority adapter must reject late inference output against a stale revision");

        transportState = authority.applyDecision(transportState, 1, "Z=M;B=riverbank;F=I");
        require(authority.validateDecision(transportState).readyToFinalize(),
            "authority adapter must delegate semantic validation rather than reimplement it");
        require(authority.finalizeDecision(transportState).state().finalized(),
            "authority adapter must delegate finalization to the authoritative provider");
    }
}
"""


class BlueprintDecisionChainJavaTests(unittest.TestCase):
    def test_decision_chain_compiles_and_executes_as_java_17(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac, "javac is required to verify the Continuity Works Java API")
        self.assertIsNotNone(java, "java is required to execute the decision-chain harness")
        sources = sorted(API_SRC.rglob("*.java"))

        with tempfile.TemporaryDirectory(prefix="continuityworks-decision-javac-") as temp:
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

            harness = temp_path / "DecisionChainHarness.java"
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
                "Decision-chain harness failed Java 17 compilation:\n" + compile_harness.stdout + compile_harness.stderr)

            execute = subprocess.run(
                [java, "-cp", str(classes), "DecisionChainHarness"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(0, execute.returncode,
                "Decision-chain Java 17 behavioral harness failed:\n" + execute.stdout + execute.stderr)


if __name__ == "__main__":
    unittest.main()
