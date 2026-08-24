# StructureForge Frontend Architecture

## Product boundary

**StructureForge** is the interactive product/workbench name. **StructureSmith** remains the underlying reusable structural-reasoning system and repository identity.

The frontend is designed as an explainable, collaborative structure-development console rather than a single-button generator. It makes the authoritative lifecycle visible and interruptible: a human can configure constraints, watch geometry appear, inspect concise decision rationales, review generated audit frames, and explicitly advance between major gates.

## State machine

The first implementation uses XState and keeps the required phases first-class:

```text
Idle → Prompting → Drafting → Auditing → Rebuilding → Finalizing
```

The state machine is not cosmetic. Each module declares the latest phase in which its settings remain editable. Once the pipeline has consumed those inputs, the corresponding controls lock. This prevents a user from silently changing a structural contract after a stage has already been evaluated against it.

## Serialized progression

The right-hand progression window consumes normalized events rather than free-form model output. Each event can contain:

- stage;
- action/message;
- concise user-facing rationale;
- block coordinate and block operation;
- audit image frame;
- validation gate result.

Events are intentionally queued and played at a selectable human-readable cadence. The default is 700 ms per event, with a slower 1.2-second mode and faster diagnostic modes. The default stage gate is manual: after a stage finishes, the user must explicitly advance.

This is an XAI summary surface, not a raw chain-of-thought viewer. The interface should explain relevant decisions in concise, auditable terms without depending on private model reasoning traces.

## 3D viewport

React Three Fiber owns the central WebGL viewport. The current voxel renderer uses one mesh per demonstration block because the visible sample is intentionally small. A production structure renderer should graduate to chunked instancing / merged geometry once actual NBT-sized artifacts are streamed.

The normalized block event supports `add`, `replace`, and `remove` semantics. That means drafting, repair, and rebuild can all use the same rendering path.

## Audit image viewports

Audit-stage image events populate three persistent evidence slots in the initial interface: oblique, plan, and damage-state review. The demo creates lightweight SVG stand-ins. A production renderer can replace those with image URLs or signed artifact URLs without changing the component contract.

## API and streaming boundary

The existing Python HTTP server is synchronous. The frontend therefore supports three execution patterns conceptually:

1. **Demo stream** — deterministic local events demonstrate the interaction contract with no backend.
2. **Synchronous API + serialized replay** — existing `/v1/*` responses are transformed into readable milestones after the call returns.
3. **Native event stream** — `connectSSE()` and `connectWebSocket()` accept future backend event streams using the same normalized event model.

A native stream should eventually emit events during the real server-side pipeline rather than reconstructing them after completion. That backend extension should be additive and should not replace the existing synchronous API contract used by tool callers.

## Control modules

The first interface exposes optional dropdown groups for:

- StructureForge Generator;
- StructureForge Purpose Model;
- StructureForge Auditor;
- StructureForge Repair;
- StructureForge Renderer;
- StructureForge Validator.

The generator request preview shows the JSON contract produced by current selections. This lets a human operator see exactly what an AI/API client would submit.

## Recommended production folder structure

```text
frontend/
├─ src/
│  ├─ components/
│  │  ├─ Dashboard.js
│  │  └─ Viewport.js
│  ├─ config/
│  │  └─ controlSchema.js
│  ├─ lib/
│  │  └─ html.js
│  ├─ services/
│  │  ├─ apiClient.js
│  │  └─ streamService.js
│  ├─ state/
│  │  └─ pipelineMachine.js
│  └─ main.js
├─ styles.css
└─ README.md
```

If/when the project adopts a compiled frontend, this structure can be migrated to TypeScript/TSX behind Vite without changing the state machine, stream event contract, API client responsibilities, or component boundaries.

## Next backend integration increment

The highest-leverage next increment is not more frontend decoration. It is a server-side execution-session/event model that assigns a session ID, publishes stage/block/rationale/audit-frame events while work is actually occurring, and preserves the final snapshot/hash result through the existing API. That would convert the current replayable XAI shell into a true live procedural-assembly console.

## Browser API access

The HTTP server now handles CORS preflight requests and emits CORS response headers so the Pages workbench can call a StructureSmith server from a browser. `STRUCTURESMITH_CORS_ORIGIN` can be left at the default `*` for the current unauthenticated development/tool API, or set to a comma-separated origin allowlist for a hosted deployment.
