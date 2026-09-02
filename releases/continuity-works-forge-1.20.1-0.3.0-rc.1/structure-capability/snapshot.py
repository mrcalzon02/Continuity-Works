from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, uuid

class SnapshotStore:
    def __init__(self, root=".structure-capability/snapshots"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, structure_id, stage, payload, artifacts=None, parent=None, generated_artifacts=None):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        token = uuid.uuid4().hex[:8]
        sid = f"{timestamp}-{structure_id.replace(':','_').replace('/','_')}-{stage}-{token}"
        d = self.root / sid
        d.mkdir(parents=True)
        copied = []
        for artifact in artifacts or []:
            p = Path(artifact)
            if p.exists():
                out = d / "artifacts" / p.name
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out)
                copied.append({
                    "source": str(p),
                    "snapshot_path": str(out.relative_to(d)),
                    "sha256": hashlib.sha256(out.read_bytes()).hexdigest()
                })
        for name, data in (generated_artifacts or {}).items():
            safe_name = Path(name).name
            out = d / "artifacts" / safe_name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            copied.append({
                "source": "generated",
                "snapshot_path": str(out.relative_to(d)),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            })
        manifest = {
            "snapshot_id": sid,
            "created_utc": timestamp,
            "structure_id": structure_id,
            "stage": stage,
            "parent": parent,
            "payload": payload,
            "artifacts": copied,
        }
        raw = json.dumps(manifest, indent=2, sort_keys=True)
        (d / "manifest.json").write_text(raw, encoding="utf-8")
        return manifest

    def load(self, snapshot_id):
        return json.loads((self.root / snapshot_id / "manifest.json").read_text(encoding="utf-8"))

    def list(self):
        return [p.name for p in sorted(self.root.iterdir()) if (p / "manifest.json").exists()]
