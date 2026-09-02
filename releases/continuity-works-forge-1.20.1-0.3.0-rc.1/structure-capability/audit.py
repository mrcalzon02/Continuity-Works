from __future__ import annotations
from pathlib import Path
import json, hashlib
from .geospatial import evaluate_context, clearance_dimensions
from .minecraft.nbt import load_structure_nbt

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _audit_json(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    size = data.get("size", [0, 0, 0])
    blocks = data.get("blocks", [])
    return {
        "format": "structure-json",
        "size": size,
        "block_count": len(blocks),
        "palette_count": len({b.get("block") for b in blocks if b.get("block")}),
        "metadata": data.get("metadata", {}),
    }

def audit_source(path: str | None, request=None) -> dict:
    report = {"source": path, "exists": False, "findings": [], "metrics": {}}
    if not path:
        report["findings"].append({"severity":"warning","code":"NO_SOURCE","message":"No source artifact supplied; planning can continue from context only."})
    else:
        p = Path(path)
        report["exists"] = p.exists()
        if not p.exists():
            report["findings"].append({"severity":"error","code":"SOURCE_MISSING","message":f"Source not found: {p}"})
        else:
            report["sha256"] = sha256_file(p)
            try:
                if p.suffix.lower() == ".nbt":
                    s = load_structure_nbt(p)
                    report["metrics"] = {
                        "format": "minecraft-structure-nbt",
                        "size": s.get("size"),
                        "block_count": len(s.get("blocks", [])),
                        "palette_count": len(s.get("palette", [])),
                        "entity_count": len(s.get("entities", [])),
                        "data_version": s.get("DataVersion"),
                    }
                elif p.suffix.lower() == ".json":
                    report["metrics"] = _audit_json(p)
                else:
                    report["findings"].append({"severity":"warning","code":"UNINSPECTED_FORMAT","message":f"No built-in parser for {p.suffix}; source hash recorded."})
            except Exception as e:
                report["findings"].append({"severity":"error","code":"PARSE_FAILED","message":str(e)})
    if request:
        for finding in evaluate_context(request.context, request.purpose):
            report["findings"].append(finding.__dict__)
        w, h = clearance_dimensions(request.physical_clearance.value)
        report["required_clearance"] = {"width": w, "height": h, "class": request.physical_clearance.value}
        required_zones = request.purpose.required_zones
        if not required_zones:
            report["findings"].append({"severity":"warning","code":"PURPOSE_UNDERDEFINED","message":"Purpose profile declares no required functional zones."})
    report["status"] = "FAIL" if any(x["severity"] == "error" for x in report["findings"]) else "PASS_WITH_NOTES" if report["findings"] else "PASS"
    return report
