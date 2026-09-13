from pathlib import Path
import unittest


class RenderBlueprintContractTests(unittest.TestCase):
    def test_canonical_render_subdomain_is_explicitly_enabled(self):
        repo = Path(__file__).resolve().parents[1]
        blueprint = (repo / "render.yaml").read_text(encoding="utf-8")

        self.assertIn("name: continuity-works-mrcalzon02-api", blueprint)
        self.assertIn("healthCheckPath: /v1/health", blueprint)
        self.assertIn("renderSubdomainPolicy: enabled", blueprint)
        self.assertIn(
            "value: https://continuity-works-mrcalzon02-api.onrender.com",
            blueprint,
        )


if __name__ == "__main__":
    unittest.main()
