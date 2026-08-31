# Aerospace Support Infrastructure — Ordered Phased Build Plan

## Purpose

This document is the implementation roadmap for the next aerospace expansion in Continuity Works. It converts the launch-support ideas already established in design discussion into an ordered build program that can be executed phase by phase without losing architectural consistency.

The central rule is simple:

> **Support facilities are not freestanding ornaments. They are infrastructure-bound structures that must jigsaw into roads, heavy logistics routes, crawlerways, utility spines, personnel circulation, staging systems, and launch-support connections.**

The program inherits the existing Aerospace & Orbital Infrastructure Corpus, its six scale tiers, its operator languages, its function-first recognizability doctrine, and its rule that scale changes composition rather than merely dimensions.

This roadmap commits to building **actual vanilla materializable reference structures** as implementation progresses. A planned archetype is not considered complete until there is a concrete structure, a valid network attachment contract, and a passing recognition/connectivity audit.

The machine-readable companion to this document is:

`facility_library/aerospace_orbital/support_program.json`

---

# 1. Authoritative inherited architecture

The support program inherits the six established aerospace operator languages without replacing or renaming them:

1. **Asterion Aerospace** — immaculate white precision, cool glazing, strong symmetry, slender towers, clean enclosed utility systems.
2. **Helium Orbital Works** — exposed modular trusses, orange service framing, visible machinery and dense utility infrastructure.
3. **Black Glass Launch Systems** — dark monolithic massing, tinted glazing, sparse luminous accents, severe geometry, highly enclosed technical spaces.
4. **Atlas Heavy Industries** — massive structural frames, thick platforms, heavy concrete/metal language, oversized transport and production architecture.
5. **Pel Roma Astronautics** — elegant civic aerospace architecture, bright shells, ceremonial public-facing frontage, refined hangars and service facilities.
6. **VCF Colonial Launch Authority** — standardized repetitive modules, durable mass-produced bays, coded bands, rugged colonial infrastructure.

A support facility must visibly inherit the selected operator language while preserving its own operational role. An Asterion assembly bay and an Atlas assembly bay may differ greatly in silhouette, materials, bay rhythm, lighting and exposed structure, but both must remain immediately legible as assembly facilities.

Cross-operator campuses are allowed only when explicitly requested as mixed-use, acquired, retrofit, abandoned, or historical sites. The default campus should inherit one coherent operator language from its launch complex.

---

# 2. Hard corpus requirements

The support-facility corpus uses the same six scale tiers as the launch corpus:

- `micro`
- `light`
- `standard`
- `heavy`
- `superheavy`
- `megastructure`

The support corpus must contain **at least two distinct support-facility archetypes at every scale tier**. Different seeds, palettes, or corporate/operator skins of the same archetype do not satisfy this minimum.

Every completed support reference must satisfy all of the following:

1. It is an actual materializable vanilla structure.
2. It exposes at least one valid site-network connection.
3. If it directly supports launch operations, it can route through the site graph to a launch anchor.
4. If it manufactures or assembles vehicles/components, it has plausible inbound and outbound logistics.
5. If it requires utilities, it exposes a utility socket.
6. Heavy and superheavy facilities cannot silently downgrade to undersized road/transport profiles.
7. Operator design language remains visually coherent with the associated launch campus.
8. Vessel construction or maintenance states shown inside the structure are appropriate to the facility's function.
9. Scale changes zoning, infrastructure, repetition, circulation, service density, or internal organization—not simply dimensions.

---

# 3. Site-network doctrine

## 3.1 Facilities are nodes in a graph

Every support structure must be understood as a node in a larger site graph. The graph contains roads, heavy logistics corridors, crawlerways, utility spines, personnel routes, staging links, gantry interfaces and launch anchors.

The generator should be able to answer:

- What facility does this structure receive material or vehicles from?
- Where can a completed stage or vehicle go next?
- Which network segment reaches the launch pad?
- How do workers reach the structure?
- How do utilities enter the facility?
- Which route is appropriate for ordinary vehicles versus oversized aerospace hardware?

A support building that cannot answer any of these questions is incomplete.

## 3.2 Socket groups

Support structures should expose semantic socket groups rather than one generic connector type.

### `frontage`
Normal public/service approach to a facility.

Allowed planned profiles:
- `local_road_6w`
- `industrial_road_8w`
- `checkpoint_road_interface`

