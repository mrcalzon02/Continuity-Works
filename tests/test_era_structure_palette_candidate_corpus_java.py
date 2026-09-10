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

public final class EraPaletteCorpusHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "palette_corpus_verification")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero palette corpus verification",
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
        EraStructurePaletteCandidateSource direct = new EraStructurePaletteCandidateSource(heroDir);
        BlueprintDecisionCandidateSource routed = ContinuityWorksDecisionAuthorityBootstrap.productionCandidateSource(ledger);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.Mutator palette = BlueprintDecisionChain.profile().mutators().stream()
            .filter(candidate -> candidate.code().equals("K"))
            .findFirst().orElseThrow();

        Map<String, List<String>> expected = new LinkedHashMap<>();
        expected.put("E01-001", List.of(
            "GEOLOGICAL_PALETTE", "ORGANIC_PALETTE", "HUMAN_MADE_PALETTE_RESTRICTIONS"
        ));
        expected.put("E01-002", List.of(
            "GEOLOGY", "CARRIED_STONE", "ORGANIC_MATERIALS", "FORBIDDEN_BASE_MATERIALS"
        ));
        expected.put("E01-003", List.of(
            "GEOLOGICAL_STRUCTURE", "CARRIED_MATERIAL", "HUMAN_REARRANGEMENT"
        ));
        expected.put("E01-004", List.of(
            "STRUCTURAL_ORGANICS", "COVER", "STONE", "GROUND"
        ));
        expected.put("E01-005", List.of(
            "STRUCTURAL_MEMBERS", "INFILL", "GROUND_TREATMENT", "FORBIDDEN_BASE_MATERIALS"
        ));
        expected.put("E01-006", List.of(
            "HIDE_MEMBRANE", "SUPPORTS", "ANCHORS_AND_WEIGHTS", "GROUND_TREATMENT"
        ));
        expected.put("E01-007", List.of(
            "HEARTH_SUBSTRATE", "CONTAINMENT_STONES", "FUEL", "RESIDUE", "FORBIDDEN_BASE_MATERIALS"
        ));
        expected.put("E01-008", List.of(
            "HEARTH_MATERIALS", "FUEL", "ACTIVITY_RESIDUES", "TEMPORARY_SHELTER_MATERIALS", "FORBIDDEN_MATERIALS"
        ));
        expected.put("E01-009", List.of(
            "STRUCTURAL_TERRAIN", "TOOLSTONE_PALETTE", "HAMMERSTONE_PALETTE", "ORGANIC_PALETTE", "FORBIDDEN_BASE_MATERIALS"
        ));
        expected.put("E01-011", List.of(
            "HOST_ROCK", "QUARTZITE_ROLE_SOURCE", "COARSE_SPOIL_REJECT", "COMPACTED_GROUND",
            "HAMMERSTONE_ROLE_DURABLE_BLOCK", "OPTIONAL_WEATHERING_MATERIAL_FOR_ABANDONED_CONDITIONS"
        ));

        int ordinal = 0;
        for (Map.Entry<String, List<String>> entry : expected.entrySet()) {
            BlueprintRequest request = request(new UUID(0L, 300L + ordinal++));
            BlueprintDecisionChain.State state = api.applyDecision(
                api.beginDecision(request), "A=" + entry.getKey() + ";B=TEMPERATE_FOREST"
            );

            BlueprintDecisionCandidateSource.CandidateSet directSet = direct.candidates(request, state, palette);
            require(directSet.values().equals(entry.getValue()),
                entry.getKey() + " direct palette candidates must match its explicit hero-spec vocabulary");
            require(directSet.sourceVersion().startsWith("cw-hero-palette-sha256:")
                && directSet.sourceVersion().length() == 87,
                entry.getKey() + " palette authority must bind to the exact hero-spec bytes");

            BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(request, state, "K", routed);
            require(dictionary.choices().size() == entry.getValue().size(),
                entry.getKey() + " production palette dictionary size mismatch");
            for (int i = 0; i < entry.getValue().size(); i++) {
                require(dictionary.choices().get(i).semanticValue().equals(entry.getValue().get(i)),
                    entry.getKey() + " production palette order mismatch at " + i);
            }
            int last = entry.getValue().size() - 1;
            BlueprintDecisionChain.State selected = api.applyCandidateDecision(
                state, dictionary, Integer.toString(last)
            );
            require(entry.getValue().get(last).equals(selected.selection("K")),
                entry.getKey() + " compact palette code must resolve to the authoritative semantic value");
        }

        BlueprintRequest narrativeRequest = request(new UUID(0L, 399L));
        BlueprintDecisionChain.State narrativeState = api.applyDecision(
            api.beginDecision(narrativeRequest), "A=E01-010;B=TEMPERATE_BOREAL"
        );
        boolean directRefused = false;
        try {
            direct.candidates(narrativeRequest, narrativeState, palette);
        } catch (IllegalStateException expectedFailure) {
            directRefused = expectedFailure.getMessage().contains("refusing to infer candidates from prose");
        }
        require(directRefused, "E01-010 narrative-only palette guidance must fail closed in the direct source");

        boolean routedRefused = false;
        try {
            api.decisionCandidates(narrativeRequest, narrativeState, "K", routed);
        } catch (IllegalStateException expectedFailure) {
            routedRefused = expectedFailure.getMessage().contains("refusing to infer candidates from prose");
        }
        require(routedRefused, "E01-010 narrative-only palette guidance must fail closed in production routing");
    }
}
"""


class EraStructurePaletteCandidateCorpusJavaTests(unittest.TestCase):
    def test_explicit_palette_vocabularies_are_stable_through_production_routing(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-palette-corpus-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraPaletteCorpusHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraPaletteCorpusHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
