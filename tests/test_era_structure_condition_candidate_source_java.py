from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"
HERO_DIR = ROOT / "docs" / "era_structure_hero"
LEDGER = HERO_DIR / "ERA_STRUCTURE_HERO_LEDGER.md"

HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public final class EraConditionCandidateHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request() {
        return new BlueprintRequest(
            UUID.fromString("11111111-1111-1111-1111-111111111111"),
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld", "authoritative condition candidate verification",
            new ConstructionVolume(
                UUID.fromString("44444444-4444-4444-4444-444444444444"),
                new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
                1L, Map.of("biome", "condition_candidate_verification")
            ),
            new BlockPosition(8, 8, 8), Facing.NORTH,
            List.of(), List.of(), List.of(), Set.of()
        );
    }

    private static final class FakeApi implements ContinuityWorksCompactBlueprintApi {
        public BlueprintApiVersion apiVersion() { return BlueprintApiVersion.CURRENT; }
        public BlueprintVocabulary vocabulary() { return null; }
        public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
            return CompletableFuture.completedFuture(null);
        }
        public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) { return null; }
        public MaterialManifest getCompactMaterials(UUID blueprintId) { return null; }
        public void cancelCompact(UUID requestId) {}
    }

    public static void main(String[] args) throws Exception {
        Path heroDir = Path.of(args[0]);
        Path ledger = Path.of(args[1]);
        BlueprintRequest request = request();
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.State state = api.applyDecision(api.beginDecision(request), "A=E01-012");
        BlueprintDecisionChain.Mutator condition = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("Q"))
            .findFirst().orElseThrow();

        EraStructureConditionCandidateSource source = new EraStructureConditionCandidateSource(heroDir);
        BlueprintDecisionCandidateSource.CandidateSet candidates = source.candidates(request, state, condition);
        List<String> expected = List.of(
            "ACTIVE", "RECENT", "REPEATED", "ABANDONED", "WEATHERED",
            "SCAVENGER_REWORKED", "SEDIMENT_REWORKED", "REPURPOSED"
        );
        require(candidates.values().equals(expected),
            "E01-012 must expose exactly its explicit ordered condition variants");
        require(candidates.sourceVersion().startsWith("cw-hero-condition-sha256:"),
            "condition source version must bind to the exact hero-spec snapshot");

        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(request, state, "Q", routed);
        require(dictionary.choices().stream().map(BlueprintDecisionCandidates.Choice::semanticValue).toList().equals(expected),
            "production routing must expose the authoritative E01-012 condition order");
        BlueprintDecisionChain.State selected = api.applyCandidateDecision(state, dictionary, "5");
        require("SCAVENGER_REWORKED".equals(selected.selection("Q")),
            "compact condition code must resolve back to the authoritative semantic condition");

        boolean missingArchetypeRejected = false;
        try {
            source.candidates(request, api.beginDecision(request), condition);
        } catch (IllegalStateException expectedFailure) {
            missingArchetypeRejected = true;
        }
        require(missingArchetypeRejected, "CONDITION candidate discovery must require archetype A");
    }
}
"""


class EraStructureConditionCandidateSourceJavaTests(unittest.TestCase):
    def test_explicit_condition_profiles_route_through_production_authority(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-condition-candidate-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            harness = temp_path / "EraConditionCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "EraConditionCandidateHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
