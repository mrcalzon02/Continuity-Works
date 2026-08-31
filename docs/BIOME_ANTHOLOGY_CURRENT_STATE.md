# Continuity Works — Biome Anthology Current State

**Effective state date:** 2026-08-30  
**Branch:** `main`  
**Supersedes the stale anthology implementation counts in `BIOME_ANTHOLOGY_TERRAIN_FEATURE_BUILDOUT_PLAN.md` until that large tracker is reconciled.**

## Committed runtime implementation

The previously missing 128-biome anthology is now implemented on `main` by commit `0c0a5338ae4d515b7a6dfa3d6f0911d9a297594b`.

The authoritative anthology ID catalog is:

`examples/biome_expander/runtime_mod/1.20.1/src/main/anthology/biomes.json`

It contains exactly eight 16-biome families:

- primordial — 16
- ancient — 16
- medieval — 16
- renaissance_clockwork — 16
- industrial — 16
- atomic_post_collapse — 16
- advanced_scifi — 16
- neon_virtual — 16

**Anthology total: 128/128 committed.**

The ordinary Gradle/Forge build materializes the catalog into 128 worldgen biome definitions, family tags, an aggregate anthology tag, and the generated Java catalog used by runtime configuration and TerraBlender. This is build-time source materialization only; the player does not run a generator or preflight.

Every anthology biome has:

- a runtime biome definition generated into the JAR;
- a family master config gate;
- an individual biome natural-generation config gate;
- a unique TerraBlender climate parameter point;
- a baseline climate/effect profile;
- vanilla carvers and baseline ore geology;
- family/profile ecology or deliberate synthetic/sparse ecology;
- family/biome-specific surface-material behavior;
- family and aggregate biome tags.

The eight primary Abyssal biomes were subsequently wired into additive natural TerraBlender placement by commit `dd7fe2185c7eb5c59e4370c8d07d35a2b74be004`.

OSF-049 Wood Fall's missing additive biome modifier was completed by commit `2bbdc0afc4a322a37dd413dc183f7f55e00216f3`.

## Land topology expansion from the Abyssal feature system

The procedural ideas proven by the Abyssal seafloor implementation are now generalized across every non-Abyssal Continuity Works biome: **8 foundation land biomes + 128 anthology biomes = 136 land topology profiles.**

The generalized engine is implemented by:

- `LandTopologyFeature.java` — chunk-continuous absolute-coordinate terrain deformation;
- `LandTopologyProfiles.java` — authoritative profile assignment for all 136 land biomes;
- `LandTopologyMode.java` / `LandTopologyProfile.java` — reusable topology contracts;
- `LandTerrainFeatures.java` — Forge feature registration;
- `land/topology` configured and placed features;
- additive Forge biome modifiers for `#continuityworks_biomes:templates` and `#continuityworks_biomes:anthology`.

The Abyssal concepts are translated rather than blindly copied:

- pockmark/depression logic -> basins, sinkholes, karst and impact craters;
- turbidity-current channels -> gullies, river cuts, drainage channels, canals and rifts;
- shelf sand-wave morphology -> dunes, moraines and ridge trains;
- clustered seafloor/nodule/pillow relief -> tors, spoil heaps, rubble fields and synthetic spires.

Sixteen reusable land topology modes are available: `KNOLLS`, `BASINS`, `CHANNELS`, `RIDGES`, `TERRACES`, `DUNES`, `MORAINE`, `KARST`, `SCARPS`, `CRATERS`, `RIFTS`, `HUMMOCKS`, `SPOIL`, `GRID`, `SPIRES`, and `RUBBLE`.

Each anthology biome receives a biome-specific combination of primary mode, secondary mode, relief, horizontal scale, secondary strength and deterministic salt. This means similarly themed biomes do not reconstruct the same field. Wetland/channel profiles may water-fill excavated depressions; dry and engineered profiles remain open/solid according to their topology.

The eight foundation land biomes have explicit hand-set profiles matching their intended signatures: grove knolls/swales, meadow rolling relief, highland ridges/scarps, marsh hummock/channel mosaics, taiga moraine/kettle terrain, scrubland arroyos/dunes, badland scarps/ridges and ash-waste rifts/dunes.

Terrain mutation remains non-destructive toward arbitrary modded blocks: the generator only edits known natural blocks or the owning biome's declared surface materials. Absolute-coordinate sampling prevents obvious 16x16 stamp seams, and biome-boundary relief is reduced to soften transitions.

## Current conservative dashboard

| Category | Target | Runtime implementation committed | Natural placement wired | Terrain topology wired | Developer acceptance |
|---|---:|---:|---:|---:|---|
| Foundation land | 8 | 8 | 8 | 8 | pending formal run |
| Abyssal primary | 8 | 8 | 8 | existing Abyssal system | pending formal run |
| Anthology | 128 | 128 | 128 | 128 | pending formal run |
| **Total primary** | **144** | **144** | **144** | **136 generalized land + 8 Abyssal** | **pending formal run** |

`COMMITTED` and `wired` do not mean compile/runtime/worldgen acceptance has been falsely claimed. Those checks remain acceptance work. The implementation count, however, is no longer 16; all 144 primary biome definitions now have an implementation path on `main`, and every primary biome now has a terrain-topology system assigned.

No GitHub Actions are required or used for this biome implementation.
