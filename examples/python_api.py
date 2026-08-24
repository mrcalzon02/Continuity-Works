from structure_capability import StructureCapability
import json

cap = StructureCapability(project_root=".")
request = json.load(open("examples/requests/heavy_rebuild.json", encoding="utf-8"))

print(json.dumps(cap.plan(request), indent=2, default=str))
