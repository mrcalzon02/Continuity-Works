# PUBLIC_SERVICEABILITY Contract

StructureSmith distinguishes implementation from external availability. A capability is **not externally available** merely because a Python method exists, it appears in `/v1/tools`, or it works on localhost. It is externally callable only after a clean remote client can discover the canonical HTTPS service and invoke it successfully.

## Three public surfaces

These are separate products and must never be conflated:

- Human frontend: `https://mrcalzon02.github.io/StructureSmith/`
- Executable API: `https://structuresmith-mrcalzon02-api.onrender.com/`
- Machine discovery on the executable API: `/openapi.json`, `/v1/tools`, `/.well-known/structuresmith.json`, `/v1/serviceability`

GitHub Pages is static. It must not imply that `/v1/*` executes on the Pages origin.

## Canonical capability publication matrix

`structure_capability.publication.PUBLIC_CAPABILITIES` is the publication registry. Every externally intended tool-catalog entry must declare, in one place: tool name, Python `StructureCapability` method, HTTP method, canonical route, argument mode, and manual UI state/surface.

The OpenAPI route table and public publication metadata are derived from this registry. A tool-catalog entry without a matching publication record is `internal_unpublished` and causes the local `PUBLIC_SERVICEABILITY` gate to fail.

## Deployment state is not implementation state

Public `/v1/tools` entries carry separate `implementation`, `http_route`, `canonical_endpoint`, `public_deployment`, `external_verification`, `manual_ui`, and `publication_state` fields. Local validation may produce `READY_FOR_REMOTE_VERIFICATION`; it never upgrades itself to `VERIFIED`. External verification is performed from outside the service.

## Build identity

`GET /v1/health` returns service name, API version, installed package version, tool schema version, deployed Git commit, deployment environment, and API/frontend addresses. On Render, the commit comes from platform-provided `RENDER_GIT_COMMIT`; this lets acceptance tests reject a healthy but stale deployment.

## Zero-JavaScript discovery

The source `index.html` contains absolute API metadata and visible service addresses. Vite copies/builds a static `api.json` into the Pages artifact. A crawler that executes no React, WebGL, or JavaScript can therefore learn the executable API, health endpoint, tool catalog, OpenAPI document, and discovery document.

The manual web workbench obtains its available capability list from the live `/v1/tools` publication catalog. It does not maintain a separate handwritten advertised list.

## CORS

Browser usability is part of the public API contract. The production service must accept at least `https://mrcalzon02.github.io`. Additional supported production UI origins can be added through `STRUCTURESMITH_CORS_ORIGIN` as a comma-separated set. Remote acceptance sends an Origin header and fails `CORS_REJECTED` if the allow-origin header is absent or wrong.

## Deterministic failure codes

The external `PUBLIC_SERVICEABILITY` gate uses: `API_HOST_UNREACHABLE`, `DISCOVERY_MISSING`, `TOOL_ROUTE_MISSING`, `OPENAPI_MISMATCH`, `CORS_REJECTED`, `FRONTEND_STALE`, and `DEPLOYMENT_COMMIT_MISMATCH`. Local-only structural checks may additionally report `IMPLEMENTATION_MISSING`, `CATALOG_MISMATCH`, or `MANUAL_UI_UNCLASSIFIED`.

## Promotion sequence

**implement → unit test → API contract test → frontend build → local HTTP smoke → commit → deploy API → remote API smoke → deploy Pages → Pages-to-API discovery test → external-service VERIFIED**

`.github/workflows/validate.yml` handles the pre-deployment gates. Render deploys `main` only after checks pass. `.github/workflows/public-service.yml` waits until Render reports the exact target commit, runs remote API acceptance, builds/stamps the Pages artifact, deploys it explicitly, then begins with only the Pages URL and follows the raw discovery chain to invoke `minecraft_version`.

The final workflow publishes GitHub status context `structuresmith/public-serviceability`. Only a success status means **external-service VERIFIED**.

## External acceptance commands

```bash
python scripts/public_serviceability.py \
  --api https://structuresmith-mrcalzon02-api.onrender.com \
  --expected-commit <git-sha> \
  --origin https://mrcalzon02.github.io
```

Gemini-style discovery beginning with only the Pages URL:

```bash
python scripts/public_serviceability.py \
  --pages https://mrcalzon02.github.io/StructureSmith/ \
  --expected-commit <git-sha>
```

Static artifact validation before Pages deployment:

```bash
python scripts/public_serviceability.py --static-dir dist
```

## Pages publishing source

The repository contains an explicit `actions/configure-pages` → `actions/upload-pages-artifact` → `actions/deploy-pages` workflow. The repository's GitHub Pages setting must use **GitHub Actions** as its publishing source; branch-root publishing is intentionally no longer the authoritative deployment method.
