# Continuity Works interactive frontend

This directory contains the browser interface for the **Continuity Works** structural-development workbench and public capability surface.

The published GitHub Pages root (`/index.html`) is built through the repository's existing Vite production path. The frontend remains a client of the Continuity Works HTTP API and does not create a second authoritative generation system.

## Runtime architecture

```text
index.html
└─ frontend/src/main.js
   └─ Dashboard
      ├─ XState pipeline machine
      ├─ Control schema / API request builder
      ├─ Continuity Works HTTP API client
      ├─ Serialized event player + SSE/WebSocket adapters
      └─ React Three Fiber voxel viewport
```

Pipeline state is deliberately explicit:

```text
Idle → Prompting → Drafting → Auditing → Rebuilding → Finalizing
```

Controls lock as the relevant stage begins. By default, execution also pauses after each completed stage so a human can inspect the geometry, concise decision-rationale feed, and optional audit image frames before advancing.

## Stream event contract

The UI normalizes demo, HTTP-replay, future SSE, and future WebSocket input into the same shape:

```json
{
  "type": "block | rationale | image | validation",
  "stage": "drafting | auditing | rebuilding | finalizing",
  "message": "short action description",
  "rationale": "short user-facing explanation of why this action was selected",
  "coordinate": { "x": 0, "y": 1, "z": 0 },
  "block": { "id": "minecraft:stone_bricks", "op": "add" }
}
```

`rationale` is intentionally a concise explainability field. It is not intended to expose hidden model chain-of-thought.

## Existing API compatibility

The current Continuity Works server is synchronous. **Live API + serialized replay** calls the existing `/v1/generate`, `/v1/audit`, `/v1/plan`, and `/v1/minecraft/version` endpoints and then replays returned milestones at human-readable speed. `connectSSE()` and `connectWebSocket()` remain available for a future native streaming backend using the same normalized event contract.

The published demo mode requires no backend and remains useful for inspecting the frontend interaction model independently of API availability.

## Browser access / CORS

The paired server supports browser-safe CORS/OPTIONS handling. The canonical configuration variable is `CONTINUITY_WORKS_CORS_ORIGIN`; production deployments should set it to the trusted Pages origin or another explicit comma-separated allowlist.

```bash
CONTINUITY_WORKS_CORS_ORIGIN=https://mrcalzon02.github.io python -m structure_capability.cli serve
```

## Vite workflow

The production frontend uses the committed Vite build:

```bash
cd frontend
npm install
npm run dev
# or: npm run build
```

The build emits to `dist/` using the `/Continuity-Works/` Pages base path and runs the rendered-artifact branding validation before acceptance.
