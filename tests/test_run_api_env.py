import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_API = PROJECT_ROOT / "scripts" / "run_api.py"


class RunApiEnvironmentTests(unittest.TestCase):
    def _run_entrypoint(self, env):
        with patch.dict(os.environ, env, clear=True), patch(
            "structure_capability.server.serve"
        ) as serve:
            runpy.run_path(str(RUN_API), run_name="__main__")
        serve.assert_called_once()
        return serve.call_args.kwargs

    def test_canonical_environment_takes_precedence(self):
        kwargs = self._run_entrypoint(
            {
                "CONTINUITY_WORKS_PROJECT_ROOT": "/canonical/project",
                "STRUCTURESMITH_PROJECT_ROOT": "/legacy/project",
                "CONTINUITY_WORKS_HOST": "127.0.0.2",
                "HOST": "127.0.0.3",
                "CONTINUITY_WORKS_PORT": "9191",
                "PORT": "9292",
            }
        )
        self.assertEqual(kwargs["project_root"], "/canonical/project")
        self.assertEqual(kwargs["host"], "127.0.0.2")
        self.assertEqual(kwargs["port"], 9191)

    def test_compatibility_environment_remains_supported(self):
        kwargs = self._run_entrypoint(
            {
                "STRUCTURESMITH_PROJECT_ROOT": "/legacy/project",
                "HOST": "127.0.0.3",
                "PORT": "9292",
            }
        )
        self.assertEqual(kwargs["project_root"], "/legacy/project")
        self.assertEqual(kwargs["host"], "127.0.0.3")
        self.assertEqual(kwargs["port"], 9292)

    def test_defaults_are_unchanged(self):
        kwargs = self._run_entrypoint({})
        self.assertEqual(kwargs["project_root"], ".")
        self.assertEqual(kwargs["host"], "0.0.0.0")
        self.assertEqual(kwargs["port"], 8787)

    def test_canonical_port_must_be_a_valid_tcp_port(self):
        for invalid_port in ("0", "65536", "not-a-port"):
            with self.subTest(invalid_port=invalid_port), self.assertRaisesRegex(
                ValueError, "API port must be an integer from 1 through 65535"
            ):
                self._run_entrypoint({"CONTINUITY_WORKS_PORT": invalid_port})

    def test_compatibility_port_must_be_a_valid_tcp_port(self):
        for invalid_port in ("-1", "70000", ""):
            with self.subTest(invalid_port=invalid_port), self.assertRaisesRegex(
                ValueError, "API port must be an integer from 1 through 65535"
            ):
                self._run_entrypoint({"PORT": invalid_port})


if __name__ == "__main__":
    unittest.main()
