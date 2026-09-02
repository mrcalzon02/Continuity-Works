from __future__ import annotations

import json
import os
from pathlib import Path


class StructureLibraryError(ValueError):
    pass


class StructureLibrary:
    """Manifest-backed access to Continuity Works structural library data."""

    VALID_FACES = {"north", "east", "south", "west", "up", "down"}

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
        contract_path = self.manifest.get("policy", {}).get(
            "connector_contracts_path", "contracts/connector_profiles.json"
        )
        self.connector_contract_path = (self.root / contract_path).resolve()
        self.connector_contract = (
            self._read_json(self.connector_contract_path)
            if self.connector_contract_path.is_file()
            else {"profiles": {}}
        )

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

    def entries(
        self,
        kind: str | None = None,
        tags: set[str] | None = None,
        category: str | None = None,
    ) -> list[dict]:
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
            raise KeyError(f"Unknown structural library id: {entry_id}") from exc

    def path(self, entry_id: str) -> Path:
        entry = self.entry(entry_id)
        target = (self.root / entry["path"]).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise StructureLibraryError(
                f"Library entry escapes root: {entry_id} -> {target}"
            ) from exc
        return target

    def load(self, entry_id: str) -> dict:
        return self._read_json(self.path(entry_id))

    def connector_profiles(self) -> dict[str, dict]:
        profiles = self.connector_contract.get("profiles", {})
        return {name: dict(value) for name, value in profiles.items()}

    def connector_profile(self, profile_id: str) -> dict:
        profiles = self.connector_contract.get("profiles", {})
        try:
            return dict(profiles[profile_id])
        except KeyError as exc:
            raise KeyError(f"Unknown connector profile: {profile_id}") from exc

    def profiles_compatible(self, left: str, right: str) -> bool:
        left_profile = self.connector_profile(left)
        right_profile = self.connector_profile(right)
        return (
            right in set(left_profile.get("mates", []))
            and left in set(right_profile.get("mates", []))
        )

    def validate(self) -> dict:
        findings = []

        def fail(code: str, detail: str):
            findings.append({"status": "FAIL", "code": code, "detail": detail})

        expected = self.manifest.get("counts", {})
        actual_layouts = len(self.ids("layout"))
        actual_modules = len(self.ids("module"))
        actual_structures = len(self.ids("test_structure"))
        if expected.get("layouts") != actual_layouts:
            fail("LAYOUT_COUNT_MISMATCH", f"{expected.get('layouts')} != {actual_layouts}")
        if expected.get("modules") != actual_modules:
            fail("MODULE_COUNT_MISMATCH", f"{expected.get('modules')} != {actual_modules}")
        if expected.get("test_structures") != actual_structures:
            fail(
                "TEST_STRUCTURE_COUNT_MISMATCH",
                f"{expected.get('test_structures')} != {actual_structures}",
            )
        if expected.get("entries") != len(self._entries):
            fail(
                "ENTRY_COUNT_MISMATCH",
                f"{expected.get('entries')} != {len(self._entries)}",
            )

        profiles = self.connector_contract.get("profiles")
        if not isinstance(profiles, dict) or not profiles:
            fail("CONNECTOR_CONTRACT_MISSING", str(self.connector_contract_path))
            profiles = {}
        else:
            self._validate_connector_contract(profiles, fail)

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
            elif entry.get("kind") == "module":
                base_layout = data.get("base_layout")
                if base_layout is not None:
                    base_entry = self._entries.get(base_layout)
                    if not base_entry or base_entry.get("kind") != "layout":
                        fail("UNKNOWN_BASE_LAYOUT", f"{entry_id}: {base_layout}")
                self._validate_module(entry_id, data, profiles, fail)
            elif entry.get("kind") == "test_structure":
                self._validate_structure(entry_id, data, fail)
            else:
                fail("UNKNOWN_KIND", f"{entry_id}: {entry.get('kind')}")

        return {
            "gate": "STRUCTURE_LIBRARY",
            "status": "FAIL" if findings else "PASS",
            "library_version": self.manifest.get("library_version"),
            "entry_count": len(self._entries),
            "counts": {
                "layouts": actual_layouts,
                "modules": actual_modules,
                "test_structures": actual_structures,
            },
            "connector_profiles": len(profiles),
            "findings": findings,
        }

    @staticmethod
    def _validate_connector_contract(profiles: dict, fail) -> None:
        for profile_id, profile in sorted(profiles.items()):
            mates = profile.get("mates")
            if not isinstance(mates, list) or not mates:
                fail("INVALID_CONNECTOR_MATES", profile_id)
                continue
            for mate in mates:
                if mate not in profiles:
                    fail("UNKNOWN_CONNECTOR_MATE", f"{profile_id}: {mate}")
                    continue
                reverse = set(profiles[mate].get("mates", []))
                if profile_id not in reverse:
                    fail(
                        "ASYMMETRIC_CONNECTOR_MATE",
                        f"{profile_id} -> {mate} but reverse is absent",
                    )

    @staticmethod
    def _validate_layout(entry_id: str, data: dict, fail) -> None:
        if data.get("layout_id") != entry_id:
            fail("LAYOUT_ID_MISMATCH", f"{entry_id}: {data.get('layout_id')}")
        footprint = data.get("footprint")
        dims = StructureLibrary._footprint_dims(entry_id, footprint, fail)
        if dims is None:
            return
        StructureLibrary._validate_connector_bounds(
            entry_id, data.get("connectors", []), dims, fail, require_contract=False
        )
        StructureLibrary._validate_zone_bounds(
            entry_id, data.get("zones", []), dims, fail
        )

    @staticmethod
    def _validate_module(entry_id: str, data: dict, profiles: dict, fail) -> None:
        if data.get("module_id") != entry_id:
            fail("MODULE_ID_MISMATCH", f"{entry_id}: {data.get('module_id')}")
        family = data.get("family")
        if not isinstance(family, str) or not family:
            fail("MODULE_FAMILY_MISSING", entry_id)
        footprint = data.get("footprint")
        dims = StructureLibrary._footprint_dims(entry_id, footprint, fail)
        if dims is None:
            return
        connectors = data.get("connectors", [])
        if not isinstance(connectors, list) or not connectors:
            fail("MODULE_CONNECTORS_MISSING", entry_id)
        else:
            StructureLibrary._validate_connector_bounds(
                entry_id, connectors, dims, fail, require_contract=True, profiles=profiles
            )
        StructureLibrary._validate_zone_bounds(
            entry_id, data.get("zones", []), dims, fail
        )

    @staticmethod
    def _footprint_dims(entry_id: str, footprint: object, fail):
        if not isinstance(footprint, dict):
            fail("MISSING_FOOTPRINT", entry_id)
            return None
        dims = [
            footprint.get("width"),
            footprint.get("height"),
            footprint.get("depth"),
        ]
        if not all(isinstance(value, int) and value > 0 for value in dims):
            fail("INVALID_FOOTPRINT", f"{entry_id}: {footprint}")
            return None
        return tuple(dims)

    @staticmethod
    def _validate_connector_bounds(
        entry_id: str,
        connectors: object,
        dims: tuple[int, int, int],
        fail,
        *,
        require_contract: bool,
        profiles: dict | None = None,
    ) -> None:
        if not isinstance(connectors, list):
            fail("INVALID_CONNECTOR_LIST", entry_id)
            return
        width, height, depth = dims
        seen = set()
        for connector in connectors:
            if not isinstance(connector, dict):
                fail("INVALID_CONNECTOR", f"{entry_id}: {connector}")
                continue
            connector_id = connector.get("id")
            if not isinstance(connector_id, str) or not connector_id:
                fail("CONNECTOR_ID_MISSING", entry_id)
            elif connector_id in seen:
                fail("DUPLICATE_CONNECTOR_ID", f"{entry_id}: {connector_id}")
            else:
                seen.add(connector_id)

            center = connector.get("center")
            if (
                not isinstance(center, list)
                or len(center) != 3
                or not all(isinstance(value, int) for value in center)
            ):
                fail("INVALID_CONNECTOR", f"{entry_id}: {connector}")
                continue
            x, y, z = center
            if not (0 <= x < width and 0 <= y < height and 0 <= z < depth):
                fail(
                    "CONNECTOR_OUT_OF_BOUNDS",
                    f"{entry_id}: {connector_id} {center}",
                )
                continue

            if require_contract:
                face = connector.get("face")
                if face not in StructureLibrary.VALID_FACES:
                    fail("INVALID_CONNECTOR_FACE", f"{entry_id}: {connector_id} {face}")
                elif not StructureLibrary._center_on_face(face, center, dims):
                    fail(
                        "CONNECTOR_NOT_ON_FACE",
                        f"{entry_id}: {connector_id} {face} {center}",
                    )
                profile = connector.get("profile")
                if profile not in (profiles or {}):
                    fail(
                        "UNKNOWN_CONNECTOR_PROFILE",
                        f"{entry_id}: {connector_id} {profile}",
                    )

    @staticmethod
    def _center_on_face(
        face: str, center: list[int], dims: tuple[int, int, int]
    ) -> bool:
        width, height, depth = dims
        x, y, z = center
        return {
            "north": z == 0,
            "south": z == depth - 1,
            "west": x == 0,
            "east": x == width - 1,
            "down": y == 0,
            "up": y == height - 1,
        }[face]

    @staticmethod
    def _validate_zone_bounds(entry_id: str, zones: object, dims, fail) -> None:
        if not isinstance(zones, list):
            fail("INVALID_ZONE_LIST", entry_id)
            return
        width, height, depth = dims
        for zone in zones:
            if not isinstance(zone, dict):
                fail("INVALID_ZONE", f"{entry_id}: {zone}")
                continue
            bounds = zone.get("bounds")
            if not isinstance(bounds, dict):
                fail("INVALID_ZONE_BOUNDS", f"{entry_id}: {zone.get('id')}")
                continue
            mn, mx = bounds.get("min"), bounds.get("max")
            if (
                not isinstance(mn, list)
                or not isinstance(mx, list)
                or len(mn) != 3
                or len(mx) != 3
                or not all(isinstance(v, int) for v in mn + mx)
            ):
                fail("INVALID_ZONE_BOUNDS", f"{entry_id}: {zone.get('id')}")
                continue
            if any(mn[i] > mx[i] for i in range(3)):
                fail("INVERTED_ZONE_BOUNDS", f"{entry_id}: {zone.get('id')}")
                continue
            if not (
                0 <= mn[0] <= mx[0] < width
                and 0 <= mn[1] <= mx[1] < height
                and 0 <= mn[2] <= mx[2] < depth
            ):
                fail(
                    "ZONE_OUT_OF_BOUNDS",
                    f"{entry_id}: {zone.get('id')} {mn}..{mx}",
                )

    @staticmethod
    def _validate_structure(entry_id: str, data: dict, fail) -> None:
        size = data.get("size")
        if (
            not isinstance(size, list)
            or len(size) != 3
            or not all(isinstance(value, int) and value > 0 for value in size)
        ):
            fail("INVALID_STRUCTURE_SIZE", f"{entry_id}: {size}")
            return
        metadata = data.get("metadata", {})
        if metadata.get("library_id") != entry_id:
            fail(
                "STRUCTURE_ID_MISMATCH",
                f"{entry_id}: {metadata.get('library_id')}",
            )
        seen = set()
        for index, block in enumerate(data.get("blocks", [])):
            pos = block.get("pos")
            name = block.get("block")
            if (
                not isinstance(pos, list)
                or len(pos) != 3
                or not all(isinstance(value, int) for value in pos)
            ):
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