The existing six-block road width remains the normal local-road standard. The established five-block terrain transition/padding rule should remain available at road/world boundaries. Dedicated industrial and heavy aerospace routes are additional site infrastructure, not a redefinition of ordinary city roads.

### `service`
Maintenance vehicles, ordinary facility support traffic and secondary circulation.

- `service_lane_4w`
- `industrial_road_8w`

### `logistics`
Freight and large component movement.

- `heavy_logistics_10w`
- `freight_yard_interface`
- `component_transfer_interface`
- `vehicle_transfer_interface`

### `heavy_transport`
Crawler/transporter-scale movement.

- existing `crawler_lane_9x5`
- existing `superheavy_crawler_lane_15x8`
- planned `transport_spine_interface`

### `personnel`
Crew, technicians and protected human circulation.

- `crew_access_3x3`
- `pedestrian_causeway_5x3`
- `crew_bridge_interface`

### `utility`
Power, process, service and buried/visible utility systems.

- `utility_spine_3x3`
- existing `process_pipe_1x1`
- `power_service_corridor_3x3`

### `launch_support`
Connections whose purpose is to feed launch operations.

- `launch_support_road_8w`
- `pad_queue_interface`
- `gantry_support_interface`
- `launch_mount_service_axis`

### `staging`
Holding and queue infrastructure.

- `staging_pad_interface`
- `queue_alignment_interface`

### `maintenance`
Vehicle service/refit interfaces.

- `maintenance_bay_interface`
- `refit_service_interface`

### `subterranean`
Buried factory, staging, silo-support and underground integration systems.

- `subterranean_support_interface`
- existing `silo_vertical_7x7`
- existing `mega_silo_vertical_15x15`

---

# 4. Road and infrastructure hierarchy

A launch campus should not flatten all circulation into one road type.

## Tier A — Public/perimeter access

Purpose:
- facility entrance
- staff arrival
- ordinary service traffic
- security/checkpoint approach

Primary profiles:
- `local_road_6w`
- `industrial_road_8w`

## Tier B — Intra-campus service circulation

Purpose:
- connect support buildings
- maintenance traffic
- ordinary cargo movement
- facility-to-facility service access

Primary profiles:
- `service_lane_4w`
- `industrial_road_8w`

## Tier C — Heavy logistics

Purpose:
- move large fabricated sections
- freight transfer
- oversized cargo
- assembly-to-staging movement

Primary profiles:
- `heavy_logistics_10w`
- freight yard and component-transfer interfaces

## Tier D — Launch vehicle transport

Purpose:
- move integrated launch vehicles or superheavy stages
- connect integration buildings to staging and launch pads

Primary profiles:
- `crawler_lane_9x5`
- `superheavy_crawler_lane_15x8`
- `transport_spine_interface`

These routes must remain visually distinct from ordinary roads.

## Tier E — Personnel and protected access

Purpose:
- crew routes
- protected technician movement
- elevated bridges and enclosed accessways

## Tier F — Utilities

Purpose:
- power
- process services
- pipe systems
- buried utility corridors

The network planner may parallel these systems but must not treat them as interchangeable connector profiles.

---

# 5. Planned infrastructure jigsaw pieces

Phase 0 should establish the network pieces before broad support-facility production begins.

1. `local_road_segment_6w`
2. `industrial_road_segment_8w`
3. `heavy_logistics_segment_10w`
4. `service_lane_segment_4w`
5. `road_checkpoint_gate`
6. `industrial_turnout_loop`
7. `heavy_crawlerway_junction`
8. `superheavy_crawlerway_junction`
9. `utility_spine_segment`
10. `crew_causeway_segment`
11. `elevated_service_bridge_segment`
12. `pad_access_apron`
13. `queue_alignment_segment`
14. `freight_transfer_node`
15. `transport_spine_junction`
16. `launch_support_interchange`

These should be genuine structural modules/jigsaw pieces, not decorative line markings embedded independently into each facility.

---

# 6. Support-system architecture modes

The support corpus introduces a second architecture-language layer beneath operator styling.

## `assembly_first`

The enclosed vehicle construction volume dominates. Oversized apertures, cranes/gantry analogues, service galleries, build platforms and staging aprons reinforce assembly.

## `transfer_first`

The movement system dominates. Long directional geometry, clearance, transfer platforms and strong endpoints make the component/vehicle path obvious.

## `fabrication_first`

Repeated production halls, fabrication annexes, loading/receiving, utilities and component output dominate.

## `staging_first`

Queueing, storage cradles, marked holding positions, sheltered component zones and orderly access dominate.

