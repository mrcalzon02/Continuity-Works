from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"


class BlueprintApiJavaCompileTests(unittest.TestCase):
    def test_blueprint_api_compiles_as_java_17(self) -> None:
        javac = shutil.which("javac")
        self.assertIsNotNone(javac, "javac is required to verify the published Continuity Works Java API")
        sources = sorted(API_SRC.rglob("*.java"))
        self.assertGreaterEqual(len(sources), 20, "blueprint API source set is unexpectedly incomplete")
        with tempfile.TemporaryDirectory(prefix="continuityworks-api-javac-") as output:
            result = subprocess.run(
                [javac, "--release", "17", "-d", output, *map(str, sources)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        self.assertEqual(
            0,
            result.returncode,
            "Continuity Works blueprint API failed Java 17 compilation:\n" + result.stdout + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
