# Generation Provider Contract

The core API plans and governs generation. A provider performs concrete geometry authoring.

A conforming provider must:

1. read the full request, audit, context and grade;
2. preserve frozen integration/ID/selector contracts;
3. resolve materials through verified registry inventory;
4. use vanilla-first fallback roles when mod assets are unavailable;
5. derive purpose before decoration;
6. honor physical and access clearances;
7. honor geospatial connectors and exclusion zones;
8. obey grade mutation limits;
9. save a snapshot after each verified coherent batch;
10. run target-relevant static/mechanical validation;
11. export the shipping artifact deterministically where format permits;
12. return sufficient geometry/artifact metadata for a consuming client to inspect or render the result;
13. never require StructureSmith's server to create visual renders or perform visual approval;
14. return exact changed files/artifacts, checks, uncertainties and next action.

Visual rendering and visual review are **optional client concerns**, not provider promotion gates. A browser, desktop tool, game/editor integration, Gemini/ChatGPT client, or other consumer may render the returned three-dimensional information using compute it owns. StructureForge is the reference browser-side implementation of this boundary.

A client may impose its own visual-review policy for its own project. That client-side policy does not become a mandatory StructureSmith API gate and must not cause the public StructureSmith service to allocate visual-generation compute on the caller's behalf.

The provider may be:
- deterministic procedural Python;
- Codex/agent tooling;
- an editor bridge;
- a WorldEdit/Amulet integration;
- an external build model;
- a project-specific procedural grammar.

The contract, not the provider implementation, is the API boundary.
