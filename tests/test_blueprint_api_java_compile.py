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

public final class CompactModifierHarness {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        UUID sourceId = UUID.fromString("11111111-1111-1111-1111-111111111111");
        ConstructionVolume volume = new ConstructionVolume(
            UUID.fromString("22222222-2222-2222-2222-222222222222"),
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(99, 99, 99)),
            7L,
            Map.of()
        );
        List<PaletteEntry> palette = List.of(
            new PaletteEntry("stone", "minecraft:stone", "minecraft:stone", Map.of("role", "wall")),
            new PaletteEntry("glass", "minecraft:glass", "minecraft:glass", Map.of("role", "window"))
        );
        List<CompactBlueprintPrimitive> primitives = List.of(
            CompactBlueprintPrimitive.fillBox(0, new BlockPosition(0, 0, 0), new BlockPosition(2, 0, 4), "stone"),
            CompactBlueprintPrimitive.block(1, new BlockPosition(0, 1, 0), "glass")
        );
        MaterialManifest materials = new MaterialManifest(
            sourceId,
            Map.of(),
            Map.of("minecraft:stone", 1000L, "minecraft:glass", 1000L),
            Map.of()
        );
        CompactBlueprintPlan source = new CompactBlueprintPlan(
            sourceId,
            "test/v1",
            "SHA-256",
            "source-hash",
            "minecraft:overworld",
            volume,
            new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(2, 1, 4)),
            new BlockPosition(10, 10, 10),
            Facing.NORTH,
            List.of(),
            palette,
            materials,
            primitives,
            List.of(),
            new WorkloadEstimate(16L, 0L, 0L, 16L),
            new PreviewMetadata("Harness", "Compact modifier harness", "test", Map.of()),
            1.0,
            List.of()
        );

        CompactBlueprintPlan rotated = CompactBlueprintModifier.rotate(
            source, CompactBlueprintModifier.Rotation.CLOCKWISE_90);
        require(rotated.facing() == Facing.EAST, "90 degree rotation must rotate facing");
        require(rotated.dimensions().width() == 5 && rotated.dimensions().depth() == 3,
            "90 degree rotation must swap horizontal envelope dimensions");
        require(rotated.primitives().size() == 2, "rotation must remain primitive based");
        require("true".equals(rotated.preview().attributes().get("requires_revalidation")),
            "modified plans must advertise revalidation");
        require(rotated.warnings().stream().anyMatch(w -> "REVALIDATION_REQUIRED".equals(w.code())),
            "modified plans must carry revalidation warning");

        CompactBlueprintPlan mirrored = CompactBlueprintModifier.mirror(
            rotated, CompactBlueprintModifier.MirrorAxis.X);
        require(mirrored.facing() == Facing.WEST, "X mirror must swap east/west facing");

        CompactBlueprintPlan translated = CompactBlueprintModifier.translate(
            rotated, new BlockPosition(5, 0, 0));
        require(translated.anchor().equals(new BlockPosition(15, 10, 10)),
            "translation must move world anchor without block materialization");

        CompactBlueprintPlan remapped = CompactBlueprintModifier.remapPalette(
            source, Map.of("glass", "stone"));
        require("stone".equals(remapped.primitives().get(1).paletteKey()),
            "palette remap must rewrite primitive references");
        require(remapped.materials().required().getOrDefault("minecraft:stone", 0L) == 16L,
            "palette remap must recompute material requirements");
        require(remapped.materials().required().getOrDefault("minecraft:glass", 0L) == 0L,
            "remapped material must no longer be required");

        CompactBlueprintPlan paletteReplaced = CompactBlueprintModifier.replacePaletteEntry(
            source,
            "stone",
            new PaletteEntry("stone", "minecraft:cobblestone", "minecraft:cobblestone", Map.of("role", "wall"))
        );
        require(paletteReplaced.materials().required().getOrDefault("minecraft:cobblestone", 0L) == 15L,
            "palette entry replacement must recompute material identity");
        require(paletteReplaced.materials().missing().getOrDefault("minecraft:cobblestone", 0L) == 15L,
            "palette entry replacement must recompute missing materials from retained availability");

        CompactBlueprintPrimitive replacement = CompactBlueprintPrimitive.block(
            1, new BlockPosition(0, 1, 0), "stone");
        CompactBlueprintPlan replaced = CompactBlueprintModifier.replacePrimitive(source, 1, replacement);
        require(replaced.materials().required().getOrDefault("minecraft:stone", 0L) == 16L,
            "primitive replacement must recompute materials");

        CompactBlueprintModule module = new CompactBlueprintModule(
            "pillar",
            List.of(CompactBlueprintPrimitive.line(
                0, new BlockPosition(0, 0, 0), new BlockPosition(0, 2, 0), "stone"))
        );
        CompactBlueprintPlan repeated = CompactBlueprintModifier.repeat(
            source, module, 2, new BlockPosition(5, 0, 0), new BlockPosition(3, 0, 0));
        require(repeated.primitives().size() == 4, "repeat must append compact module primitives only");
        require(repeated.dimensions().width() == 9 && repeated.dimensions().height() == 3,
            "repeat must recompute compact geometry bounds");
        require(repeated.materials().required().getOrDefault("minecraft:stone", 0L) == 21L,
            "repeat must recompute material requirements");
        CompactBlueprintPlan repeatedAgain = CompactBlueprintModifier.repeat(
            source, module, 2, new BlockPosition(5, 0, 0), new BlockPosition(3, 0, 0));
        require(repeated.blueprintId().equals(repeatedAgain.blueprintId())
                && repeated.integrityHash().equals(repeatedAgain.integrityHash()),
            "identical compact edits must produce deterministic identity");

        boolean rejectedOutside = false;
        try {
            CompactBlueprintModifier.translate(source, new BlockPosition(100, 0, 0));
        } catch (IllegalArgumentException expected) {
            rejectedOutside = true;
        }
        require(rejectedOutside, "modification leaving ConstructionVolume must fail closed");

        boolean rejectedRepeat = false;
        try {
            CompactBlueprintModifier.repeat(
                source, module, CompactBlueprintModifier.MAX_REPEAT_COPIES + 1,
                new BlockPosition(0, 0, 0), new BlockPosition(1, 0, 0));
        } catch (IllegalArgumentException expected) {
            rejectedRepeat = true;
        }
        require(rejectedRepeat, "repeat count over resource ceiling must fail closed");
    }
}
"""


class BlueprintApiJavaCompileTests(unittest.TestCase):
    def test_blueprint_api_compiles_and_compact_modifier_executes_as_java_17(self) -> None:
        javac = shutil.which("javac")
        java = shutil.which("java")
        self.assertIsNotNone(javac, "javac is required to verify the published Continuity Works Java API")
        self.assertIsNotNone(java, "java is required to execute the Continuity Works Java API harness")
        sources = sorted(API_SRC.rglob("*.java"))
        self.assertGreaterEqual(len(sources), 20, "blueprint API source set is unexpectedly incomplete")

        with tempfile.TemporaryDirectory(prefix="continuityworks-api-javac-") as temp:
            temp_path = Path(temp)
            classes = temp_path / "classes"
            classes.mkdir()
            compile_api = subprocess.run(
                [javac, "--release", "17", "-d", str(classes), *map(str, sources)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            self.assertEqual(
                0,
                compile_api.returncode,
                "Continuity Works blueprint API failed Java 17 compilation:\n"
                + compile_api.stdout
                + compile_api.stderr,
            )

            harness = temp_path / "CompactModifierHarness.java"
            harness.write_text(textwrap.dedent(HARNESS), encoding="utf-8")
            compile_harness = subprocess.run(
                [javac, "--release", "17", "-cp", str(classes), "-d", str(classes), str(harness)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(
                0,
                compile_harness.returncode,
                "Compact modifier harness failed Java 17 compilation:\n"
                + compile_harness.stdout
                + compile_harness.stderr,
            )

            execute = subprocess.run(
                [java, "-cp", str(classes), "CompactModifierHarness"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(
                0,
                execute.returncode,
                "Compact modifier Java 17 behavioral harness failed:\n"
                + execute.stdout
                + execute.stderr,
            )


if __name__ == "__main__":
    unittest.main()
