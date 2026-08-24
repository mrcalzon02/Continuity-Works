# Public API Deployment

StructureSmith has two deliberately separate deployment surfaces:

```text
Gemini / ChatGPT / external client
                |
                v
public HTTPS StructureSmith API
                |
                v
StructureCapability -> generators/content tools

GitHub Pages StructureForge frontend
                |
                +---------> same public HTTPS StructureSmith API
```

GitHub Pages remains a static frontend host. It does not execute Python and must never be treated as the runtime location for `/v1/*`.

## Configured production service

The repository includes `render.yaml` for a persistent Render Python web service named `structuresmith-mrcalzon02-api`.

Configured public base URL:

```text
https://structuresmith-mrcalzon02-api.onrender.com
```

The service uses the existing dependency-free `structure_capability.server` implementation. Render starts `scripts/run_api.py`, which binds to `0.0.0.0` and reads the provider-assigned `PORT` environment variable.

`render.yaml` selects the `starter` plan so the API is intended to remain resident rather than relying on a free service that can spin down. The health check is `/v1/health`, and deployment is configured from the authoritative `main` branch after checks pass.

A Render account must perform the one-time Blueprint connection/creation for this repository. Repository configuration alone cannot create a service in an unrelated hosting account. After that connection, pushes to `main` can deploy automatically through the Blueprint configuration.

If Render assigns a different hostname, update `frontend/src/config/runtime.js` or define `globalThis.STRUCTURESMITH_API_BASE_URL` before StructureForge starts. The server also accepts `STRUCTURESMITH_PUBLIC_BASE_URL` when an explicit canonical external URL is needed in generated discovery/OpenAPI metadata.

## Machine discovery

External clients should begin with one of these machine-readable endpoints:

```text
GET /.well-known/structuresmith.json
GET /openapi.json
GET /v1/tools
GET /v1/health
```

`/.well-known/structuresmith.json` points to health, OpenAPI, and the portable StructureSmith tool catalog. `/openapi.json` is OpenAPI 3.1 and mirrors the actual dependency-free HTTP handler. Tool request schemas are taken from the authoritative `tool_catalog()` definitions rather than duplicated into a separate framework.

The public capability routes are:

```text
GET  /v1/health
GET  /v1/capabilities
GET  /v1/tools
POST /v1/inventory
POST /v1/audit
POST /v1/plan
POST /v1/generate
POST /v1/dungeon/layout
POST /v1/infrastructure/layout
POST /v1/minecraft/version
POST /v1/minecraft/registry/probe
POST /v1/minecraft/book
POST /v1/minecraft/loot-table
POST /v1/minecraft/recipe
POST /v1/minecraft/icon
POST /v1/resume
```

## External-agent usage

Retrieve the catalog:

```bash
curl -fsS https://structuresmith-mrcalzon02-api.onrender.com/v1/tools
```

Retrieve the OpenAPI description:

```bash
curl -fsS https://structuresmith-mrcalzon02-api.onrender.com/openapi.json
```

Execute a real infrastructure capability:

```bash
curl -fsS \
  -H 'Content-Type: application/json' \
  -d '{
    "module_type":"inner_city_road",
    "seed":20260824,
    "world_seed":20260824,
    "road":{"width":6,"terrain_padding":5},
    "purpose":{"depth":3}
  }' \
  https://structuresmith-mrcalzon02-api.onrender.com/v1/infrastructure/layout
```

For Gemini or another tool-calling client, use `/v1/tools` as the portable function catalog or import `/openapi.json` where the client supports OpenAPI tooling. Capability execution continues to flow through the existing `StructureCapability`; the HTTP layer does not replace its validation, registry, generation, snapshot, or content-tool logic.

## CORS

The default browser origin allowed by the API is exactly:

```text
https://mrcalzon02.github.io
```

This permits the GitHub Pages StructureForge frontend to call the public API without opening browser access to arbitrary origins. Additional trusted origins can be supplied as a comma-separated `STRUCTURESMITH_CORS_ORIGIN` environment value. `*` is still supported only when explicitly configured and is not the production default.

## Local production-equivalent run

After installing the project:

```bash
python -m pip install -e .
HOST=0.0.0.0 PORT=8787 python scripts/run_api.py
```

On PowerShell:

```powershell
$env:HOST='0.0.0.0'
$env:PORT='8787'
python scripts/run_api.py
```

Then run the same reusable smoke harness used by CI and by public deployment validation:

```bash
python scripts/http_smoke.py http://127.0.0.1:8787
```

After the HTTPS service is active, the completion proof is the same command against the public host:

```bash
python scripts/http_smoke.py https://structuresmith-mrcalzon02-api.onrender.com
```

The smoke test requires health, tool catalog, OpenAPI, discovery metadata, and a successful real `/v1/infrastructure/layout` execution. A static GitHub Pages response is never accepted as API proof.
