# Seeded Facility Generation

## Purpose

Continuity Works now has a deterministic example-generation layer above `FacilityLibrary`. It is intended to exercise facility archetypes repeatedly with different world-style seeds while preserving the semantic requirements that make a gas station, travel stop, well pad, tank farm, refinery, or truck terminal recognizable.

`SeededFacilityGenerator` is not a substitute for Minecraft world placement. It produces bounded vanilla block structures and a generation report that can be handed to later NBT, terrain-integration, audit, or worldgen stages.

## Deterministic seed contract

The generation contract is `continuityworks:seeded_facility/v1`.

An integer or string seed is normalized to text and combined with the archetype ID. SHA-256 derives the deterministic random state. The Python process-global random state is never used.

For a fixed contract version, archetype, seed, requested corporate language, and requested scale, the same generated structure and SHA-256 structure fingerprint must be reproduced.

Changing the seed is allowed to vary:

- pump, tank, process-column, and loading-bay counts within the archetype grammar;
- storefront dimensions and support-building presence;
- sign placement;
- equipment spacing and grid density;
- automatically selected corporate language when the caller does not specify one.

Seed variation may not remove required recognition signatures.

## Semantic gates

Generation begins by resolving an existing `FacilityLibrary` archetype. The selected scale must be one of that archetype's declared tiers and the selected corporate language must be explicitly allowed by the archetype.

Every grammar returns the archetype's mandatory recognition signatures. The generation report compares those signatures against the authoritative archetype definition and reports `PASS` only when the required fraction is met.

Corporate language is resolved through the existing vanilla palette contract. Generated blocks are therefore restricted to `minecraft:` IDs in this baseline.

## Current seeded grammars

Version 1 includes procedural grammars for all six fuel/petroleum archetypes:

| Archetype | Seed-controlled variation |
| --- | --- |
| Rural gas station | pump count, store size, pylon side, rear-service building |
| Highway travel stop | pump count, truck bays, store size, parking field |
| Crude-oil well pad | temporary tank count and extraction-site arrangement |
| Bulk tank farm | tank-grid width/density and storage count |
| Compact diesel refinery | process-column count/heights, product tanks, loading bays |
| Truck fuel terminal | bulk tanks, repeated loading bays, fleet queue geometry |

The grammars also preserve the synthetic corporate design languages already defined by the semantic facility library. A Northstar retail facility remains visually different from a Frontier Cooperative facility even when the two runs use the same functional archetype.

## Example corpus

`examples/seeded_facility_runs/runs.json` contains 18 committed replay records: three runs for each archetype. The set deliberately mixes numeric and text seeds, explicit and automatic corporate selection, and both supported scale tiers.

The corpus does not store thousands of generated block coordinates. Each compact run record stores:

- the original replay request;
- the resolved corporate language and scale;
- generated variant parameters;
- recognition status;
- site size;
- compiled block count;
- SHA-256 structure fingerprint.

The full generation report still contains the normalized seed digest, module counts, and recognition-signature detail when a run is executed.

This keeps the repository compact while making every example exactly replayable.

## Rebuild and verification

Run:

```bash
python scripts/generate_seeded_facility_examples.py
```

to regenerate the committed records.

Run:

```bash
python scripts/generate_seeded_facility_examples.py --check
```

to fail if any committed result no longer reproduces exactly.

A fingerprint change is therefore an explicit generation-contract change, not an invisible implementation detail.

## Extension rules

New facility families should add their own seeded grammar only after the underlying archetype and structural vocabulary exist. Seed logic may vary valid composition, scale, density, wear, landscaping, or optional equipment, but it must not bypass archetype recognition or corporate-language rules.

Future extensions can add biome/site context, road alignment, terrain fitting, dereliction profiles, mod-aware material substitutions, and structure/NBT export while preserving this deterministic replay boundary.
