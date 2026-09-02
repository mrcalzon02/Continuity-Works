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


def _snbt_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


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
        "advancement": ("minecraft:experience_bottle", "AD"),
        "tag": ("minecraft:name_tag", "TG"),
        "datapack": ("minecraft:bundle", "DP"),
        "package": ("minecraft:chest_minecart", "PK"),
        "structure": ("minecraft:bricks", "ST"),
        "audit": ("minecraft:spyglass", "AU"),
        "plan": ("minecraft:map", "PL"),
        "version": ("minecraft:clock", "VR"),
        "registry": ("minecraft:knowledge_book", "ID"),
    }

    TAG_FOLDERS_PRE_121 = {
        "item": "items",
        "block": "blocks",
        "fluid": "fluids",
        "entity_type": "entity_types",
        "function": "functions",
        "game_event": "game_events",
    }
    TAG_FOLDERS_121_PLUS = {
        "item": "item",
        "block": "block",
        "fluid": "fluid",
        "entity_type": "entity_type",
        "function": "function",
        "game_event": "game_event",
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
        if _at_least(version, (1, 20, 5)):
            findings.append(GateFinding("book_pages", "PASS", "BOOK_PAGE_LIMIT_REMOVED", "Minecraft 1.20.5+ no longer imposes the legacy written-book page-count ceiling.", {"pages": len(pages)}))
        elif len(pages) > 100:
            findings.append(GateFinding("book_pages", "FAIL", "BOOK_PAGE_LIMIT", "Written books before 1.20.5 support at most 100 pages.", {"pages": len(pages), "max": 100}))
        else:
            findings.append(GateFinding("book_pages", "PASS", "BOOK_PAGE_LIMIT_OK", "Book page count is within the legacy 100-page limit.", {"pages": len(pages)}))
        if not 0 <= generation <= 3:
            findings.append(GateFinding("book_generation", "FAIL", "BOOK_GENERATION_RANGE", "Book generation must be between 0 and 3.", {"generation": generation}))

        page_components = [_json_text(page) for page in pages]
        if _at_least(version, (1, 20, 5)):
            written_content = {
                "title": {"raw": _json_text(title)},
                "author": author,
                "generation": generation,
                "resolved": resolved,
                "pages": page_components,
            }
            payload = {
                "id": item_id,
                "count": 1,
                "components": {"minecraft:written_book_content": written_content},
            }
            loot_entry = {
                "id": item_id,
                "count": 1,
                "components": {"minecraft:written_book_content": written_content},
            }
            format_id = "item_components_1_20_5_plus"
        else:
            legacy_tag = {
                "title": title,
                "author": author,
                "generation": generation,
                "resolved": resolved,
                "pages": page_components,
            }
            payload = {"id": item_id, "Count": 1, "tag": legacy_tag}
            pages_snbt = ",".join(_snbt_string(page) for page in page_components)
            legacy_snbt = (
                "{"
                f"title:{_snbt_string(title)},author:{_snbt_string(author)},"
                f"generation:{generation},resolved:{'1b' if resolved else '0b'},pages:[{pages_snbt}]"
                "}"
            )
            loot_entry = {"id": item_id, "count": 1, "nbt": legacy_snbt}
            format_id = "legacy_written_book_nbt"

        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_book",
            "target_version": version,
            "format": format_id,
            "item_stack": payload,
            "loot_entry": loot_entry,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "book", "target_version": version})["icon"],
        }

    def _loot_entry(self, item: dict, policy: str, findings: list[GateFinding], version: str) -> dict:
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
        functions = []
        if minimum != 1 or maximum != 1:
            count = int(minimum) if int(minimum) == int(maximum) else {"type": "minecraft:uniform", "min": int(minimum), "max": int(maximum)}
            functions.append({"function": "minecraft:set_count", "count": count})
        components = item.get("components") or {}
        nbt = item.get("nbt")
        if components:
            if _at_least(version, (1, 20, 5)):
                functions.append({"function": "minecraft:set_components", "components": components})
                findings.append(GateFinding("loot_components", "PASS", "LOOT_COMPONENTS_SUPPORTED", "Item components are emitted with minecraft:set_components for 1.20.5+.", {"id": item_id}))
            else:
                findings.append(GateFinding("loot_components", "FAIL", "LOOT_COMPONENTS_UNAVAILABLE", "Item components require Minecraft 1.20.5+; use legacy nbt for older targets.", {"id": item_id}))
        if nbt:
            if _at_least(version, (1, 20, 5)):
                findings.append(GateFinding("loot_nbt", "FAIL", "LOOT_SET_NBT_RENAMED", "Legacy set_nbt is not emitted on 1.20.5+; provide components/custom data instead.", {"id": item_id}))
            else:
                functions.append({"function": "minecraft:set_nbt", "tag": str(nbt)})
                findings.append(GateFinding("loot_nbt", "PASS", "LOOT_LEGACY_NBT_SUPPORTED", "Legacy item NBT is emitted with minecraft:set_nbt.", {"id": item_id}))
        if functions:
            entry["functions"] = functions
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
            entries = [self._loot_entry(item, policy, findings, version) for item in items]
            pools.append({"rolls": request.get("rolls", 1), "bonus_rolls": request.get("bonus_rolls", 0), "entries": entries})
        for item in guaranteed:
            pools.append({"rolls": 1, "entries": [self._loot_entry(item, policy, findings, version)]})

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

    def advancement(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        advancement_id = _resource_id(request.get("advancement_id") or request.get("id") or "structuresmith:generated_advancement", request.get("namespace") or "structuresmith")
        policy = str(request.get("id_policy") or "namespace")
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Advancement format resolved for Minecraft Java {version}.", {"family": profile.family})]
        criteria = dict(request.get("criteria") or {})
        if not criteria:
            findings.append(GateFinding("advancement_criteria", "FAIL", "ADVANCEMENT_CRITERIA_EMPTY", "Advancements require at least one criterion."))
        normalized_criteria = {}
        for name, criterion in criteria.items():
            if isinstance(criterion, str):
                criterion = {"trigger": criterion}
            if not isinstance(criterion, dict):
                raise ValueError(f"Advancement criterion {name!r} must be a trigger string or object")
            trigger = _resource_id(criterion.get("trigger") or "minecraft:impossible")
            normalized = {"trigger": trigger}
            if criterion.get("conditions") is not None:
                normalized["conditions"] = criterion["conditions"]
            normalized_criteria[str(name)] = normalized
        data = {"criteria": normalized_criteria}

        parent = request.get("parent")
        if parent:
            data["parent"] = _resource_id(parent)
        display = dict(request.get("display") or {})
        if display:
            title = display.get("title", "Generated Advancement")
            description = display.get("description", "Generated by StructureSmith")
            icon_spec = display.get("icon") or "minecraft:knowledge_book"
            if isinstance(icon_spec, str):
                icon_spec = {"id": icon_spec}
            icon_id = _resource_id(icon_spec.get("id") or icon_spec.get("item") or "minecraft:knowledge_book")
            findings.append(self._id_gate(icon_id, "item", policy))
            if _at_least(version, (1, 20, 5)):
                icon = {"id": icon_id}
                if icon_spec.get("components"):
                    icon["components"] = icon_spec["components"]
            else:
                icon = {"item": icon_id}
                if icon_spec.get("nbt"):
                    icon["nbt"] = str(icon_spec["nbt"])
            data["display"] = {
                "icon": icon,
                "title": title if isinstance(title, dict) else {"text": str(title)},
                "description": description if isinstance(description, dict) else {"text": str(description)},
                "frame": str(display.get("frame") or "task"),
                "show_toast": bool(display.get("show_toast", True)),
                "announce_to_chat": bool(display.get("announce_to_chat", True)),
                "hidden": bool(display.get("hidden", False)),
            }
            if display.get("background"):
                data["display"]["background"] = _resource_id(display["background"])
        if request.get("requirements") is not None:
            data["requirements"] = request["requirements"]
        if request.get("sends_telemetry_event") is not None:
            data["sends_telemetry_event"] = bool(request["sends_telemetry_event"])

        rewards = dict(request.get("rewards") or {})
        if rewards:
            normalized_rewards = {}
            if rewards.get("experience") is not None:
                normalized_rewards["experience"] = int(rewards["experience"])
            if rewards.get("loot"):
                normalized_rewards["loot"] = [_resource_id(value) for value in rewards["loot"]]
            if rewards.get("recipes"):
                normalized_rewards["recipes"] = [_resource_id(value) for value in rewards["recipes"]]
            if rewards.get("function"):
                normalized_rewards["function"] = _resource_id(rewards["function"])
            data["rewards"] = normalized_rewards

        namespace, path = advancement_id.split(":", 1)
        if _at_least(version, (1, 21, 0)):
            datapack_path = f"data/{namespace}/advancement/{path}.json"
        elif _at_least(version, (1, 13, 0)):
            datapack_path = f"data/{namespace}/advancements/{path}.json"
        else:
            datapack_path = f"data/advancements/{namespace}/{path}.json"
            findings.append(GateFinding("advancement_packaging", "WARN", "LEGACY_WORLD_SAVE_LAYOUT", "Minecraft 1.12 uses legacy world-save advancement layout rather than modern datapacks."))
        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_advancement",
            "target_version": version,
            "resource_id": advancement_id,
            "path": datapack_path,
            "json": data,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "advancement", "target_version": version})["icon"],
        }

    def tag(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        tag_id = _resource_id(request.get("tag_id") or request.get("id") or "structuresmith:generated_tag", request.get("namespace") or "structuresmith")
        registry_type = str(request.get("registry") or request.get("registry_type") or "item").replace("minecraft:", "")
        policy = str(request.get("id_policy") or "namespace")
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Tag format resolved for Minecraft Java {version}.", {"family": profile.family})]
        folder_map = self.TAG_FOLDERS_121_PLUS if _at_least(version, (1, 21, 0)) else self.TAG_FOLDERS_PRE_121
        if registry_type not in folder_map:
            findings.append(GateFinding("tag_registry", "FAIL", "TAG_REGISTRY_UNSUPPORTED", f"Simplified tag generator does not materialize registry type {registry_type!r}.", {"supported": sorted(folder_map)}))
            folder = registry_type
        else:
            findings.append(GateFinding("tag_registry", "PASS", "TAG_REGISTRY_SUPPORTED", f"Tag registry type {registry_type} is supported."))
            folder = folder_map[registry_type]
        values = list(request.get("values") or [])
        if not values:
            findings.append(GateFinding("tag_values", "WARN", "TAG_EMPTY", "Empty tags are valid but usually indicate an incomplete package."))
        normalized_values = []
        for value in values:
            if isinstance(value, dict):
                item_id = _resource_id(value.get("id") or value.get("value"))
                normalized_values.append({"id": item_id, "required": bool(value.get("required", True))})
                if registry_type == "item":
                    findings.append(self._id_gate(item_id, "item", policy))
                continue
            raw = str(value)
            if raw.startswith("#"):
                normalized_values.append(f"#{_resource_id(raw[1:])}")
            else:
                item_id = _resource_id(raw)
                normalized_values.append(item_id)
                if registry_type == "item":
                    findings.append(self._id_gate(item_id, "item", policy))
        namespace, path = tag_id.split(":", 1)
        datapack_path = f"data/{namespace}/tags/{folder}/{path}.json"
        if not _at_least(version, (1, 13, 0)):
            findings.append(GateFinding("tag_packaging", "FAIL", "DATAPACK_TAGS_UNAVAILABLE", "The deliberate tag generator targets datapack-era custom tags (Minecraft 1.13+)."))
        data = {"replace": bool(request.get("replace", False)), "values": normalized_values}
        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_tag",
            "target_version": version,
            "resource_id": tag_id,
            "registry": registry_type,
            "path": datapack_path,
            "json": data,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "tag", "target_version": version})["icon"],
        }

    def datapack_manifest(self, request: dict) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Datapack manifest target resolved for Minecraft Java {version}.", {"family": profile.family})]
        pack_format = request.get("pack_format", profile.data_pack_format)
        if not _at_least(version, (1, 13, 0)):
            findings.append(GateFinding("datapack_manifest", "FAIL", "DATAPACK_UNAVAILABLE", "Minecraft datapacks are not available on 1.12.x targets."))
        if pack_format is None:
            findings.append(GateFinding("datapack_manifest", "FAIL", "DATAPACK_FORMAT_UNKNOWN", "Exact data pack format is not bundled for this target; supply pack_format explicitly."))
            pack_format = 0
        else:
            findings.append(GateFinding("datapack_manifest", "PASS", "DATAPACK_FORMAT_RESOLVED", f"Using data pack format {int(pack_format)}.", {"exact_release_metadata": profile.exact_release_metadata}))
        description = request.get("description") or "Generated by StructureSmith"
        data = {"pack": {"pack_format": int(pack_format), "description": description}}
        if request.get("supported_formats") is not None:
            data["pack"]["supported_formats"] = request["supported_formats"]
        gate = _gate_report(findings)
        return {
            "artifact_type": "minecraft_datapack_manifest",
            "target_version": version,
            "path": "pack.mcmeta",
            "json": data,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "icon": self.assign_icon({"subject": "datapack", "target_version": version})["icon"],
        }

    def package(self, request: dict, structure_result: dict | None = None) -> dict:
        profile = self._profile(request)
        version = profile.normalized
        package_id = _resource_id(request.get("package_id") or request.get("id") or "structuresmith:generated_package", request.get("namespace") or "structuresmith")
        policy = str(request.get("id_policy") or "namespace")
        link_policy = str(request.get("link_policy") or "strict")
        namespace, base_path = package_id.split(":", 1)
        findings = [GateFinding("version", "PASS", "VERSION_RESOLVED", f"Content package target resolved for Minecraft Java {version}.", {"family": profile.family})]

        def inherited(spec: dict) -> dict:
            out = dict(spec)
            out.setdefault("target_version", version)
            out.setdefault("id_policy", policy)
            return out

        aliases: dict[str, dict] = {}
        books = []
        for index, spec in enumerate(request.get("books") or []):
            spec = dict(spec)
            alias = str(spec.pop("name", f"book_{index + 1}"))
            artifact = self.book(inherited(spec))
            books.append(artifact)
            aliases[f"book:{alias}"] = artifact

        loot_specs = []
        loot_aliases = {}
        for index, raw_spec in enumerate(request.get("loot_tables") or []):
            spec = dict(raw_spec)
            alias = str(spec.pop("name", f"loot_{index + 1}"))
            spec.setdefault("table_id", f"{namespace}:{base_path}/loot/{alias}")
            loot_specs.append((alias, spec))
            loot_aliases[alias] = spec

        links = []
        for binding in request.get("bindings") or []:
            binding_type = str(binding.get("type") or "")
            if binding_type != "book_as_guaranteed_loot":
                findings.append(GateFinding("package_binding", "FAIL" if link_policy == "strict" else "WARN", "PACKAGE_BINDING_UNSUPPORTED", f"Unsupported package binding type {binding_type!r}."))
                continue
            book_alias = str(binding.get("book") or "")
            loot_alias = str(binding.get("loot_table") or "")
            book_artifact = aliases.get(f"book:{book_alias}")
            loot_spec = loot_aliases.get(loot_alias)
            if not book_artifact or not loot_spec:
                findings.append(GateFinding("package_binding", "FAIL" if link_policy == "strict" else "WARN", "PACKAGE_BINDING_TARGET_MISSING", "Book-to-loot binding references a missing alias.", {"book": book_alias, "loot_table": loot_alias}))
                continue
            loot_spec.setdefault("guaranteed", []).append(dict(book_artifact["loot_entry"]))
            links.append({"type": binding_type, "book": book_alias, "loot_table": loot_alias, "status": "linked"})
            findings.append(GateFinding("package_binding", "PASS", "PACKAGE_BOOK_BOUND_TO_LOOT", f"Book {book_alias!r} is guaranteed in loot table {loot_alias!r}."))

        loot_tables = []
        for alias, spec in loot_specs:
            artifact = self.loot_table(inherited(spec))
            loot_tables.append(artifact)
            aliases[f"loot_table:{alias}"] = artifact

        recipes = []
        for index, raw_spec in enumerate(request.get("recipes") or []):
            spec = dict(raw_spec)
            alias = str(spec.pop("name", f"recipe_{index + 1}"))
            spec.setdefault("recipe_id", f"{namespace}:{base_path}/recipe/{alias}")
            artifact = self.recipe(inherited(spec))
            recipes.append(artifact)
            aliases[f"recipe:{alias}"] = artifact

        advancements = []
        for index, raw_spec in enumerate(request.get("advancements") or []):
            spec = dict(raw_spec)
            alias = str(spec.pop("name", f"advancement_{index + 1}"))
            spec.setdefault("advancement_id", f"{namespace}:{base_path}/advancement/{alias}")
            artifact = self.advancement(inherited(spec))
            advancements.append(artifact)
            aliases[f"advancement:{alias}"] = artifact

        tags = []
        for index, raw_spec in enumerate(request.get("tags") or []):
            spec = dict(raw_spec)
            alias = str(spec.pop("name", f"tag_{index + 1}"))
            spec.setdefault("tag_id", f"{namespace}:{base_path}/tag/{alias}")
            artifact = self.tag(inherited(spec))
            tags.append(artifact)
            aliases[f"tag:{alias}"] = artifact

        manifest_request = dict(request.get("manifest") or {})
        manifest_request.setdefault("target_version", version)
        manifest_request.setdefault("description", f"StructureSmith package {package_id}")
        manifest = self.datapack_manifest(manifest_request)

        artifact_groups = {
            "books": books,
            "loot_tables": loot_tables,
            "recipes": recipes,
            "advancements": advancements,
            "tags": tags,
        }
        flat_artifacts = [artifact for group in artifact_groups.values() for artifact in group] + [manifest]
        for artifact in flat_artifacts:
            status = artifact.get("gate", {}).get("status", "PASS")
            if status == "FAIL":
                findings.append(GateFinding("package_artifact", "FAIL", "PACKAGE_CHILD_FAILED", f"Child artifact {artifact.get('resource_id') or artifact.get('artifact_type')} failed its materialization gate."))
            elif status == "WARN":
                findings.append(GateFinding("package_artifact", "WARN", "PACKAGE_CHILD_WARNING", f"Child artifact {artifact.get('resource_id') or artifact.get('artifact_type')} requires runtime review."))

        if structure_result is not None:
            structure_status = str((structure_result.get("generation") or {}).get("status") or "unknown")
            if structure_status.lower() in {"failed", "fail", "error"}:
                findings.append(GateFinding("package_structure", "FAIL", "PACKAGE_STRUCTURE_FAILED", "Attached structure generation did not complete successfully.", {"status": structure_status}))
            else:
                findings.append(GateFinding("package_structure", "PASS", "PACKAGE_STRUCTURE_ATTACHED", "Generated structure result is attached to the package.", {"status": structure_status}))

        gate = _gate_report(findings)
        file_manifest = [
            {
                "artifact_type": artifact.get("artifact_type"),
                "resource_id": artifact.get("resource_id"),
                "path": artifact.get("path"),
                "status": artifact.get("gate", {}).get("status"),
            }
            for artifact in flat_artifacts
            if artifact.get("path")
        ]
        return {
            "artifact_type": "minecraft_content_package",
            "package_id": package_id,
            "target_version": version,
            "materialization_allowed": gate["status"] != "FAIL",
            "gate": gate,
            "manifest": file_manifest,
            "links": links,
            "artifacts": {**artifact_groups, "pack_mcmeta": manifest, "structure": structure_result},
            "icon": self.assign_icon({"subject": "package", "target_version": version})["icon"],
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
