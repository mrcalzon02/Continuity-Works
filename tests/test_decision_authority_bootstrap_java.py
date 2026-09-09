from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"
HERO_LEDGER = ROOT / "docs" / "era_structure_hero" / "ERA_STRUCTURE_HERO_LEDGER.md"

HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.net.*;
import java.net.http.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public final class DecisionAuthorityBootstrapHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
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

    private static HttpResponse<String> send(HttpClient client, int port, String method, String path, String body)
        throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder(
            URI.create("http://127.0.0.1:" + port + path)
        ).header("Accept", "application/json");
        if ("GET".equals(method)) builder.GET();
        else builder.header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(body));
        return client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
    }

    public static void main(String[] args) throws Exception {
        Path ledger = Path.of(args[0]);
        require(Files.isRegularFile(ledger), "authoritative hero ledger must exist");
        try (ContinuityWorksDecisionAuthorityHttpServer server =
                 ContinuityWorksDecisionAuthorityBootstrap.fromEraStructureHeroLedger(
                     new FakeApi(), ledger, new InetSocketAddress("127.0.0.1", 0))) {
            require(server.dynamicCandidateSourceConfigured(),
                "production bootstrap must configure the authoritative dynamic candidate source");
            server.start();
            int port = server.address().getPort();
            HttpClient client = HttpClient.newHttpClient();

            HttpResponse<String> profile = send(client, port, "GET", "/v1/blueprints/decision/profile", "");
            require(profile.statusCode() == 200, "profile request must succeed");
            require(profile.body().contains("\"dynamicCandidateSourceConfigured\":true"),
                "profile must advertise configured dynamic candidates");

            String requestId = "11111111-1111-1111-1111-111111111111";
            String begin = "{\"request\":{" +
                "\"requestId\":\"" + requestId + "\"," +
                "\"companionUuid\":\"22222222-2222-2222-2222-222222222222\"," +
                "\"ownerUuid\":\"33333333-3333-3333-3333-333333333333\"," +
                "\"dimensionId\":\"minecraft:overworld\"," +
                "\"buildPurpose\":\"authoritative era catalog bootstrap verification\"," +
                "\"constructionVolume\":{" +
                    "\"volumeId\":\"44444444-4444-4444-4444-444444444444\"," +
                    "\"bounds\":{\"min\":{\"x\":0,\"y\":0,\"z\":0},\"max\":{\"x\":31,\"y\":31,\"z\":31}}," +
                    "\"snapshotEpoch\":1,\"attributes\":{}}," +
                "\"preferredOrigin\":{\"x\":8,\"y\":8,\"z\":8}," +
                "\"preferredFacing\":\"NORTH\"," +
                "\"specifications\":[],\"availableMaterials\":[],\"candidateSites\":[],\"permittedStyles\":[]}}";
            HttpResponse<String> begun = send(client, port, "POST", "/v1/blueprints/decision/begin", begin);
            require(begun.statusCode() == 200, "decision begin must succeed");

            String state = "{\"requestId\":\"" + requestId + "\",\"revision\":0,\"selections\":{},\"finalized\":false}";
            HttpResponse<String> candidates = send(
                client, port, "POST", "/v1/blueprints/decision/candidates",
                "{\"state\":" + state + ",\"mutator_code\":\"A\"}"
            );
            require(candidates.statusCode() == 200, "catalog candidate request must succeed");
            String body = candidates.body();
            require(body.contains("\"semanticValue\":\"E01-001\""),
                "bootstrap must expose first materialized hero catalog entry");
            require(body.contains("\"semanticValue\":\"E01-017\""),
                "bootstrap must expose latest materialized hero catalog entry");
            require(!body.contains("\"semanticValue\":\"E01-018\""),
                "unmaterialized catalog row must remain unavailable to inference");
            require(body.contains("\"sourceVersion\":\"cw-era-ledger-sha256:"),
                "dictionary must carry the content-derived era-ledger source version");
        }
    }
}
"""


class DecisionAuthorityBootstrapJavaTests(unittest.TestCase):
    def test_bootstrap_serves_authoritative_era_catalog_candidates(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        self.assertTrue(HERO_LEDGER.is_file())
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-authority-bootstrap-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            harness = temp_path / "DecisionAuthorityBootstrapHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "DecisionAuthorityBootstrapHarness", str(HERO_LEDGER)],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
