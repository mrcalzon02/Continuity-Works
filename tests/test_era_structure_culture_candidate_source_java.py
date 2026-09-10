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

public final class EraCultureCandidateHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "culture_candidate_verification")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero culture candidate verification",
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
        EraStructureCultureCandidateSource source = new EraStructureCultureCandidateSource(heroDir);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.Mutator culture = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("C"))
            .findFirst().orElseThrow();

        BlueprintRequest butcheryRequest = request(UUID.fromString("11111111-1111-1111-1111-111111111111"));
        BlueprintDecisionChain.State butchery = api.applyDecision(
            api.beginDecision(butcheryRequest), "A=E01-012"
        );
        BlueprintDecisionCandidateSource.CandidateSet candidates = source.candidates(
            butcheryRequest, butchery, culture
        );
        require(candidates.values().equals(List.of(
            "EXPEDIENT_FIELD_DRESSING", "TRANSPORT_FOCUSED", "MARROW_INTENSIVE", "CONSUMPTION_BIASED"
        )), "E01-012 must expose exactly its four explicit supported behavioral culture profiles");
        require(candidates.sourceVersion().startsWith("cw-hero-culture-sha256:")
            && candidates.sourceVersion().length() == 87,
            "culture source version must bind to the exact hero-spec snapshot");

        BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(
            butcheryRequest, butchery, "C", source
        );
        require(dictionary.choices().size() == 4,
            "E01-012 culture dictionary must expose four authoritative choices");
        BlueprintDecisionChain.State selected = api.applyCandidateDecision(butchery, dictionary, "3");
        require("CONSUMPTION_BIASED".equals(selected.selection("C")),
            "compact culture code must resolve back to the authoritative semantic profile");

        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        BlueprintDecisionCandidates.Dictionary routedDictionary = api.decisionCandidates(
            butcheryRequest, butchery, "C", routed
        );
        require(routedDictionary.choices().size() == 4
            && routedDictionary.choices().get(0).semanticValue().equals("EXPEDIENT_FIELD_DRESSING")
            && routedDictionary.choices().get(3).semanticValue().equals("CONSUMPTION_BIASED"),
            "production routing must expose E01-012 authoritative CULTURE candidates");
        BlueprintDecisionChain.State routedSelected = api.applyCandidateDecision(
            butchery, routedDictionary, "3"
        );
        require("CONSUMPTION_BIASED".equals(routedSelected.selection("C")),
            "production-routed compact culture code must resolve to its authoritative semantic profile");

        BlueprintRequest overhangRequest = request(UUID.fromString("55555555-5555-5555-5555-555555555555"));
        BlueprintDecisionChain.State overhang = api.applyDecision(
            api.beginDecision(overhangRequest), "A=E01-001"
        );
        boolean narrativeOnlyRejected = false;
        try {
            source.candidates(overhangRequest, overhang, culture);
        } catch (IllegalStateException expected) {
            narrativeOnlyRejected = expected.getMessage().contains("refusing to infer candidates from prose");
        }
        require(narrativeOnlyRejected,
            "narrative-only culture hooks must fail closed rather than becoming inferred vocabulary");

        boolean routedNarrativeOnlyRejected = false;
        try {
            routed.candidates(overhangRequest, overhang, culture);
        } catch (IllegalStateException expected) {
            routedNarrativeOnlyRejected = expected.getMessage().contains("refusing to infer candidates from prose");
        }
        require(routedNarrativeOnlyRejected,
            "production routing must preserve fail-closed behavior for narrative-only culture hooks");

        boolean missingArchetypeRejected = false;
        try {
            source.candidates(overhangRequest, api.beginDecision(overhangRequest), culture);
        } catch (IllegalStateException expected) {
            missingArchetypeRejected = true;
        }
        require(missingArchetypeRejected, "CULTURE candidate discovery must require archetype A");
    }
}
"""


class EraStructureCultureCandidateSourceJavaTests(unittest.TestCase):
    def test_explicit_culture_profiles_are_authoritative_and_prose_fails_closed(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-culture-candidate-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraCultureCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraCultureCandidateHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
