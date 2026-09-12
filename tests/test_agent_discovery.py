from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from structure_capability.tooling import tool_catalog


ROOT = Path(__file__).resolve().parents[1]
API = "https://continuity-works-mrcalzon02-api.onrender.com"
FRONTEND = "https://mrcalzon02.github.io/Continuity-Works/"
TRUNCATED_HOST = "https://onrender.com"


class AgentDiscoveryContractTests(unittest.TestCase):
    def test_source_tree_is_zero_js_agent_discoverable(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "agent_discoverability.py"),
                "--static-dir",
                str(ROOT),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_builder_emits_complete_agent_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "api.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_pages_discovery.py"),
                    "--output",
                    str(out),
                    "--commit",
                    "test-commit",
                    "--deployment",
                    "candidate",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

            expected_files = (
                out,
                out.parent / "llms.txt",
                out.parent / "ai.json",
                out.parent / ".well-known" / "continuity-works.json",
            )
            for path in expected_files:
                self.assertTrue(path.is_file(), path)

            tool_schema_version = str(tool_catalog()["schema_version"])
            api_doc = json.loads(out.read_text(encoding="utf-8"))
            agent_doc = json.loads((out.parent / "ai.json").read_text(encoding="utf-8"))
            pages_doc = json.loads(
                (out.parent / ".well-known" / "continuity-works.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(api_doc["api"], API)
            self.assertEqual(api_doc["frontend"], FRONTEND)
            self.assertEqual(api_doc["capabilities"], f"{API}/v1/capabilities")
            self.assertEqual(api_doc["frontend_commit"], "test-commit")
            self.assertEqual(api_doc["tool_schema_version"], tool_schema_version)
            self.assertEqual(agent_doc["tool_schema_version"], tool_schema_version)
            self.assertEqual(pages_doc["tool_schema_version"], tool_schema_version)

            combined = "\n".join(path.read_text(encoding="utf-8") for path in expected_files)
            self.assertIn(API, combined)
            self.assertNotIn(TRUNCATED_HOST, combined)


if __name__ == "__main__":
    unittest.main()
