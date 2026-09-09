# Continuity Works Blueprint Runtime Budget

The in-game blueprint builder is deliberately deterministic and lightweight. Continuity Works does **not** embed a neural model, tokenizer, vector database, ONNX runtime, native inference library, or model weights. Semantic inference belongs to the optional consuming mod (for example Alfheim Companion); Continuity Works receives compact planning intent and resolves it with deterministic Java code and bundled architectural data.

## Resource contract

The architectural target is comfortably below a 1 GiB Continuity Works overhead inside the Minecraft JVM, with normal blueprint-planning overhead expected to be far smaller. Exact heap impact must be measured in a Forge runtime before making a numerical runtime claim.

The provider enforces at most 3 active or queued requests, 4,096 completed generations in one runtime session, 32 semantic specifications, 32 site candidates, 512 material rows, and 32 permitted styles per request. Corpus planning examines at most 8 candidate references and refuses to expand more than 131,072 placement operations for one proposal.

## Tiny-inference control assumption

The reference integration assumption is a **Qwen 2.5 Instruct Q4-class** local controller or another comparably small real-time inference engine. This is a reference workload profile, not a model dependency: Continuity Works remains model-agnostic and does not ship model weights.

The inference controller receives an absolute **64-token output ceiling per decision call**, with roughly 32 tokens preferred for normal operation. The system must never depend on a single inference producing a complete structure description. Instead, a generation decision is accumulated through consecutive bounded semantic mutations while rich state remains outside the model context/output budget.

The invariant is:

> **Inference selects. State accumulates. Catalog defines. Generator builds. Validator decides legality.**

The model does not emit blocks, NBT, commands, primitive geometry, jigsaw pieces, collision rules, exclusion geometry, loot-table bodies, or materialized structures. Those remain deterministic Continuity Works responsibilities.

## Decision-chain and mutator contract

`BlueprintDecisionChain` is the compact decision state machine exposed by `ContinuityWorksCompactBlueprintApi`. Its protocol version is `cw-decision-1`. A caller begins a decision state, requests the currently dependency-valid next mutators, performs one or more tiny inferences, applies the returned compact mutations, validates accumulated state, and finalizes the accepted selections into semantic `BlueprintSpecification` values before deterministic generation.

The initial mutation vocabulary is deliberately terse:

| Code | Meaning | Value source | Dependency |
|---|---|---|---|
| `A` | archetype/catalog ID | authoritative structure catalog | none |
| `Z` | scale | fixed `S/M/L` | `A` |
| `B` | biome/environment profile | selected archetype | `A` |
| `C` | culture variant | selected archetype | `A` |
| `F` | family mode | fixed `I/P` (independent / same-parent family) | `A` |
| `O` | orientation | fixed `AUTO/N/E/S/W` | `B` |
| `Q` | condition/state | selected archetype | `A` |
| `K` | palette profile | selected archetype + biome | `A,B` |
| `D` | detail density | fixed `L/N/H` | `A,Z` |

The normal inference output is therefore a tiny string such as `A=E01-017`, `Z=M`, or `B=riverbank;F=I`. Up to four semantic mutations are permitted in one response, but one mutation per inference is preferred when the next decision depends on the previous result.

Changing an upstream choice invalidates only its dependent downstream choices. For example, changing `B` invalidates `O` and `K` but preserves independent decisions such as `Z` and `F`; changing `A` invalidates all archetype-dependent selections. This makes correction cheap and prevents a repair from rebuilding an entire decision tree.

The decision state, revision counter, accumulated selections, validation findings, catalog metadata and eventual generated structure are **not** charged against the model's 64-token output budget. Only the compact model response is budgeted. Seed derivation should normally remain deterministic from caller/world/request context rather than wasting inference tokens on arbitrary random numbers; a consuming integration may deliberately expose seed selection only when variation itself is a user-visible decision.

## Decision API surface

`ContinuityWorksCompactBlueprintApi` exposes the chain without requiring a second implementation:

- `decisionProfile()` — protocol version, reference inference profile, token ceilings, principles and mutator graph;
- `beginDecision(request)` — create deterministic state associated with the request ID;
- `nextDecision(state)` — expose only dependency-valid next semantic mutators and a compact prompt hint;
- `applyDecision(state, encodedMutations)` — parse/apply a bounded mutation response;
- `validateDecision(state)` — deterministic semantic/dependency validation without geometry generation;
- `finalizeDecision(state)` — freeze valid selections into semantic `BlueprintSpecification` values.

The existing compact edit surface remains complementary. `BlueprintDecisionChain` decides *what kind of structure should be generated* while `CompactEditIntent` performs bounded plan-level edits such as translate, rotate, mirror, palette remap, compose and repeat after a plan exists. Neither surface permits raw world mutation instructions from inference.

## Lazy pre-solved corpus

The budgeted provider first attempts a deterministic pre-solved match against the bundled facility library. `REFERENCE`, `ARCHETYPE`, and `CATEGORY` are open semantic selectors so small inference engines can request known construction families without learning raw block geometry. The manifest index is loaded once; the runtime opens at most eight candidate reference JSON files and then loads only the selected corporate palette. It does not hydrate the full corpus, create embeddings, or add a model runtime.

Fixed references support the existing `block`, `fill_box`, `hollow_box`, `line`, and `cylinder` blueprint primitives, are rotated to the requested facing, must fit the caller's hard `ConstructionVolume`, and compile into the same `BlueprintProposal` contract. If no suitable pre-solved reference exists, Continuity Works falls back to the existing bounded procedural planner.

Geometry-changing fields such as `STYLE`, `ROOF`, `FLOORS`, and `ENTRANCE` normally route to the procedural fallback rather than pretending a fixed corpus reference can mutate itself. Required unsupported fields remain visible through the specification-resolution/warning contract.

## Memory discipline

Blueprint block lists are request products, not permanent companion memory. The consumer should retain the blueprint UUID, objective, location, progress, decision state and modifications rather than duplicate the full operation list. World scans stay on the Minecraft server thread; planning runs on a single low-priority daemon worker against immutable request/snapshot data.

The sub-1 GiB requirement is a hard architectural ceiling, not permission to consume close to 1 GiB. Future model weights, bulk corpus hydration, unbounded queues/caches, unconstrained operation expansion, or inference protocols that require large free-form structure output violate this runtime contract.
