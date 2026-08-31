# Aerospace & Orbital Infrastructure Corpus

Continuity Works treats aerospace infrastructure as a semantic facility family, not as a collection of decorative sci-fi pads. Every facility must communicate its operational purpose through silhouette, zoning, access relationships, and scale before metadata is consulted.

This baseline commits to **two distinct complete facilities at every size rating** and to building each one as an actual vanilla materializable reference structure.

## Hard corpus rules

1. Six scale tiers are authoritative: `micro`, `light`, `standard`, `heavy`, `superheavy`, and `megastructure`.
2. Every tier must contain at least **two different archetype IDs** and at least **two complete reference structures**.
3. Two seeds, corporate skins, or palette swaps of one archetype do not satisfy the minimum.
4. Function precedes branding. Corporate language may change visual character but may not erase the facility's required operational signatures.
5. Scale changes composition. A superheavy or megastructure facility must add systems, relationships, and zones rather than uniformly enlarging a smaller structure.
6. References are Minecraft architectural representations, not real aerospace engineering specifications.
7. Baseline materialization remains vanilla-only.

## Itemized baseline: 12 complete facilities

### Micro

1. **Utility Landing Station** — `pad_first`
   - Compact landing surface is the dominant read.
   - Small service edge, local operations block, approach lighting, and telemetry/beacon identity.
   - Baseline reference: Pel Roma Astronautics.

2. **Emergency Recovery Outpost** — `recovery_first`
   - Emergency-marked pad paired with a visibly larger response/recovery hangar.
   - Equipment yard and high-visibility beacon communicate rescue rather than routine passenger use.
   - Baseline reference: Helium Orbital Works.

### Light

3. **Light Orbital Launch Pad** — `tower_first`
   - Compact launch mount, service tower, exhaust/flame-trench analogue, small tankage, and remote blockhouse.
   - Must read as vertical launch infrastructure rather than a landing pad.
   - Baseline reference: Asterion Aerospace.

4. **Small Cargo Spaceport** — `logistics_first`
   - Landing surface, freight apron, enclosed cargo hangar, terminal frontage, and telemetry.
   - Cargo transfer is the defining relationship; no launch tower dominates the site.
   - Baseline reference: VCF Colonial Launch Authority.

### Standard

5. **Reusable Orbital Launch Complex** — `pad_first`
   - Separate launch and recovery anchors, propellant/service infrastructure, telemetry, and launch control.
   - Recovery remains spatially distinct from the active launch mount.
   - Baseline reference: Asterion Aerospace.

6. **Vertical Integration Launch Center** — `integration_first`
   - Tall vehicle integration building is a major silhouette anchor.
   - A visible crawler/transporter axis connects assembly to a separate launch pad and gantry.
   - Baseline reference: Helium Orbital Works.

### Heavy

7. **Heavy Orbital Launch Complex** — `tower_first`
   - Heavy launch platform, tall gantry/tower systems, broad crawler route, large service yard, tankage, and remote control.
   - Heavy transport and pad servicing must be visually obvious.
   - Baseline reference: Atlas Heavy Industries.

8. **Tandem Launch Gantry Complex** — `multi_anchor`
   - Two independent launch mounts and two gantries.
   - One shared integration/service spine visibly unifies the pair.
   - Shared tankage and access distinguish it from two unrelated pads placed beside one another.
   - Baseline reference: Black Glass Launch Systems.

### Superheavy

9. **Superheavy Booster Launch Center** — `tower_first`
   - Massive launch platform and tower are dominant.
   - Mega integration building, superheavy crawlerway, multiple tank clusters, pipe/service systems, and remote operations create a full campus.
   - Baseline reference: Atlas Heavy Industries.

10. **Superheavy Assembly & Launch Campus** — `integration_first`
    - Mega integration building, not the launch tower, dominates the first read.
    - Long illuminated transporter axis and staging apron separate assembly from the distant pad.
    - Baseline reference: Asterion Aerospace.

### Megastructure

11. **Deep Multi-Level Rocket Silo** — `subterranean`
    - One enormous surface aperture implies a much larger buried facility.
    - Deep shaft, repeated service-ring levels, galleries, freight/service access, and remote control compound.
    - Baseline reference: Black Glass Launch Systems.

12. **Colossal Tandem Underground Launch Complex** — `subterranean_multi_anchor`
    - Two independently legible deep launch shafts and two large surface apertures.
    - Shared subterranean integration hall and service galleries make the site one coherent megastructure.
    - Baseline reference: VCF Colonial Launch Authority.

## Reusable aerospace module vocabulary

The baseline adds 21 structural modules:

- Landing surfaces: `landing_pad_17x2x17`, `heavy_landing_pad_31x3x31`
- Launch mounts: `launch_mount_13x7x13`, `superheavy_launch_mount_25x10x25`
- Vertical service: `launch_tower_9x32x9`, `superheavy_launch_tower_15x48x15`, `gantry_frame_13x24x9`, `service_arm_9x4x7`
- Integration/recovery: `integration_bay_17x20x21`, `mega_integration_bay_31x40x39`, `recovery_hangar_17x9x21`
- Ground access: `crawlerway_segment_11x2x17`, `superheavy_crawlerway_segment_17x3x25`, `access_causeway_7x5x17`
- Mission operations: `control_blockhouse_13x5x17`, `telemetry_array_13x12x13`
- Launch exhaust language: `flame_trench_9x4x17`, `blast_deflector_9x7x3`
- Underground launch: `silo_shaft_17x24x17`, `mega_silo_shaft_31x48x31`, `silo_service_ring_25x7x25`

