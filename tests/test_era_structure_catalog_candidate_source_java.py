from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"
LEDGER = ROOT / "docs" / "era_structure_hero" / "ERA_STRUCTURE_HERO_LEDGER.md"

HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public final class EraCatalogCandidateHarness {
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
            "authoritative era catalog candidate verification",
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
        Path ledgerPath = Path.of(args[0]);
        EraStructureCatalogCandidateSource source = EraStructureCatalogCandidateSource.fromHeroLedger(ledgerPath);

        require(source.catalogIds().size() == 17,
            "live authoritative ledger must expose exactly the 17 materialized hero-spec entries currently present");
        require(source.catalogIds().get(0).equals("E01-001"), "catalog ordering must preserve ledger order");
        require(source.catalogIds().get(16).equals("E01-017"), "latest materialized catalog ID must be E01-017");
        require(!source.catalogIds().contains("E01-018"),
            "unmaterialized placeholder E01-018 must not become an inference candidate");
        require(source.sourceVersion().startsWith("cw-era-ledger-sha256:") && source.sourceVersion().length() == 85,
            "source version must be content-derived from the exact authority snapshot");

        UUID requestId = UUID.fromString("11111111-1111-1111-1111-111111111111");
        BlueprintRequest request = request(requestId);
        FakeApi api = new FakeApi();
        BlueprintDecisionChain.State state = api.beginDecision(request);
        BlueprintDecisionCandidates.Dictionary dictionary = api.decisionCandidates(request, state, "A", source);

        require(dictionary.choices().size() == 17, "dictionary must expose all and only selectable ledger IDs");
        require(dictionary.choices().get(0).semanticValue().equals("E01-001"),
            "dictionary semantic values must remain authoritative catalog IDs");
        require(dictionary.choices().get(16).semanticValue().equals("E01-017"),
            "dictionary must include the current last materialized catalog ID");
        require(dictionary.sourceVersion().equals(source.sourceVersion()),
            "dictionary must bind to the ledger content fingerprint");

        BlueprintDecisionChain.State selected = api.applyCandidateDecision(state, dictionary, "G");
        require(selected.revision() == 1, "compact selection must advance decision revision");
        require("E01-017".equals(selected.selection("A")),
            "base-36 local code G must resolve back to the seventeenth semantic catalog ID");

        boolean wrongMutatorRejected = false;
        try {
            BlueprintDecisionChain.Mutator biome = BlueprintDecisionChain.profile().mutators().stream()
                .filter(candidate -> candidate.code().equals("B"))
                .findFirst().orElseThrow();
            source.candidates(request, selected, biome);
        } catch (IllegalArgumentException expected) {
            wrongMutatorRejected = true;
        }
        require(wrongMutatorRejected, "catalog source must not answer archetype-profile mutators");

        String ledgerText = Files.readString(ledgerPath);
        EraStructureCatalogCandidateSource changed = EraStructureCatalogCandidateSource.fromHeroLedger(
            new StringReader(ledgerText + System.lineSeparator())
        );
        require(changed.catalogIds().equals(source.catalogIds()),
            "non-semantic ledger byte change may preserve candidate IDs");
        require(!changed.sourceVersion().equals(source.sourceVersion()),
            "any authority snapshot byte change must invalidate the source version");

        boolean emptyRejected = false;
        try {
            EraStructureCatalogCandidateSource.fromHeroLedger(new StringReader(
                "# Empty ledger\n| Catalog | Era | Archetype | Stage 1 |\n|---|---|---|---|\n"
            ));
        } catch (IllegalArgumentException expected) {
            emptyRejected = true;
        }
        require(emptyRejected, "ledger with no materialized hero-spec rows must fail closed");
    }
}
"""


class EraStructureCatalogCandidateSourceJavaTests(unittest.TestCase):
    def test_live_hero_ledger_drives_structure_catalog_candidates(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(LEDGER.is_file())
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-era-catalog-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            harness = temp_path / "EraCatalogCandidateHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, compiled_harness.returncode, compiled_harness.stdout + compiled_harness.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "EraCatalogCandidateHarness", str(LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
