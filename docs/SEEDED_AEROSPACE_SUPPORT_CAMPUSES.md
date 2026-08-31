# Seeded Aerospace Support Campuses

## Purpose

Continuity Works can now synthesize complete aerospace support **site graphs** from deterministic seeds instead of generating only isolated facility references. The campus layer composes the support facilities implemented in Phases 1–5 with the typed road, logistics, utility, personnel, crawler, staging, and launch-support interfaces established in Phase 0.

The implementation is deliberately graph-first. It does not fake a campus by merging unrelated block arrays or by placing buildings without proving their operational connections. The generated graph is validated by the same `AerospaceSupportNetworkValidator` used for hand-authored site graphs before a run is reported as passing.

Primary implementation:

`src/structure_capability/seeded_aerospace_support_campus.py`

Generation contract:

`continuityworks:seeded_aerospace_support_campus/v1`

Site-graph contract:

`continuityworks:aerospace_support_site_graph/v1`

## Determinism contract

A campus request accepts:

- one support scale: `micro`, `light`, `standard`, `heavy`, `superheavy`, or `megastructure`;
- a non-empty integer or string seed;
- an optional explicit corporate/operator language.

The generator derives a private `random.Random` instance from SHA-256 of:

`generation_contract | scale | normalized_seed`

It does not use process-global random state.

For the same generation contract, scale, seed, facility library, connector contract, and explicit operator constraint, the generator reproduces the same:

- selected operator;
- site orientation;
- spacing model;
- terrain treatment token;
- facility vessel classes;
- facility vessel build states;
- node positions;
- typed socket graph;
- canonical campus fingerprint.

The campus fingerprint is SHA-256 over canonical JSON for the complete generated graph before the fingerprint field itself is inserted.

## Operator inheritance

A campus uses one common corporate language across its generated facilities. The generator intersects every selected archetype's `allowed_corporate_languages` and chooses only from the resulting common set.

An explicit operator must be valid for every selected facility or generation fails. Branding therefore cannot be used to bypass an archetype compatibility rule.

## Scale-specific compositions

The six scale templates intentionally change composition and network hierarchy rather than uniformly scaling one campus.

### Micro

A micro campus combines:

- Utility Component Service Shed;
- Microcraft Maintenance Bay;
- independent utility and refit support;
- two six-block local-road branches;
- a nearby launch anchor.

The local-road contract remains exactly six blocks wide with five blocks of terrain padding reserved on each side by the Phase 0 network policy.

### Light

A light campus forms a linear production-to-pad chain:

`component supplier -> small assembly bay -> component transfer gantry -> controlled launch-support road -> pad apron -> queue alignment -> launch anchor`

Assembly utilities are attached independently.

### Standard

A standard campus combines a Precision Components Factory and Dual-Bay Assembly Hall around an industrial turnout. Their factory/assembly logistics remain explicit while the shared road hierarchy reaches a controlled launch feeder and pad queue.

### Heavy

A heavy campus changes over to crawler-scale movement:

`heavy supplier -> component marshalling -> crawler junction -> vertical integration / launch queue -> pad`

The crawler junction provides separate branches to final vertical fitout and pre-launch queueing. Ordinary industrial frontage is not accepted as a substitute for the required heavy route.

### Superheavy

A superheavy campus is organized around a dedicated megascale vehicle spine:

`mega vehicle production factory -> superheavy transfer spine -> superheavy vehicle integration factory`

The transfer spine also provides the launch-bound branch. Connected transport must use `superheavy_crawler_lane_15x8` or `transport_spine_interface`; smaller roads do not satisfy the superheavy route gate.

### Megastructure

A megastructure campus connects three major protected systems:

`mega enclosed assembly campus -> colossal transfer hall -> underground vehicle staging/integration complex -> launch anchor`

Each facility has independent utility attachment. The underground complex is final vehicle staging/integration, not a duplicate of the separate subterranean production-factory archetype.

