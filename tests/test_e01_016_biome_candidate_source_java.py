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

public final class E01016BiomeCandidateHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request() {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "freshwater_margin")
        );
        return new BlueprintRequest(
            UUID.fromString("16161616-1616-1616-1616-161616161616"),
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "E01-016 authoritative biome candidate verification",
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
        FakeApi api = new FakeApi();
        BlueprintRequest request = request();
        BlueprintDecisionChain.State wateringHole = api.applyDecision(
            api.beginDecision(request), "A=E01-016"
        );
        BlueprintDecisionChain.Mutator biome = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("B"))
            .findFirst().orElseThrow();

        EraStructureBiomeCandidateSource source = new EraStructureBiomeCandidateSource(heroDir);
        BlueprintDecisionCandidateSource.CandidateSet candidates = source.candidates(
            request, wateringHole, biome
        );
        require(candidates.values().equals(List.of(
            "TEMPERATE", "BOREAL", "TUNDRA", "SAVANNA", "ARID", "TROPICAL", "COASTAL_TRANSITION"
        )), "E01-016 must expose its seven explicit environmental profiles in source order");
        require(candidates.sourceVersion().startsWith("cw-hero-biome-sha256:")
            && candidates.sourceVersion().length() == 85,
            "E01-016 source identity must bind to the exact hero-spec snapshot");

        BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(
            request, wateringHole, "B", source
        );
        require(dictionary.choices().size() == 7,
            "E01-016 must expose a seven-choice B dictionary");
        BlueprintDecisionChain.State selected = api.applyCandidateDecision(
            wateringHole, dictionary, "6"
        );
        require("COASTAL_TRANSITION".equals(selected.selection("B")),
            "compact candidate 6 must resolve back to semantic COASTAL_TRANSITION");

        BlueprintDecisionCandidateSource routed =
            ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        BlueprintDecisionCandidates.Dictionary routedDictionary = api.decisionCandidates(
            request, wateringHole, "B", routed
        );
        require(routedDictionary.choices().size() == 7,
            "production routing must expose seven E01-016 BIOME choices");
        require("TEMPERATE".equals(routedDictionary.choices().get(0).semanticValue())
            && "COASTAL_TRANSITION".equals(routedDictionary.choices().get(6).semanticValue()),
            "production routing must preserve E01-016 authoritative source order and semantics");
    }
}
"""


class E01016BiomeCandidateSourceJavaTests(unittest.TestCase):
    def test_e01_016_biome_candidates_and_production_routing(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue((HERO_DIR / "E01-016_WATERING_HOLE_CAMP.md").is_file())
        self.assertTrue(LEDGER.is_file())
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-e01-016-biome-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            harness = temp_path / "E01016BiomeCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "E01016BiomeCandidateHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
