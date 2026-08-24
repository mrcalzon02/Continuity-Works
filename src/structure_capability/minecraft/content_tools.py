from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from html import escape

from ..versioning import resolve_minecraft_version

_RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")


def _version_tuple(version: str) -> tuple[int, int, int]:
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", str(version))
    if not m:
        raise ValueError(f"Unsupported Minecraft version syntax: {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def _at_least(version: str, target: tuple[int, int, int]) -> bool:
    return _version_tuple(version) >= target


def _resource_id(value: str, default_namespace: str = "minecraft") -> str:
    value = str(value or "").strip().lower()
    if ":" not in value:
        value = f"{default_namespace}:{value}"
    if not _RESOURCE_ID.match(value):
        raise ValueError(f"Invalid Minecraft resource location: {value!r}")
    return value


def _json_text(value) -> str:
    if isinstance(value, str):
        component = {"text": value}
    elif isinstance(value, dict):
        component = value
    else:
        component = {"text": str(value)}
    return json.dumps(component, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class GateFinding:
    gate: str
    status: str
    code: str
    message: str
    evidence: dict | None = None

    def to_dict(self):
        return asdict(self)


def _gate_report(findings: list[GateFinding]) -> dict:
    statuses = {f.status for f in findings}
    status = "FAIL" if "FAIL" in statuses else "WARN" if "WARN" in statuses else "PASS"
    return {
        "status": status,
        "findings": [f.to_dict() for f in findings],
        "public_reasoning": "Deterministic validation gates and reason codes only; no hidden chain-of-thought is exposed.",
    }


class MinecraftContentTools:
    """Version-aware, mod-aware Minecraft content authoring tools.

    The class deliberately exposes public validation gates rather than free-form
    internal reasoning. Output is portable JSON suitable for API/tool callers.
    """

    SEMANTIC_ICONS = {
        "book": ("minecraft:written_book", "BK"),
        "loot": ("minecraft:chest", "LT"),
        "loot_table": ("minecraft:chest", "LT"),
        "recipe": ("minecraft:crafting_table", "RC"),
        "structure": ("minecraft:bricks", "ST"),
        "audit": ("minecraft:spyglass", "AU"),
        "plan": ("minecraft:map", "PL"),
        "version": ("minecraft:clock", "VR"),
        "registry": ("minecraft:knowledge_book", "ID"),
    }

    def __init__(self, registry, inventory=None):
        self.registry = registry
        self.inventory = inventory or getattr(registry, "inventory", None)

    def _profile(self, request: dict):
        return resolve_minecraft_version(request.get("target_version") or request.get("version") or "1.20.1")

    def _id_gate(self, registry_id: str, kind: str, policy: str = "namespace") -> GateFinding:
        registry_id = _resource_id(registry_id)
        if registry_id.startswith("minecraft:"):
            return GateFinding("registry_id", "PASS", "VANILLA_ID", f"{registry_id} is a vanilla namespace ID.", {"id": registry_id, "confidence": "vanilla"})
        probe = self.registry.probe(registry_id, kind=kind) if hasattr(self.registry, "probe") else {"level": "namespace" if self.registry.verified(registry_id) else "unknown"}
        level = probe.get("level", "unknown")
        if level in {"exact", "candidate"}:
            status = "PASS" if level == "exact" else "WARN"
            code = "MOD_ID_EXACT" if level == "exact" else "MOD_ID_CANDIDATE"
            return GateFinding("registry_id", status, code, f"{registry_id} was discovered in the connected project inventory.", probe)
        if level == "namespace":
            if policy == "strict":
                return GateFinding("registry_id", "FAIL", "MOD_ID_NAMESPACE_ONLY", f"Namespace exists but {registry_id} was not discovered as an exact resource ID.", probe)
            return GateFinding("registry_id", "WARN", "MOD_ID_NAMESPACE_ONLY", f"Namespace exists; exact registry membership must be runtime-validated.", probe)
        if policy == "permissive":
            return GateFinding("registry_id", "WARN", "MOD_ID_UNVERIFIED", f"{registry_id} is not present in the scanned inventory; emitted only because permissive ID policy was selected.", probe)
        return GateFinding("registry_id", "FAIL", "MOD_ID_UNVERIFIED", f"{registry_id} is not present in the scanned mod/data/resource inventory.", probe)

    def registry_probe(self, request: dict) -> dict:
        registry_id = _resource_id(request.get("id") or request.get("registry_id"), request.get("namespace") or "minecraft")
        kind = str(request.get("kind") or "registry")
        policy = str(request.get("id_policy") or "namespace")
        finding = self._id_gate(registry_id, kind, policy)
        gate = _gate_report([finding])
        return {
            "registry_id": registry_id,
            "kind": kind,
            "accepted": gate["status"] != "FAIL",
            "gate": gate,
            "probe": finding.evidence or {},
        }

    def book(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        title = str(request.get("title") or "Untitled")
        author = str(request.get("author") or "StructureSmith")
        pages = list(request.get("pages") or [])
        generation = int(request.get("generation", 0))
        resolved = bool(request.get("resolved", True))
        item_id = _resource_id(request.get("item_id") or "minecraft:written_book")
        policy = str(request.get("id_policy") or "namespace")
        findings = [
            GateFinding("version", "PASS", "VERSION_RESOLVED", f"Book format resolved for Minecraft Java {version}.", {"family": profile.family}),
            self._id_gate(item_id, "item", policy),
        ]
        if len(pages) > 100:
            findings.append(GateFinding("book_pages", "FAIL", "BOOK_PAGE_LIMIT", "Written books support at most 100 pages.", {"pages": len(pages), "max": 100}))
        else:
            findings.append(GateFinding("book_pages", "PASS", "BOOK_PAGE_LIMIT_OK", "Book page count is within the supported 100-page limit.", {"pages": len(pages)}))
        if not 0 <= generation <= 3:
            findings.append(GateFinding("book_generation", "FAIL", "BOOK_GENERATION_RANGE", "Book generation must be between 0 and 3.", {"generation": generation}))

        page_components = [_json_text(page) for page in pages]
        if _at_least(version, (1, 20, 5)):
            payload = {
                "id": item_id,
                "count": 1,
                "components": {
                    "minecraft:written_book_content": {
                        "title": {"raw": _json_text(title)},
                        "author": author,
                        "generation": generation,
                        "resolved": resolved,
                        "pages": page_components,
                    }
                },
            }
            format_id = "item_components_1_20_5_plus"
        else:
            payload = {
                "id": item_id,
                "Count": 1,
                "tag": {
                    "title": title,
                    "author": author,
                    "generation": generation,
                    "resolved": resolved,
                    "pages": page_components,
                },
            }
            format_id = "legacy_written_book_nbt"

        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_book",
            "target_version": version,
            "format": format_id,
            "item_stack": payload,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "book", "target_version": version})["icon"],
        }

    def _loot_entry(self, item: dict, policy: str, findings: list[GateFinding]) -> dict:
        item_id = _resource_id(item.get("id") or item.get("item"))
        findings.append(self._id_gate(item_id, "item", policy))
        entry = {"type": "minecraft:item", "name": item_id}
        weight = int(item.get("weight", 1))
        if weight != 1:
            entry["weight"] = weight
        quality = int(item.get("quality", 0))
        if quality:
            entry["quality"] = quality
        minimum = item.get("min_count", item.get("count", 1))
        maximum = item.get("max_count", minimum)
        if minimum != 1 or maximum != 1:
            count = int(minimum) if int(minimum) == int(maximum) else {"type": "minecraft:uniform", "min": int(minimum), "max": int(maximum)}
            entry["functions"] = [{"function": "minecraft:set_count", "count": count}]
        return entry

    def loot_table(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        table_id = _resource_id(request.get("table_id") or request.get("id") or "structuresmith:generated_loot", request.get("namespace") or "structuresmith")
        policy = str(request.get("id_policy") or "namespace")
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Loot-table format resolved for Minecraft Java {version}.", {"family": profile.family})]
        items = list(request.get("items") or [])
        guaranteed = list(request.get("guaranteed") or [])
        if not items and not guaranteed:
            findings.append(GateFinding("loot_entries", "FAIL", "LOOT_EMPTY", "At least one weighted or guaranteed loot item is required."))
        pools = []
        if items:
            entries = [self._loot_entry(item, policy, findings) for item in items]
            pools.append({"rolls": request.get("rolls", 1), "bonus_rolls": request.get("bonus_rolls", 0), "entries": entries})
        for item in guaranteed:
            pools.append({"rolls": 1, "entries": [self._loot_entry(item, policy, findings)]})

        namespace, path = table_id.split(":", 1)
        if _at_least(version, (1, 21, 0)):
            datapack_path = f"data/{namespace}/loot_table/{path}.json"
        elif _at_least(version, (1, 13, 0)):
            datapack_path = f"data/{namespace}/loot_tables/{path}.json"
        else:
            datapack_path = f"data/loot_tables/{namespace}/{path}.json"
            findings.append(GateFinding("packaging", "WARN", "LEGACY_WORLD_SAVE_LAYOUT", "Minecraft 1.12 uses the legacy world-save loot-table layout rather than modern datapacks."))

        artifact = {"type": request.get("type") or "minecraft:chest", "pools": pools}
        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_loot_table",
            "target_version": version,
            "resource_id": table_id,
            "path": datapack_path,
            "json": artifact,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "loot_table", "target_version": version})["icon"],
        }

    def _ingredient(self, spec, version: str, policy: str, findings: list[GateFinding]):
        if isinstance(spec, str):
            spec = {"tag": spec[1:]} if spec.startswith("#") else {"item": spec}
        if not isinstance(spec, dict):
            raise ValueError(f"Recipe ingredient must be a string or object, got {type(spec).__name__}")
        if "items" in spec:
            choices = [self._ingredient(x, version, policy, findings) for x in spec["items"]]
            return choices
        if "tag" in spec:
            tag_id = _resource_id(spec["tag"])
            findings.append(self._id_gate(tag_id, "item_tag", policy))
            return f"#{tag_id}" if _at_least(version, (1, 21, 2)) else {"tag": tag_id}
        item_id = _resource_id(spec.get("item") or spec.get("id"))
        findings.append(self._id_gate(item_id, "item", policy))
        return item_id if _at_least(version, (1, 21, 2)) else {"item": item_id}

    def _recipe_result(self, result: dict | str, version: str, cooking: bool = False, stonecutting: bool = False):
        if isinstance(result, str):
            result = {"id": result}
        item_id = _resource_id(result.get("id") or result.get("item"))
        count = int(result.get("count", 1))
        components = result.get("components") or {}
        if _at_least(version, (1, 20, 5)):
            payload = {"id": item_id}
            if not cooking and count != 1:
                payload["count"] = count
            if components:
                payload["components"] = components
            return payload
        if cooking:
            return item_id
        if stonecutting:
            return item_id, count
        payload = {"item": item_id}
        if count != 1:
            payload["count"] = count
        return payload

    def recipe(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        recipe_id = _resource_id(request.get("recipe_id") or request.get("id") or "structuresmith:generated_recipe", request.get("namespace") or "structuresmith")
        recipe_type = str(request.get("type") or "crafting_shaped").replace("minecraft:", "")
        policy = str(request.get("id_policy") or "namespace")
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Recipe format resolved for Minecraft Java {version}.", {"family": profile.family})]
        supported = {"crafting_shaped", "crafting_shapeless", "smelting", "blasting", "smoking", "campfire_cooking", "stonecutting"}
        if recipe_type not in supported:
            findings.append(GateFinding("recipe_type", "FAIL", "RECIPE_TYPE_UNSUPPORTED", f"Simplified generator does not yet materialize recipe type {recipe_type!r}.", {"supported": sorted(supported)}))
        else:
            findings.append(GateFinding("recipe_type", "PASS", "RECIPE_TYPE_SUPPORTED", f"Recipe type {recipe_type} is supported by the simplified materializer."))

        result_spec = request.get("result") or {}
        result_id = _resource_id(result_spec if isinstance(result_spec, str) else result_spec.get("id") or result_spec.get("item"))
        findings.append(self._id_gate(result_id, "item", policy))
        data = {"type": f"minecraft:{recipe_type}"}
        if request.get("group"):
            data["group"] = str(request["group"])
        if request.get("category"):
            data["category"] = str(request["category"])

        if recipe_type == "crafting_shaped":
            pattern = list(request.get("pattern") or [])
            key = dict(request.get("key") or {})
            if not pattern or not key:
                findings.append(GateFinding("recipe_shape", "FAIL", "SHAPED_RECIPE_INCOMPLETE", "Shaped recipes require both pattern and key."))
            data["pattern"] = pattern
            data["key"] = {symbol: self._ingredient(spec, version, policy, findings) for symbol, spec in key.items()}
            data["result"] = self._recipe_result(result_spec, version)
        elif recipe_type == "crafting_shapeless":
            ingredients = list(request.get("ingredients") or [])
            if not ingredients:
                findings.append(GateFinding("recipe_ingredients", "FAIL", "SHAPELESS_RECIPE_EMPTY", "Shapeless recipes require at least one ingredient."))
            data["ingredients"] = [self._ingredient(spec, version, policy, findings) for spec in ingredients]
            data["result"] = self._recipe_result(result_spec, version)
        elif recipe_type in {"smelting", "blasting", "smoking", "campfire_cooking"}:
            ingredient = request.get("ingredient")
            if ingredient is None:
                findings.append(GateFinding("recipe_ingredient", "FAIL", "COOKING_RECIPE_EMPTY", "Cooking recipes require ingredient."))
                ingredient = "minecraft:air"
            data["ingredient"] = self._ingredient(ingredient, version, policy, findings)
            data["result"] = self._recipe_result(result_spec, version, cooking=True)
            data["experience"] = float(request.get("experience", 0.0))
            data["cookingtime"] = int(request.get("cookingtime", request.get("cooking_time", 200)))
        elif recipe_type == "stonecutting":
            ingredient = request.get("ingredient")
            if ingredient is None:
                findings.append(GateFinding("recipe_ingredient", "FAIL", "STONECUTTING_RECIPE_EMPTY", "Stonecutting recipes require ingredient."))
                ingredient = "minecraft:air"
            data["ingredient"] = self._ingredient(ingredient, version, policy, findings)
            result = self._recipe_result(result_spec, version, stonecutting=True)
            if _at_least(version, (1, 20, 5)):
                data["result"] = result
            else:
                data["result"], data["count"] = result

        namespace, path = recipe_id.split(":", 1)
        folder = "recipe" if _at_least(version, (1, 21, 0)) else "recipes"
        datapack_path = f"data/{namespace}/{folder}/{path}.json"
        if not _at_least(version, (1, 13, 0)):
            findings.append(GateFinding("recipe_packaging", "FAIL", "DATAPACK_RECIPES_UNAVAILABLE", "The deliberate recipe generator targets datapack-era custom recipes (Minecraft 1.13+)."))

        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_recipe",
            "target_version": version,
            "resource_id": recipe_id,
            "path": datapack_path,
            "json": data,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "recipe", "target_version": version, "item_id": result_id})["icon"],
        }

    def _badge_svg(self, label: str, subject: str) -> str:
        label = (label or "SS")[:3].upper()
        digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()
        hue = int(digest[:4], 16) % 360
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img">'
            f'<rect x="4" y="4" width="56" height="56" rx="12" fill="hsl({hue} 45% 38%)"/>'
            '<rect x="9" y="9" width="46" height="46" rx="8" fill="none" stroke="white" stroke-opacity=".65" stroke-width="3"/>'
            f'<text x="32" y="39" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="white">{escape(label)}</text>'
            '</svg>'
        )

    def assign_icon(self, request: dict) -> dict:
        subject = str(request.get("subject") or request.get("kind") or "structure").lower()
        default_item, default_label = self.SEMANTIC_ICONS.get(subject, ("minecraft:knowledge_book", subject[:2].upper() or "SS"))
        item_id = _resource_id(request.get("item_id") or default_item)
        mode = str(request.get("mode") or "auto")
        custom_label = str(request.get("label") or default_label)
        probe = self.registry.probe(item_id, kind="item") if hasattr(self.registry, "probe") else {"level": "vanilla" if item_id.startswith("minecraft:") else "unknown"}
        use_item = mode in {"auto", "minecraft_item"} and probe.get("level") != "unknown"
        svg = self._badge_svg(custom_label, f"{subject}:{item_id}")
        icon = {
            "semantic": subject,
            "kind": "minecraft_item" if use_item else "svg_badge",
            "item_id": item_id if use_item else None,
            "label": custom_label,
            "fallback_svg": svg,
        }
        finding = GateFinding(
            "icon_assignment", "PASS" if use_item else "WARN",
            "ICON_REGISTRY_ITEM" if use_item else "ICON_SVG_FALLBACK",
            f"Assigned {'Minecraft item icon ' + item_id if use_item else 'deterministic SVG badge fallback'}.",
            probe,
        )
        return {"icon": icon, "gate": _gate_report([finding])}
