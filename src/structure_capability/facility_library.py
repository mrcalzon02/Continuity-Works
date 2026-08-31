from __future__ import annotations

import json
import os
from pathlib import Path

from .structure_library import StructureLibrary


class FacilityLibraryError(ValueError):
    pass


class FacilityLibrary:
    """Semantic facility archetypes, corporate languages, and vanilla references."""

    VALID_KINDS = {"corporate_language", "archetype", "facility_reference"}
    VALID_PRIMITIVES = {"block", "fill_box", "hollow_box", "line", "cylinder"}

    def __init__(self, root: str | Path | None = None, structure_root: str | Path | None = None):
        self.root = self._resolve_root(root)
        self.manifest_path = self.root / "manifest.json"
        self.manifest = self._read_json(self.manifest_path)
        self.structures = StructureLibrary(structure_root)
        self._entries: dict[str, dict] = {}
        for entry in self.manifest.get("entries", []):
            entry_id = entry.get("id")
            if not isinstance(entry_id, str) or not entry_id:
                raise FacilityLibraryError("Facility manifest entry missing id")
            if entry_id in self._entries:
                raise FacilityLibraryError(f"Duplicate facility library id: {entry_id}")
            self._entries[entry_id] = dict(entry)

    @staticmethod
    def _resolve_root(root: str | Path | None) -> Path:
        if root is not None:
            return Path(root).expanduser().resolve()
        env = os.environ.get("CONTINUITY_WORKS_FACILITY_LIBRARY")
        if env:
            return Path(env).expanduser().resolve()
        repo_candidate = Path(__file__).resolve().parents[2] / "facility_library"
        if repo_candidate.is_dir():
            return repo_candidate
        cwd_candidate = Path.cwd() / "facility_library"
        if cwd_candidate.is_dir():
            return cwd_candidate.resolve()
        raise FileNotFoundError(
            "Continuity Works facility library not found; pass root= or set "
            "CONTINUITY_WORKS_FACILITY_LIBRARY"
        )

    @staticmethod
    def _read_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise FacilityLibraryError(f"Expected object JSON in {path}")
        return data

    def ids(self, kind: str | None = None) -> list[str]:
        items = self._entries.values()
        if kind is not None:
            items = (entry for entry in items if entry.get("kind") == kind)
        return sorted(entry["id"] for entry in items)

    def entries(self, kind: str | None = None, tags: set[str] | None = None, category: str | None = None) -> list[dict]:
        required = set(tags or ())
        output = []
        for entry in self._entries.values():
            if kind is not None and entry.get("kind") != kind:
                continue
            if category is not None and entry.get("category") != category:
                continue
            if required and not required.issubset(set(entry.get("tags", []))):
                continue
            output.append(dict(entry))
        return sorted(output, key=lambda entry: entry["id"])

    def entry(self, entry_id: str) -> dict:
        try:
            return dict(self._entries[entry_id])
        except KeyError as exc:
            raise KeyError(f"Unknown facility library id: {entry_id}") from exc

    def path(self, entry_id: str) -> Path:
        entry = self.entry(entry_id)
        target = (self.root / entry["path"]).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise FacilityLibraryError(f"Facility library entry escapes root: {entry_id} -> {target}") from exc
        return target

    def load(self, entry_id: str) -> dict:
        return self._read_json(self.path(entry_id))

    def corporate_palette(self, corporate_language_id: str) -> dict[str, str]:
        if self.entry(corporate_language_id).get("kind") != "corporate_language":
            raise FacilityLibraryError(f"Not a corporate language: {corporate_language_id}")
        profile = self.load(corporate_language_id)
        palette = profile.get("palette")
        if not isinstance(palette, dict) or not palette:
            raise FacilityLibraryError(f"Corporate language has no palette: {corporate_language_id}")
        return dict(palette)

    def evaluate_reference(self, reference_id: str) -> dict:
        reference = self.load(reference_id)
        if self.entry(reference_id).get("kind") != "facility_reference":
            raise FacilityLibraryError(f"Not a facility reference: {reference_id}")
        archetype = self.load(reference["archetype_id"])
        recognition = archetype.get("recognition", {})
        required = list(recognition.get("required_signatures", []))
        present = set(reference.get("present_signatures", []))
        missing = [item for item in required if item not in present]
        fraction = 1.0 if not required else (len(required) - len(missing)) / len(required)
        minimum = float(recognition.get("minimum_required_fraction", 1.0))
        compiled = self.compile_reference(reference_id)
        return {
            "gate": "FACILITY_RECOGNITION",
            "status": "PASS" if fraction >= minimum else "FAIL",
            "reference_id": reference_id,
            "archetype_id": reference["archetype_id"],
            "corporate_language_id": reference["corporate_language_id"],
            "required_signatures": required,
            "present_signatures": sorted(present),
            "missing_signatures": missing,
            "recognition_fraction": fraction,
            "minimum_required_fraction": minimum,
            "compiled_block_count": len(compiled["blocks"]),
        }

    def compile_reference(self, reference_id: str, corporate_language_id: str | None = None) -> dict:
        reference = self.load(reference_id)
        if self.entry(reference_id).get("kind") != "facility_reference":
            raise FacilityLibraryError(f"Not a facility reference: {reference_id}")
        archetype = self.load(reference["archetype_id"])
        selected_corporate = corporate_language_id or reference["corporate_language_id"]
        if selected_corporate not in set(archetype.get("allowed_corporate_languages", [])):
            raise FacilityLibraryError(f"{selected_corporate} is not allowed for {reference['archetype_id']}")
        palette = self.corporate_palette(selected_corporate)
        size = reference.get("size")
        if not isinstance(size, list) or len(size) != 3 or not all(isinstance(v, int) and v > 0 for v in size):
            raise FacilityLibraryError(f"Invalid reference size: {reference_id}: {size}")

        blocks: dict[tuple[int, int, int], str] = {}

        def resolve_block(primitive: dict) -> str:
            direct = primitive.get("block")
            if direct is not None:
                block = direct
            else:
                role = primitive.get("role")
                block = palette.get(role)
                if block is None:
                    raise FacilityLibraryError(f"Unknown material role {role!r} in {reference_id}")
            if not isinstance(block, str) or not block.startswith("minecraft:"):
                raise FacilityLibraryError(f"Reference material is not vanilla: {reference_id}: {block}")
            return block

        def put(pos: tuple[int, int, int], block: str) -> None:
            if not all(0 <= pos[axis] < size[axis] for axis in range(3)):
                raise FacilityLibraryError(f"Blueprint block out of bounds: {reference_id}: {pos} outside {size}")
            blocks[pos] = block

        for index, primitive in enumerate(reference.get("blueprint", [])):
            if not isinstance(primitive, dict):
                raise FacilityLibraryError(f"Invalid blueprint primitive: {reference_id}[{index}]")
            op = primitive.get("op")
            if op not in self.VALID_PRIMITIVES:
                raise FacilityLibraryError(f"Unknown blueprint primitive {op!r}: {reference_id}[{index}]")
            block = resolve_block(primitive)
            if op == "block":
                put(self._vec3(primitive.get("pos"), reference_id, index), block)
            elif op in {"fill_box", "hollow_box"}:
                mn = self._vec3(primitive.get("min"), reference_id, index)
                mx = self._vec3(primitive.get("max"), reference_id, index)
                if any(mn[i] > mx[i] for i in range(3)):
                    raise FacilityLibraryError(f"Inverted box primitive: {reference_id}[{index}]")
                for x in range(mn[0], mx[0] + 1):
                    for y in range(mn[1], mx[1] + 1):
                        for z in range(mn[2], mx[2] + 1):
                            if op == "fill_box" or x in {mn[0], mx[0]} or y in {mn[1], mx[1]} or z in {mn[2], mx[2]}:
                                put((x, y, z), block)
            elif op == "line":
                start = self._vec3(primitive.get("start"), reference_id, index)
                end = self._vec3(primitive.get("end"), reference_id, index)
                delta = tuple(end[i] - start[i] for i in range(3))
                steps = max(abs(v) for v in delta)
                if steps == 0:
                    put(start, block)
                else:
                    for step in range(steps + 1):
                        t = step / steps
                        put(tuple(int(round(start[i] + delta[i] * t)) for i in range(3)), block)
            elif op == "cylinder":
                center = primitive.get("center")
                if not isinstance(center, list) or len(center) != 2 or not all(isinstance(v, int) for v in center):
                    raise FacilityLibraryError(f"Invalid cylinder center: {reference_id}[{index}]")
                cx, cz = center
                radius = primitive.get("radius")
                y_min = primitive.get("y_min")
                y_max = primitive.get("y_max")
                if not isinstance(radius, int) or radius < 1 or not isinstance(y_min, int) or not isinstance(y_max, int) or y_min > y_max:
                    raise FacilityLibraryError(f"Invalid cylinder dimensions: {reference_id}[{index}]")
                mode = primitive.get("mode", "shell")
                if mode not in {"shell", "solid"}:
                    raise FacilityLibraryError(f"Invalid cylinder mode: {reference_id}[{index}]: {mode}")
                caps = bool(primitive.get("caps", False))
                for x in range(cx - radius, cx + radius + 1):
                    for z in range(cz - radius, cz + radius + 1):
                        if (x - cx) ** 2 + (z - cz) ** 2 > radius ** 2:
                            continue
                        boundary = any((nx - cx) ** 2 + (nz - cz) ** 2 > radius ** 2 for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)))
                        for y in range(y_min, y_max + 1):
                            if mode == "solid" or boundary or (caps and y in {y_min, y_max}):
                                put((x, y, z), block)

        return {
            "size": list(size),
            "blocks": [{"pos": list(pos), "block": block} for pos, block in sorted(blocks.items())],
            "metadata": {
                "facility_reference_id": reference_id,
                "archetype_id": reference["archetype_id"],
                "corporate_language_id": selected_corporate,
                "source_format": "vanilla_blueprint_primitives/v1",
                "architectural_reference": True,
                "engineering_specification": False,
            },
        }

    @staticmethod
    def _vec3(value, reference_id: str, index: int) -> tuple[int, int, int]:
        if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, int) for v in value):
            raise FacilityLibraryError(f"Invalid vector: {reference_id}[{index}]: {value}")
        return tuple(value)

    @staticmethod
    def _version_tuple(value: object) -> tuple[int, ...]:
        if not isinstance(value, str):
            return ()
        try:
            return tuple(int(piece) for piece in value.split("."))
        except ValueError:
            return ()

    def validate(self) -> dict:
        findings: list[dict] = []

        def fail(code: str, detail: str) -> None:
            findings.append({"status": "FAIL", "code": code, "detail": detail})

        structural = self.structures.validate()
        if structural.get("status") != "PASS":
            fail("STRUCTURE_LIBRARY_DEPENDENCY_FAILED", str(structural.get("findings")))
        requirements = self.manifest.get("requires", {})
        minimum_structural = self._version_tuple(requirements.get("structure_library_min_version"))
        actual_structural = self._version_tuple(self.structures.manifest.get("library_version"))
        if minimum_structural and actual_structural < minimum_structural:
            fail("STRUCTURE_LIBRARY_VERSION_TOO_OLD", f"{actual_structural} < {minimum_structural}")
        minimum_connector = requirements.get("connector_contract_min_version")
        actual_connector = self.structures.connector_contract.get("version")
        if isinstance(minimum_connector, int) and (not isinstance(actual_connector, int) or actual_connector < minimum_connector):
            fail("CONNECTOR_CONTRACT_VERSION_TOO_OLD", f"{actual_connector} < {minimum_connector}")

        expected = self.manifest.get("counts", {})
        actual = {
            "corporate_languages": len(self.ids("corporate_language")),
            "archetypes": len(self.ids("archetype")),
            "facility_references": len(self.ids("facility_reference")),
            "entries": len(self._entries),
        }
        for key, value in actual.items():
            if expected.get(key) != value:
                fail(f"{key.upper()}_COUNT_MISMATCH", f"{expected.get(key)} != {value}")

        for entry_id, entry in sorted(self._entries.items()):
            kind = entry.get("kind")
            if kind not in self.VALID_KINDS:
                fail("UNKNOWN_FACILITY_KIND", f"{entry_id}: {kind}")
                continue
            try:
                path = self.path(entry_id)
            except Exception as exc:
                fail("INVALID_PATH", f"{entry_id}: {exc}")
                continue
            if not path.is_file():
                fail("MISSING_FILE", f"{entry_id}: {path}")
                continue
            try:
                data = self._read_json(path)
            except Exception as exc:
                fail("INVALID_JSON", f"{entry_id}: {exc}")
                continue
            if kind == "corporate_language":
                self._validate_corporate(entry_id, data, fail)
            elif kind == "archetype":
                self._validate_archetype(entry_id, data, fail)
            else:
                self._validate_reference(entry_id, data, fail)

        return {
            "gate": "FACILITY_LIBRARY",
            "status": "FAIL" if findings else "PASS",
            "library_version": self.manifest.get("library_version"),
            "counts": actual,
            "structure_library_version": self.structures.manifest.get("library_version"),
            "connector_profiles": len(self.structures.connector_profiles()),
            "findings": findings,
        }

    def _validate_corporate(self, entry_id: str, data: dict, fail) -> None:
        if data.get("corporate_language_id") != entry_id:
            fail("CORPORATE_ID_MISMATCH", f"{entry_id}: {data.get('corporate_language_id')}")
        palette = data.get("palette")
        if not isinstance(palette, dict) or not palette:
            fail("CORPORATE_PALETTE_MISSING", entry_id)
            return
        for role, block in sorted(palette.items()):
            if not isinstance(block, str) or not block.startswith("minecraft:"):
                fail("NON_VANILLA_CORPORATE_BLOCK", f"{entry_id}: {role}={block}")
        language = data.get("design_language")
        if not isinstance(language, dict) or not language.get("silhouette_tokens"):
            fail("CORPORATE_DESIGN_LANGUAGE_MISSING", entry_id)

    def _validate_archetype(self, entry_id: str, data: dict, fail) -> None:
        if data.get("archetype_id") != entry_id:
            fail("ARCHETYPE_ID_MISMATCH", f"{entry_id}: {data.get('archetype_id')}")
        required_modules = data.get("required_modules")
        if not isinstance(required_modules, list) or not required_modules:
            fail("ARCHETYPE_REQUIRED_MODULES_MISSING", entry_id)
            required_modules = []
        optional_modules = data.get("optional_modules", [])
        if not isinstance(optional_modules, list):
            fail("ARCHETYPE_OPTIONAL_MODULES_INVALID", entry_id)
            optional_modules = []
        for module_id in required_modules + optional_modules:
            try:
                module_entry = self.structures.entry(module_id)
            except KeyError:
                fail("UNKNOWN_ARCHETYPE_MODULE", f"{entry_id}: {module_id}")
                continue
            if module_entry.get("kind") != "module":
                fail("ARCHETYPE_REFERENCE_NOT_MODULE", f"{entry_id}: {module_id}")
        corporate_ids = data.get("allowed_corporate_languages")
        if not isinstance(corporate_ids, list) or not corporate_ids:
            fail("ARCHETYPE_CORPORATE_OPTIONS_MISSING", entry_id)
        else:
            for corporate_id in corporate_ids:
                target = self._entries.get(corporate_id)
                if not target or target.get("kind") != "corporate_language":
                    fail("UNKNOWN_ARCHETYPE_CORPORATE", f"{entry_id}: {corporate_id}")
        recognition = data.get("recognition", {})
        if not isinstance(recognition.get("required_signatures"), list) or not recognition.get("required_signatures"):
            fail("ARCHETYPE_SIGNATURES_MISSING", entry_id)
        for other in data.get("distinction", {}).get("not_confusable_with", []):
            target = self._entries.get(other)
            if not target or target.get("kind") != "archetype":
                fail("UNKNOWN_DISTINCTION_ARCHETYPE", f"{entry_id}: {other}")

    def _validate_reference(self, entry_id: str, data: dict, fail) -> None:
        if data.get("reference_id") != entry_id:
            fail("REFERENCE_ID_MISMATCH", f"{entry_id}: {data.get('reference_id')}")
        archetype_id = data.get("archetype_id")
        corporate_id = data.get("corporate_language_id")
        archetype_entry = self._entries.get(archetype_id)
        corporate_entry = self._entries.get(corporate_id)
        if not archetype_entry or archetype_entry.get("kind") != "archetype":
            fail("UNKNOWN_REFERENCE_ARCHETYPE", f"{entry_id}: {archetype_id}")
            return
        if not corporate_entry or corporate_entry.get("kind") != "corporate_language":
            fail("UNKNOWN_REFERENCE_CORPORATE", f"{entry_id}: {corporate_id}")
            return
        archetype = self.load(archetype_id)
        if corporate_id not in set(archetype.get("allowed_corporate_languages", [])):
            fail("REFERENCE_CORPORATE_NOT_ALLOWED", f"{entry_id}: {corporate_id}")

        size = data.get("size")
        if not isinstance(size, list) or len(size) != 3 or not all(isinstance(v, int) and v > 0 for v in size):
            fail("INVALID_REFERENCE_SIZE", f"{entry_id}: {size}")
            return
        composition = data.get("module_composition")
        if not isinstance(composition, list):
            fail("INVALID_MODULE_COMPOSITION", entry_id)
            composition = []
        used_modules: list[str] = []
        for placement in composition:
            if not isinstance(placement, dict):
                fail("INVALID_MODULE_PLACEMENT", f"{entry_id}: {placement}")
                continue
            module_id = placement.get("module_id")
            used_modules.append(module_id)
            try:
                module = self.structures.load(module_id)
            except Exception:
                fail("UNKNOWN_REFERENCE_MODULE", f"{entry_id}: {module_id}")
                continue
            origin = placement.get("origin")
            if not isinstance(origin, list) or len(origin) != 3 or not all(isinstance(v, int) for v in origin):
                fail("INVALID_MODULE_ORIGIN", f"{entry_id}: {module_id}: {origin}")
                continue
            footprint = module.get("footprint", {})
            dims = [footprint.get("width"), footprint.get("height"), footprint.get("depth")]
            if not all(isinstance(v, int) and v > 0 for v in dims):
                fail("INVALID_REFERENCED_MODULE_FOOTPRINT", f"{entry_id}: {module_id}")
                continue
            if any(origin[axis] < 0 or origin[axis] + dims[axis] > size[axis] for axis in range(3)):
                fail("MODULE_PLACEMENT_OUT_OF_BOUNDS", f"{entry_id}: {module_id} at {origin} size {dims} outside {size}")
        for module_id in archetype.get("required_modules", []):
            if module_id not in used_modules:
                fail("REQUIRED_MODULE_MISSING", f"{entry_id}: {module_id}")
        required_signatures = set(archetype.get("recognition", {}).get("required_signatures", []))
        present_signatures = set(data.get("present_signatures", []))
        missing = sorted(required_signatures - present_signatures)
        if missing:
            fail("REFERENCE_SIGNATURES_MISSING", f"{entry_id}: {missing}")
        try:
            compiled = self.compile_reference(entry_id)
        except Exception as exc:
            fail("REFERENCE_COMPILE_FAILED", f"{entry_id}: {exc}")
            return
        if not compiled.get("blocks"):
            fail("REFERENCE_EMPTY", entry_id)
        for block in compiled.get("blocks", []):
            if not block.get("block", "").startswith("minecraft:"):
                fail("REFERENCE_NON_VANILLA_BLOCK", f"{entry_id}: {block.get('block')}")
