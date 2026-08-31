# Continuity Works — Biome Cave Networks Current State

**Primary implementation commit:** `03b7afb7cea5680b85ab165cb61c3b0e6349c61d`  
**Branch:** `main`  
**Runtime:** Minecraft Java 1.20.1 / Forge

## Coverage

The cave-network system now has a deterministic profile for every one of the 144 primary Continuity Works biomes:

- 8 foundation land biomes;
- 8 primary Abyssal biomes;
- 128 anthology biomes.

`BiomeCaveProfiles.profileCount()` therefore resolves 144 primary cave signatures from the authoritative biome catalogs.

## Multi-method volumetric generation

Each biome receives a different weighted combination of:

- Perlin-style 3-D gradient noise;
- cellular / Worley nearest-cell fields;
- quantized mosaic fields;
- periodic tile fields with biome-specific rotation and phase;
- coordinate-scramble fields;
- plasma/interference noise;
- ridged multi-octave fractal masks;
- warped 3-D tunnel lattices;
- cellular chamber cores;
- vertically biased shaft fields.

The exact weights, horizontal scale, vertical scale, tunnel bias, chamber bias, shaft bias, carve threshold, flood chance, roof depth and salt are derived from the exact biome ID plus family identity. This means two biomes in the same era do not receive the same cave system.

## Partial / complete / opaque network behavior

Every primary biome is assigned one of three network coverage modes:

- `PARTIAL` — broken and branching networks with deliberate interruptions;
- `COMPLETE` — more strongly connected tunnels/chambers;
- `OPAQUE` — deep sealed networks protected by a substantially thicker roof buffer.

Semantic biome identities influence the assignment. Karst, caves, mines, quarries, fractures, trenches and geodes favor connected systems; bunkers, habitats, research zones, reactor areas and null-sector style environments favor opaque/sealed systems.

## Hydrology

Abyssal cave networks are fully flooded below sea level. Wetland, river, canal, floodplain, delta, harbor and coastal identities receive deterministic partial flooding. Arid desert/badland/waste identities remain dry by default.

## Compatibility and safety

The cave feature is attached additively through the `all_primary_biomes` tag and executes at `local_modifications`, before later underground structures are generated.

The carver only replaces recognized base geology such as Overworld base stone, deepslate, tuff, calcite, basalt, blackstone, dripstone, terracotta and sandstone. Ores, arbitrary modded blocks and structure materials are not carve targets.

Fields are evaluated from absolute world coordinates plus the world seed, preserving cross-chunk continuity rather than stamping isolated 16x16 cave pieces.

## Runtime chain

- feature registry: `BiomeCaveFeatures`
- generator: `BiomeCaveNetworkFeature`
- profiles: `BiomeCaveProfiles`
- configured feature: `caves/biome_network`
- placed feature: `caves/biome_network`
- biome modifier: `biome_cave_networks`
- biome tag: `all_primary_biomes`

## Acceptance state

Implementation and runtime wiring are **COMMITTED**.

Formal Forge compile, game load and fresh-world cave/worldgen acceptance remain **PENDING** until an execution environment is run. No compile/runtime result is being falsely claimed here.

No GitHub Actions are used or required.
