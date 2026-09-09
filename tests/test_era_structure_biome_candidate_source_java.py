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

public final class EraBiomeCandidateHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "riverbank")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero biome candidate verification",
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

    private static BlueprintDecisionChain.State selectArchetype(
        FakeApi api, BlueprintRequest request, String archetype
    ) {
        return api.applyDecision(api.beginDecision(request), "A=" + archetype);
    }

    public static void main(String[] args) throws Exception {
        Path heroDir = Path.of(args[0]);
        Path ledger = Path.of(args[1]);
        EraStructureBiomeCandidateSource biomeSource = new EraStructureBiomeCandidateSource(heroDir);
        FakeApi api = new FakeApi();

        BlueprintDecisionChain.Mutator biome = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("B"))
            .findFirst().orElseThrow();

        UUID requestId = UUID.fromString("11111111-1111-1111-1111-111111111111");
        BlueprintRequest request = request(requestId);
        BlueprintDecisionChain.State overhang = selectArchetype(api, request, "E01-001");
        BlueprintDecisionCandidateSource.CandidateSet overhangSet = biomeSource.candidates(request, overhang, biome);
        require(overhangSet.values().equals(List.of(
            "TEMPERATE_FOREST", "BOREAL_COLD", "TUNDRA_ALPINE", "SAVANNA_DRY_GRASSLAND",
            "ARID_DESERT", "TROPICAL_HUMID", "COASTAL"
        )), "E01-001 explicit biome headings must become ordered canonical semantic candidates");
        require(overhangSet.sourceVersion().startsWith("cw-hero-biome-sha256:")
            && overhangSet.sourceVersion().length() == 85,
            "biome source version must bind to the exact hero-spec snapshot");

        BlueprintDecisionCandidates.Dictionary overhangDictionary = api.decisionCandidates(
            request, overhang, "B", biomeSource
        );
        require(overhangDictionary.choices().size() == 7, "E01-001 dictionary must expose seven explicit profiles");
        BlueprintDecisionChain.State selectedBiome = api.applyCandidateDecision(overhang, overhangDictionary, "1");
        require("BOREAL_COLD".equals(selectedBiome.selection("B")),
            "local biome code must resolve back to the authoritative semantic profile");

        BlueprintRequest riverRequest = request(UUID.fromString("55555555-5555-5555-5555-555555555555"));
        BlueprintDecisionChain.State river = selectArchetype(api, riverRequest, "E01-017");
        BlueprintDecisionCandidateSource.CandidateSet riverSet = biomeSource.candidates(riverRequest, river, biome);
        require(riverSet.values().equals(List.of(
            "TEMPERATE", "BOREAL", "TUNDRA", "SAVANNA", "ARID", "TROPICAL", "COASTAL_TRANSITION"
        )), "E01-017 explicit bold biome labels must remain ordered semantic candidates");

        BlueprintRequest procurementRequest = request(UUID.fromString("66666666-6666-6666-6666-666666666666"));
        BlueprintDecisionChain.State procurement = selectArchetype(api, procurementRequest, "E01-010");
        BlueprintDecisionCandidateSource.CandidateSet procurementSet = biomeSource.candidates(
            procurementRequest, procurement, biome
        );
        require(procurementSet.values().equals(List.of(
            "TEMPERATE_BOREAL", "TUNDRA_ALPINE", "SAVANNA_ARID", "TROPICAL", "COASTAL_RIVERINE"
        )), "E01-010 normalized headings must expose only the five pre-existing environmental groupings");
        BlueprintDecisionCandidates.Dictionary procurementDictionary = api.decisionCandidates(
            procurementRequest, procurement, "B", biomeSource
        );
        require(procurementDictionary.choices().size() == 5,
            "E01-010 dictionary must expose five normalized authoritative profiles");
        BlueprintDecisionChain.State selectedProcurementBiome = api.applyCandidateDecision(
            procurement, procurementDictionary, "4"
        );
        require("COASTAL_RIVERINE".equals(selectedProcurementBiome.selection("B")),
            "E01-010 compact candidate must resolve back to the normalized authoritative semantic profile");

        BlueprintRequest quarryRequest = request(UUID.fromString("77777777-7777-7777-7777-777777777777"));
        BlueprintDecisionChain.State quarry = selectArchetype(api, quarryRequest, "E01-011");
        BlueprintDecisionCandidateSource.CandidateSet quarrySet = biomeSource.candidates(
            quarryRequest, quarry, biome
        );
        require(quarrySet.values().equals(List.of(
            "TEMPERATE", "BOREAL", "TUNDRA", "SAVANNA", "ARID", "TROPICAL", "COASTAL"
        )), "E01-011 normalized headings must expose exactly its seven pre-existing environmental categories");
        BlueprintDecisionCandidates.Dictionary quarryDictionary = api.decisionCandidates(
            quarryRequest, quarry, "B", biomeSource
        );
        require(quarryDictionary.choices().size() == 7,
            "E01-011 dictionary must expose seven normalized authoritative profiles");
        BlueprintDecisionChain.State selectedQuarryBiome = api.applyCandidateDecision(
            quarry, quarryDictionary, "6"
        );
        require("COASTAL".equals(selectedQuarryBiome.selection("B")),
            "E01-011 compact candidate must resolve back to the normalized authoritative semantic profile");

        boolean missingArchetypeRejected = false;
        try {
            biomeSource.candidates(request, api.beginDecision(request), biome);
        } catch (IllegalStateException expected) {
            missingArchetypeRejected = true;
        }
        require(missingArchetypeRejected, "BIOME candidate discovery must require archetype A");

        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        BlueprintDecisionCandidates.Dictionary routedA = api.decisionCandidates(
            request, api.beginDecision(request), "A", routed
        );
        require(routedA.choices().size() == 17, "production routing must preserve the live catalog authority");
        BlueprintDecisionCandidates.Dictionary routedB = api.decisionCandidates(request, overhang, "B", routed);
        require(routedB.choices().get(0).semanticValue().equals("TEMPERATE_FOREST"),
            "production routing must expose the selected hero spec's BIOME authority");
        BlueprintDecisionCandidates.Dictionary routedProcurementB = api.decisionCandidates(
            procurementRequest, procurement, "B", routed
        );
        require(routedProcurementB.choices().get(0).semanticValue().equals("TEMPERATE_BOREAL")
            && routedProcurementB.choices().size() == 5,
            "production routing must expose E01-010 normalized BIOME authority");
        BlueprintDecisionCandidates.Dictionary routedQuarryB = api.decisionCandidates(
            quarryRequest, quarry, "B", routed
        );
        require(routedQuarryB.choices().get(0).semanticValue().equals("TEMPERATE")
            && routedQuarryB.choices().get(6).semanticValue().equals("COASTAL")
            && routedQuarryB.choices().size() == 7,
            "production routing must expose E01-011 normalized BIOME authority");

        BlueprintDecisionChain.Mutator culture = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("C"))
            .findFirst().orElseThrow();
        boolean unconfiguredRejected = false;
        try {
            routed.candidates(request, overhang, culture);
        } catch (IllegalArgumentException expected) {
            unconfiguredRejected = true;
        }
        require(unconfiguredRejected, "unconfigured future profile mutators must fail closed");

        Path changedDir = Files.createTempDirectory("cw-biome-source-change-");
        try {
            String sourceName = "E01-001_ROCK_OVERHANG_CAMP.md";
            String original = Files.readString(heroDir.resolve(sourceName));
            Files.writeString(changedDir.resolve(sourceName), original + System.lineSeparator());
            EraStructureBiomeCandidateSource changed = new EraStructureBiomeCandidateSource(changedDir);
            BlueprintDecisionCandidateSource.CandidateSet changedSet = changed.candidates(request, overhang, biome);
            require(changedSet.values().equals(overhangSet.values()),
                "non-semantic hero-spec byte change may preserve explicit candidates");
            require(!changedSet.sourceVersion().equals(overhangSet.sourceVersion()),
                "any hero-spec snapshot byte change must invalidate source identity");
        } finally {
            try (var paths = Files.walk(changedDir)) {
                paths.sorted(Comparator.reverseOrder()).forEach(path -> {
                    try { Files.deleteIfExists(path); } catch (Exception ignored) {}
                });
            }
        }
    }
}
"""


class EraStructureBiomeCandidateSourceJavaTests(unittest.TestCase):
    def test_live_hero_specs_drive_biome_candidates_without_prose_guessing(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-era-biome-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            harness = temp_path / "EraBiomeCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "EraBiomeCandidateHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
