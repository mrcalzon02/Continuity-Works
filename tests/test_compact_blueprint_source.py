from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "modules" / "continuityworks-api" / "src" / "main" / "java" / "io" / "continuityworks" / "api" / "blueprint"
RUNTIME = ROOT / "modules" / "continuityworks_runtime" / "forge-1.20.1" / "src" / "main" / "java" / "io" / "continuityworks" / "blueprint" / "runtime"


class CompactBlueprintSourceTests(unittest.TestCase):
    def read(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"missing compact blueprint source: {path}")
        return path.read_text(encoding="utf-8")

    def test_api_is_versioned_and_primitive_first(self) -> None:
        version = self.read(API / "BlueprintApiVersion.java")
        properties = self.read(ROOT / "modules" / "continuityworks-api" / "gradle.properties")
        primitive = self.read(API / "CompactBlueprintPrimitive.java")
        plan = self.read(API / "CompactBlueprintPlan.java")
        self.assertIn("new BlueprintApiVersion(1, 6, 0)", version)
        self.assertIn("api_version=1.6.0", properties)
        for kind in ("BLOCK", "LINE", "FILL_BOX", "HOLLOW_BOX", "CYLINDER"):
            self.assertIn(kind, primitive)
        self.assertIn("PlacementOperation.Kind operationKind", primitive)
        self.assertIn("List<CompactBlueprintPrimitive> primitives", plan)
        self.assertNotIn("List<PlacementOperation> operations", plan)

    def test_streaming_is_bounded_and_zero_retention_by_default(self) -> None:
        materializer = self.read(API / "CompactBlueprintMaterializer.java")
        sink = self.read(API / "CompactPlacementSink.java")
        self.assertIn("MAX_STREAM_OPERATIONS = 1_048_576L", materializer)
        self.assertIn("forEachPlacement(List<CompactBlueprintPrimitive> primitives", materializer)
        self.assertIn("long maxOperations", materializer)
        self.assertIn("Compact blueprint exceeds streaming limit", materializer)
        self.assertIn("for (long x", materializer)
        self.assertIn("Math.subtractExact(cx, r)", materializer)
        self.assertIn("@FunctionalInterface", sink)
        self.assertIn("boolean accept", sink)

    def test_modifier_layer_is_compact_bounded_and_revalidation_gated(self) -> None:
        modifier = self.read(API / "CompactBlueprintModifier.java")
        module = self.read(API / "CompactBlueprintModule.java")
        self.assertIn('MODIFIER_VERSION = "compact-modifier/v1"', modifier)
        self.assertIn("MAX_MODIFIED_PRIMITIVES = 4096", modifier)
        self.assertIn("MAX_REPEAT_COPIES = 64", modifier)
        self.assertIn("MAX_MODIFIED_OPERATIONS = CompactBlueprintMaterializer.MAX_STREAM_OPERATIONS", modifier)
        for method in (
            "translate(",
            "rotate(",
            "mirror(",
            "remapPalette(",
            "replacePaletteEntry(",
            "replacePrimitive(",
            "compose(",
            "repeat(",
        ):
            self.assertIn(method, modifier)
        self.assertIn('"REVALIDATION_REQUIRED"', modifier)
        self.assertIn('attributes.put("requires_revalidation", "true")', modifier)
        self.assertIn("modified compact plan leaves the selected construction volume", modifier)
        self.assertIn("CompactBlueprintMaterializer.forEachPlacement", modifier)
        self.assertNotIn("List<PlacementOperation>", modifier)
        self.assertIn("record CompactBlueprintModule", module)
        self.assertIn("module primitive sequence must be contiguous from zero", module)

    def test_runtime_installs_corpus_aware_compact_provider(self) -> None:
        mod = self.read(RUNTIME / "ContinuityWorksBlueprintMod.java")
        router = self.read(RUNTIME / "CorpusAwareCompactBlueprintProvider.java")
        self.assertIn("ContinuityWorksCompactBlueprintServices.install(new CorpusAwareCompactBlueprintProvider())", mod)
        self.assertIn("MAX_ACTIVE_REQUESTS = 3", router)
        self.assertIn("MAX_RETAINED_CORPUS_MANIFESTS = 16", router)
        self.assertIn("FacilityCorpusVocabulary", router)
        for key in ("REFERENCE", "ARCHETYPE", "CATEGORY"):
            self.assertIn(f'new SpecificationDescriptor("{key}"', router)
        self.assertIn("enforcePermittedStyle", router)
        self.assertIn("correctConfidence", router)

    def test_corpus_planner_is_lazy_and_never_block_expands(self) -> None:
        corpus = self.read(RUNTIME / "CompactFacilityCorpusPlanner.java")
        self.assertIn("MAX_CANDIDATES = 8", corpus)
        self.assertIn("if (opened++ >= MAX_CANDIDATES) break", corpus)
        self.assertIn("CompactBlueprintProvider.MAX_PRIMITIVES", corpus)
        self.assertIn("CompactBlueprintProvider.MAX_RAW_PLACEMENTS", corpus)
        self.assertIn("CompactBlueprintPrimitive.fillBox", corpus)
        self.assertIn("CompactBlueprintPrimitive.hollowBox", corpus)
        self.assertIn("CompactBlueprintPrimitive.line", corpus)
        self.assertIn("CompactBlueprintPrimitive.cylinder", corpus)
        self.assertNotIn("TreeMap<P", corpus)
        rank_start = corpus.index("private List<Scored> rank")
        ledger_start = corpus.index("private List<SpecificationResolution> ledger")
        self.assertNotIn("json(entry.path())", corpus[rank_start:ledger_start])
        self.assertIn("case EAST -> new BlockPosition(depth - 1 - p.z(), p.y(), p.x())", corpus)
        self.assertIn("case WEST -> new BlockPosition(p.z(), p.y(), width - 1 - p.x())", corpus)

    def test_fixed_reference_remains_compact(self) -> None:
        reference = ROOT / "facility_library" / "references" / "fuel_petroleum" / "northstar_rural_gas_station.json"
        payload = json.loads(self.read(reference))
        self.assertEqual([31, 9, 25], payload["size"])
        self.assertEqual(23, len(payload["blueprint"]))
        self.assertEqual(
            {"block", "fill_box", "hollow_box", "line"},
            {primitive["op"] for primitive in payload["blueprint"]},
        )

    def test_compact_sources_do_not_embed_inference_runtime(self) -> None:
        paths = [
            API / "CompactBlueprintPrimitive.java",
            API / "CompactBlueprintMaterializer.java",
            API / "CompactBlueprintModifier.java",
            API / "CompactBlueprintModule.java",
            API / "ContinuityWorksCompactBlueprintApi.java",
            RUNTIME / "CompactBlueprintProvider.java",
            RUNTIME / "CompactFacilityCorpusPlanner.java",
            RUNTIME / "CorpusAwareCompactBlueprintProvider.java",
        ]
        combined = "\n".join(self.read(path).lower() for path in paths)
        for forbidden in ("onnxruntime", "tensorflow", "pytorch", "safetensors", ".gguf", ".onnx"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
