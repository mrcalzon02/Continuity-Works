#!/usr/bin/env python3
"""Fail closed when the in-game Continuity Works blueprint runtime stops being lightweight."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "modules" / "continuityworks_runtime" / "forge-1.20.1"
API = ROOT / "modules" / "continuityworks-api"
RELEASE_VALIDATOR = ROOT / "releases" / "continuity-works-forge-1.20.1-0.3.0-rc.2" / "build_release_jar.py"

BUDGETED = RUNTIME / "src/main/java/io/continuityworks/blueprint/runtime/ResourceBudgetedBlueprintApi.java"
CORPUS = RUNTIME / "src/main/java/io/continuityworks/blueprint/runtime/FacilityCorpusPlanner.java"
VOCAB = RUNTIME / "src/main/java/io/continuityworks/blueprint/runtime/FacilityCorpusVocabulary.java"
BOOTSTRAP = RUNTIME / "src/main/java/io/continuityworks/blueprint/runtime/ContinuityWorksBlueprintMod.java"
CODEC = API / "src/main/java/io/continuityworks/api/blueprint/BlueprintIntentCodec.java"
BUILD = RUNTIME / "build.gradle"

FORBIDDEN_DEPENDENCY_TOKENS = (
    "onnxruntime", "tensorflow", "pytorch", "torchscript", "safetensors", "llama.cpp",
    "llamacpp", "ggml", "gguf", "tflite",
)
FORBIDDEN_MODEL_SUFFIXES = {".gguf", ".onnx", ".tflite", ".safetensors", ".pth", ".pt"}


def text(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Missing blueprint budget source: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_literal(source: str, literal: str, label: str) -> None:
    if literal not in source:
        raise SystemExit(f"Blueprint runtime budget invariant missing: {label}: {literal}")


def integer_constant(source: str, name: str) -> int:
    match = re.search(rf"\b{name}\s*=\s*([0-9][0-9_]*)\s*;", source)
    if not match:
        raise SystemExit(f"Unable to resolve blueprint runtime constant {name}")
    return int(match.group(1).replace("_", ""))


def main() -> int:
    budgeted = text(BUDGETED)
    corpus = text(CORPUS)
    vocabulary = text(VOCAB)
    bootstrap = text(BOOTSTRAP)
    codec = text(CODEC)
    build = text(BUILD)
    release = text(RELEASE_VALIDATOR)

    require_literal(bootstrap, "new ResourceBudgetedBlueprintApi()", "Forge installs the bounded provider")
    require_literal(build, "facility_library", "facility corpus is packaged as data")
    require_literal(budgeted, "new ArrayBlockingQueue<>(MAX_ACTIVE_REQUESTS - 1)", "request queue is bounded")
    require_literal(budgeted, "new ThreadPoolExecutor(", "planner uses an explicit bounded executor")
    require_literal(vocabulary, "manifest.json", "tiny-model vocabulary comes from the compact manifest")
    require_literal(codec, "MAX_TEXT_CHARS = 2_048", "semantic transport is bounded")
    require_literal(codec, "SETBLOCK", "raw placement commands are rejected")
    require_literal(release, "MAX_RELEASE_BYTES = 1024 * 1024 * 1024", "release package has a sub-1-GiB ceiling")
    require_literal(release, "ResourceBudgetedBlueprintApi.class", "release requires the budgeted provider")
    require_literal(release, "FacilityCorpusPlanner.class", "release requires the lazy corpus planner")

    values = {
        "max_active_requests": integer_constant(budgeted, "MAX_ACTIVE_REQUESTS"),
        "max_completed_requests": integer_constant(budgeted, "MAX_COMPLETED_REQUESTS_PER_RUNTIME"),
        "max_specifications": integer_constant(budgeted, "MAX_SPECIFICATIONS"),
        "max_material_rows": integer_constant(budgeted, "MAX_AVAILABLE_MATERIAL_ROWS"),
        "max_site_candidates": integer_constant(budgeted, "MAX_SITE_CANDIDATES"),
        "max_permitted_styles": integer_constant(budgeted, "MAX_PERMITTED_STYLES"),
        "max_corpus_candidates": integer_constant(corpus, "MAX_CANDIDATES"),
        "max_corpus_operations": integer_constant(corpus, "MAX_OPERATIONS"),
        "max_intent_chars": integer_constant(codec, "MAX_TEXT_CHARS"),
        "max_intent_fields": integer_constant(codec, "MAX_FIELDS"),
    }

    ceilings = {
        "max_active_requests": 3,
        "max_completed_requests": 4096,
        "max_specifications": 32,
        "max_material_rows": 512,
        "max_site_candidates": 32,
        "max_permitted_styles": 32,
        "max_corpus_candidates": 8,
        "max_corpus_operations": 131072,
        "max_intent_chars": 2048,
        "max_intent_fields": 32,
    }
    for key, ceiling in ceilings.items():
        if values[key] > ceiling:
            raise SystemExit(f"Blueprint runtime budget exceeded: {key}={values[key]} > {ceiling}")

    dependency_surface = (build + "\n" + budgeted + "\n" + corpus + "\n" + vocabulary).lower()
    found_dependencies = sorted(token for token in FORBIDDEN_DEPENDENCY_TOKENS if token in dependency_surface)
    if found_dependencies:
        raise SystemExit("Forbidden inference dependency found in in-game blueprint runtime: " + ", ".join(found_dependencies))

    model_files = sorted(
        str(path.relative_to(ROOT))
        for base in (RUNTIME, API)
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_MODEL_SUFFIXES
    )
    if model_files:
        raise SystemExit("Model-weight files are forbidden in Continuity Works runtime modules: " + ", ".join(model_files))

    print(json.dumps({
        "gate": "BLUEPRINT_RUNTIME_BUDGET",
        "status": "PASS",
        "policy": "deterministic_no_embedded_inference",
        "limits": values,
        "forbidden_inference_dependencies": found_dependencies,
        "model_weight_files": model_files,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
