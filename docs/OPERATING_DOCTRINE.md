# Operating Doctrine

## 1. Authority and single source of truth

Before mutation, identify the authoritative source artifact, builder/generator, integration registry, worldgen binding, loot/proof references, and validation path. Modify those directly. Do not create stacked mutators or shadow registries.

Generated/shipping artifacts are outputs unless the project explicitly declares otherwise.

## 2. Two independent completion tracks

**Functional track:** indexed → parses → registered → integrated → mechanically validated → worldgen/runtime ready.

**Quality track:** baseline → purpose program → massing → circulation → architectural pass → interior/operations → historical/damage pass → detailing → visual review → approved.

One track cannot substitute for the other.

## 3. Existing geometry is evidence, not sacred geometry

At heavy-rebuild levels, a rough structure is a program diagram. Preserve:
- IDs and external contracts;
- good spatial ideas;
- quest/evidence/loot bindings;
- critical approaches/connectors;
- intentionally strong hero spaces.

Do not preserve crude boxes, meaningless symmetry, empty halls, arbitrary stairs/windows, or nonfunctional rooms merely because they already exist.

## 4. Real function first

Ask in order:
1. What is the structure?
2. How would the real-world thing work?
3. What functional zones, access classes, utilities, service routes, exterior infrastructure, emergency routes and clearances does it require?
4. How would this culture/institution build it?
5. What happened to it?
6. How should a player/user discover and navigate that history?

Only then choose blocks.

## 5. Precedent

Major rebuilds should study multiple real facilities of the same functional family. Translate proportionally to a 1 m voxel grid; do not copy literal dimensions that produce unplayable or cardboard architecture.

## 6. Massing before decoration

Silhouette, spans, entrance hierarchy, circulation, floor heights, structural thickness and site relationship precede trapdoors, pipes, furniture and surface clutter.

## 7. Context is part of the structure

A warehouse needs loading/service context. A port needs water and cargo staging. A hospital needs ambulance/service access. A subsea installation needs a navigable approach and seabed fit. A rail building needs plausible rail relationship.

Location-aware generation is not optional metadata.

## 8. Damage is an event, not random deletion

Condition variants should express causes: fire, flood, impact, structural failure, burial, corrosion, biological overgrowth, occupation, scavenging, containment breach, etc. Damage must preserve enough causal/structural information to remain readable.

## 9. Visual review is independent

A render, image metric, hash or serializer success is not visual approval. Persist fixed-camera artifacts and require an independent reviewer (human or explicitly independent review agent) to inspect the exact candidate revision.

## 10. Vanilla first; verified mods second

Use vanilla defaults unless:
- a local mod/namespace is discovered;
- an exact registry ID is verified;
- the modded asset serves a coherent functional/theme role.

Never hallucinate registry IDs.

## 11. Promotion gate

A production asset should normally satisfy:
- provenance/source known;
- source preserved;
- normalization complete;
- identifiers/integration complete;
- mechanical checks pass;
- purpose/clearance/context checks pass;
- visual review completed where required;
- generated artifact hash/provenance recorded;
- regression/rotation/terrain placement checked at the appropriate project gate.
