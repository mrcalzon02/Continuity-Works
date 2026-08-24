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
    """Local-only mod/namespace discovery. Never invents registry IDs."""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.mods: list[ModRecord] = []
        self.namespaces: set[str] = {"minecraft"}
        self.registry_ids: set[str] = set()

    def _extract_ids_from_toml(self, text: str) -> list[str]:
        return sorted(set(re.findall(r'(?m)^\s*modId\s*=\s*["\']([^"\']+)["\']', text)))

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
        except zipfile.BadZipFile:
            pass
        self.namespaces.update(namespaces)
        rec = ModRecord(str(path), sorted(mod_ids), sorted(namespaces), sources)
        self.mods.append(rec)
        return rec

    def scan(self) -> dict:
        mods_dir = self.project_root / "mods"
        if mods_dir.exists():
            for p in sorted(mods_dir.glob("*.jar")):
                self.scan_jar(p)
        for base in (self.project_root / "data", self.project_root / "assets"):
            if base.exists():
                for p in base.iterdir():
                    if p.is_dir():
                        self.namespaces.add(p.name)
        # Datapack/resource-pack style project roots.
        for p in self.project_root.rglob("data"):
            if p.is_dir() and len(p.parts) - len(self.project_root.parts) <= 4:
                for ns in p.iterdir():
                    if ns.is_dir():
                        self.namespaces.add(ns.name)
        return self.to_dict()

    def add_registry_ids(self, ids):
        self.registry_ids.update(str(x) for x in ids)

    def knows(self, registry_id: str) -> bool:
        namespace = registry_id.split(":", 1)[0] if ":" in registry_id else "minecraft"
        return namespace == "minecraft" or registry_id in self.registry_ids or namespace in self.namespaces

    def to_dict(self):
        payload = {
            "mods": [asdict(x) for x in self.mods],
            "namespaces": sorted(self.namespaces),
            "registry_ids": sorted(self.registry_ids),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        payload["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
        return payload
