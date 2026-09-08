from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

DEFAULT_API = "https://continuity-works-mrcalzon02-api.onrender.com"
DEFAULT_FRONTEND = "https://mrcalzon02.github.io/Continuity-Works/"
KNOWN_TRUNCATED_HOST = "https://onrender.com"

REQUIRED_ENDPOINTS = {
    "health": "/v1/health",
    "capabilities": "/v1/capabilities",
    "tools": "/v1/tools",
    "openapi": "/openapi.json",
    "discovery": "/.well-known/continuity-works.json",
    "serviceability": "/v1/serviceability",
}


class DiscoverabilityFailure(RuntimeError):
    pass


def _normalize_frontend(frontend: str) -> str:
    return frontend.rstrip("/") + "/"


def _request_text(url: str, timeout: int = 30) -> str:
    req = Request(
        url,
        headers={
            "Accept": "text/plain,text/html,application/json;q=0.9,*/*;q=0.1",
            "User-Agent": "ContinuityWorks-AgentDiscoverability/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise DiscoverabilityFailure(f"{url} returned HTTP {response.status}")
            return response.read().decode("utf-8", "replace")
    except HTTPError as exc:
        raise DiscoverabilityFailure(f"{url} returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise DiscoverabilityFailure(f"Could not fetch {url}: {exc}") from exc


def _request_json(url: str) -> dict:
    text = _request_text(url)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DiscoverabilityFailure(f"{url} did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise DiscoverabilityFailure(f"{url} must return a JSON object")
    return value


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DiscoverabilityFailure(f"Missing discovery file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DiscoverabilityFailure(f"Invalid JSON in discovery file: {path}") from exc
    if not isinstance(value, dict):
        raise DiscoverabilityFailure(f"Discovery file must contain a JSON object: {path}")
    return value


def _assert_no_truncated_host(label: str, text: str) -> None:
    if KNOWN_TRUNCATED_HOST in text:
        raise DiscoverabilityFailure(
            f"{label} contains the known truncated hosting root {KNOWN_TRUNCATED_HOST!r}"
        )


def _expected_endpoints(api: str) -> dict[str, str]:
    base = api.rstrip("/")
    return {name: f"{base}{path}" for name, path in REQUIRED_ENDPOINTS.items()}


def _validate_text_surface(label: str, text: str, api: str, frontend: str) -> None:
    _assert_no_truncated_host(label, text)
    expected = _expected_endpoints(api)
    required_strings = [
        api.rstrip("/"),
        expected["health"],
        expected["capabilities"],
        expected["tools"],
        expected["openapi"],
        expected["discovery"],
    ]
    for value in required_strings:
        if value not in text:
            raise DiscoverabilityFailure(f"{label} does not visibly contain {value}")
    if frontend not in text:
        raise DiscoverabilityFailure(f"{label} does not visibly identify frontend {frontend}")


def _validate_api_json(doc: dict, api: str, frontend: str) -> None:
    expected = _expected_endpoints(api)
    if doc.get("name") != "Continuity Works":
        raise DiscoverabilityFailure("api.json does not identify Continuity Works")
    if str(doc.get("api", "")).rstrip("/") != api.rstrip("/"):
        raise DiscoverabilityFailure("api.json does not identify the canonical executable API")
    if doc.get("frontend") != frontend:
        raise DiscoverabilityFailure("api.json does not identify the canonical frontend")
    for key, value in expected.items():
        if doc.get(key) != value:
            raise DiscoverabilityFailure(f"api.json endpoint {key!r} is not canonical")
    if doc.get("llms") != f"{frontend}llms.txt":
        raise DiscoverabilityFailure("api.json does not publish llms.txt")
    if doc.get("agent") != f"{frontend}ai.json":
        raise DiscoverabilityFailure("api.json does not publish ai.json")
    if doc.get("pages_discovery") != f"{frontend}.well-known/continuity-works.json":
        raise DiscoverabilityFailure("api.json does not publish the Pages-local well-known document")


def _validate_agent_json(doc: dict, api: str, frontend: str) -> None:
    expected = _expected_endpoints(api)
    if doc.get("name") != "Continuity Works" or doc.get("kind") != "agent-discovery":
        raise DiscoverabilityFailure("ai.json does not identify the Continuity Works agent contract")
    if doc.get("frontend") != frontend or doc.get("frontend_is_executable") is not False:
        raise DiscoverabilityFailure("ai.json does not clearly mark GitHub Pages as non-executable")
    if str(doc.get("canonical_api", "")).rstrip("/") != api.rstrip("/"):
        raise DiscoverabilityFailure("ai.json does not identify the canonical executable API")
    endpoints = doc.get("endpoints") or {}
    for key, value in expected.items():
        if endpoints.get(key) != value:
            raise DiscoverabilityFailure(f"ai.json endpoint {key!r} is not canonical")


def _validate_pages_well_known(doc: dict, api: str, frontend: str) -> None:
    expected = _expected_endpoints(api)
    if doc.get("name") != "Continuity Works" or doc.get("kind") != "pages-agent-discovery":
        raise DiscoverabilityFailure("Pages well-known document has the wrong identity")
    if doc.get("surface") != "static" or doc.get("executable") is not False:
        raise DiscoverabilityFailure("Pages well-known document does not mark the surface as static")
    if doc.get("frontend") != frontend:
        raise DiscoverabilityFailure("Pages well-known document has the wrong frontend")
    if str(doc.get("api", "")).rstrip("/") != api.rstrip("/"):
        raise DiscoverabilityFailure("Pages well-known document has the wrong API")
    endpoints = doc.get("endpoints") or {}
    for key, value in expected.items():
        if endpoints.get(key) != value:
            raise DiscoverabilityFailure(f"Pages well-known endpoint {key!r} is not canonical")


def _validate_bundle(
    *,
    html: str,
    llms: str,
    api_doc: dict,
    agent_doc: dict,
    pages_doc: dict,
    api: str,
    frontend: str,
) -> dict:
    frontend = _normalize_frontend(frontend)
    api = api.rstrip("/")
    for label, text in (
        ("index.html", html),
        ("llms.txt", llms),
        ("api.json", json.dumps(api_doc, sort_keys=True)),
        ("ai.json", json.dumps(agent_doc, sort_keys=True)),
        ("Pages well-known discovery", json.dumps(pages_doc, sort_keys=True)),
    ):
        _assert_no_truncated_host(label, text)

    _validate_text_surface("index.html", html, api, frontend)
    _validate_text_surface("llms.txt", llms, api, frontend)

    for relative in (
        "./llms.txt",
        "./ai.json",
        "./api.json",
        "./.well-known/continuity-works.json",
    ):
        if relative not in html:
            raise DiscoverabilityFailure(f"index.html does not link {relative}")

    _validate_api_json(api_doc, api, frontend)
    _validate_agent_json(agent_doc, api, frontend)
    _validate_pages_well_known(pages_doc, api, frontend)

    return {
        "gate": "AGENT_DISCOVERABILITY",
        "status": "VERIFIED",
        "frontend": frontend,
        "api": api,
        "entrypoints": [
            frontend,
            f"{frontend}llms.txt",
            f"{frontend}ai.json",
            f"{frontend}api.json",
            f"{frontend}.well-known/continuity-works.json",
        ],
    }


def verify_static(directory: str, expected_api: str, expected_frontend: str) -> dict:
    root = Path(directory)
    index = root / "index.html"
    llms = root / "llms.txt"
    api_json = root / "api.json"
    agent_json = root / "ai.json"
    pages_well_known = root / ".well-known" / "continuity-works.json"

    for path in (index, llms, api_json, agent_json, pages_well_known):
        if not path.is_file():
            raise DiscoverabilityFailure(f"Static discovery bundle is missing {path}")

    return _validate_bundle(
        html=index.read_text(encoding="utf-8"),
        llms=llms.read_text(encoding="utf-8"),
        api_doc=_load_json(api_json),
        agent_doc=_load_json(agent_json),
        pages_doc=_load_json(pages_well_known),
        api=expected_api,
        frontend=_normalize_frontend(expected_frontend),
    )


def verify_pages(pages_url: str, expected_api: str, expected_frontend: str) -> dict:
    pages = _normalize_frontend(pages_url)
    expected_frontend = _normalize_frontend(expected_frontend)
    if pages != expected_frontend:
        raise DiscoverabilityFailure(
            f"Pages URL {pages!r} does not match expected frontend {expected_frontend!r}"
        )

    return _validate_bundle(
        html=_request_text(pages),
        llms=_request_text(urljoin(pages, "llms.txt")),
        api_doc=_request_json(urljoin(pages, "api.json")),
        agent_doc=_request_json(urljoin(pages, "ai.json")),
        pages_doc=_request_json(urljoin(pages, ".well-known/continuity-works.json")),
        api=expected_api,
        frontend=expected_frontend,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Continuity Works can be discovered by a zero-JavaScript uninformed agent."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--static-dir")
    group.add_argument("--pages")
    parser.add_argument("--expected-api", default=DEFAULT_API)
    parser.add_argument("--expected-frontend", default=DEFAULT_FRONTEND)
    args = parser.parse_args()

    try:
        if args.static_dir:
            result = verify_static(
                args.static_dir,
                expected_api=args.expected_api,
                expected_frontend=args.expected_frontend,
            )
        else:
            result = verify_pages(
                args.pages,
                expected_api=args.expected_api,
                expected_frontend=args.expected_frontend,
            )
    except DiscoverabilityFailure as exc:
        print(
            json.dumps(
                {
                    "gate": "AGENT_DISCOVERABILITY",
                    "status": "FAIL",
                    "message": str(exc),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
