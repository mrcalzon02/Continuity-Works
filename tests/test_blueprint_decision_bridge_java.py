from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from structure_capability import StructureCapability
from structure_capability.server import Handler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"

SERVER_HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

public final class DecisionAuthorityServerHarness {
    private static final class FakeApi implements ContinuityWorksCompactBlueprintApi {
        @Override
        public BlueprintApiVersion apiVersion() {
            return BlueprintApiVersion.CURRENT;
        }

        @Override
        public BlueprintVocabulary vocabulary() {
            return null;
        }

        @Override
        public CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request) {
            return CompletableFuture.completedFuture(null);
        }

        @Override
        public ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context) {
            return null;
        }

        @Override
        public MaterialManifest getCompactMaterials(UUID blueprintId) {
            return null;
        }

        @Override
        public void cancelCompact(UUID requestId) {
        }
    }

    public static void main(String[] args) throws Exception {
        try (ContinuityWorksDecisionAuthorityHttpServer server =
                 new ContinuityWorksDecisionAuthorityHttpServer(
                     new FakeApi(), new InetSocketAddress("127.0.0.1", 0))) {
            server.start();
            System.out.println("PORT=" + server.address().getPort());
            System.out.flush();
            System.in.read();
        }
    }
}
"""


class DecisionBridgeJavaIntegrationTests(unittest.TestCase):
    def request(self, base_url: str, method: str, path: str, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(f"{base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=10) as response:
                raw = response.read()
                return response.status, json.loads(raw) if raw else None
        except HTTPError as error:
            raw = error.read()
            return error.code, json.loads(raw) if raw else None

    def test_python_bridge_executes_against_real_java_authority(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac, "javac is required to verify the Java decision authority")
        self.assertIsNotNone(java, "java is required to execute the Java decision authority")
        sources = sorted(API_SRC.rglob("*.java"))

        with tempfile.TemporaryDirectory(prefix="continuityworks-decision-bridge-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            harness = temp_path / "DecisionAuthorityServerHarness.java"
            harness.write_text(textwrap.dedent(SERVER_HARNESS), encoding="utf-8")

            compile_process = subprocess.run(
                [
                    javac,
                    "--release",
                    "17",
                    "-d",
                    str(classes),
                    *map(str, sources),
                    str(harness),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            self.assertEqual(
                0,
                compile_process.returncode,
                "Continuity Works Java decision authority failed compilation:\n"
                + compile_process.stdout
                + compile_process.stderr,
            )

            java_process = subprocess.Popen(
                [java, "-cp", str(classes), "DecisionAuthorityServerHarness"],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            bridge = None
            bridge_thread = None
            previous_authority = os.environ.get("CONTINUITY_WORKS_DECISION_AUTHORITY_URL")
            try:
                self.assertIsNotNone(java_process.stdout)
                line = java_process.stdout.readline().strip()
                self.assertTrue(line.startswith("PORT="), f"unexpected Java authority startup output: {line!r}")
                authority_port = int(line.split("=", 1)[1])
                os.environ["CONTINUITY_WORKS_DECISION_AUTHORITY_URL"] = f"http://127.0.0.1:{authority_port}"

                class BridgeHandler(Handler):
                    pass

                BridgeHandler.capability = StructureCapability(temp_path / "python-project")
                bridge = ThreadingHTTPServer(("127.0.0.1", 0), BridgeHandler)
                bridge_thread = threading.Thread(target=bridge.serve_forever, daemon=True)
                bridge_thread.start()
                base_url = f"http://127.0.0.1:{bridge.server_address[1]}"

                status, profile = self.request(base_url, "GET", "/v1/blueprints/decision/profile")
                self.assertEqual(status, 200, profile)
                self.assertEqual(profile["protocolVersion"], "cw-decision-1")
                self.assertEqual(profile["apiVersion"], "1.8.0")
                self.assertEqual(profile["maxOutputTokens"], 64)

                request_id = "11111111-1111-1111-1111-111111111111"
                begin_body = {
                    "request": {
                        "requestId": request_id,
                        "companionUuid": "22222222-2222-2222-2222-222222222222",
                        "ownerUuid": "33333333-3333-3333-3333-333333333333",
                        "dimensionId": "minecraft:overworld",
                        "buildPurpose": "foraging camp",
                        "constructionVolume": {
                            "volumeId": "44444444-4444-4444-4444-444444444444",
                            "bounds": {
                                "min": {"x": 0, "y": 60, "z": 0},
                                "max": {"x": 63, "y": 127, "z": 63},
                            },
                            "snapshotEpoch": 1,
                            "attributes": {"biome": "riverbank"},
                        },
                        "preferredOrigin": {"x": 16, "y": 64, "z": 16},
                        "preferredFacing": "NORTH",
                        "specifications": [],
                        "availableMaterials": [],
                        "candidateSites": [],
                        "permittedStyles": [],
                    }
                }
                status, begun = self.request(base_url, "POST", "/v1/blueprints/decision/begin", begin_body)
                self.assertEqual(status, 200, begun)
                state0 = begun["state"]
                self.assertEqual(state0["requestId"], request_id)
                self.assertEqual(state0["revision"], 0)

                status, next_step = self.request(
                    base_url, "POST", "/v1/blueprints/decision/next", {"state": state0}
                )
                self.assertEqual(status, 200, next_step)
                self.assertEqual([item["code"] for item in next_step["nextMutators"]], ["A"])

                status, applied = self.request(
                    base_url,
                    "POST",
                    "/v1/blueprints/decision/apply",
                    {
                        "state": state0,
                        "encoded_mutations": "A=continuityworks:e01_017_riverbank_foraging_camp",
                    },
                )
                self.assertEqual(status, 200, applied)
                state1 = applied["state"]
                self.assertEqual(state1["revision"], 1)

                status, stale = self.request(
                    base_url,
                    "POST",
                    "/v1/blueprints/decision/apply",
                    {"state": state0, "encoded_mutations": "A=E01-017"},
                )
                self.assertEqual(status, 409, stale)
                self.assertEqual(stale["error"], "stale_decision_state")

                status, applied_required = self.request(
                    base_url,
                    "POST",
                    "/v1/blueprints/decision/apply",
                    {
                        "state": state1,
                        "encoded_mutations": "Z=M;B=riverbank;F=I",
                    },
                )
                self.assertEqual(status, 200, applied_required)
                state2 = applied_required["state"]
                self.assertEqual(state2["revision"], 2)

                status, validation = self.request(
                    base_url, "POST", "/v1/blueprints/decision/validate", {"state": state2}
                )
                self.assertEqual(status, 200, validation)
                self.assertTrue(validation["valid"])
                self.assertTrue(validation["readyToFinalize"])

                status, finalized = self.request(
                    base_url, "POST", "/v1/blueprints/decision/finalize", {"state": state2}
                )
                self.assertEqual(status, 200, finalized)
                self.assertTrue(finalized["state"]["finalized"])
                self.assertEqual(finalized["state"]["revision"], 3)
                self.assertTrue(
                    any(
                        item["key"] == "ARCHETYPE"
                        and item["value"] == "continuityworks:e01_017_riverbank_foraging_camp"
                        for item in finalized["specifications"]
                    )
                )
            finally:
                if bridge is not None:
                    bridge.shutdown()
                    bridge.server_close()
                if bridge_thread is not None:
                    bridge_thread.join(timeout=2)
                if previous_authority is None:
                    os.environ.pop("CONTINUITY_WORKS_DECISION_AUTHORITY_URL", None)
                else:
                    os.environ["CONTINUITY_WORKS_DECISION_AUTHORITY_URL"] = previous_authority
                if java_process.stdin is not None:
                    java_process.stdin.close()
                try:
                    java_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    java_process.kill()
                    java_process.wait(timeout=5)
                stderr = java_process.stderr.read() if java_process.stderr is not None else ""
                self.assertEqual(0, java_process.returncode, "Java authority failed:\n" + stderr)


if __name__ == "__main__":
    unittest.main()
