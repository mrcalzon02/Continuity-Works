# StructureForge Frontend Architecture

## Product boundary

**StructureForge** is the interactive workbench/client name. **Continuity Works** is the underlying reusable structural-reasoning API/system and repository identity.

The frontend is designed as an explainable, collaborative structure-development console rather than a single-button generator. It makes the authoritative lifecycle visible and interruptible: a human can configure constraints, watch geometry appear, inspect concise decision rationales, review optional client-rendered audit views, and explicitly advance between major stages.

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
- optional client-rendered audit image frame;
- validation result.

Events are intentionally queued and played at a selectable human-readable cadence. The default is 700 ms per event, with a slower 1.2-second mode and faster diagnostic modes. The default stage gate is manual: after a stage finishes, the user must explicitly advance.

This is an XAI summary surface, not a raw chain-of-thought viewer. The interface should explain relevant decisions in concise, auditable terms without depending on private model reasoning traces.

## 3D viewport

React Three Fiber owns the central WebGL viewport. The current voxel renderer uses one mesh per demonstration block because the visible sample is intentionally small. A production structure renderer should graduate to chunked instancing / merged geometry once actual NBT-sized artifacts are streamed.

**This browser renderer is deliberately client-side.** Continuity Works is responsible for returning geometry/artifacts/metadata, not for paying to render images or 3D previews for API callers. External clients should follow the same model: render returned three-dimensional information locally or in infrastructure they control.

The normalized block event supports `add`, `replace`, and `remove` semantics. That means drafting, repair, and rebuild can all use the same rendering path.

## Optional audit image viewports

Audit-stage image events can populate three evidence slots in the interface: oblique, plan, and damage-state review. These are a **client presentation feature**, not a Continuity Works server requirement. The demo can create lightweight SVG stand-ins, and a client renderer can create views from returned geometry without changing the API contract.

No API call is required to create these images, and generation must not be blocked because they are absent.

## API and streaming boundary

The existing Python HTTP server is synchronous. The frontend therefore supports three execution patterns conceptually:

1. **Demo stream** — deterministic local events demonstrate the interaction contract with no backend.
2. **Synchronous API + serialized replay** — existing `/v1/*` responses are transformed into readable milestones after the call returns.
3. **Native event stream** — `connectSSE()` and `connectWebSocket()` accept future backend event streams using the same normalized event model.

A native stream should eventually emit events during the real server-side pipeline rather than reconstructing them after completion. That backend extension should be additive and should not replace the existing synchronous API contract used by tool callers. It also must not convert browser rendering into a server-side rendering obligation.

## Control modules

The interface exposes optional dropdown groups for StructureForge Generator, Purpose Model, Auditor, Repair, Renderer, and Validator.

The **StructureForge Renderer** module is local/client functionality. Selecting it controls how the browser presents returned data; it does not request paid visual-generation work from the Continuity Works API host.

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

## Next backend integration increment

A future execution-session/event model may assign a session ID and publish stage/block/rationale events while work is actually occurring, preserving the final snapshot/hash through the existing API. Any richer visual presentation should remain client-side unless a separate, explicitly funded rendering service is introduced by a consuming project.

## Browser API access

The HTTP server handles CORS preflight requests and emits CORS response headers so the Pages workbench can call a Continuity Works server from a browser. Production deployments should use the configured trusted origin allowlist rather than treating browser access as permission to expose unrelated server-side rendering resources.
