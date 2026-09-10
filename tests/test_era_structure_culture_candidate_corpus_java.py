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

public final class EraCultureCorpusHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "culture_corpus_verification")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero culture corpus verification",
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
        EraStructureCultureCandidateSource direct = new EraStructureCultureCandidateSource(heroDir);
        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.Mutator culture = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("C"))
            .findFirst().orElseThrow();

        Map<String, List<String>> expected = new LinkedHashMap<>();
        expected.put("E01-012", List.of(
            "EXPEDIENT_FIELD_DRESSING", "TRANSPORT_FOCUSED", "MARROW_INTENSIVE", "CONSUMPTION_BIASED"
        ));
        expected.put("E01-013", List.of(
            "COOPERATIVE_DISARTICULATION", "MARROW_INTENSIVE", "TRANSPORT_PRIORITY", "HIDE_RETENTION"
        ));
        expected.put("E01-014", List.of(
            "MARROW_INTENSIVE", "SINGLE_STATION_REUSE", "DISTRIBUTED_PERCUSSION", "CLEAN_STAGING_PRIORITY"
        ));
        expected.put("E01-015", List.of(
            "IMMEDIATE_CONSUMPTION", "DISTRIBUTED_EXTRACTION", "INTENSIVE_CLEANING", "REPEATED_USE"
        ));

        int ordinal = 0;
        for (Map.Entry<String, List<String>> entry : expected.entrySet()) {
            BlueprintRequest request = request(new UUID(0L, 100L + ordinal++));
            BlueprintDecisionChain.State state = api.applyDecision(api.beginDecision(request), "A=" + entry.getKey());

            BlueprintDecisionCandidateSource.CandidateSet directSet = direct.candidates(request, state, culture);
            require(directSet.values().equals(entry.getValue()),
                entry.getKey() + " direct culture candidates must match its explicit hero-spec vocabulary");
            require(directSet.sourceVersion().startsWith("cw-hero-culture-sha256:")
                && directSet.sourceVersion().length() == 87,
                entry.getKey() + " culture authority must bind to the exact hero-spec bytes");

            BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(request, state, "C", routed);
            require(dictionary.choices().size() == entry.getValue().size(),
                entry.getKey() + " production culture dictionary size mismatch");
            for (int i = 0; i < entry.getValue().size(); i++) {
                require(dictionary.choices().get(i).semanticValue().equals(entry.getValue().get(i)),
                    entry.getKey() + " production culture order mismatch at " + i);
            }
            int last = entry.getValue().size() - 1;
            BlueprintDecisionChain.State selected = api.applyCandidateDecision(state, dictionary, Integer.toString(last));
            require(entry.getValue().get(last).equals(selected.selection("C")),
                entry.getKey() + " compact culture code must resolve to the authoritative semantic value");
        }

        BlueprintRequest narrativeRequest = request(new UUID(0L, 999L));
        BlueprintDecisionChain.State narrative = api.applyDecision(
            api.beginDecision(narrativeRequest), "A=E01-001"
        );
        boolean rejected = false;
        try {
            routed.candidates(narrativeRequest, narrative, culture);
        } catch (IllegalStateException expectedFailure) {
            rejected = expectedFailure.getMessage().contains("refusing to infer candidates from prose");
        }
        require(rejected, "narrative-only culture hooks must remain fail-closed in production routing");
    }
}
"""


class EraStructureCultureCandidateCorpusJavaTests(unittest.TestCase):
    def test_explicit_culture_vocabularies_are_stable_through_production_routing(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-culture-corpus-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraCultureCorpusHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraCultureCorpusHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
