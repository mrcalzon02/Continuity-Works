from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java" / "io" / "continuityworks" / "api" / "blueprint"


class CompactEditIntentSourceTests(unittest.TestCase):
    def read(self, name: str) -> str:
        path = API / name
        self.assertTrue(path.is_file(), f"missing compact edit source: {path}")
        return path.read_text(encoding="utf-8")

    def test_inference_surface_is_semantic_only(self) -> None:
        intent = self.read("CompactEditIntent.java")
        codec = self.read("CompactEditIntentCodec.java")
        self.assertIn("TRANSLATE, ROTATE, MIRROR, PALETTE_REMAP, COMPOSE, REPEAT", intent)
        self.assertIn("MAX_TEXT_CHARS = 1_024", codec)
        self.assertIn("MAX_FIELDS = 12", codec)
        self.assertIn("MAX_ABSOLUTE_DELTA = 4_096", codec)
        for forbidden in (
            '"BLOCK"', '"BLOCKS"', '"BLOCK_STATE"', '"NBT"', '"SNBT"',
            '"COMMAND"', '"SETBLOCK"', '"PLACEMENT"', '"OPERATION"', '"PRIMITIVE"',
        ):
            self.assertIn(forbidden, codec)
        self.assertNotIn("blockState", intent)
        self.assertNotIn("CompactBlueprintPrimitive primitive", intent)

    def test_module_edits_require_trusted_resolution(self) -> None:
        resolver = self.read("CompactBlueprintModuleResolver.java")
        executor = self.read("CompactBlueprintEditExecutor.java")
        self.assertIn("Optional<CompactBlueprintModule> resolve", resolver)
        self.assertIn("CompactBlueprintModuleResolver.none()", executor)
        self.assertIn("Unknown pre-authored compact module", executor)
        self.assertIn("requireModule(modules, intent.moduleId())", executor)
        self.assertIn("CompactBlueprintModifier.compose", executor)
        self.assertIn("CompactBlueprintModifier.repeat", executor)

    def test_compact_api_exposes_default_symbolic_edit_path(self) -> None:
        api = self.read("ContinuityWorksCompactBlueprintApi.java")
        self.assertEqual(2, api.count("default CompactBlueprintPlan applyEdit("))
        self.assertIn("CompactBlueprintEditExecutor.parseAndApply", api)
        self.assertIn("CompactBlueprintModuleResolver modules", api)

    def test_codec_is_action_specific_and_fail_closed(self) -> None:
        codec = self.read("CompactEditIntentCodec.java")
        for field in ("DX", "TURN", "AXIS", "FROM", "TO", "MODULE", "COUNT", "FIRST_X", "STEP_X"):
            self.assertIn(f'"{field}"', codec)
        self.assertIn("requireOnly(fields", codec)
        self.assertIn("Raw placement/geometry field is forbidden", codec)
        self.assertIn("ACTION is required", codec)
        self.assertIn("TASK must be EDIT", codec)


if __name__ == "__main__":
    unittest.main()
