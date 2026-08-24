# Concrete source patterns retained from Infinite Domain

## Deterministic structure serialization
The source project uses a pure-Python `StructureBuilder`, deterministic gzip (`mtime=0`), Minecraft DataVersion tracking, and expected Git blob hashes. This export keeps that capability generically in `structure_capability.minecraft.structure_builder`.

## Generated-asset materialization
The source workflow:
1. runs generator with verification;
2. rejects unrelated generated changes;
3. stages only declared generated files;
4. commits generated outputs only when bytes changed.

Recommended for consuming projects.

## Incremental feature review
The source seafloor review ledger processes one active feature at a time:
- verify live selector/projection/spacing;
- inspect deterministic geometry;
- judge whether it communicates a real process;
- edit only authoritative generator;
- lock generated hash;
- materialize;
- then mark refined;
- defer runtime claims that were not observed.

This export generalizes the same sequence to all structures.

## Long-running family pipeline
The source structural pipeline treats an invocation as a work session, not the lifetime of the task. Persistent state records completed family/checkpoint waves so work resumes rather than restarts.