## `refit_first`

Maintenance, inspection, scaffolding, repair platforms, damaged/recovered vehicles and service yards dominate.

## `factory_campus`

Multiple production halls and service blocks form one manufacturing district connected by internal roads, utility spines and freight links.

## `vehicle_spine`

A single long transfer axis organizes multiple production, integration, staging and launch-support nodes.

## `subterranean_support`

Surface logistics and access works imply a much larger buried factory, staging or integration complex.

## `mixed_logistics`

Ordinary roads, heavy freight, personnel circulation, utilities and aerospace transfer systems coexist in one dense site while retaining typed connections.

---

# 7. Vessel representation program

Support facilities should not remain empty architectural shells. They should contain simplified, clearly readable spacecraft/launch-vehicle representations appropriate to the facility.

## Vessel classes

1. Utility shuttle
2. Cargo shuttle
3. Light launch vehicle
4. Reusable booster
5. Orbital cargo vehicle
6. Upper stage
7. Heavy launch core
8. Superheavy booster stack
9. Prototype experimental craft
10. Recovery capsule

These are architectural/gameplay vessel representations rather than engineering models.

## Vessel construction/service states

1. `crated_components`
2. `structural_frame`
3. `partial_hull`
4. `primary_structure_complete`
5. `systems_fitout`
6. `near_complete`
7. `transporter_integrated`
8. `pad_ready`
9. `recovered_damaged`
10. `stripped_for_refit`

The same vessel should therefore be able to appear differently depending on context. A reusable booster in a launch queue should not look identical to a recovered booster inside a refurbishment hangar.

Vessel state should eventually become seed-selectable while remaining constrained by the facility archetype.

---

# 8. Ordered structure corpus — 30 planned support facilities

The following ordering is authoritative for phased implementation unless a prerequisite failure forces a small reordering.

## Micro

### 1. Utility Component Service Shed — Phase 1

Mode: `fabrication_first`

Purpose: small parts preparation, tool storage and component servicing near micro/utility pads.

Required networks:
- frontage
- utility

Vessel state emphasis:
- crates/components

### 2. Microcraft Maintenance Bay — Phase 1

Mode: `refit_first`

Purpose: enclosed repair bay for microcraft and utility shuttles.

Required networks:
- frontage
- maintenance

Vessel state emphasis:
- recovered damaged
- stripped for refit

## Light

### 3. Small Assembly Bay — Phase 1

Mode: `assembly_first`

Purpose: first complete support reference for small launch vehicles and shuttles.

Required networks:
- frontage
- logistics
- utility

Vessel states:
- structural frame
- partial hull
- near complete

### 4. Component Transfer Gantry — Phase 1

Mode: `transfer_first`

Purpose: visible movement link between storage/fabrication and assembly/launch support.

Required networks:
- logistics
- launch support

### 5. Open Stage Storage Yard — Phase 1

Mode: `staging_first`

Purpose: open organized holding yard for stages and major vehicle sections.

Required networks:
- logistics
- staging

### 6. Emergency Recovery Refit Shelter — Phase 2

Mode: `refit_first`

Purpose: small recovery shelter attached to launch/recovery networks.

Required networks:
- service
- maintenance
- launch support

## Standard

### 7. Dual-Bay Assembly Hall — Phase 2

Two independently usable assembly bays with shared services and internal transfer apron.

### 8. Precision Components Factory — Phase 1

First enclosed manufacturing reference. It should read as production rather than storage.

### 9. Orbital Shuttle Service Depot — Phase 1

First complete maintenance/refit reference with crew/service access.

### 10. Covered Component Depot — Phase 2

Sheltered storage with obvious freight in/out relationship.

### 11. Partial Vehicle Staging Hall — Phase 2

Holds incomplete vehicles between production and final integration.

### 12. Elevated Transfer Bridge — Phase 3

Elevated movement system for components/personnel between major structures.

### 13. Crew and Cargo Processing Annex — Phase 3

Human/cargo interface for a functioning spaceport campus.

## Heavy

### 14. Hull Section Fabrication Plant — Phase 2

Large repeated production bays producing visible vehicle hull/structural sections.

### 15. Engine Module Works — Phase 3

Dense industrial fabrication building for engine-module analogues and service hardware.

### 16. Booster Refurbishment Hangar — Phase 2

Large recovery/refit facility built around damaged and stripped reusable boosters.

### 17. Heavy Vehicle Retrofit Works — Phase 3

