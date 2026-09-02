from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, re, zipfile, hashlib

@dataclass
class ModRecord:
    file: str
    mod_ids: list[str]
    namespaces: list[str]
    metadata_sources: list[str]

class ModInventory:
    """Local-only mod/namespace/resource discovery. Never invents registry IDs."""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.mods: list[ModRecord] = []
        self.namespaces: set[str] = {"minecraft"}
        self.registry_ids: set[str] = set()
        self.resource_ids: dict[str, set[str]] = {
            "recipe": set(), "loot_table": set(), "item_tag": set(),
            "item_candidate": set(), "structure": set(),
        }

    def _extract_ids_from_toml(self, text: str) -> list[str]:
        return sorted(set(re.findall(r'(?m)^\s*modId\s*=\s*["\']([^"\']+)["\']', text)))

    def _record_resource_path(self, name: str):
        clean = name.replace("\\", "/").lstrip("/")
        parts = clean.split("/")
        if len(parts) < 4:
            return
        if parts[0] == "data":
            ns, category = parts[1], parts[2]
            self.namespaces.add(ns)
            tail = "/".join(parts[3:])
            if tail.endswith(".json"):
                rid = f"{ns}:{tail[:-5]}"
                if category in {"recipe", "recipes"}:
                    self.resource_ids["recipe"].add(rid)
                elif category in {"loot_table", "loot_tables"}:
                    self.resource_ids["loot_table"].add(rid)
                elif category in {"structure", "structures"}:
                    self.resource_ids["structure"].add(rid)
            if category == "tags" and len(parts) >= 5 and parts[3] in {"item", "items"} and clean.endswith(".json"):
                tail = "/".join(parts[4:])
                self.resource_ids["item_tag"].add(f"{ns}:{tail[:-5]}")
        elif parts[0] == "assets":
            ns = parts[1]
            self.namespaces.add(ns)
            if parts[2] == "models" and len(parts) >= 5 and parts[3] == "item" and clean.endswith(".json"):
                tail = "/".join(parts[4:])
                self.resource_ids["item_candidate"].add(f"{ns}:{tail[:-5]}")
            elif parts[2] == "textures" and len(parts) >= 5 and parts[3] == "item" and clean.endswith(".png"):
                tail = "/".join(parts[4:])
                self.resource_ids["item_candidate"].add(f"{ns}:{tail[:-4]}")

    def scan_jar(self, path: Path) -> ModRecord:
        mod_ids, namespaces, sources = set(), set(), []
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                for candidate in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
                    if candidate in names:
                        sources.append(candidate)
                        mod_ids.update(self._extract_ids_from_toml(z.read(candidate).decode("utf-8", "replace")))
                if "fabric.mod.json" in names:
                    sources.append("fabric.mod.json")
                    try:
                        data = json.loads(z.read("fabric.mod.json"))
                        if data.get("id"):
                            mod_ids.add(data["id"])
                    except Exception:
                        pass
                for name in names:
                    parts = name.split("/")
                    if len(parts) >= 3 and parts[0] in {"data", "assets"} and parts[1]:
                        namespaces.add(parts[1])
                    self._record_resource_path(name)
        except zipfile.BadZipFile:
            pass
        self.namespaces.update(namespaces)
        rec = ModRecord(str(path), sorted(mod_ids), sorted(namespaces), sources)
        self.mods.append(rec)
        return rec

    def _scan_pack_tree(self, root: Path):
        if not root.exists():
            return
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                rel = p.relative_to(self.project_root).as_posix()
            except ValueError:
                continue
            if "/data/" in f"/{rel}" or rel.startswith("data/") or "/assets/" in f"/{rel}" or rel.startswith("assets/"):
                # Trim leading pack folders so _record_resource_path sees data/... or assets/...
                marker = rel.find("data/")
                asset_marker = rel.find("assets/")
                starts = [x for x in (marker, asset_marker) if x >= 0]
                if starts:
                    self._record_resource_path(rel[min(starts):])

    def scan(self) -> dict:
        mods_dir = self.project_root / "mods"
        if mods_dir.exists():
            for p in sorted(mods_dir.glob("*.jar")):
                self.scan_jar(p)
        max_depth = len(self.project_root.parts) + 6
        for folder_name in ("data", "assets"):
            for base in self.project_root.rglob(folder_name):
                if not base.is_dir() or len(base.parts) > max_depth:
                    continue
                for ns in base.iterdir():
                    if ns.is_dir():
                        self.namespaces.add(ns.name)
                self._scan_pack_tree(base)
        return self.to_dict()

    def add_registry_ids(self, ids, kind="registry"):
        values = {str(x) for x in ids}
        self.registry_ids.update(values)
        if kind in self.resource_ids:
            self.resource_ids[kind].update(values)

    def probe(self, registry_id: str, kind: str | None = None) -> dict:
        registry_id = str(registry_id)
        namespace = registry_id.split(":", 1)[0] if ":" in registry_id else "minecraft"
        if namespace == "minecraft":
            return {"id": registry_id, "kind": kind, "level": "vanilla", "namespace_known": True, "evidence": ["minecraft namespace"]}
        evidence = []
        if registry_id in self.registry_ids:
            evidence.append("explicit_registry_id")
            return {"id": registry_id, "kind": kind, "level": "exact", "namespace_known": namespace in self.namespaces, "evidence": evidence}
        kind_map = {"item": "item_candidate", "item_tag": "item_tag", "recipe": "recipe", "loot_table": "loot_table", "structure": "structure"}
        bucket = kind_map.get(kind or "", kind or "")
        if bucket in self.resource_ids and registry_id in self.resource_ids[bucket]:
            evidence.append(f"resource:{bucket}")
            level = "candidate" if bucket == "item_candidate" else "exact"
            return {"id": registry_id, "kind": kind, "level": level, "namespace_known": True, "evidence": evidence}
        if namespace in self.namespaces:
            return {"id": registry_id, "kind": kind, "level": "namespace", "namespace_known": True, "evidence": ["namespace_discovered"]}
        return {"id": registry_id, "kind": kind, "level": "unknown", "namespace_known": False, "evidence": []}

    def knows(self, registry_id: str) -> bool:
        return self.probe(registry_id).get("level") != "unknown"

    def to_dict(self):
        payload = {
            "mods": [asdict(x) for x in self.mods],
            "namespaces": sorted(self.namespaces),
            "registry_ids": sorted(self.registry_ids),
            "resource_ids": {k: sorted(v) for k, v in sorted(self.resource_ids.items())},
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        payload["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
        return payload
