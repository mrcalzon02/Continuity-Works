import tempfile
import unittest
from pathlib import Path

from scripts.verify_branding import find_retired_branding, verify_static_branding


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


if __name__ == "__main__":
    unittest.main()