Upgrade facility for already-built heavy vehicles; should not read as a first-build factory.

### 18. Vertical Integration Support Tower — Phase 3

Support structure feeding a launch center rather than duplicating the launch tower itself.

### 19. Launch Queue Preparation Yard — Phase 3

Organized pre-pad queue with launch-support routing and vehicle-ready positions.

### 20. Heavy Component Marshalling Yard — Phase 3

Freight and heavy-component sorting yard connecting factories to integration.

## Superheavy

### 21. Superheavy Vehicle Integration Factory — Phase 4

Huge enclosed integration building with dedicated superheavy transporter interface.

### 22. Superheavy Transfer Spine — Phase 4

Long high-clearance transfer system connecting production, staging and launch.

### 23. Superheavy Assembly Gantry Hall — Phase 4

Large enclosed hall dominated by internal assembly frames and heavy lifting analogues.

### 24. Superheavy Stage Storage Hangar — Phase 4

Protected storage for enormous completed stages awaiting integration.

### 25. Superheavy Recovery Refurbishment Works — Phase 4

Recovery/refit campus with extensive heavy transport and maintenance systems.

### 26. Mega Vehicle Systems Factory — Phase 4

Multi-hall superheavy production campus that begins bridging into megastructure-scale industrial architecture.

## Megastructure

### 27. Mega Enclosed Assembly Campus — Phase 5

A fully enclosed multi-building assembly campus capable of housing several massive vehicles/build stages simultaneously.

The megastructure read should come from multiple halls, internal logistics, large transfer axes and deep service organization—not just a giant box.

### 28. Colossal Transfer Hall — Phase 5

An enormous protected transfer building where superheavy vehicles move between production systems and launch infrastructure.

### 29. Subterranean Support Factory — Phase 5

A buried production complex connected to surface freight, utilities and underground aerospace infrastructure.

### 30. Underground Vehicle Staging and Integration Complex — Phase 5

A deep staging/integration environment directly capable of feeding underground silos or subterranean launch systems.

---

# 9. Phased execution plan

## Phase 0 — Network contract foundation

### Goal

Create the structural connection system that every later support reference will use.

### Deliverables

1. Connector contract v4.
2. Socket-group schema/validation.
3. New road/logistics/personnel/utility/launch-support connector profiles.
4. The 16 initial infrastructure jigsaw modules.
5. Typed site-graph representation.
6. Connectivity validator.
7. Route-width compatibility rules.
8. Launch-anchor reachability rule.
9. Explicit boundary-termination rules for roads/utilities leaving generated sites.

### Verification gate

Phase 0 does not pass until a synthetic test graph can connect:

`industrial road -> factory -> heavy logistics -> assembly -> crawler/transfer -> staging -> launch-support interface -> launch pad`

without connector-type violations.

### Commit boundary

Commit the connector/network foundation before building the first support references. This creates one authoritative infrastructure contract for every later phase.

---

## Phase 1 — Anchor support structures

### Goal

Prove all major support roles with a small first set of actual structures.

### Required actual references

1. Utility Component Service Shed
2. Microcraft Maintenance Bay
3. Small Assembly Bay
4. Component Transfer Gantry
5. Open Stage Storage Yard
6. Precision Components Factory
7. Orbital Shuttle Service Depot

The machine-readable program sets a minimum Phase-1 target of five, but implementation should aim to complete all seven above if no blocking architecture problem appears.

### Required vessel fixtures

- utility shuttle frame
- partial light launch vehicle
- component crate/rack set
- near-complete shuttle
- damaged/recovered shuttle

### Required operator fixtures

At least three operators should be represented in this phase so operator inheritance is tested independently from facility function.

Recommended:
- Asterion
- Helium
- VCF

### Verification

Every reference must:
- compile to vanilla blocks;
- expose valid network sockets;
- connect to at least one infrastructure jigsaw piece;
- pass archetype recognition;
- pass operator-language validation;
- show an appropriate vessel state where the archetype calls for one.

---

## Phase 2 — Standard/heavy manufacturing depth

### Goal

Create complete manufacturing-to-storage-to-recovery chains.

### Structures

- Emergency Recovery Refit Shelter
- Dual-Bay Assembly Hall
- Covered Component Depot
- Partial Vehicle Staging Hall
- Hull Section Fabrication Plant
- Booster Refurbishment Hangar

### New behaviors

- repeated production bays
- shared utility/service yards
- multiple inbound/outbound freight sockets
- recovered vehicle handling
- partial-build vessel storage
- assembly-bay concurrency

