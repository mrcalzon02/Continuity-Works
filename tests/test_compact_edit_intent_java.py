from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java"

HARNESS = r"""
import io.continuityworks.api.blueprint.*;
import java.util.*;

public final class CompactEditIntentHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static CompactBlueprintPlan source() {
        UUID id = UUID.fromString("11111111-1111-1111-1111-111111111111");
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(99, 99, 99)), 9L, Map.of());
        List<PaletteEntry> palette = List.of(
            new PaletteEntry("stone", "minecraft:stone", "minecraft:stone", Map.of()),
            new PaletteEntry("glass", "minecraft:glass", "minecraft:glass", Map.of()));
        List<CompactBlueprintPrimitive> primitives = List.of(
            CompactBlueprintPrimitive.fillBox(0, new BlockPosition(0, 0, 0), new BlockPosition(2, 0, 4), "stone"),
            CompactBlueprintPrimitive.block(1, new BlockPosition(0, 1, 0), "glass"));
        return new CompactBlueprintPlan(
            id, "test/v1", "SHA-256", "source-hash", "minecraft:overworld", volume,
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(2, 1, 4)),
            new BlockPosition(10, 10, 10), Facing.NORTH, List.of(), palette,
            new MaterialManifest(id, Map.of(), Map.of("minecraft:stone", 1000L, "minecraft:glass", 1000L), Map.of()),
            primitives, List.of(), new WorkloadEstimate(16, 0, 0, 16),
            new PreviewMetadata("Harness", "Intent harness", "test", Map.of()), 1.0, List.of());
    }

    private static void rejects(String text, String label) {
        boolean rejected = false;
        try { CompactEditIntentCodec.parse(text); }
        catch (IllegalArgumentException expected) { rejected = true; }
        require(rejected, label);
    }

    public static void main(String[] args) {
        CompactBlueprintPlan source = source();

        String rotateText = "TASK=EDIT\nACTION=ROTATE\nTURN=90";
        CompactEditIntent rotateIntent = CompactEditIntentCodec.parse(rotateText);
        require(rotateIntent.action() == CompactEditIntent.Action.ROTATE, "ROTATE action must parse");
        require(rotateIntent.rotation() == CompactBlueprintModifier.Rotation.CLOCKWISE_90, "TURN=90 must resolve clockwise");
        CompactEditIntent roundTrip = CompactEditIntentCodec.parse(CompactEditIntentCodec.encode(rotateIntent));
        require(roundTrip.equals(rotateIntent), "semantic edit encode/parse must round-trip");

        CompactBlueprintPlan symbolicRotate = CompactBlueprintEditExecutor.parseAndApply(source, rotateText);
        CompactBlueprintPlan directRotate = CompactBlueprintModifier.rotate(source, CompactBlueprintModifier.Rotation.CLOCKWISE_90);
        require(symbolicRotate.integrityHash().equals(directRotate.integrityHash()),
            "symbolic ROTATE must resolve to the deterministic direct modifier");

        CompactBlueprintPlan symbolicPalette = CompactBlueprintEditExecutor.parseAndApply(
            source, "ACTION=PALETTE_REMAP\nFROM=GLASS\nTO=STONE");
        require("stone".equals(symbolicPalette.primitives().get(1).paletteKey()),
            "palette identifiers must resolve case-insensitively against existing plan keys");

        CompactBlueprintModule pillar = new CompactBlueprintModule(
            "pillar",
            List.of(CompactBlueprintPrimitive.line(0, new BlockPosition(0, 0, 0), new BlockPosition(0, 2, 0), "stone")));
        CompactBlueprintModuleResolver modules = CompactBlueprintModuleResolver.fromMap(Map.of("PILLAR", pillar));
        String repeatText = "TASK=EDIT\nACTION=REPEAT\nMODULE=pillar\nCOUNT=2\nFIRST_X=5\nSTEP_X=3";
        CompactBlueprintPlan symbolicRepeat = CompactBlueprintEditExecutor.parseAndApply(source, repeatText, modules);
        CompactBlueprintPlan directRepeat = CompactBlueprintModifier.repeat(
            source, pillar, 2, new BlockPosition(5, 0, 0), new BlockPosition(3, 0, 0));
        require(symbolicRepeat.integrityHash().equals(directRepeat.integrityHash()),
            "symbolic REPEAT must resolve only through the trusted module resolver");
        require(symbolicRepeat.primitives().size() == 4, "symbolic repeat must remain compact primitive composition");

        boolean missingModule = false;
        try { CompactBlueprintEditExecutor.parseAndApply(source, repeatText); }
        catch (IllegalArgumentException expected) { missingModule = true; }
        require(missingModule, "module edits without a trusted module resolver must fail closed");

        rejects("ACTION=TRANSLATE\nBLOCK=minecraft:stone", "raw BLOCK field must be rejected");
        rejects("ACTION=ROTATE\nTURN=90\nBOGUS=1", "unknown action field must be rejected");
        rejects("ACTION=TRANSLATE\nDX=4097", "translation beyond semantic transport bound must be rejected");
        rejects("ACTION=REPEAT\nMODULE=pillar\nCOUNT=2", "multi-copy repeat with zero step must be rejected");
        rejects("TASK=BLUEPRINT\nACTION=MIRROR\nAXIS=X", "non-EDIT task must be rejected");
    }
}
"""


class CompactEditIntentJavaTests(unittest.TestCase):
    def test_symbolic_compact_edit_boundary_executes_as_java_17(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac)
        self.assertIsNotNone(java)
        sources = sorted(API_SRC.rglob("*.java"))
        with tempfile.TemporaryDirectory(prefix="continuityworks-edit-intent-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            harness = temp_path / "CompactEditIntentHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compiled = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources), str(harness)],
                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            executed = subprocess.run(
                [java, "-cp", str(classes), "CompactEditIntentHarness"],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(0, executed.returncode, executed.stdout + executed.stderr)


if __name__ == "__main__":
    unittest.main()
