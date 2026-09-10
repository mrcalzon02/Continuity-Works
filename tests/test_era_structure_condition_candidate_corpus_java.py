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

public final class EraConditionCorpusHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "condition_corpus_verification")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero condition corpus verification",
            volume,
            new BlockPosition(8, 8, 8),
            Facing.NORTH,
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
        EraStructureConditionCandidateSource direct = new EraStructureConditionCandidateSource(heroDir);
        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.Mutator condition = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("Q"))
            .findFirst().orElseThrow();

        Map<String, List<String>> expected = new LinkedHashMap<>();
        expected.put("E01-001", List.of(
            "ACTIVE_RECENTLY_OCCUPIED", "TEMPORARILY_VACANT", "REPEATEDLY_OCCUPIED",
            "ABANDONED", "PARTIALLY_COLLAPSED", "BURIED_ARCHAEOLOGICAL", "REPURPOSED"
        ));
        expected.put("E01-002", List.of(
            "ACTIVE_RECENTLY_OCCUPIED", "TEMPORARILY_VACANT", "REPEATEDLY_OCCUPIED",
            "ABANDONED", "PARTIALLY_COLLAPSED", "HEAVILY_SILTED_BURIED",
            "ANIMAL_REOCCUPIED", "LATER_ERA_REPURPOSED"
        ));
        expected.put("E01-003", List.of(
            "ACTIVE_EMERGENCY_REFUGE", "TEMPORARILY_VACANT", "REPEATED_REFUGE", "ABANDONED",
            "ENTRANCE_BLOCKED_LEGACY_REFUGE", "PARTIALLY_COLLAPSED", "FLOOD_DAMAGED",
            "ANIMAL_REOCCUPIED", "LATER_ERA_REPURPOSED"
        ));
        expected.put("E01-004", List.of(
            "ACTIVE_INTACT", "MAINTAINED_REPEATEDLY_REUSED", "TEMPORARILY_VACANT", "WEATHER_DAMAGED",
            "PARTIALLY_COLLAPSED", "ABANDONED_DECAYED", "ARCHAEOLOGICAL_TRACE", "LATER_ERA_REPURPOSED"
        ));
        expected.put("E01-005", List.of(
            "ACTIVE_NEWLY_BUILT", "MAINTAINED_REPEATEDLY_USED", "TEMPORARILY_VACANT", "WEATHER_DAMAGED",
            "PARTIALLY_COLLAPSED", "ABANDONED", "ARCHAEOLOGICAL_TRACE", "LATER_ERA_REPURPOSED"
        ));

        int ordinal = 0;
        for (Map.Entry<String, List<String>> entry : expected.entrySet()) {
            BlueprintRequest request = request(new UUID(0L, 200L + ordinal++));
            BlueprintDecisionChain.State state = api.applyDecision(api.beginDecision(request), "A=" + entry.getKey());

            BlueprintDecisionCandidateSource.CandidateSet directSet = direct.candidates(request, state, condition);
            require(directSet.values().equals(entry.getValue()),
                entry.getKey() + " direct condition candidates must match its explicit hero-spec vocabulary");
            require(directSet.sourceVersion().startsWith("cw-hero-condition-sha256:")
                && directSet.sourceVersion().length() == 89,
                entry.getKey() + " condition authority must bind to the exact hero-spec bytes");

            BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(request, state, "Q", routed);
            require(dictionary.choices().size() == entry.getValue().size(),
                entry.getKey() + " production condition dictionary size mismatch");
            for (int i = 0; i < entry.getValue().size(); i++) {
                require(dictionary.choices().get(i).semanticValue().equals(entry.getValue().get(i)),
                    entry.getKey() + " production condition order mismatch at " + i);
            }
            int last = entry.getValue().size() - 1;
            BlueprintDecisionChain.State selected = api.applyCandidateDecision(state, dictionary, Integer.toString(last));
            require(entry.getValue().get(last).equals(selected.selection("Q")),
                entry.getKey() + " compact condition code must resolve to the authoritative semantic value");
        }
    }
}
"""


class EraStructureConditionCandidateCorpusJavaTests(unittest.TestCase):
    def test_explicit_condition_vocabularies_are_stable_through_production_routing(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-condition-corpus-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraConditionCorpusHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraConditionCorpusHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