### Verification chain

Demonstrate at least one generated operational chain:

`Hull Fabrication -> Heavy Logistics -> Dual-Bay Assembly -> Staging -> Launch Queue/Launch Support`

and one recovery chain:

`Recovery Pad -> Recovery Route -> Booster Refurbishment -> Staging`

---

## Phase 3 — Heavy integration and launch-feed logistics

### Goal

Connect the support corpus directly into mature heavy launch campuses.

### Structures

- Elevated Transfer Bridge
- Crew and Cargo Processing Annex
- Engine Module Works
- Heavy Vehicle Retrofit Works
- Vertical Integration Support Tower
- Launch Queue Preparation Yard
- Heavy Component Marshalling Yard

### Network emphasis

This phase must exercise simultaneously:
- ordinary road frontage
- heavy logistics
- crawler/vehicle transfer
- personnel circulation
- utilities
- launch-support routing

### Verification

A heavy campus generated from these parts must contain no isolated support node unless its archetype explicitly allows independent operation.

The launch queue must have a valid route to a heavy launch anchor.

---

## Phase 4 — Superheavy production campus

### Goal

Make superheavy launch facilities feel supported by an industrial ecosystem of comparable scale.

### Structures

- Superheavy Vehicle Integration Factory
- Superheavy Transfer Spine
- Superheavy Assembly Gantry Hall
- Superheavy Stage Storage Hangar
- Superheavy Recovery Refurbishment Works
- Mega Vehicle Systems Factory

### Composition requirements

Superheavy structures must introduce more than larger dimensions. They should add:
- multiple service levels
- repeated heavy bays
- dedicated internal yards
- redundant utilities
- dedicated superheavy transport
- expanded personnel circulation
- multiple staging positions
- operator-specific mega-scale geometry

### Verification

No superheavy facility may satisfy its heavy-transport requirement using a normal industrial road alone.

At least one complete site must route a superheavy vehicle:

`Factory -> Integration -> Transfer Spine -> Queue -> Superheavy Launch Center`

---

## Phase 5 — Megastructure support systems

### Goal

Extend support architecture into enormous enclosed and subterranean industrial environments.

### Structures

- Mega Enclosed Assembly Campus
- Colossal Transfer Hall
- Subterranean Support Factory
- Underground Vehicle Staging and Integration Complex

### Megastructure rules

These structures require explicit vertical datums and surface/subsurface relationships.

A megastructure support facility must communicate:
- multiple operational zones
- internal logistics
- repeated service levels
- large-scale personnel movement
- utility hierarchy
- surface access
- buried or enclosed vehicle movement

### Integration targets

The underground structures must be able to connect semantically to:
- Deep Multi-Level Rocket Silo
- Colossal Tandem Underground Launch Complex

without converting the silo shaft itself into a generic corridor.

---

## Phase 6 — Seeded campus synthesis and regression corpus

### Goal

Move from individual validated structures to reproducible complete aerospace industrial sites.

### Generator responsibilities

A seeded support-campus generator should select:
- operator language
- scale tier
- support facility mix
- facility condition
- expansion/retrofit history
- road orientation
- logistics topology
- vessel classes
- vessel construction states
- launch relationship
- staging density
- utility density

### Required seeded examples

At least three deterministic campus runs for each launch scale tier should ultimately be retained.

The corpus should include:
- clean new-build corporate campus
- expanded/retrofitted campus
- weathered or partially abandoned campus
- mixed above/below-ground campus where applicable

### Regression data

Store compact deterministic records:
- request
- resolved site graph
- structure IDs
- vessel-state selections
- dimensions
- block count
- site fingerprint
- network fingerprint
- recognition/connectivity gate status

Do not commit duplicate full block dumps when the generator can reproduce them deterministically.

---

# 10. Validation gates

The support program should eventually expose the following explicit gates.

## `SUPPORT_CORPUS_SCALE_COVERAGE`

At least two distinct completed support archetypes at every scale tier.

## `SUPPORT_REFERENCE_MATERIALIZATION`

Every completed reference materializes into actual in-bounds vanilla block geometry.

## `SUPPORT_SOCKET_COMPATIBILITY`

All required sockets resolve to known connector profiles and mate only with compatible network types.

## `SUPPORT_SITE_GRAPH_REACHABILITY`

Every required non-isolated support node is reachable from the campus graph.

## `SUPPORT_LAUNCH_ANCHOR_REACHABILITY`

