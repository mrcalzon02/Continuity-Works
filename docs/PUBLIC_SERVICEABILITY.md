# PUBLIC_SERVICEABILITY Contract

Continuity Works distinguishes implementation from external availability. A capability is **not externally available** merely because a Python method exists, it appears in `/v1/tools`, or it works on localhost. It is externally callable only after a clean remote client can discover the canonical HTTPS service and invoke it successfully.

## Three public surfaces

These are separate surfaces and must never be conflated:

- Human frontend: `https://mrcalzon02.github.io/Continuity-Works/`
- Configured executable API candidate: `https://continuity-works-mrcalzon02-api.onrender.com/`
- Machine discovery on the executable API: `/openapi.json`, `/v1/tools`, `/.well-known/continuity-works.json`, `/v1/serviceability`

GitHub Pages is static. It must not imply that `/v1/*` executes on the Pages origin.

## Canonical naming contract

The public product/service name is **Continuity Works** and the machine slug is `continuity-works`.

Canonical machine-facing names use:

- OpenAPI vendor extension: `x-continuity-works`
- Per-operation tool extension: `x-continuity-works-tool`
- Environment prefix: `CONTINUITY_WORKS_*`
- Discovery endpoint: `/.well-known/continuity-works.json`
- GitHub status prefix: `continuity-works/*`

The retired `/.well-known/structuresmith.json` path may remain temporarily as an unadvertised compatibility alias, but responses identify Continuity Works and point clients to the canonical Continuity Works discovery URL. Legacy `STRUCTURESMITH_*` environment variables are read only as migration fallbacks and are not the documented convention.

## Canonical capability publication matrix

`structure_capability.publication.PUBLIC_CAPABILITIES` is the publication registry. Every externally intended tool-catalog entry must declare, in one place: tool name, Python `StructureCapability` method, HTTP method, canonical route, argument mode, and manual UI state/surface.

The OpenAPI route table and public publication metadata are derived from this registry. A tool-catalog entry without a matching publication record is `internal_unpublished` and causes the local `PUBLIC_SERVICEABILITY` gate to fail.

## Deployment state is not implementation state

Public `/v1/tools` entries carry separate `implementation`, `http_route`, `canonical_endpoint`, `public_deployment`, `external_verification`, `manual_ui`, and `publication_state` fields under `x-continuity-works`. Local validation may produce `READY_FOR_REMOTE_VERIFICATION`; it never upgrades itself to `VERIFIED`. External verification is performed from outside the service.

## Build identity

`GET /v1/health` returns `service: "Continuity Works"`, `service_slug: "continuity-works"`, API version, installed package version, tool schema version, deployed Git commit, deployment environment, and API/frontend addresses. Platform-provided deployment commit metadata lets acceptance tests reject a healthy but stale deployment.

## Zero-JavaScript discovery

The source `index.html` contains absolute Continuity Works API metadata and visible service addresses. Vite copies/builds a static `api.json` into the Pages artifact. A crawler that executes no React, WebGL, or JavaScript can therefore learn the executable API, health endpoint, tool catalog, OpenAPI document, and discovery document.

The manual StructureForge workbench obtains its available capability list from the live `/v1/tools` Continuity Works publication catalog. It does not maintain a separate handwritten advertised list.

## CORS

Browser usability is part of the public API contract. The service must accept at least `https://mrcalzon02.github.io` when the Pages client is being used. Additional supported origins can be added through `CONTINUITY_WORKS_CORS_ORIGIN` as a comma-separated set. The old `STRUCTURESMITH_CORS_ORIGIN` name is accepted only as a migration fallback.

## Deterministic failure codes

The external `PUBLIC_SERVICEABILITY` gate uses: `API_HOST_UNREACHABLE`, `DISCOVERY_MISSING`, `TOOL_ROUTE_MISSING`, `OPENAPI_MISMATCH`, `CORS_REJECTED`, `FRONTEND_STALE`, and `DEPLOYMENT_COMMIT_MISMATCH`. Local-only structural checks may additionally report `IMPLEMENTATION_MISSING`, `CATALOG_MISMATCH`, or `MANUAL_UI_UNCLASSIFIED`.

## Promotion sequence

**implement → unit test → API contract test → frontend build → local HTTP smoke → commit → optional API deployment → remote API smoke → deploy Pages → Pages-to-API discovery test → external-service VERIFIED**

`.github/workflows/validate.yml` handles the local/pre-deployment gates. `.github/workflows/public-service.yml` performs remote verification only when a configured external host actually serves the target commit.

The final remote workflow publishes GitHub status context `continuity-works/public-serviceability`. Only a success status means **external-service VERIFIED**.

## External acceptance commands

```bash
python scripts/public_serviceability.py \
  --api https://continuity-works-mrcalzon02-api.onrender.com \
  --expected-commit <git-sha> \
  --origin https://mrcalzon02.github.io
```

Discovery beginning with only the Pages URL:

```bash
python scripts/public_serviceability.py \
  --pages https://mrcalzon02.github.io/Continuity-Works/ \
  --expected-commit <git-sha>
```

Static artifact validation before Pages deployment:

```bash
python scripts/public_serviceability.py --static-dir dist
```

## Pages publishing source

The repository contains an explicit `actions/configure-pages` → `actions/upload-pages-artifact` → `actions/deploy-pages` workflow. The repository's GitHub Pages setting must use **GitHub Actions** as its publishing source; branch-root publishing is intentionally no longer the authoritative deployment method.
