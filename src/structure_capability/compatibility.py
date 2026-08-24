from __future__ import annotations

from typing import Any

COMPATIBILITY_MODE = "append_only"
NON_DESTRUCTIVE_MODES = frozenset({"append_only", "additive", "non_destructive"})
DESTRUCTIVE_FLAGS = (
    "replace",
    "replace_existing",
    "override",
    "overwrite",
    "delete_existing",
    "remove_existing",
    "clear_existing",
    "disable_native",
    "exclusive",
)
STRATEGY_KEYS = ("merge_strategy", "table_strategy", "selector_strategy")
ADDITIVE_STRATEGIES = frozenset({"append", "append_only", "additive", "extend", "merge"})


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return bool(value)


def compatibility_policy() -> dict[str, Any]:
    return {
        "mode": COMPATIBILITY_MODE,
        "non_destructive": True,
        "base_authority": "preserved",
        "allowed_operations": [
            "append_entries",
            "extend_tables",
            "register_additional_parts",
            "add_optional_selectors",
            "add_namespaced_resources",
            "add_adapter_metadata",
        ],
        "forbidden_operations": [
            "replace_existing",
            "override_native",
            "delete_existing",
            "clear_existing",
            "disable_native",
            "exclusive_takeover",
        ],
        "rule": (
            "Compatibility is an additive overlay. Existing native behavior, tables, selectors, "
            "resources, and generators remain intact and authoritative."
        ),
    }


def validate_compatibility_request(*sections: dict[str, Any] | None) -> None:
    for section in sections:
        if not isinstance(section, dict):
            continue

        mode = section.get("mode", section.get("integration_mode"))
        if mode is not None and str(mode).strip().lower() not in NON_DESTRUCTIVE_MODES:
            raise ValueError("compatibility mode is fixed to append_only/non_destructive")

        for key in DESTRUCTIVE_FLAGS:
            if key in section and _truthy(section[key]):
                raise ValueError(f"destructive compatibility option is forbidden: {key}")

        for key in STRATEGY_KEYS:
            if key not in section or section[key] is None:
                continue
            strategy = str(section[key]).strip().lower()
            if strategy not in ADDITIVE_STRATEGIES:
                raise ValueError(
                    f"{key} must be additive (append/extend/merge); replacement strategies are forbidden"
                )
