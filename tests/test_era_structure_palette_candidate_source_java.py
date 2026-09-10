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

public final class EraPaletteCandidateHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static BlueprintRequest request(UUID requestId) {
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("44444444-4444-4444-4444-444444444444"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(31, 31, 31)),
            1L,
            Map.of("biome", "palette_candidate_verification")
        );
        return new BlueprintRequest(
            requestId,
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            UUID.fromString("33333333-3333-3333-3333-333333333333"),
            "minecraft:overworld",
            "authoritative hero palette candidate verification",
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

        BlueprintRequest shelterRequest = request(UUID.fromString("11111111-1111-1111-1111-111111111111"));
        BlueprintDecisionChain.State shelter = api.applyDecision(api.beginDecision(shelterRequest),
            "A=E01-004;B=TEMPERATE_FOREST");
        BlueprintDecisionCandidateSource.CandidateSet shelterSet = direct.candidates(shelterRequest, shelter, palette);
        require(shelterSet.values().equals(List.of("STRUCTURAL_ORGANICS", "COVER", "STONE", "GROUND")),
            "E01-004 palette candidates must be only its explicit material-palette headings");
        require(shelterSet.sourceVersion().startsWith("cw-hero-palette-sha256:")
            && shelterSet.sourceVersion().length() == 87,
            "palette source version must bind to the exact hero-spec bytes");

        BlueprintDecisionCandidates.Dictionary routedK = api.decisionCandidates(shelterRequest, shelter, "K", routed);
        require(routedK.choices().size() == 4,
            "production routing must expose four explicit E01-004 palette candidates");
        require(routedK.choices().get(0).semanticValue().equals("STRUCTURAL_ORGANICS")
            && routedK.choices().get(3).semanticValue().equals("GROUND"),
            "production palette routing must preserve authoritative order");
        BlueprintDecisionChain.State selected = api.applyCandidateDecision(shelter, routedK, "1");
        require("COVER".equals(selected.selection("K")),
            "compact palette code must resolve to the authoritative semantic value");

        BlueprintRequest missingBiomeRequest = request(UUID.fromString("55555555-5555-5555-5555-555555555555"));
        BlueprintDecisionChain.State missingBiome = api.applyDecision(api.beginDecision(missingBiomeRequest), "A=E01-004");
        boolean missingBiomeRejected = false;
        try {
            direct.candidates(missingBiomeRequest, missingBiome, palette);
        } catch (IllegalArgumentException expected) {
            missingBiomeRejected = true;
        }
        require(missingBiomeRejected, "PALETTE candidate discovery must require biome B as well as archetype A");

        BlueprintRequest proseOnlyRequest = request(UUID.fromString("66666666-6666-6666-6666-666666666666"));
        BlueprintDecisionChain.State proseOnly = api.applyDecision(api.beginDecision(proseOnlyRequest),
            "A=E01-010;B=TEMPERATE");
        boolean proseOnlyRejected = false;
        try {
            direct.candidates(proseOnlyRequest, proseOnly, palette);
        } catch (IllegalStateException expected) {
            proseOnlyRejected = true;
        }
        require(proseOnlyRejected,
            "ordinary material prose/bullets must fail closed rather than becoming guessed palette candidates");
    }
}
"""


class EraStructurePaletteCandidateSourceJavaTests(unittest.TestCase):
    def test_explicit_palette_authority_routes_and_prose_only_specs_fail_closed(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_DIR.is_dir())
        self.assertTrue(LEDGER.is_file())

        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-palette-candidate-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)

            harness = temp_path / "EraPaletteCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)

            executed = subprocess.run(
                [java, "-cp", str(classes), "EraPaletteCandidateHarness", str(HERO_DIR), str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
