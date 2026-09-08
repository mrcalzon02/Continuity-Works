# Continuity Works Blueprint Runtime Budget

The in-game blueprint builder is deliberately deterministic and lightweight. Continuity Works does **not** embed a neural model, tokenizer, vector database, ONNX runtime, native inference library, or model weights. Semantic inference belongs to the optional consuming mod (for example Alfheim Companion); Continuity Works receives compact planning intent and resolves it with deterministic Java code and bundled architectural data.

## Resource contract

The architectural target is comfortably below a 1 GiB Continuity Works overhead inside the Minecraft JVM, with normal blueprint-planning overhead expected to be far smaller. Exact heap impact must be measured in a Forge runtime before making a numerical runtime claim.

The current provider enforces:

- at most 3 active or queued blueprint requests globally;
- at most 4,096 completed blueprint generations in one runtime session;
- at most 32 semantic specifications per request;
- at most 32 site candidates per request;
- at most 512 material-availability rows per request;
- at most 32 permitted style identifiers per request;
- only 16 recent material manifests retained by the budgeted provider.

The current deterministic planner already uses one daemon planning worker and hard spatial caps. The budgeted provider sits in front of it so untrusted or tiny-model callers cannot create unbounded request fan-out or giant semantic input lists.

## Pre-solved-first direction

The next planner layer should resolve purpose, `REFERENCE`, `ARCHETYPE`, or `CATEGORY` against the bundled facility corpus and load only the small manifest plus the selected reference/palette. It must not hydrate the whole architectural corpus, create embeddings, or add a model runtime. Fixed corpus references should be compiled directly into the same `BlueprintProposal` contract and fall back to the existing bounded procedural kernel when no pre-solved reference fits.

## Memory discipline

Blueprint block lists are request products, not permanent world memory. The consumer should retain the blueprint UUID, objective, location, progress, and modifications rather than duplicating the full operation list in companion memory. World scans stay on the Minecraft server thread; deterministic planning runs away from that thread against immutable request/snapshot data.

The sub-1 GiB requirement is a hard architectural ceiling, not permission to consume close to 1 GiB. Any future feature that introduces model weights, bulk corpus hydration, unbounded queues/caches, or unconstrained operation expansion violates this runtime contract.
