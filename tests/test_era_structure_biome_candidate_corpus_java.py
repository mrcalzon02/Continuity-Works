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

public final class EraStructureBiomeCandidateCorpusHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(String archetypeId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.nameUUIDFromBytes(("volume:" + archetypeId).getBytes(java.nio.charset.StandardCharsets.UTF_8)),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "corpus_reconciliation")
        );
        return new BlueprintRequest(
            UUID.nameUUIDFromBytes(("request:" + archetypeId).getBytes(java.nio.charset.StandardCharsets.UTF_8)),
            UUID.nameUUIDFromBytes(("project:" + archetypeId).getBytes(java.nio.charset.StandardCharsets.UTF_8)),
            UUID.nameUUIDFromBytes(("world:" + archetypeId).getBytes(java.nio.charset.StandardCharsets.UTF_8)),
            "minecraft:overworld",
            archetypeId + " corpus biome candidate verification",
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
        EraStructureBiomeCandidateSource direct = new EraStructureBiomeCandidateSource(heroDir);
        BlueprintDecisionCandidateSource routed =
            ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        BlueprintDecisionChain.Mutator biome = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("B"))
            .findFirst().orElseThrow();

        for (int index = 1; index <= 17; index++) {
            String archetypeId = String.format("E01-%03d", index);
            BlueprintRequest request = request(archetypeId);
            BlueprintDecisionChain.State selectedArchetype = api.applyDecision(
                api.beginDecision(request), "A=" + archetypeId
            );

            BlueprintDecisionCandidateSource.CandidateSet directCandidates = direct.candidates(
                request, selectedArchetype, biome
            );
            require(!directCandidates.values().isEmpty(),
                archetypeId + " must expose at least one explicit B candidate");
            require(new LinkedHashSet<>(directCandidates.values()).size() == directCandidates.values().size(),
                archetypeId + " B candidates must be unique in authoritative source order");
            require(directCandidates.sourceVersion().startsWith("cw-hero-biome-sha256:")
                && directCandidates.sourceVersion().length() == 85,
                archetypeId + " B source identity must bind to the exact hero-spec snapshot");

            BlueprintDecisionCandidates.Dictionary routedDictionary = api.decisionCandidates(
                request, selectedArchetype, "B", routed
            );
            List<String> routedValues = routedDictionary.choices().stream()
                .map(BlueprintDecisionCandidates.Choice::semanticValue)
                .toList();
            require(routedValues.equals(directCandidates.values()),
                archetypeId + " production B routing must exactly preserve direct authoritative candidates");

            String finalCode = Integer.toString(routedDictionary.choices().size() - 1, 36).toUpperCase(Locale.ROOT);
            BlueprintDecisionChain.State selectedBiome = api.applyCandidateDecision(
                selectedArchetype, routedDictionary, finalCode
            );
            require(directCandidates.values().get(directCandidates.values().size() - 1)
                    .equals(selectedBiome.selection("B")),
                archetypeId + " compact B candidate must resolve back to its authoritative semantic value");
        }
    }
}
"""


class EraStructureBiomeCandidateCorpusJavaTests(unittest.TestCase):
    def test_all_eligible_hero_specs_expose_production_b_candidates(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(LEDGER.is_file())
        for index in range(1, 18):
            self.assertEqual(
                1,
                len(list(HERO_DIR.glob(f"E01-{index:03d}_*.md"))),
                f"E01-{index:03d} must have exactly one authoritative hero specification",
            )

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-biome-corpus-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraStructureBiomeCandidateCorpusHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraStructureBiomeCandidateCorpusHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