Facilities whose role feeds launch operations have an allowed path to a launch-capable anchor.

## `SUPPORT_LOGISTICS_INBOUND_OUTBOUND`

Manufacturing/assembly facilities have valid logistics ingress and egress rather than dead-end decorative roads.

## `SUPPORT_UTILITY_ATTACHMENT`

Facilities declaring utility dependence expose a valid utility connection.

## `SUPPORT_HEAVY_ROUTE_FIT`

Heavy and superheavy movement does not pass through connector profiles below required capacity.

## `SUPPORT_OPERATOR_LANGUAGE_INHERITANCE`

Material, massing and geometry remain consistent with the chosen aerospace operator.

## `SUPPORT_VESSEL_STATE_FIT`

Displayed vessel class/state combinations are valid for the host facility.

## `SUPPORT_ARCHETYPE_DISTINCTION`

Assembly, fabrication, storage, staging, refit and transfer facilities remain visually and semantically distinguishable.

## `SUPPORT_SEEDED_DETERMINISM`

Identical seeded requests produce identical campus, network and vessel-state fingerprints.

---

# 11. Required operational chains

The finished system should be able to assemble complete facility networks such as:

## Light production chain

`Precision Components Factory`
→ `Component Transfer Gantry`
→ `Small Assembly Bay`
→ `Vehicle Transfer Interface`
→ `Light Orbital Launch Pad`

## Standard cargo/spaceport chain

`Covered Component Depot`
→ `Dual-Bay Assembly Hall`
→ `Partial Vehicle Staging Hall`
→ `Cargo/Processing Annex`
→ `Small Cargo Spaceport`

## Heavy launch chain

`Hull Section Fabrication Plant`
→ `Heavy Component Marshalling Yard`
→ `Dual-Bay Assembly Hall`
→ `Vertical Integration Support Tower`
→ `Launch Queue Preparation Yard`
→ `Heavy Orbital Launch Complex`

## Heavy recovery chain

`Recovery/Landing Anchor`
→ `Recovery Access Route`
→ `Booster Refurbishment Hangar`
→ `Heavy Vehicle Retrofit Works`
→ `Launch Queue Preparation Yard`

## Superheavy chain

`Mega Vehicle Systems Factory`
→ `Superheavy Assembly Gantry Hall`
→ `Superheavy Vehicle Integration Factory`
→ `Superheavy Transfer Spine`
→ `Superheavy Stage Storage/Queue`
→ `Superheavy Booster Launch Center`

## Underground megastructure chain

`Surface Freight/Utility Entry`
→ `Subterranean Support Factory`
→ `Underground Vehicle Staging and Integration Complex`
→ `Colossal Transfer Hall / underground transfer system`
→ `Deep Silo or Tandem Underground Launch Complex`

These chains should eventually become testable site-graph fixtures rather than remaining documentation-only examples.

---

# 12. Phase completion discipline

Each phase should follow the same implementation discipline:

1. Inspect current authoritative `main` before editing.
2. Preserve parallel work and avoid broad rewrites.
3. Add structural modules/connectors before archetypes that depend on them.
4. Add archetype definitions.
5. Build actual reference structures.
6. Add vessel fixtures appropriate to those references.
7. Add/update manifests.
8. Validate structure bounds and vanilla block policy.
9. Validate recognition.
10. Validate network sockets and graph reachability.
11. Validate operator inheritance.
12. Add deterministic regression fixtures where generation is involved.
13. Commit the phase as one coherent fast-forward change to `main`.

No phase is complete merely because its planning metadata exists.

---

# 13. Definition of done for the support program

The support program is considered mature when:

- all 30 planned support archetypes are implemented or deliberately superseded by documented better equivalents;
- at least two distinct support facilities exist at every scale tier;
- every completed support archetype has at least one actual materializable reference;
- all support structures can participate in typed site graphs;
- factories and assembly facilities have valid logistics flow;
- launch-support structures can route to launch anchors;
- heavy/superheavy transport remains type-safe;
- all six inherited operator languages can be applied without erasing facility purpose;
- representative vessels can appear in appropriate build/refit states;
- seeded campuses can reproduce complete road/logistics/utility/launch-support networks deterministically;
- the network can generate coherent multi-facility launch campuses rather than isolated structure scatter.

The first implementation action after this planning baseline is **Phase 0: connector v4 + infrastructure jigsaw foundation**, followed immediately by the Phase-1 anchor support structures.
