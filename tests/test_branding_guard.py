import tempfile
import unittest
from pathlib import Path

from scripts.verify_branding import (
    find_retired_branding,
    find_retired_source_branding,
    verify_source_branding,
    verify_static_branding,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BrandingGuardTests(unittest.TestCase):
    def test_clean_static_artifact_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<title>Continuity Works</title>", encoding="utf-8")
            (root / "assets").mkdir()
            (root / "assets" / "app.js").write_text("console.log('Continuity Works')", encoding="utf-8")
            verify_static_branding(root)
            self.assertEqual(find_retired_branding(root), [])

    def test_compact_retired_brand_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<title>StructureForge</title>", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                verify_static_branding(root)

    def test_spaced_retired_brand_fails_case_insensitively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.js").write_text("const label = 'structure forge';", encoding="utf-8")
            findings = find_retired_branding(root)
            self.assertTrue(findings)
            with self.assertRaises(RuntimeError):
                verify_static_branding(root)

    def test_structuresmith_retired_brand_fails_case_insensitively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.js").write_text("const generatedBy = 'structuresmith';", encoding="utf-8")
            findings = find_retired_branding(root)
            self.assertTrue(any(brand == "StructureSmith" for _, brand in findings))
            with self.assertRaises(RuntimeError):
                verify_static_branding(root)

    def test_binary_or_unrelated_files_do_not_false_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "asset.bin").write_bytes(b"StructureForge")
            (root / "index.html").write_text("Continuity Works", encoding="utf-8")
            verify_static_branding(root)

    def test_source_guard_catches_backend_docs_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "status.md").write_text("Retired Structure Forge service", encoding="utf-8")
            (root / "service.py").write_text("NAME = 'Continuity Works'", encoding="utf-8")
            findings = find_retired_source_branding(root)
            self.assertTrue(any(path == Path("docs/status.md") for path, _ in findings))
            with self.assertRaises(RuntimeError):
                verify_source_branding(root)

    def test_source_guard_skips_generated_dependencies_and_historical_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("dist", "node_modules", ".git", "releases"):
                path = root / directory
                path.mkdir()
                (path / "ignored.js").write_text("StructureForge", encoding="utf-8")
            (root / "README.md").write_text("Continuity Works", encoding="utf-8")
            verify_source_branding(root)

    def test_active_python_runtime_source_is_structure_forge_clean(self):
        verify_source_branding(PROJECT_ROOT / "src")

    def test_active_frontend_source_is_structure_forge_clean(self):
        verify_source_branding(PROJECT_ROOT / "frontend")

    def test_whole_active_repository_source_is_structure_forge_clean(self):
        """Fail closed if retired Forge branding returns anywhere in active authority."""
        verify_source_branding(PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
