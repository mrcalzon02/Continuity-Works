# Infinite Domain extraction reference

This directory records the concrete project mechanisms from which the generic capability was derived.

The standalone API intentionally does **not** hard-code Infinite Domain factions, quest IDs, registry paths or progression. Those remain consuming-project concerns.

The most important extracted architectural rules are:

- single authoritative implementation path;
- deterministic generated assets and locked hashes;
- generated-asset materialization through CI;
- static integration validation;
- explicit contextual/biome ownership;
- graded rebuild depth;
- purpose before decoration;
- fixed-camera snapshot/review;
- independent author and reviewer roles;
- resumable long-running state;
- family-level batching and checkpoint waves;
- honest distinction between static/mechanical and visual/runtime proof.
