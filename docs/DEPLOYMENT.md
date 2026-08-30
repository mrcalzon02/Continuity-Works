# Continuity Works API Deployment

Continuity Works keeps the human frontend and executable capability runtime separate:

```text
Gemini / ChatGPT / external client
                |
                v
Continuity Works API runtime
                |
                v
StructureCapability -> generators/content tools

GitHub Pages StructureForge frontend
                |
                +---------> same API contract when a runtime is configured
```

GitHub Pages remains a static frontend host. It does not execute Python and must never be treated as the runtime location for `/v1/*`.

## Naming convention

The public service identity is **Continuity Works**. Canonical machine names are:

```text
slug: continuity-works
OpenAPI vendor extension: x-continuity-works
OpenAPI tool extension: x-continuity-works-tool
discovery: /.well-known/continuity-works.json
environment prefix: CONTINUITY_WORKS_*
status prefix: continuity-works/*
```

The old `/.well-known/structuresmith.json` path is retained only as an unadvertised migration alias. Old `STRUCTURESMITH_*` environment variables are accepted only as compatibility fallbacks.

## Configured deployment candidate

The repository contains an optional `render.yaml` reference definition named `continuity-works-mrcalzon02-api`. It is configuration only: the repository does **not** claim that a Render account or public service has been activated.

Configured candidate base URL:

```text
https://continuity-works-mrcalzon02-api.onrender.com
```

The runtime uses the existing dependency-free `structure_capability.server` implementation. `scripts/run_api.py` binds to `0.0.0.0` and reads the provider-assigned `PORT` environment variable. A different host can set `CONTINUITY_WORKS_PUBLIC_BASE_URL` and `CONTINUITY_WORKS_FRONTEND_URL` without changing the API implementation.

Continuity Works does not require the project owner to provide free public compute. A consuming client or integrator may run the Python service locally or on infrastructure it controls. Server-side visual rendering is not part of the API contract; clients render returned geometry using their own resources when desired.

## Machine discovery

External clients should begin with one of these machine-readable endpoints on the runtime they are using:

```text
GET /.well-known/continuity-works.json
GET /openapi.json
GET /v1/tools
GET /v1/health
GET /v1/serviceability
```

`/.well-known/continuity-works.json` points to health, OpenAPI, and the portable Continuity Works tool catalog. `/openapi.json` is OpenAPI 3.1 and mirrors the actual dependency-free HTTP handler. Tool request schemas are taken from the authoritative `tool_catalog()` definitions rather than duplicated into another framework.

The public capability routes include:

```text
GET  /v1/health
GET  /v1/serviceability
GET  /v1/capabilities
GET  /v1/tools
GET  /v1/tools/index
GET  /v1/tools/{tool_name}
GET  /v1/presets
GET  /v1/presets/{preset_id}
POST /v1/resolve
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
POST /v1/minecraft/advancement
POST /v1/minecraft/tag
POST /v1/minecraft/datapack-manifest
POST /v1/minecraft/content-package
POST /v1/minecraft/icon
POST /v1/resume
```

## External-agent usage

Against any running Continuity Works base URL:

```bash
curl -fsS "$CONTINUITY_WORKS_API/v1/tools"
curl -fsS "$CONTINUITY_WORKS_API/openapi.json"
```

A real infrastructure call:

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
  "$CONTINUITY_WORKS_API/v1/infrastructure/layout"
```

For Gemini or another tool-calling client, use `/v1/tools` as the portable function catalog or import `/openapi.json` where the client supports OpenAPI tooling. Capability execution continues to flow through the existing internal `StructureCapability`; that internal class name is an implementation detail, not the public product name.

## CORS

The default browser origin allowed by the API is:

```text
https://mrcalzon02.github.io
```

Additional trusted origins can be supplied as a comma-separated `CONTINUITY_WORKS_CORS_ORIGIN` environment value. `*` remains available only when explicitly configured.

## Local run

After installing the project:

```bash
python -m pip install -e .
HOST=0.0.0.0 PORT=8787 python scripts/run_api.py
```

Then run the same reusable smoke harness used by CI:

```bash
python scripts/http_smoke.py http://127.0.0.1:8787
python scripts/public_serviceability.py --api http://127.0.0.1:8787
```

A remote host is not declared externally verified until the same acceptance harness succeeds against that actual host. Static GitHub Pages output is never accepted as Python API execution proof.
