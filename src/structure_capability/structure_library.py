from __future__ import annotations

import json
import os
from pathlib import Path


class StructureLibraryError(ValueError):
    pass


class StructureLibrary:
    """Manifest-backed access to Continuity Works structural library data."""

    def __init__(self, root: str | Path | None = None):
        self.root = self._resolve_root(root)
        self.manifest_path = self.root / "manifest.json"
        self.manifest = self._read_json(self.manifest_path)
        self._entries = {}
        for entry in self.manifest.get("entries", []):
            entry_id = entry.get("id")
            if not entry_id:
                raise StructureLibraryError("Manifest entry missing id")
            if entry_id in self._entries:
                raise StructureLibraryError(f"Duplicate library id: {entry_id}")
            self._entries[entry_id] = dict(entry)

    @staticmethod
    def _resolve_root(root: str | Path | None) -> Path:
        if root is not None:
            return Path(root).expanduser().resolve()
        env = os.environ.get("CONTINUITY_WORKS_LIBRARY")
        if env:
            return Path(env).expanduser().resolve()
        repo_candidate = Path(__file__).resolve().parents[2] / "library"
        if repo_candidate.is_dir():
            return repo_candidate
        cwd_candidate = Path.cwd() / "library"
        if cwd_candidate.is_dir():
            return cwd_candidate.resolve()
        raise FileNotFoundError(
            "Continuity Works structural library not found; pass root= or set CONTINUITY_WORKS_LIBRARY"
        )

    @staticmethod
    def _read_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise StructureLibraryError(f"Expected object JSON in {path}")
        return data

    def ids(self, kind: str | None = None) -> list[str]:
        items = self._entries.values()
        if kind is not None:
            items = (entry for entry in items if entry.get("kind") == kind)
        return sorted(entry["id"] for entry in items)

    def entries(self, kind: str | None = None, tags: set[str] | None = None) -> list[dict]:
        required = set(tags or ())
        output = []
        for entry in self._entries.values():
            if kind is not None and entry.get("kind") != kind:
                continue
            if required and not required.issubset(set(entry.get("tags", []))):
                continue
            output.append(dict(entry))
        return sorted(output, key=lambda entry: entry["id"])

    def entry(self, entry_id: str) -> dict:
        try:
            return dict(self._entries[entry_id])
        except KeyError as exc:
            raise KeyError(f"Unknown structural library id: {entry_id}") from exc

    def path(self, entry_id: str) -> Path:
        entry = self.entry(entry_id)
        target = (self.root / entry["path"]).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise StructureLibraryError(f"Library entry escapes root: {entry_id} -> {target}") from exc
        return target

    def load(self, entry_id: str) -> dict:
        return self._read_json(self.path(entry_id))

    def validate(self) -> dict:
        findings = []

        def fail(code: str, detail: str):
            findings.append({"status": "FAIL", "code": code, "detail": detail})

        expected = self.manifest.get("counts", {})
        actual_layouts = len(self.ids("layout"))
        actual_structures = len(self.ids("test_structure"))
        if expected.get("layouts") != actual_layouts:
            fail("LAYOUT_COUNT_MISMATCH", f"{expected.get('layouts')} != {actual_layouts}")
        if expected.get("test_structures") != actual_structures:
            fail("TEST_STRUCTURE_COUNT_MISMATCH", f"{expected.get('test_structures')} != {actual_structures}")
        if expected.get("entries") != len(self._entries):
            fail("ENTRY_COUNT_MISMATCH", f"{expected.get('entries')} != {len(self._entries)}")

        for entry_id, entry in sorted(self._entries.items()):
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
            if entry.get("kind") == "layout":
                self._validate_layout(entry_id, data, fail)
            elif entry.get("kind") == "test_structure":
                self._validate_structure(entry_id, data, fail)
            else:
                fail("UNKNOWN_KIND", f"{entry_id}: {entry.get('kind')}")

        return {"gate":"STRUCTURE_LIBRARY","status":"FAIL" if findings else "PASS","library_version":self.manifest.get("library_version"),"entry_count":len(self._entries),"findings":findings}

    @staticmethod
    def _validate_layout(entry_id: str, data: dict, fail) -> None:
        if data.get("layout_id") != entry_id:
            fail("LAYOUT_ID_MISMATCH", f"{entry_id}: {data.get('layout_id')}")
        footprint = data.get("footprint")
        if not isinstance(footprint, dict):
            fail("MISSING_FOOTPRINT", entry_id)
            return
        dims = [footprint.get("width"), footprint.get("height"), footprint.get("depth")]
        if not all(isinstance(value, int) and value > 0 for value in dims):
            fail("INVALID_FOOTPRINT", f"{entry_id}: {footprint}")
            return
        width, height, depth = dims
        for connector in data.get("connectors", []):
            center = connector.get("center")
            if not isinstance(center, list) or len(center) != 3 or not all(isinstance(value, int) for value in center):
                fail("INVALID_CONNECTOR", f"{entry_id}: {connector}")
                continue
            x, y, z = center
            if not (0 <= x < width and 0 <= y < height and 0 <= z < depth):
                fail("CONNECTOR_OUT_OF_BOUNDS", f"{entry_id}: {connector.get('id')} {center}")

    @staticmethod
    def _validate_structure(entry_id: str, data: dict, fail) -> None:
        size = data.get("size")
        if not isinstance(size, list) or len(size) != 3 or not all(isinstance(value, int) and value > 0 for value in size):
            fail("INVALID_STRUCTURE_SIZE", f"{entry_id}: {size}")
            return
        metadata = data.get("metadata", {})
        if metadata.get("library_id") != entry_id:
            fail("STRUCTURE_ID_MISMATCH", f"{entry_id}: {metadata.get('library_id')}")
        seen = set()
        for index, block in enumerate(data.get("blocks", [])):
            pos = block.get("pos")
            name = block.get("block")
            if not isinstance(pos, list) or len(pos) != 3 or not all(isinstance(value, int) for value in pos):
                fail("INVALID_BLOCK_POSITION", f"{entry_id}[{index}]: {pos}")
                continue
            key = tuple(pos)
            if key in seen:
                fail("DUPLICATE_BLOCK_POSITION", f"{entry_id}: {pos}")
            seen.add(key)
            if not all(0 <= pos[axis] < size[axis] for axis in range(3)):
                fail("BLOCK_OUT_OF_BOUNDS", f"{entry_id}: {pos} outside {size}")
            if not isinstance(name, str) or ":" not in name:
                fail("UNNAMESPACED_BLOCK", f"{entry_id}: {name}")
