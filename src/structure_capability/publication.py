from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from importlib.metadata import PackageNotFoundError, version as package_version
import os
from typing import Any

CANONICAL_FRONTEND_URL = "https://mrcalzon02.github.io/Continuity-Works/"
CANONICAL_API_URL = "https://continuity-works-mrcalzon02-api.onrender.com"
PUBLIC_GATE = "PUBLIC_SERVICEABILITY"


def _env(primary: str, legacy: str | None = None, default: str = "") -> str:
    value = os.environ.get(primary)
    if value is not None:
        return value
    if legacy:
        legacy_value = os.environ.get(legacy)
        if legacy_value is not None:
            return legacy_value
    return default


@dataclass(frozen=True)
class PublicCapabilitySpec:
    name: str
    http_method: str
    path: str
    capability_method: str
    argument_mode: str = "body"  # none | body | version
    manual_ui: str = "available"  # available | not_applicable
    manual_surface: str | None = "manual_workbench"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# This is the authoritative publication matrix. A tool is not public merely
# because it exists in Python or in the JSON tool catalog. Every catalog tool
# must have one and only one entry here before PUBLIC_SERVICEABILITY can pass.
PUBLIC_CAPABILITIES: dict[str, PublicCapabilitySpec] = {
    "structure_capabilities": PublicCapabilitySpec(
        "structure_capabilities", "GET", "/v1/capabilities", "capabilities",
        argument_mode="none", manual_ui="not_applicable", manual_surface=None,
    ),
    "structure_inventory": PublicCapabilitySpec(
        "structure_inventory", "POST", "/v1/inventory", "inventory_project",
        argument_mode="none", manual_ui="not_applicable", manual_surface=None,
    ),
    "structure_audit": PublicCapabilitySpec(
        "structure_audit", "POST", "/v1/audit", "audit",
        manual_surface="structureforge_dashboard",
    ),
    "structure_plan": PublicCapabilitySpec(
        "structure_plan", "POST", "/v1/plan", "plan",
        manual_surface="structureforge_dashboard",
    ),
    "structure_generate": PublicCapabilitySpec(
        "structure_generate", "POST", "/v1/generate", "generate",
        manual_surface="structureforge_dashboard",
    ),
    "dungeon_layout": PublicCapabilitySpec(
        "dungeon_layout", "POST", "/v1/dungeon/layout", "dungeon_layout",
        manual_surface="structureforge_dashboard",
    ),
    "infrastructure_layout": PublicCapabilitySpec(
        "infrastructure_layout", "POST", "/v1/infrastructure/layout", "infrastructure_layout",
        manual_surface="structureforge_dashboard",
    ),
    "minecraft_version": PublicCapabilitySpec(
        "minecraft_version", "POST", "/v1/minecraft/version", "minecraft_version",
        argument_mode="version", manual_surface="manual_workbench",
    ),
    "minecraft_registry_probe": PublicCapabilitySpec(
        "minecraft_registry_probe", "POST", "/v1/minecraft/registry/probe", "minecraft_registry_probe",
        manual_surface="manual_workbench",
    ),
    "minecraft_book_generate": PublicCapabilitySpec(
        "minecraft_book_generate", "POST", "/v1/minecraft/book", "minecraft_book_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_loot_table_generate": PublicCapabilitySpec(
        "minecraft_loot_table_generate", "POST", "/v1/minecraft/loot-table", "minecraft_loot_table_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_recipe_generate": PublicCapabilitySpec(
        "minecraft_recipe_generate", "POST", "/v1/minecraft/recipe", "minecraft_recipe_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_advancement_generate": PublicCapabilitySpec(
        "minecraft_advancement_generate", "POST", "/v1/minecraft/advancement", "minecraft_advancement_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_tag_generate": PublicCapabilitySpec(
        "minecraft_tag_generate", "POST", "/v1/minecraft/tag", "minecraft_tag_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_datapack_manifest_generate": PublicCapabilitySpec(
        "minecraft_datapack_manifest_generate", "POST", "/v1/minecraft/datapack-manifest", "minecraft_datapack_manifest_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_content_package_generate": PublicCapabilitySpec(
        "minecraft_content_package_generate", "POST", "/v1/minecraft/content-package", "minecraft_content_package_generate",
        manual_surface="manual_workbench",
    ),
    "minecraft_icon_assign": PublicCapabilitySpec(
        "minecraft_icon_assign", "POST", "/v1/minecraft/icon", "minecraft_icon_assign",
        manual_surface="manual_workbench",
    ),
}


def canonical_api_url() -> str:
    return _env("CONTINUITY_WORKS_PUBLIC_BASE_URL", "STRUCTURESMITH_PUBLIC_BASE_URL", CANONICAL_API_URL).rstrip("/")


def canonical_frontend_url() -> str:
    return _env("CONTINUITY_WORKS_FRONTEND_URL", "STRUCTURESMITH_FRONTEND_URL", CANONICAL_FRONTEND_URL).rstrip("/") + "/"


def installed_version() -> str:
    for distribution in ("continuity-works-capability", "structure-generation-capability"):
        try:
            return package_version(distribution)
        except PackageNotFoundError:
            pass
    return _env("CONTINUITY_WORKS_VERSION", "STRUCTURESMITH_VERSION", "source")


def deployment_identity(base_url: str | None = None, tool_schema_version: str | None = None) -> dict[str, Any]:
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
    resolved_base = (base_url or render_url or canonical_api_url()).rstrip("/")
    commit = (
        os.environ.get("RENDER_GIT_COMMIT")
        or _env("CONTINUITY_WORKS_COMMIT", "STRUCTURESMITH_COMMIT")
        or os.environ.get("GITHUB_SHA")
        or "unknown"
    )
    deployment = _env("CONTINUITY_WORKS_DEPLOYMENT", "STRUCTURESMITH_DEPLOYMENT") or ("production" if os.environ.get("RENDER") == "true" else "local")
    return {
        "service": "Continuity Works",
        "service_slug": "continuity-works",
        "api_version": "v1",
        "package_version": installed_version(),
        "tool_schema_version": tool_schema_version or "unknown",
        "commit": commit,
        "deployment": deployment,
        "api": resolved_base,
        "frontend": canonical_frontend_url(),
        "verification": "external_acceptance_required",
    }


def publication_record(spec: PublicCapabilitySpec, capability: Any, base_url: str, deployment: dict[str, Any]) -> dict[str, Any]:
    implementation_ready = callable(getattr(capability, spec.capability_method, None))
    route_ready = bool(spec.path and spec.http_method)
    ui_ready = spec.manual_ui in {"available", "not_applicable"}
    locally_publishable = implementation_ready and route_ready and ui_ready
    runtime_deployed = deployment.get("deployment") == "production"
    return {
        "implementation": "ready" if implementation_ready else "missing",
        "http_route": "ready" if route_ready else "missing",
        "canonical_endpoint": f"{base_url.rstrip('/')}{spec.path}",
        "http_method": spec.http_method,
        "public_deployment": "running_unverified" if runtime_deployed else "local_or_candidate",
        "external_verification": "required",
        "manual_ui": {
            "state": spec.manual_ui,
            "surface": spec.manual_surface,
            "frontend": canonical_frontend_url() if spec.manual_ui == "available" else None,
        },
        "publication_state": "publishable_pending_remote_verification" if locally_publishable else "internal_unpublished",
    }


def _continuity_extension(tool: dict[str, Any]) -> dict[str, Any]:
    legacy = tool.pop("x-structuresmith", None)
    current = tool.setdefault("x-continuity-works", {})
    if legacy:
        for key, value in legacy.items():
            current.setdefault(key, value)
    return current


def published_tool_catalog(catalog: dict[str, Any], capability: Any, base_url: str | None = None) -> dict[str, Any]:
    base = (base_url or canonical_api_url()).rstrip("/")
    output = deepcopy(catalog)
    deployment = deployment_identity(base, str(output.get("schema_version", "unknown")))
    for tool in output.get("tools", []):
        name = tool.get("name")
        spec = PUBLIC_CAPABILITIES.get(name)
        xs = _continuity_extension(tool)
        if spec is None:
            xs["publication"] = {
                "implementation": "unknown",
                "http_route": "missing",
                "public_deployment": "unpublished",
                "manual_ui": {"state": "unclassified", "surface": None},
                "publication_state": "internal_unpublished",
            }
            continue
        xs["publication"] = publication_record(spec, capability, base, deployment)
    output["public_service"] = deployment
    output["public_service"]["gate"] = PUBLIC_GATE
    return output


def compact_publication(capability: Any, base_url: str | None = None) -> list[dict[str, Any]]:
    base = (base_url or canonical_api_url()).rstrip("/")
    deployment = deployment_identity(base)
    rows: list[dict[str, Any]] = []
    for spec in PUBLIC_CAPABILITIES.values():
        row = {"name": spec.name}
        row.update(publication_record(spec, capability, base, deployment))
        rows.append(row)
    return rows


def static_serviceability(capability: Any, catalog: dict[str, Any], openapi: dict[str, Any], discovery: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    """Evaluate local publication completeness without pretending to prove internet reachability."""
    base = (base_url or canonical_api_url()).rstrip("/")
    findings: list[dict[str, Any]] = []
    tools = {tool.get("name"): tool for tool in catalog.get("tools", [])}

    for name in sorted(tools):
        spec = PUBLIC_CAPABILITIES.get(name)
        if spec is None:
            findings.append({"severity": "error", "code": "TOOL_ROUTE_MISSING", "capability": name, "message": "Catalog tool has no canonical public route declaration."})
            continue
        if not callable(getattr(capability, spec.capability_method, None)):
            findings.append({"severity": "error", "code": "IMPLEMENTATION_MISSING", "capability": name, "message": f"Python method {spec.capability_method} is missing or not callable."})
        operation = openapi.get("paths", {}).get(spec.path, {}).get(spec.http_method.lower())
        if not operation or operation.get("x-continuity-works-tool") != name:
            findings.append({"severity": "error", "code": "OPENAPI_MISMATCH", "capability": name, "message": "Canonical route is absent or mismatched in OpenAPI."})
        if spec.manual_ui not in {"available", "not_applicable"}:
            findings.append({"severity": "error", "code": "MANUAL_UI_UNCLASSIFIED", "capability": name, "message": "Manual UI availability was not classified."})

    for name in sorted(set(PUBLIC_CAPABILITIES) - set(tools)):
        findings.append({"severity": "error", "code": "CATALOG_MISMATCH", "capability": name, "message": "Public route declaration has no tool-catalog entry."})

    required_discovery = ("api", "frontend", "health", "tools", "openapi")
    endpoints = discovery.get("endpoints", {})
    if discovery.get("api") != base:
        findings.append({"severity": "error", "code": "DISCOVERY_MISSING", "message": "Discovery document does not expose the canonical API base as an absolute URL."})
    for key in required_discovery[2:]:
        value = endpoints.get(key)
        if not isinstance(value, str) or not value.startswith(("https://", "http://")):
            findings.append({"severity": "error", "code": "DISCOVERY_MISSING", "message": f"Discovery endpoint {key!r} is missing or not absolute."})

    status = "FAIL" if any(item["severity"] == "error" for item in findings) else "READY_FOR_REMOTE_VERIFICATION"
    return {
        "gate": PUBLIC_GATE,
        "status": status,
        "findings": findings,
        "public_deployment": "not_verified_by_local_gate",
        "required_remote_failure_codes": [
            "API_HOST_UNREACHABLE",
            "DISCOVERY_MISSING",
            "TOOL_ROUTE_MISSING",
            "OPENAPI_MISMATCH",
            "CORS_REJECTED",
            "FRONTEND_STALE",
            "DEPLOYMENT_COMMIT_MISMATCH",
        ],
    }