Existing generic and petroleum modules such as storage tanks, pipe racks, utility rooms, standard rooms, and general circulation remain reusable. Aerospace does not duplicate them unnecessarily.

## Aerospace connector contract v3

Connector v3 retains every previous profile and adds:

- `crawler_lane_9x5` — heavy transporter/crawler routing
- `launch_mount_interface_5x5` — abstract vertical launch-vehicle/mount interface
- `heavy_hangar_aperture_9x7` — heavy integration/recovery opening
- `superheavy_crawler_lane_15x8` — megascale transporter routing
- `superheavy_hangar_aperture_15x12` — superheavy integration aperture
- `silo_vertical_7x7` — deep silo/service-ring vertical interface
- `mega_silo_vertical_15x15` — megastructure silo vertical interface

These profiles prevent personnel corridors, ordinary vehicle lanes, heavy transport routes, hangars, and silo shafts from being treated as interchangeable connection types.

## System design language modes

The machine-readable authority is `facility_library/aerospace_orbital/design_language.json`.

### `pad_first`
Use for landing fields and reusable launch/recovery sites. Horizontal flight surfaces are primary; service buildings, telemetry, and lighting support them.

### `recovery_first`
Use for emergency and recovery facilities. Pad-to-hangar and response-yard relationships dominate; passenger-terminal language is suppressed.

### `logistics_first`
Use for cargo spaceports and payload handling. Aprons, hangars, freight routes, and terminals form the primary hierarchy.

### `tower_first`
Use for vertical launch centers. Launch mount and vertical service tower dominate; exhaust, tankage, and remote control reinforce the pad.

### `integration_first`
Use when assembly/integration is the principal architectural landmark. Oversized doors and long transporter relationships visibly connect vehicle assembly to a remote pad.

### `multi_anchor`
Use for tandem or multi-pad complexes. Each operational anchor must remain independently legible while shared service infrastructure makes them one system.

### `subterranean`
Use for deep silos and underground launch facilities. Surface works communicate the presence of a much larger buried shaft, rings, galleries, and access network.

### `subterranean_multi_anchor`
Use for buried megastructures with multiple shafts. Shared underground infrastructure must visibly unify the launch anchors.

## Synthetic aerospace operator languages

Six baseline identities establish different architectural/corporate reads without copying real organizations:

- **Asterion Aerospace** — immaculate white precision, cool glazing, strong symmetry, slender towers.
- **Helium Orbital Works** — exposed modular trusses, orange service frames, dense visible utility infrastructure.
- **Black Glass Launch Systems** — dark monolithic massing, tinted glazing, sparse luminous accents, severe geometry.
- **Atlas Heavy Industries** — oversized structural frames, thick platforms, utilitarian concrete/metal massing.
- **Pel Roma Astronautics** — elegant civic aerospace language, light stone/quartz shells, ceremonial landing architecture.
- **VCF Colonial Launch Authority** — standardized durable bays, coded bands, repetitive infrastructure intended to read as mass-produced colonial hardware.

## System architecture layers

A complete aerospace facility is composed from explicit systems rather than one building mass:

1. **Flight interface** — landing pad, launch mount, or silo aperture.
2. **Vertical service** — tower, gantry, service arms, crew access.
3. **Vehicle integration** — hangar, integration bay, recovery bay.
4. **Ground logistics** — crawlerways, transporter routes, cargo aprons, access causeways.
5. **Mission operations** — blockhouses, control centers, telemetry and communications.
6. **Utilities** — tanks, pipe racks, power/service compounds.
7. **Launch exhaust representation** — flame trench and blast-deflector analogues for visual differentiation.
8. **Underground systems** — shafts, service rings, galleries, buried integration volumes.

## Scale doctrine

Scale is semantic and compositional:

- **Micro** adds only the support needed to make a landing/recovery function legible.
- **Light** introduces dedicated launch or cargo-processing systems.
- **Standard** introduces multiple operational zones and explicit transfer relationships.
- **Heavy** requires heavy transport, larger service campuses, and stronger separation of operations.
- **Superheavy** requires mega integration, superheavy transport, expanded utilities, staging, and substantially larger exclusion/service relationships.
- **Megastructure** introduces deep vertical or multi-anchor underground architecture, repeated service levels, galleries, and surface-to-subsurface hierarchy.

A generator that merely multiplies dimensions fails the design doctrine even if the resulting structure is large.

## Validation gates

The baseline is intended to pass all of the following:

- Structural Library count and connector validation.
- Facility Semantic Library dependency and count validation.
- All required archetype modules exist and are modules.
- All corporate palettes remain `minecraft:` namespace only.
- All reference module placements fit declared structure bounds.
- All references contain every mandatory recognition signature.
- Every reference compiles to actual block geometry.
- Every aerospace scale tier contains at least two distinct archetypes and two complete references.
- All eight required system design modes are represented.
- Megastructure references include an explicit placement datum for surface/subsurface interpretation.

## Next aerospace expansion

The baseline is deliberately extensible. Priority additions after the initial 12 are heavy landing fields, orbital cargo terminals, horizontal spaceplane runways, mass-driver terminals, offshore launch platforms, lunar/airless-body sites, large passenger spaceports, telemetry campuses, payload-clean facilities, booster recovery ports, and larger multi-pad complexes. Each new archetype must preserve the same function-first, scale-compositional, corporate-language-separated doctrine.
