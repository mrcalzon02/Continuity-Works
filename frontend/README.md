# StructureForge interactive frontend

This directory contains the browser interface for the **StructureForge** product surface built on the **StructureSmith** structural-reasoning system.

The published GitHub Pages root (`/index.html`) intentionally uses browser-native ES modules and pinned ESM dependencies so the workbench can deploy from the repository's existing branch-based Pages configuration without introducing a second build/deployment system. The modules are still ordinary React components and can be moved behind Vite or another bundler later without changing the event contract.

## Runtime architecture

```text
index.html
└─ frontend/src/main.js
   └─ Dashboard
      ├─ XState pipeline machine
      ├─ Control schema / API request builder
      ├─ StructureSmith HTTP API client
      ├─ Serialized event player + SSE/WebSocket adapters
      └─ React Three Fiber voxel viewport
```

Pipeline state is deliberately explicit:

```text
Idle → Prompting → Drafting → Auditing → Rebuilding → Finalizing
```

Controls lock as the relevant stage begins. By default, execution also pauses after each completed stage so a human can inspect the geometry, decision-rationale feed, and audit image frames before advancing.

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

The current StructureSmith server is synchronous. **Live API + serialized replay** calls the existing `/v1/generate`, `/v1/audit`, `/v1/plan`, and `/v1/minecraft/version` endpoints and then replays returned milestones at human-readable speed. `connectSSE()` and `connectWebSocket()` are already stubbed so a future native streaming backend can feed the same components without rewriting the UI.

The published demo mode requires no backend and is the safest way to inspect the frontend interaction model.

## Browser access / CORS

The paired server change adds browser-safe CORS/OPTIONS handling. The default is `Access-Control-Allow-Origin: *`, appropriate for the current unauthenticated local/tool API. Deployments that want a narrower browser policy can set `STRUCTURESMITH_CORS_ORIGIN` to one origin or a comma-separated allowlist, for example:

```bash
STRUCTURESMITH_CORS_ORIGIN=https://mrcalzon02.github.io python -m structure_capability.cli serve
```

## Optional Vite workflow

The committed Pages entry remains directly runnable from the repository root, but the same modules also have a pinned Vite manifest for local development or a future compiled deployment:

```bash
cd frontend
npm install
npm run dev
# or: npm run build
```

The Vite build uses the repository root `index.html` as its entry and emits to `dist/` with the correct `/StructureSmith/` base path.
