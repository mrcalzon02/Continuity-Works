from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from .tooling import tool_catalog

BUILTIN_PRESETS = {
    "structure.modular_dungeon_nbt": {
        "tool": "structure_generate",
        "description": "Version-aware modular dungeon/complex generation with automatic NBT fragmentation.",
        "request": {
            "target_version": "1.20.1", "structure_type": "underground_complex", "scale": 1.0,
            "generation": {"kind": "dungeon", "materialize_nbt": True, "materialization_mode": "auto", "layout": {
                "scale": 1.0, "layout_shape": "rectangle", "room_layout": "packed", "corridor_style": "bent",
                "dead_end_policy": "some", "cell_scale_blocks": 3,
                "modularity": {"triple_fold": True, "macro_module": 12, "meso_module": 4, "micro_module": 1, "connector_width": 3},
            }},
        },
    },
    "layout.modular_dungeon": {
        "tool": "dungeon_layout",
        "description": "Reusable macro/meso/micro spatial layout without forcing artifact materialization.",
        "request": {"scale": 1.0, "layout_shape": "rectangle", "room_layout": "packed", "corridor_style": "bent",
            "dead_end_policy": "some", "cell_scale_blocks": 3,
            "modularity": {"triple_fold": True, "macro_module": 12, "meso_module": 4, "micro_module": 1, "connector_width": 3}},
    },
    "layout.urban_road_tile": {
        "tool": "infrastructure_layout",
        "description": "Tileable urban road segment using the established 6-block roadbed and 5-block terrain margins.",
        "request": {"module_type": "inner_city_road", "variant": "urban", "orientation": "north_south", "segment_length": 64,
            "road": {"width": 6, "terrain_padding": 5},
            "jigsaw": {"enabled": True, "connector_width": 6, "max_depth": 8},
            "lost_cities": {"enabled": True, "spawn_modes": ["tileable_grid", "sequential_jigsaw"], "tile_span_chunks": 4},
            "purpose": {"depth": 1}},
    },
    "layout.highway_tile": {
        "tool": "infrastructure_layout",
        "description": "Reusable highway segment with deterministic modular/jigsaw assembly.",
        "request": {"module_type": "highway", "variant": "urban", "orientation": "north_south", "segment_length": 96,
            "highway": {"profile": "surface_highway", "lane_count": 4, "lane_width": 3, "shoulder_width": 2,
                "median_width": 2, "elevated": False, "support_spacing": 16, "deck_thickness": 2, "min_clearance": 5},
            "jigsaw": {"enabled": True, "connector_width": 8, "max_depth": 8}, "purpose": {"depth": 1}},
    },
    "layout.aerospace_support_campus": {
        "tool": "aerospace_support_campus_generate",
        "description": "Deterministic validated aerospace support-campus graph; caller supplies a seed and may override the default standard scale/operator.",
        "request": {"scale": "standard"},
    },
    "content.written_book": {
        "tool": "minecraft_book_generate",
        "description": "Version-compatible written book assembly; caller supplies only the book-specific content.",
        "request": {"target_version": "1.20.1", "generation": 0, "resolved": True, "item_id": "minecraft:written_book"},
    },
    "content.chest_loot": {
        "tool": "minecraft_loot_table_generate",
        "description": "Version-compatible chest loot table with caller-provided weighted or guaranteed entries.",
        "request": {"target_version": "1.20.1", "type": "minecraft:chest", "rolls": 1, "bonus_rolls": 0},
        "requires_any": [["items", "guaranteed"]],
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict): out[key] = _deep_merge(out[key], value)
        else: out[key] = deepcopy(value)
    return out


def _apply_defaults(schema: dict, value):
    if not isinstance(schema, dict): return value
    if value is None and "default" in schema: value = deepcopy(schema["default"])
    if schema.get("type") == "object" and isinstance(value, dict):
        out = deepcopy(value)
        for key, child in schema.get("properties", {}).items():
            if key not in out and isinstance(child, dict) and "default" in child: out[key] = deepcopy(child["default"])
            if key in out: out[key] = _apply_defaults(child, out[key])
        return out
    if schema.get("type") == "array" and isinstance(value, list):
        return [_apply_defaults(schema.get("items", {}), item) for item in value]
    return value


def _missing_required(schema: dict, value, prefix=""):
    if not isinstance(schema, dict) or not isinstance(value, dict): return []
    missing=[]; properties=schema.get("properties", {})
    for key in schema.get("required", []):
        path=f"{prefix}.{key}" if prefix else key
        if key not in value or value[key] is None or value[key] == "": missing.append(path)
    for key, child in properties.items():
        if key in value and isinstance(value[key], dict):
            missing.extend(_missing_required(child, value[key], f"{prefix}.{key}" if prefix else key))
    return missing


def _schema_at_path(schema: dict, path: str):
    current=schema
    for part in path.split("."):
        current=current.get("properties", {}).get(part, {})
        if not isinstance(current, dict): return {}
    return deepcopy(current)


def _compact_description(text):
    text=" ".join(str(text or "").split())
    if not text: return ""
    first=text.split(". ",1)[0]
    return first if first.endswith(".") else first+"."


def _group_for(name):
    if name in {"structure_capabilities","structure_inventory","minecraft_registry_probe","minecraft_version"}: return "discovery"
    if name in {"structure_audit","structure_plan","structure_generate"}: return "structure"
    if name in {"dungeon_layout","infrastructure_layout","aerospace_support_campus_generate"}: return "layout"
    if name.startswith("minecraft_"): return "minecraft_content"
    return "other"


class CapabilityResolver:
    CONTRACT_VERSION="1.0"
    def __init__(self, project_root=".", *, catalog=None, presets=None):
        self.project_root=Path(project_root); self.catalog=deepcopy(catalog or tool_catalog())
        self._tools={tool["name"]:tool for tool in self.catalog.get("tools", [])}; self._presets=deepcopy(BUILTIN_PRESETS)
        config_path=self.project_root/"config"/"tool_presets.json"
        if config_path.exists():
            raw=json.loads(config_path.read_text(encoding="utf-8")); configured=raw.get("presets", raw)
            if not isinstance(configured, dict): raise ValueError("config/tool_presets.json must contain an object or {'presets': {...}}")
            self._presets.update(configured)
        if presets: self._presets.update(deepcopy(presets))
    def index(self, group=None):
        tools=[]
        for name, tool in sorted(self._tools.items()):
            item_group=_group_for(name)
            if group and item_group != group: continue
            params=tool.get("parameters") or {}; preset_ids=sorted(pid for pid,p in self._presets.items() if p.get("tool")==name)
            tools.append({"name":name,"group":item_group,"summary":_compact_description(tool.get("description","")),"required":list(params.get("required",[])),"preset_ids":preset_ids})
        return {"contract_version":self.CONTRACT_VERSION,"mode":"compact_index","count":len(tools),"groups":sorted({x["group"] for x in tools}),"tools":tools,
            "usage":{"next":"Fetch one exact contract with tool_contract(name), then resolve only supplied overrides.","http":{"index":"/v1/tools/index","contract":"/v1/tools/{tool_name}","resolve":"/v1/resolve"}}}
    def contract(self, name):
        if name not in self._tools: raise KeyError(f"Unknown Continuity Works tool: {name}")
        tool=deepcopy(self._tools[name]); params=tool.get("parameters") or {}
        return {"contract_version":self.CONTRACT_VERSION,"name":name,"group":_group_for(name),"description":tool.get("description",""),"required":list(params.get("required",[])),"parameters":params,
            "preset_ids":sorted(pid for pid,p in self._presets.items() if p.get("tool")==name)}
    def presets(self, *, compact=True):
        if compact:
            items=[{"id":pid,"tool":p.get("tool"),"summary":_compact_description(p.get("description","")),"requires_any":deepcopy(p.get("requires_any",[]))} for pid,p in sorted(self._presets.items())]
        else: items=[{"id":pid,**deepcopy(p)} for pid,p in sorted(self._presets.items())]
        return {"contract_version":self.CONTRACT_VERSION,"mode":"compact" if compact else "full","count":len(items),"presets":items}
    def preset(self, preset_id):
        if preset_id not in self._presets: raise KeyError(f"Unknown Continuity Works preset: {preset_id}")
        return {"id":preset_id,**deepcopy(self._presets[preset_id])}
    def resolve(self, tool_name, supplied=None, *, preset_id=None):
        contract=self.contract(tool_name); schema=contract["parameters"]; request={}; requires_any=[]
        if preset_id:
            preset=self.preset(preset_id)
            if preset.get("tool") != tool_name: raise ValueError(f"Preset {preset_id!r} targets {preset.get('tool')!r}, not {tool_name!r}")
            request=deepcopy(preset.get("request") or {}); requires_any=deepcopy(preset.get("requires_any") or [])
        request=_apply_defaults(schema,_deep_merge(request,supplied or {})); missing=_missing_required(schema,request); any_missing=[]
        for alternatives in requires_any:
            if not any(request.get(name) not in (None,"",[],{}) for name in alternatives):
                missing.append("|".join(alternatives)); any_missing.append({"one_of":list(alternatives),"message":f"Supply at least one of: {', '.join(alternatives)}."})
        unknown=[]
        if schema.get("additionalProperties") is False: unknown=sorted(set(request)-set(schema.get("properties",{})))
        required_inputs={path:_schema_at_path(schema,path) for path in missing if "|" not in path}
        ready=not missing and not unknown
        return {"contract_version":self.CONTRACT_VERSION,"tool":tool_name,"preset_id":preset_id,"ready":ready,"next_action":"invoke" if ready else "supply_variables","request":request,
            "missing":missing,"required_inputs":required_inputs,"requires_any":any_missing,"unknown_fields":unknown,
            "token_efficiency":{"strategy":"progressive_disclosure","loaded_contracts":[tool_name],"instruction":"Do not reload unrelated Continuity Works schemas for this operation."}}
    def resolve_request(self, request):
        if not isinstance(request, dict): raise TypeError("Resolver request must be an object.")
        tool_name=request.get("tool") or request.get("tool_name")
        if not tool_name: raise ValueError("Resolver request requires 'tool'.")
        supplied=request.get("request") or request.get("overrides") or {}
        if not isinstance(supplied, dict): raise TypeError("'request'/'overrides' must be an object.")
        return self.resolve(str(tool_name), supplied, preset_id=request.get("preset_id") or request.get("preset"))