## Seeded site context

The seed also selects high-level site treatment tokens.

Orientation:

- north
- east
- south
- west

Spacing:

- compact
- distributed

Terrain choices are scale-aware. Smaller sites can use flat or gentle grades; heavy and superheavy sites add terraced and engineered plateau treatments; megastructures can select engineered plateau, terraced, or deep-cut contexts.

These tokens alter generated campus positions and future materialization context without mutating the individual authoritative facility references.

## Vessel-state variation

Every facility node carries a deterministic `vessel_class` and `vessel_state` selected only from that archetype's declared `vessel_state_support` contract. This lets campuses represent different moments in an operational lifecycle while preserving the facility's intended function.

Examples include:

- crated components;
- structural frame;
- partial hull;
- systems fitout;
- near-complete vehicle;
- transporter-integrated vehicle;
- pad-ready vehicle;
- recovered/damaged vehicle;
- stripped-for-refit vehicle.

## Network validation

Every generated graph is passed to `AerospaceSupportNetworkValidator.validate_graph()` before the seeded-campus gate is reported.

Validation includes:

- known connector profiles;
- compatible connector mating;
- no socket reuse;
- network isolation checks;
- utility attachment;
- inbound and outbound logistics;
- heavy-route capacity;
- superheavy-route capacity;
- launch-anchor presence;
- launch-anchor reachability.

A generated campus reports `PASS` only when the site graph passes these checks.

## Output

`SeededAerospaceSupportCampusGenerator.generate()` returns both the site graph and a compact report.

The graph contains:

- generation and graph contracts;
- normalized seed and digest;
- scale and operator;
- site context;
- facility, infrastructure, external-anchor, and launch-anchor nodes;
- facility reference IDs;
- vessel classes/states;
- typed sockets;
- edges;
- campus fingerprint.

The report contains the validation status, selected facilities, site context, node/edge counts, launch-anchor count, fingerprint, and any network findings.

## Example requests and replay corpus

Twelve example requests—two for every support scale—live at:

`examples/seeded_aerospace_support_campuses/requests.json`

Regenerate the compact replay corpus with:

`python scripts/generate_seeded_aerospace_support_examples.py`

Once `runs.json` has been generated in a full repository checkout, verify exact deterministic replay with:

`python scripts/generate_seeded_aerospace_support_examples.py --check`

The compact corpus deliberately omits the full graph arrays. It records the selected operator, site context, facility build states, topology counts, launch-anchor count, selected facility archetypes, and canonical SHA-256 campus fingerprint.

## Regression tests

`tests/test_seeded_aerospace_support_campus.py` covers:

- exact same-seed graph replay;
- different-seed fingerprint separation;
- all six scale templates;
- network PASS and launch-anchor reachability;
- campus-wide operator compatibility;
- facility-reference resolution;
- invalid seed/scale/operator rejection;
- megascale transport enforcement;
- underground final staging in megastructure synthesis;
- six-block local-road preservation;
- normalized seeded site positions.

The broader Facility Library tests also enforce all 30 support archetypes and all 30 support references through Phase 5.

## Materialization boundary

Phase 6 intentionally produces a validated composition graph rather than flattening the entire campus into one monolithic block structure. Facility references remain independently materializable and authoritative. The graph identifies what must be placed, how it is operationally connected, and what site-level seeded variation applies.

A later placement/export layer may translate these graph nodes into Minecraft structure/NBT placements, jigsaw pools, or runtime worldgen requests. That layer should consume this graph contract rather than duplicate its facility selection, transport-capacity, or reachability logic.

## Compatibility policy

This subsystem is additive. It does not replace existing launch facilities, road generators, Lost Cities integration, biome expansion, spawn-protection systems, or source-mod worldgen. It supplies typed support-campus composition that those systems can consume where appropriate.

All current reference structures remain Minecraft architectural representations rather than petroleum, aerospace, or civil engineering specifications.
