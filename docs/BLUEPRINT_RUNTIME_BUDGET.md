# Continuity Works Blueprint Runtime Budget

The in-game blueprint builder is deliberately deterministic and lightweight. Continuity Works does **not** embed a neural model, tokenizer, vector database, ONNX runtime, native inference library, or model weights. Semantic inference belongs to the optional consuming mod (for example Alfheim Companion); Continuity Works receives compact planning intent and resolves it with deterministic Java code and bundled architectural data.

## Resource contract

The architectural target is comfortably below a 1 GiB Continuity Works overhead inside the Minecraft JVM, with normal blueprint-planning overhead expected to be far smaller. Exact heap impact must be measured in a Forge runtime before making a numerical runtime claim.

The provider enforces at most 3 active or queued requests, 4,096 completed generations in one runtime session, 32 semantic specifications, 32 site candidates, 512 material rows, and 32 permitted styles per request. Corpus planning examines at most 8 candidate references and refuses to expand more than 131,072 placement operations for one proposal.

## Lazy pre-solved corpus

The budgeted provider first attempts a deterministic pre-solved match against the bundled facility library. `REFERENCE`, `ARCHETYPE`, and `CATEGORY` are open semantic selectors so small inference engines can request known construction families without learning raw block geometry. The manifest index is loaded once; the runtime opens at most eight candidate reference JSON files and then loads only the selected corporate palette. It does not hydrate the full corpus, create embeddings, or add a model runtime.

Fixed references support the existing `block`, `fill_box`, `hollow_box`, `line`, and `cylinder` blueprint primitives, are rotated to the requested facing, must fit the caller's hard `ConstructionVolume`, and compile into the same `BlueprintProposal` contract. If no suitable pre-solved reference exists, Continuity Works falls back to the existing bounded procedural planner.

Geometry-changing fields such as `STYLE`, `ROOF`, `FLOORS`, and `ENTRANCE` normally route to the procedural fallback rather than pretending a fixed corpus reference can mutate itself. Required unsupported fields remain visible through the specification-resolution/warning contract.

## Memory discipline

Blueprint block lists are request products, not permanent companion memory. The consumer should retain the blueprint UUID, objective, location, progress, and modifications rather than duplicate the full operation list. World scans stay on the Minecraft server thread; planning runs on a single low-priority daemon worker against immutable request/snapshot data.

The sub-1 GiB requirement is a hard architectural ceiling, not permission to consume close to 1 GiB. Future model weights, bulk corpus hydration, unbounded queues/caches, or unconstrained operation expansion violate this runtime contract.
