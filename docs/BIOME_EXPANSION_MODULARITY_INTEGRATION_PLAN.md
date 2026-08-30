# Continuity Works - Biome Expansion Modularity Integration Plan

**Module working name:** Biome Expander  
**Internal capability family:** `biome_expansion`  
**Repository target:** `mrcalzon02/Continuity-Works`  
**Authoritative branch:** `main`  
**Planning baseline:** August 30, 2026  
**Document purpose:** Implementation blueprint, API contract plan, staged verification program, compatibility doctrine, and release acceptance criteria for adding modular biome authoring and biome-expansion tooling to Continuity Works.

---

## 1. Executive Summary

Biome Expander is a new first-class Continuity Works capability for inspecting, modeling, creating, extending, combining, simulating, auditing, exporting, and validating Minecraft biomes in a deliberate and modular manner. It is not intended to be a monolithic "generate a biome" command. The core design is a composable biome model where climate, terrain, surface, vegetation, features, fauna, resources, structures, hydrology, atmosphere, transitions, distribution, compatibility, and performance can each be reasoned about and modified independently.

The integration must extend the existing Continuity Works implementation rather than replace it. The current repository already has the key architectural mechanisms that Biome Expander needs: a public `StructureCapability` facade, a provider-oriented generation pipeline, snapshot/resume behavior, registry and mod awareness, a portable JSON-Schema tool catalog, a publication matrix that drives executable HTTP routes and OpenAPI, serviceability gates, deterministic seeded generation patterns, and an explicit additive compatibility doctrine. Biome Expander should reuse those facilities and add biome-specific domain logic beneath them.

The most important architectural decision is that **biome changes are represented as explicit plans and patches before export**. A request to "make this forest denser" should not directly mutate files. It should resolve the environment, profile the target biome, construct a normalized patch, evaluate compatibility and ecological effects, calculate metrics, optionally simulate distribution, and only then pass an approved plan to a provider/exporter. Every material stage creates a snapshot or verification record so the system can stop safely, explain why it stopped, resume, and avoid repeating already-verified work.

Compatibility remains non-destructive. Continuity Works may author new resources under namespaces it owns and may supersede its own earlier generated resources through normal project versioning. It must not replace, clear, disable, or silently take ownership of vanilla or third-party biome generation. Changes to upstream biomes are expressed through legal additive mechanisms such as biome modifiers, tags, feature injection, supplemental selectors, weighted additions, compatibility metadata, or loader/mod-specific append-only adapters.

The implementation is intentionally staged. Each stage has a concrete deliverable, automated checks, manual or runtime verification where necessary, explicit failure codes, and a "do not advance" gate. A later stage is not considered complete merely because code exists; its entry criteria require the preceding stage's verification record to be PASS. This avoids the common failure mode of building a large worldgen stack on top of assumptions that were never independently verified.

---

## 2. Repository Grounding and Non-Redesign Constraint

This plan is grounded in the current `main` branch of Continuity Works. The implementation presently resides primarily in `src/structure_capability/`, with the package published as `structure-generation-capability`. The public facade is `StructureCapability` in `src/structure_capability/api.py`. That facade initializes mod inventory, registry resolution, Minecraft content tooling, request resolution, snapshots, the structure pipeline, and generator providers. Biome Expander should be composed into this facade rather than introducing a competing top-level service.

The existing pipeline in `src/structure_capability/pipeline.py` is provider-oriented: generic planning produces a dossier and provider contract, while a provider performs format-specific generation. That is the correct precedent for biome generation. The biome core should produce normalized biome plans, patches, metrics, and compatibility decisions. Loader/mod-specific providers should materialize those decisions into files.

The public HTTP layer in `src/structure_capability/server.py` derives executable capability paths from the authoritative publication matrix in `src/structure_capability/publication.py`. OpenAPI and serviceability checks are also derived from that matrix and the tool catalog. Therefore, biome tools should enter the system through the same catalog-and-publication route instead of adding hard-coded request dispatch logic wherever possible.

The existing tool catalog in `src/structure_capability/tooling.py` uses portable JSON Schema and public validation gates. Biome Expander should follow the same conventions: snake-case tool names, deterministic public reason codes, compact progressive-disclosure support, explicit schemas, semantic icons, and no hidden chain-of-thought exposure.

The existing compatibility policy in `docs/COMPATIBILITY_POLICY.md` establishes the fixed project invariant:

```text
mode = append_only
non_destructive = true
base_authority = preserved
```

Biome Expander inherits this policy without exception for third-party integration.

### 2.1 Existing files that should remain authoritative

- `src/structure_capability/api.py` - public Python capability facade.
- `src/structure_capability/server.py` - HTTP boundary and OpenAPI generation.
- `src/structure_capability/publication.py` - authoritative public capability matrix and serviceability gate.
- `src/structure_capability/tooling.py` - portable AI tool catalog and JSON-Schema contracts.
- `src/structure_capability/mod_awareness.py` - installed mod/resource discovery foundation.
- `src/structure_capability/registry.py` - verified resource resolution foundation.
- `src/structure_capability/snapshot.py` - snapshot persistence/resume foundation.
- `src/structure_capability/pipeline.py` - precedent for staged plan/provider behavior.
- `src/structure_capability/models.py` - structure-domain models, including biome/site context that should interoperate with the new biome model.
- `docs/COMPATIBILITY_POLICY.md` - non-destructive integration policy.
- `schemas/` - external JSON-Schema publication location.
- `tests/` - authoritative verification surface.

### 2.2 Explicit non-goals

This integration does not redesign or replace `StructureCapability`, the existing structure pipeline, content tools, HTTP service, snapshot store, mod-awareness implementation, registry resolver, or publication/serviceability mechanism. It does not require a second web service. It does not make Biome Expander the owner of all Minecraft world generation. It does not replace TerraBlender, vanilla multi-noise selection, biome modifiers, datapack registries, or third-party biome systems. It does not certify runtime compatibility from static source inspection alone.

---

## 3. Capability Mission and User-Level Outcomes

Biome Expander should support six broad outcomes.

1. **Understand an existing worldgen environment.** Inventory biome-related namespaces, registries, datapack resources, mod metadata, biome tags, configured/placed features, structures, carvers, dimension definitions, and known integration APIs before authoring anything.
2. **Normalize an existing biome.** Convert native or mod-specific biome information into a loader-neutral `BiomeProfile` so an AI can reason about the biome without directly manipulating implementation quirks.
3. **Plan modular changes.** Express changes as `BiomePatch` operations against specific layers instead of rebuilding the entire biome definition.
4. **Create coherent new biome families.** Author individual biomes, variants, transitions, and related ecological families with shared rules and controlled divergence.
5. **Measure and simulate consequences.** Estimate or measure coverage, redundancy, transition quality, climate coherence, feature pressure, structure pressure, resource drift, spawn pressure, performance cost, and compatibility risk.
6. **Export through the correct implementation provider.** Translate an approved plan into version-appropriate datapack, loader API, biome-modifier, or mod-specific resources while retaining provenance and validation evidence.

---

## 4. Design Principles

### 4.1 Modular mutation, not monolithic regeneration

Every biome is represented as separately addressable layers. A vegetation change must not silently alter temperature, precipitation, terrain placement, mobs, or structures. An AI request may explicitly target multiple layers, but the patch records every affected layer.

### 4.2 Read first, plan second, write last

The default execution order is:

```text
ENVIRONMENT INVENTORY
  -> ID / REGISTRY RESOLUTION
  -> TARGET PROFILE
  -> INTENT NORMALIZATION
  -> EXPANSION PLAN
  -> PATCH IR
  -> COMPATIBILITY GATE
  -> METRIC / BALANCE GATE
  -> OPTIONAL SEED SIMULATION
  -> PROVIDER RESOLUTION
  -> EXPORT PREVIEW
  -> MATERIALIZATION
  -> STATIC VALIDATION
  -> RUNTIME VALIDATION
  -> PROMOTION
```

### 4.3 Append-only compatibility

Third-party integration may add compatible resources or inject additions through supported APIs. It may not disable or replace native biome selection, clear feature lists, overwrite third-party JSON resources in place, or use a replacement flag to obtain easier integration.

### 4.4 Deterministic operation

Given the same normalized request, target version, installed-inventory fingerprint, provider version, and seed, planning and simulation outputs should be repeatable. Randomized ecological variation is seeded and recorded.

### 4.5 Version awareness without guessing

If the target Minecraft version or loader-specific behavior is not known, the tool must return an explicit unsupported/unknown gate rather than inventing paths, registry formats, pack formats, or DataVersion values.

### 4.6 Provider isolation

Biome semantics live in the core. Loader/mod-specific syntax lives in providers/adapters. A TerraBlender provider must not redefine the meaning of `temperature`, `world_share_target`, or `BiomePatch`; it only translates approved semantics into TerraBlender-compatible materialization.

### 4.7 Observable reasoning through reason codes

The API should report public reasons such as `BIOME_ID_UNRESOLVED`, `UPSTREAM_REPLACEMENT_FORBIDDEN`, `COVERAGE_TARGET_UNSATISFIED`, or `RUNTIME_VALIDATION_REQUIRED`. It should not emit hidden chain-of-thought.

### 4.8 Incremental verification

Each implementation stage closes with a verification artifact. Failed gates block promotion to dependent stages. Valid completed work is preserved and should not be rewritten merely because a later stage fails.

---

## 5. Proposed Package Layout

Biome Expander should be implemented inside the existing package so the current capability remains the single public authority.

```text
src/structure_capability/
  api.py
  tooling.py
  publication.py
  server.py
  ...existing modules...
  biomes/
    __init__.py
    capability.py
    models.py
    normalization.py
    inventory.py
    registry.py
    profiling.py
    families.py
    patches.py
    planning.py
    transitions.py
    distribution.py
    metrics.py
    audit.py
    simulation.py
    compatibility.py
    provider_contract.py
    providers.py
    exporters/
      __init__.py
      base.py
      vanilla_datapack.py
      forge_biome_modifier.py
      neoforge_biome_modifier.py
      fabric_adapter.py
      terrablender.py
      generic_datapack.py
    versioning.py
    reason_codes.py
```

This is a planned layout, not a requirement that every file exist in the first commit. The first stages should establish a small stable core and split files only as responsibilities become concrete.

### 5.1 Composition into the existing facade

`StructureCapability.__init__()` should instantiate a biome service using the already-created inventory, registry resolver, snapshot store, and project root, for example conceptually:

```python
self.biomes = BiomeCapability(
    project_root=self.project_root,
    inventory=self.inventory,
    registry=self.registry,
    snapshots=self.snapshots,
)
```

Public facade methods should remain thin delegators:

```python
def biome_inventory(self, request=None):
    return self.biomes.inventory(request or {})

def biome_profile(self, request):
    return self.biomes.profile(request)

def biome_plan(self, request):
    return self.biomes.plan(request)
```

This preserves one public Python capability object and allows existing publication/serviceability checks to verify biome methods in exactly the same manner as structure tools.

---

## 6. Core Domain Model

### 6.1 `BiomeIdentity`

Required or recommended fields:

```text
biome_id
namespace
path
source_authority
ownership
family_id
variant_role
display_name
tags
source_type
source_path
provider_hint
target_version
loader
```

`ownership` must distinguish at least:

- `continuity_works_owned`
- `project_owned`
- `minecraft_upstream`
- `third_party_upstream`
- `unknown`

Ownership is essential because it determines what forms of write are legal.

### 6.2 `ClimateProfile`

Normalized fields should include:

```text
temperature
humidity
downfall
precipitation_type
continentalness_range
erosion_range
weirdness_range
depth_range
climate_tags
freeze_behavior
snow_behavior
```

The core should distinguish native values from normalized 0.0-1.0 convenience values. When a native value does not map safely to a normalized value, retain both and mark the mapping confidence.

### 6.3 `TerrainProfile`

```text
elevation_bias
terrain_roughness
slope_bias
ridge_affinity
valley_affinity
coastal_affinity
river_affinity
cave_affinity
aquifer_affinity
surface_rule_refs
noise_refs
terrain_tags
```

Biome Expander should not pretend every biome system controls terrain in the same way. Fields may be `unknown`, `not_applicable`, or `provider_defined`.

### 6.4 `SurfaceProfile`

```text
top_block_roles
subsurface_roles
stone_roles
beach_roles
riverbank_roles
underwater_roles
badlands_band_roles
surface_rules
replacement_rules
```

Palette roles should be logical where possible (`topsoil`, `subsoil`, `shore`, `exposed_rock`) and resolved to actual block IDs through the registry layer.

### 6.5 `VegetationProfile`

```text
tree_density
ground_cover_density
flower_density
grass_density
fungus_density
aquatic_flora_density
canopy_closure
vertical_layering
vegetation_features
species_roles
succession_state
```

### 6.6 `FeatureProfile`

```text
configured_features
placed_features
lakes
springs
boulders
fallen_logs
patches
geodes
ice_features
volcanic_features
special_features
placement_steps
```

Feature ordering matters. The model must retain generation-step and ordering metadata where the target platform exposes it.

### 6.7 `FaunaProfile`

```text
passive_spawns
hostile_spawns
ambient_spawns
aquatic_spawns
underground_spawns
spawn_costs
creature_probability
spawn_pressure_normalized
```

### 6.8 `ResourceProfile`

```text
ore_features
sedimentary_deposits
surface_deposits
rare_materials
resource_density
resource_biases
resource_exclusions
```

The system must report resource drift when a biome expansion alters the expected availability of progression-critical resources.

### 6.9 `StructureProfile`

```text
preferred_structure_tags
allowed_structures
discouraged_structures
excluded_structures
structure_density_bias
required_contexts
structure_set_refs
```

This is the primary bridge to the existing structure capability. Biome Expander should not generate structures itself through this profile; it exposes placement context and constraints that structure generation can consume.

### 6.10 `HydrologyProfile`

```text
river_affinity
lake_affinity
wetland_affinity
coastal_affinity
groundwater_bias
water_color
water_fog_color
fluid_roles
shore_transition_rules
```

### 6.11 `AtmosphereProfile`

```text
sky_color
fog_color
water_color
water_fog_color
foliage_color
grass_color
ambient_particles
ambient_sound
mood_sound
additions_sound
music
visual_filters
```

### 6.12 `TransitionProfile`

```text
preferred_neighbors
allowed_neighbors
discouraged_neighbors
forbidden_neighbors
edge_biomes
transition_biomes
river_transition
coastal_transition
altitude_transition
climate_tolerance
blend_distance_hint
transition_weight
```

### 6.13 `DistributionProfile`

```text
world_share_target
placement_weight
cluster_size
cluster_variance
minimum_separation
regional_affinity
allowed_dimensions
excluded_dimensions
edge_complexity
isolation
seed_salt
selection_provider
```

### 6.14 `PerformanceProfile`

```text
placed_feature_count_estimate
feature_attempts_per_chunk_estimate
expensive_predicates
structure_interaction_count
carver_interactions
simulation_cost_class
estimated_generation_cost
provider_warnings
```

### 6.15 `BiomeProfile`

`BiomeProfile` is the aggregate normalized read model. It must preserve provenance for every field where possible:

```text
value
source
confidence
provider
native_value
normalized_value
```

A missing value is not equivalent to zero.

---

## 7. `BiomePatch`: The Central Mutation Intermediate Representation

The central mutation primitive is `BiomePatch`. This object is the authoritative record of what the caller intends to change and what the engine is allowed to touch.

### 7.1 Minimum patch fields

```json
{
  "patch_id": "continuityworks:patch/ashen_forest_dense_01",
  "target": "minecraft:old_growth_pine_taiga",
  "target_ownership": "minecraft_upstream",
  "mode": "append_only",
  "scope": ["vegetation", "features"],
  "operations": [],
  "constraints": {
    "preserve_existing": true,
    "allow_upstream_replacement": false,
    "require_verified_ids": true
  },
  "provenance": {},
  "reason_codes": []
}
```

### 7.2 Patch operation families

Supported operation semantics should eventually include:

```text
add_feature
add_spawn
add_structure_affinity
add_tag
add_transition
add_surface_rule
add_resource_feature
add_atmosphere_effect
adjust_owned_scalar
adjust_owned_distribution
create_biome
create_variant
create_family_member
attach_compatibility_adapter
```

Operations that would remove, clear, replace, disable, or shadow upstream behavior are invalid for compatibility targets.

### 7.3 Owned-resource edits versus upstream overlays

For `continuity_works_owned` and explicitly `project_owned` resources, a patch may revise scalar values or replace the project's own prior generated definition as part of ordinary version control. For `minecraft_upstream` and `third_party_upstream`, only additive operations are legal. This distinction prevents the compatibility doctrine from accidentally making it impossible to maintain a biome that Continuity Works itself authored while still protecting external authority.

### 7.4 Patch invariants

Every patch must satisfy:

```text
patch has stable ID
patch target resolves or target is a declared new resource
scope lists every affected layer
operations are typed
all referenced resource IDs have registry confidence
ownership is known or gated
upstream mutations are append-only
provider feasibility is known before materialization
patch has deterministic provenance fingerprint
```

---

## 8. Biome Families and Variant Generation

A `BiomeFamily` represents related biomes that share ecological identity. Families should avoid the common content-generation failure mode where every variant is independently randomized and no longer feels related.

### 8.1 Family object

```text
family_id
base_profile
shared_palette_roles
shared_climate_envelope
shared_species_roles
shared_feature_roles
shared_structure_affinities
shared_atmosphere_language
variant_rules
transition_rules
distribution_budget
```

### 8.2 Variant roles

Recommended standard roles:

```text
core
dense
sparse
hills
highlands
lowlands
wetlands
river
coast
edge
clearing
burned
decayed
ancient
rare
extreme
```

The role list remains extensible.

### 8.3 Controlled divergence

Each variant carries deltas from the family base instead of a fully unrelated profile. Example:

```text
Dense variant:
  vegetation_density +0.25
  canopy_closure +0.20
  visibility -0.30
  ground_cover_density +0.15

Hills variant:
  elevation_bias +0.35
  terrain_roughness +0.20
  lake_affinity -0.20
```

### 8.4 Family coverage budget

A family should have a total distribution budget so adding five variants does not accidentally multiply world coverage fivefold. `family_world_share_target` is divided or weighted among members unless the user explicitly expands the family's total footprint.

---

## 9. Modification Scope Levels

Biome Expander should normalize high-level intent into one of six modification scopes.

| Scope | Meaning | Typical use |
|---|---|---|
| `micro` | One or a few features, spawns, visual effects, or tag additions | Add mushrooms or a rare tree feature |
| `meso` | Multiple ecological layers without creating a distinct biome | Denser forest ecology, new fauna and ground cover |
| `macro` | A materially distinct derived biome | Create volcanic highlands from a volcanic base |
| `family` | Multiple related variants plus transitions | Forest, hills, wetland, edge variants |
| `regional` | Coordinated change across a climate/ecological region | Rebalance all cold continental biomes |
| `global` | Distribution or ecosystem rule changes affecting the whole world | Change global biome weighting policy |

Global operations require the strongest validation gate and should initially be planning/simulation-only until provider behavior is proven.

---

## 10. Tool Catalog

Tool names should follow the repository's existing snake-case convention.

### 10.1 Phase-one public tools

| Tool | Purpose |
|---|---|
| `biome_inventory` | Inventory biome/worldgen resources and providers |
| `biome_profile` | Normalize an existing biome into a `BiomeProfile` |
| `biome_compare` | Compare profiles, layers, similarity, and redundancy |
| `biome_plan` | Build an expansion or modification plan without writing files |
| `biome_patch_build` | Produce normalized `BiomePatch` IR |
| `biome_metrics` | Calculate static expansion/ecology/performance metrics |
| `biome_audit` | Run compatibility, coherence, balance, and safety gates |
| `biome_simulate` | Run deterministic distribution sampling over seeds/regions |
| `biome_generate` | Resolve a provider and materialize an approved owned biome/patch |
| `biome_export` | Export provider-specific files/artifact bundle |

### 10.2 Phase-two tools

| Tool | Purpose |
|---|---|
| `biome_family_generate` | Create a coherent family and member deltas |
| `biome_transition_generate` | Plan or author edge/transition relationships |
| `biome_distribution_plan` | Design placement weights, cluster behavior, and coverage budgets |
| `biome_balance` | Recommend bounded adjustments based on metric failures |
| `biome_compatibility_plan` | Produce non-destructive adapter overlays for detected worldgen systems |
| `biome_provider_probe` | Explain which provider can materialize a requested change and why |

### 10.3 Tool-group metadata

All biome tools should be tagged to a `biome` tool group in the compact index so an AI can request only the biome tool surface. Progressive disclosure should work exactly as it does for existing tools.

---

## 11. Public HTTP API Plan

Recommended canonical endpoints:

```text
POST /v1/biomes/inventory
POST /v1/biomes/profile
POST /v1/biomes/compare
POST /v1/biomes/plan
POST /v1/biomes/patch
POST /v1/biomes/metrics
POST /v1/biomes/audit
POST /v1/biomes/simulate
POST /v1/biomes/generate
POST /v1/biomes/export
POST /v1/biomes/family
POST /v1/biomes/transition
POST /v1/biomes/distribution
POST /v1/biomes/balance
POST /v1/biomes/compatibility
POST /v1/biomes/provider/probe
```

Each public tool must have exactly one `PublicCapabilitySpec` entry. The existing `PUBLIC_SERVICEABILITY` gate should fail if a biome tool exists in the catalog without a route, if a route lacks a tool, if the capability method is missing, or if OpenAPI does not map the route to the correct tool.

### 11.1 Do not special-case OpenAPI

The existing server derives capability paths from `PUBLIC_CAPABILITIES`. The biome implementation should use that same path. Only generic request schemas or helper functions should be added to `server.py` if required; individual biome routes should not be manually duplicated in `do_POST`.

### 11.2 Discovery

Biome tools automatically appear in `/v1/tools`, `/v1/tools/index`, tool contracts, OpenAPI, and serviceability when the tool catalog and publication matrix are synchronized. Discovery documentation should add a human-readable biome capability summary but should not invent a second discovery document.

---

## 12. Request Schemas

### 12.1 Shared biome context

A reusable schema fragment should include:

```text
target_version
loader
project_root_hint
namespace
id_policy
seed
world_seed
dimension
provider_hint
strict_runtime_gate
metadata
```

### 12.2 `biome_profile` request

Required:

```text
biome_id
```

Optional:

```text
target_version
loader
include_native
include_provenance
include_features
include_spawns
include_structures
include_distribution
```

### 12.3 `biome_plan` request

Required:

```text
operation
```

One of:

```text
target_biome_id
new_biome_id
family_id
```

Intent fields:

```text
scope_level
target_layers
goals
constraints
preserve
world_share_target
style/theme hints
ecology hints
structure affinities
compatibility targets
```

### 12.4 `biome_simulate` request

```text
plan_id or inline plan
seeds
sample_radius_blocks
sample_grid
regions_per_seed
provider_mode
metrics
confidence_target
max_cost
```

Phase one simulation may operate on normalized distribution models rather than invoking Minecraft itself. Runtime execution is a later provider/test-harness concern and must be labeled accordingly.

---

## 13. Registry and Inventory Expansion

The existing inventory system should be extended rather than duplicated.

### 13.1 Resource types to detect

At minimum:

```text
biome
biome tag
configured feature
placed feature
carver
structure
structure set
noise settings
noise
surface rule references
density function
dimension
dimension type
world preset
multi-noise parameter list or equivalent selection data
forge/neoforge biome modifier resources
fabric worldgen entry points when statically discoverable
TerraBlender-related namespaces/config markers
known third-party biome namespaces
```

### 13.2 Confidence model

Reuse or extend the current confidence semantics:

```text
vanilla
exact
candidate
namespace
unknown
```

Biome operations that affect materialized worldgen should normally require `vanilla` or `exact` confidence for every referenced ID. `candidate` may be accepted for planning with a warning but not for final export unless the provider explicitly supports deferred resolution.

### 13.3 Inventory fingerprint

Every biome plan and export should store an inventory fingerprint based on relevant namespaces/resources. If the environment changes between plan and export, the system returns `ENVIRONMENT_FINGERPRINT_CHANGED` and revalidates affected IDs before writing.

---

## 14. Profiling and Normalization

`biome_profile` is intentionally read-only and should be implemented early because every later capability depends on it.

### 14.1 Profile pipeline

```text
resolve biome ID
 -> determine ownership/source
 -> locate native resource or provider representation
 -> parse known fields
 -> resolve referenced features/tags where safe
 -> normalize layer values
 -> attach provenance/confidence
 -> compute profile fingerprint
 -> snapshot
```

### 14.2 Partial profiles are valid

Modded systems may expose incomplete static data. A profile can return `PARTIAL` if core identity is known but some layers are provider-defined or runtime-only. It must enumerate missing domains rather than fill them with fabricated defaults.

### 14.3 Profile status

Recommended statuses:

```text
COMPLETE
PARTIAL
UNRESOLVED
UNSUPPORTED_PROVIDER
INVALID_SOURCE
```

---

## 15. Planning Engine

`biome_plan` converts user intent into an explicit proposal.

### 15.1 Planning output

```text
plan_id
request_fingerprint
inventory_fingerprint
target_profile_fingerprint
operation
scope_level
ownership_decision
layers_affected
preserve_contract
proposed_patch_ids
provider_candidates
metric_targets
simulation_requirements
runtime_validation_requirements
warnings
blocking_findings
status
snapshot
```

### 15.2 Plan status

```text
READY_FOR_PATCH
READY_FOR_SIMULATION
READY_FOR_PROVIDER
BLOCKED
NEEDS_RUNTIME_VALIDATION
UNSUPPORTED
```

### 15.3 Preserve contract

Every plan includes a preserve contract. For upstream targets it always includes:

```text
existing biome definition
native biome selector authority
existing placed/configured features
native structure selection
native spawn tables
existing tags and third-party entries
existing distribution logic unless an additive provider supports extension
```

---

## 16. Compatibility Adapter Doctrine

### 16.1 General adapter contract

Every compatibility adapter returns a normalized record:

```json
{
  "adapter_id": "...",
  "target_system": "...",
  "mode": "append_only",
  "preserve_existing": true,
  "provider": "...",
  "additions": {},
  "forbidden_operations": [
    "replace_existing",
    "disable_native",
    "clear_entries"
  ],
  "runtime_validation_required": true
}
```

### 16.2 Vanilla/datapack integration

The vanilla provider should favor creation of owned biome resources and supported datapack registries. Modifying existing vanilla biomes may require a loader-specific modifier mechanism rather than pretending vanilla datapacks provide an append API for every layer. The provider must reject unsupported modifications instead of rewriting the upstream biome JSON.

### 16.3 Forge / NeoForge biome modifiers

Where the target version exposes biome modifier systems, use them for additive feature, spawn, structure, or similar injections that the API genuinely supports. Provider capability tables must be versioned.

### 16.4 Fabric

Fabric support should be provider-driven and limited to APIs actually detected/supported for the target environment. If a generated Java/Kotlin source adapter is required, that must be clearly separated from datapack-only export.

### 16.5 TerraBlender

TerraBlender should be treated as a distribution/region provider, not as a new semantic model. The core defines desired distribution; the provider translates to TerraBlender regions/weights where supported.

### 16.6 Third-party biome mods

Adapters for Biomes O' Plenty, Regions Unexplored, Terralith, or other systems should be added only after source/runtime research establishes a supported additive integration point. Presence of a namespace does not imply permission or technical feasibility to mutate that mod's biome definitions.

---

## 17. Expansion Metrics

Metrics are divided into descriptive, risk, ecological, world-distribution, and cost domains. Static metrics must state when they are estimates rather than measured runtime values.

### 17.1 Primary 0-100 scores

```text
DiversityGain
BiomeRedundancy
TransitionQuality
ClimateCoherence
EcologicalCoherence
ExplorationValue
CompatibilityRisk
PerformanceCost
ResourceDriftRisk
SpawnPressureRisk
StructurePressureRisk
```

For risk metrics, higher means worse. For quality/value metrics, higher means better. Responses must explicitly include directionality to prevent caller confusion.

### 17.2 Coverage metrics

```text
coverage_target
coverage_estimated_mean
coverage_estimated_p05
coverage_estimated_p95
family_coverage_total
coverage_error_absolute
coverage_error_relative
```

### 17.3 Fragmentation metrics

```text
fragmentation_index
mean_cluster_area
median_cluster_area
cluster_area_variance
isolation_index
edge_to_area_ratio
```

### 17.4 Ecological metrics

```text
flora_density_index
fauna_pressure_index
vertical_layering_index
feature_diversity_index
species_role_coverage
rare_feature_rate
hostile_to_passive_ratio
```

### 17.5 Resource metrics

```text
critical_resource_delta
rare_resource_delta
ore_attempt_delta
resource_concentration_change
progression_risk
```

### 17.6 Structure interaction metrics

```text
structure_affinity_count
structure_exclusion_count
expected_structure_density_delta
biome_restriction_conflicts
terrain_requirement_conflicts
```

### 17.7 Performance metrics

```text
feature_attempts_delta
expensive_predicate_count
nested_placement_modifier_count
estimated_generation_cost_class
simulation_cost
provider_specific_cost_warnings
```

### 17.8 Metric evidence

Every metric should include:

```text
value
scale
direction
method
confidence
evidence_source
threshold
status
```

---

## 18. Similarity and Redundancy Analysis

`biome_compare` should support pairwise and family-level comparison.

A normalized similarity vector can consider:

```text
climate similarity
surface palette similarity
vegetation role similarity
feature-set overlap
spawn-table overlap
atmosphere similarity
terrain affinity similarity
resource similarity
transition neighborhood similarity
```

This prevents "new biome" generation that only changes grass color while duplicating an existing biome's ecology and distribution.

Recommended warning thresholds:

```text
0-49   materially distinct
50-69  related but distinguishable
70-84  high overlap; justify variant role
85-100 likely redundant unless intentionally a subtle variant
```

Thresholds are policy defaults and should be configurable.

---

## 19. Seed and Distribution Simulation

### 19.1 Simulation tiers

**Tier A - Analytical/static.** Uses normalized weights, climate envelopes, and provider models without launching Minecraft. Fast and appropriate for early plan validation.

**Tier B - Provider emulation.** Executes deterministic provider selection logic when it can be safely reproduced outside Minecraft. Higher confidence but provider-specific.

**Tier C - Runtime worldgen test.** Launches or instruments a supported Minecraft test environment, generates sample regions, and records actual biome placement. This is the promotion-quality distribution test and is necessarily environment-dependent.

The initial implementation should deliver Tier A cleanly before claiming Tier B or C.

### 19.2 Sampling contract

A simulation run records:

```text
simulation_id
plan_id
provider_id
provider_version
inventory_fingerprint
seed list
sample radius/grid
sample count
sampling algorithm
metric outputs
confidence interval
warnings
runtime/static classification
snapshot
```

### 19.3 Deterministic seeds

If the caller does not supply seeds, derive them deterministically from the plan fingerprint plus a documented salt. This makes CI simulation reproducible.

---

## 20. Audit Gates and Reason Codes

### 20.1 Gate categories

```text
SCHEMA_GATE
REGISTRY_GATE
OWNERSHIP_GATE
COMPATIBILITY_GATE
ECOLOGY_GATE
DISTRIBUTION_GATE
RESOURCE_GATE
STRUCTURE_INTERACTION_GATE
PERFORMANCE_GATE
PROVIDER_GATE
STATIC_EXPORT_GATE
RUNTIME_GATE
PUBLICATION_GATE
```

### 20.2 Example blocking codes

```text
BIOME_ID_UNRESOLVED
BIOME_SOURCE_UNSUPPORTED
BIOME_OWNERSHIP_UNKNOWN
UPSTREAM_REPLACEMENT_FORBIDDEN
DESTRUCTIVE_PATCH_FORBIDDEN
FEATURE_ID_UNRESOLVED
ENTITY_ID_UNRESOLVED
STRUCTURE_ID_UNRESOLVED
DIMENSION_ID_UNRESOLVED
PROVIDER_NOT_FOUND
PROVIDER_VERSION_UNSUPPORTED
PROVIDER_OPERATION_UNSUPPORTED
ENVIRONMENT_FINGERPRINT_CHANGED
COVERAGE_TARGET_UNSATISFIED
FAMILY_COVERAGE_EXCEEDED
BIOME_REDUNDANCY_EXCESSIVE
TRANSITION_CONFLICT
CLIMATE_INCOHERENCE
RESOURCE_DRIFT_EXCESSIVE
SPAWN_PRESSURE_EXCESSIVE
STRUCTURE_PRESSURE_EXCESSIVE
PERFORMANCE_BUDGET_EXCEEDED
STATIC_EXPORT_INVALID
RUNTIME_VALIDATION_REQUIRED
RUNTIME_PLACEMENT_FAILED
RUNTIME_REGISTRY_ERROR
RUNTIME_DATAPACK_REJECTED
PUBLICATION_CONTRACT_MISMATCH
```

### 20.3 Severity

```text
info
advisory
warning
error
blocking
```

Only `blocking` prevents the next stage by definition. Policy may elevate selected `error` codes to blocking for release builds.

---

## 21. Snapshot and Resume Model

Biome Expander should use the existing `SnapshotStore` rather than create its own persistence system.

Snapshot stages should include:

```text
biome_inventory
biome_profile
biome_plan
biome_patch
biome_metrics
biome_simulate
biome_export_preview
biome_generate
biome_runtime_validation
```

Every stage snapshot should link to the preceding snapshot through `parent`. Exported/generated artifacts should be attached in the same manner as existing generated artifacts.

Resume behavior should support loading the complete prior stage dossier and continuing from the first unverified stage, provided the environment fingerprint still matches. If it does not, the system should preserve the prior result, mark it stale, re-run only environment-dependent verification, and avoid rebuilding unrelated planning work.

---

## 22. Structure Capability Integration: World Context Bus

Biome Expander and Structure Generation should remain separate capabilities that exchange normalized context.

### 22.1 Shared context produced by Biome Expander

```text
biome IDs and tags
climate envelope
terrain/slope affinities
surface palette roles
hydrology/coastal flags
structure preferences/exclusions
resource pressure
spawn pressure
transition context
worldgen provider identity
```

### 22.2 Structure requests consume biome context

The existing `SiteContext` already contains `biomes`, `biome_tags`, terrain, climate, fluid, sea level, slope, nearby features, exclusion zones, and placement data. Biome Expander should populate or validate these fields rather than replacing `SiteContext`.

### 22.3 Structure-to-biome feedback

Structure Generation may return normalized constraints such as:

```text
requires_coast
requires_flat_area
avoid_wetlands
avoid_high_structure_pressure
prefer_ruined_industrial_family
requires_road_connector
```

Biome Expander can use those constraints during distribution/compatibility planning. It does not become responsible for building the structure.

### 22.4 Circular dependency prevention

The core modules should exchange plain data contracts rather than import each other's high-level capability objects. A small context contract module may eventually be justified if direct imports become cyclic.

---

## 23. Frontend / StructureForge Integration Plan

The frontend should expose Biome Expander as a separate capability surface with progressive stages rather than a single large form.

### 23.1 Recommended workflow panels

```text
1. Environment
2. Target / New Biome
3. Intent and Scope
4. Layer Editor
5. Family / Transition Editor
6. Distribution
7. Metrics
8. Simulation
9. Compatibility Provider
10. Export / Validation
```

### 23.2 Progressive visibility

A user modifying only vegetation should not be forced through every distribution setting. Advanced panels should appear when the requested scope requires them.

### 23.3 Stage status visualization

Each panel displays:

```text
NOT_STARTED
RUNNING
PASS
PASS_WITH_WARNINGS
BLOCKED
STALE
RUNTIME_REQUIRED
```

The UI should show public reason codes and the artifact/snapshot ID for each stage.

### 23.4 Visual biome review

Server-side rendering should not be required. The client may display maps, charts, palette previews, generated resource trees, or runtime screenshots when available. Visual inspection remains supplementary to machine validation.

---

## 24. Proposed External JSON Schemas

The following schema files should eventually be added under `schemas/`:

```text
biome_profile_request.schema.json
biome_plan_request.schema.json
biome_patch.schema.json
biome_metrics_request.schema.json
biome_simulation_request.schema.json
biome_export_request.schema.json
biome_family_request.schema.json
```

The tool catalog remains the runtime source of the portable AI contracts. External schema files should be validated against catalog definitions in tests to prevent drift.

---

# 25. Incremental Implementation and Verification Program

The following stages are deliberately sequential. A stage is complete only when its verification gate passes. Code existence alone is not completion.

## Stage 0 - Baseline Capture and Contract Freeze

### Goal

Record the current repository behavior and establish biome-integration invariants before code changes.

### Implementation tasks

- Confirm `main` is the implementation branch used for this work.
- Run the existing automated test suite and preserve its result.
- Record current tool catalog schema version and public tool count.
- Record current `PUBLIC_SERVICEABILITY` result locally.
- Record current OpenAPI path set.
- Record current package version.
- Confirm existing structure, dungeon, infrastructure, Minecraft content, snapshot, and publication tests pass.
- Add a planning/reference fixture describing the append-only biome doctrine.

### Verification

- Existing tests: PASS.
- Existing tool catalog unchanged: PASS.
- Existing OpenAPI routes unchanged: PASS.
- Existing public capability matrix internally consistent: PASS.

### Do not advance if

Any pre-existing test failure is unexplained, the branch is not the intended implementation branch, or the publication gate is already broken.

### Deliverables

```text
baseline test report
baseline capability inventory
baseline OpenAPI snapshot
biome invariants fixture
```

---

## Stage 1 - Biome Domain Models and Reason Codes

### Goal

Create loader-neutral biome data structures with no file writes and no public routes.

### Implementation tasks

- Add `biomes/models.py`.
- Implement `BiomeIdentity`, layer profiles, `BiomeProfile`, `BiomePatch`, `BiomeFamily`, distribution objects, metric evidence records, and provider capability records.
- Add serialization methods with stable output ordering where practical.
- Add `reason_codes.py` constants/enums.
- Implement ownership classification enum.
- Implement patch operation enum and scope enum.

### Automated verification

- Round-trip dict -> model -> dict tests.
- Unknown/missing values remain distinct from zero/false.
- Enum validation rejects invalid destructive modes.
- Upstream ownership cannot produce replacement operations.
- Serialization is deterministic for identical inputs.

### Gate: `BIOME_MODEL_CONTRACT`

PASS only when all model tests pass and no existing tests regress.

### Rollback rule

If model design proves inadequate, modify only the new biome model code. Do not change the public facade, server, or existing structure models to compensate prematurely.

---

## Stage 2 - Inventory and Registry Extension

### Goal

Teach the existing inventory/resolver enough biome/worldgen vocabulary to identify real resources without authoring.

### Implementation tasks

- Extend resource discovery for biome/worldgen paths.
- Add resource kinds to registry probing.
- Add ownership/source classification.
- Add biome-relevant inventory fingerprint calculation.
- Preserve existing item/recipe/loot/structure discovery behavior.

### Automated verification

Fixtures should include:

```text
vanilla-like datapack biome
modded namespace biome
biome tag
configured feature
placed feature
structure set
unknown ID
namespace-only candidate
malformed JSON
```

Required tests:

- Exact IDs resolve with exact confidence.
- Unknown IDs remain unknown.
- Namespace presence does not produce false exact resolution.
- Existing registry-probe tests remain unchanged.
- Fingerprint changes when relevant biome resources change.
- Fingerprint does not change for irrelevant non-worldgen file edits unless policy explicitly includes them.

### Gate: `BIOME_REGISTRY_READINESS`

Do not advance until fixture coverage is complete and there are no regressions in existing registry behavior.

---

## Stage 3 - Read-Only Biome Profiling

### Goal

Produce normalized profiles without planning or writing changes.

### Implementation tasks

- Implement biome source loading.
- Normalize vanilla/datapack fields first.
- Resolve referenced features and tags where feasible.
- Preserve provenance and confidence.
- Return partial profiles for unsupported provider-specific fields.
- Snapshot profile results.

### Automated verification

- Known vanilla-style fixture normalizes correctly.
- Missing optional fields remain unknown/not-applicable.
- Invalid source produces structured findings.
- Third-party resource is classified as upstream.
- Profile fingerprint is deterministic.
- Snapshot contains request, profile, provenance, and inventory fingerprint.

### Manual verification

Review at least three representative profiles for semantic accuracy: sparse biome, heavily featured biome, and biome with modded namespace references.

### Gate: `BIOME_PROFILE_READINESS`

PASS requires semantic fixture review plus automated tests.

---

## Stage 4 - Planning and Patch IR

### Goal

Convert intent into a legal, explicit, non-destructive proposal.

### Implementation tasks

- Implement scope normalization.
- Implement layer-target normalization.
- Implement preserve contract.
- Implement patch builder.
- Implement ownership gate.
- Implement provider feasibility placeholders.
- Add plan/patch snapshots.

### Verification scenarios

1. Add one feature to vanilla biome -> append-only PASS.
2. Remove vanilla feature -> BLOCKED with `DESTRUCTIVE_PATCH_FORBIDDEN`.
3. Replace third-party biome definition -> BLOCKED with `UPSTREAM_REPLACEMENT_FORBIDDEN`.
4. Revise Continuity Works-owned biome scalar -> allowed with provenance.
5. Create new namespaced biome -> allowed if namespace policy passes.
6. Reference unresolved placed feature -> BLOCKED before export.

### Gate: `BIOME_PATCH_SAFETY`

No provider/export implementation begins until destructive-operation tests pass.

---

## Stage 5 - Static Metrics and Audit Engine

### Goal

Evaluate quality/risk before any world-distribution simulation or file materialization.

### Implementation tasks

- Implement metric evidence wrapper.
- Implement climate coherence.
- Implement similarity/redundancy.
- Implement ecological density/coherence.
- Implement resource drift estimate.
- Implement spawn pressure estimate.
- Implement structure pressure estimate.
- Implement performance-cost heuristic.
- Implement audit gate aggregation.

### Verification

- Metric direction is explicit.
- Same inputs produce same scores.
- Missing evidence lowers confidence rather than fabricating precision.
- Threshold boundary tests exist.
- High redundancy fixture triggers warning/block according to policy.
- Extreme feature density triggers performance warning.
- Critical resource shift triggers resource-risk finding.

### Gate: `BIOME_STATIC_AUDIT`

PASS requires documented metric formulas or heuristics and tests for every blocking threshold.

---

## Stage 6 - Tier A Distribution Simulation

### Goal

Provide deterministic analytical seed/distribution sampling without claiming Minecraft runtime truth.

### Implementation tasks

- Implement deterministic seed derivation.
- Implement normalized cluster/coverage model.
- Compute coverage intervals, fragmentation, isolation, and family budget.
- Record method as `analytical_static`.
- Snapshot simulation inputs and outputs.

### Verification

- Fixed seed set is repeatable.
- More placement weight increases estimated coverage monotonically within model assumptions.
- Family budget prevents accidental multiplicative coverage.
- Coverage target failure is surfaced.
- Simulation clearly labels itself non-runtime.

### Gate: `BIOME_ANALYTICAL_SIMULATION`

The UI/API must not label Tier A output as actual generated-world coverage.

---

## Stage 7 - Provider Registry and Export Preview

### Goal

Resolve how an approved patch could be materialized, without yet promising every provider.

### Implementation tasks

- Add biome provider protocol/interface.
- Add provider registry.
- Add capability matrix: supported versions, loaders, operations, and resource types.
- Implement an export preview artifact tree.
- Implement provider probe tool internally.

### Verification

- Unsupported operations return `PROVIDER_OPERATION_UNSUPPORTED`.
- Unsupported target versions return `PROVIDER_VERSION_UNSUPPORTED`.
- Provider choice is deterministic for identical environments.
- Provider cannot change patch semantics.
- Preview contains only namespaced output paths allowed by ownership policy.

### Gate: `BIOME_PROVIDER_RESOLUTION`

No materialization until provider path ownership and operation capability are verified.

---

## Stage 8 - First Materialization Provider

### Recommended first provider

Start with the narrowest high-confidence provider: creation/export of Continuity Works-owned vanilla-style datapack biome resources for a specifically supported Minecraft version range. Do not start by trying to mutate every existing biome across every loader.

### Implementation tasks

- Implement provider version contract.
- Generate resource JSON.
- Generate pack manifest through existing version-aware content utilities where practical.
- Validate namespace/path safety.
- Attach generated artifacts to snapshot.

### Static verification

- JSON parses.
- Required registry fields exist.
- All referenced IDs pass registry gate.
- File paths match target-version contract.
- Export does not overwrite third-party source paths.
- Golden fixture comparison passes.

### Gate: `BIOME_FIRST_EXPORT`

PASS means "static artifact valid for the supported contract," not "runtime placement proven."

---

## Stage 9 - Runtime Validation Harness for First Provider

### Goal

Prove generated resources load and participate in actual Minecraft worldgen.

### Required runtime checks

```text
pack/mod loads without registry error
biome registers
world creates successfully
biome can be located or observed
expected climate/visual fields appear
expected features/spawns appear where testable
no upstream biome disappears
no worldgen crash in sampled region
generated logs captured
```

### Fresh-world requirement

Runtime verification must use fresh worlds for worldgen-placement tests. Reusing an already-generated region is not acceptable evidence that distribution changes work.

### Gate: `BIOME_RUNTIME_FIRST_PROVIDER`

Only after this gate passes may the provider be marked runtime-validated for that version/loader combination.

---

## Stage 10 - Public Tool Catalog Integration

### Goal

Expose stable read/plan/audit tools to AI clients using existing progressive disclosure.

### Recommended first public subset

```text
biome_inventory
biome_profile
biome_compare
biome_plan
biome_patch_build
biome_metrics
biome_audit
biome_provider_probe
```

Simulation and generation may remain internal until their prior gates pass.

### Implementation tasks

- Add JSON schemas to `tooling.py`.
- Add semantic icon metadata.
- Add tool group metadata.
- Add request-resolution presets if appropriate.
- Bump tool schema version.

### Verification

- `/v1/tools` includes exact schemas.
- `/v1/tools/index?group=biome` returns compact biome tools.
- Individual tool contract retrieval works.
- Existing non-biome tool contracts remain byte/semantically stable except schema-version metadata where expected.

### Gate: `BIOME_TOOL_CATALOG`

No public route publication until catalog contracts pass schema validation.

---

## Stage 11 - Public Route, OpenAPI, Discovery, and Serviceability Integration

### Goal

Publish verified biome tools through the existing public boundary.

### Implementation tasks

- Add one `PublicCapabilitySpec` per published biome tool.
- Add thin delegator methods to `StructureCapability`.
- Confirm server route dispatch requires no tool-specific hard coding.
- Confirm OpenAPI operation maps include `x-structuresmith-tool`.
- Update discovery capability list automatically through publication tooling.

### Verification

- Local `PUBLIC_SERVICEABILITY` status is `READY_FOR_REMOTE_VERIFICATION`.
- No `TOOL_ROUTE_MISSING`.
- No `CATALOG_MISMATCH`.
- No `OPENAPI_MISMATCH`.
- Capability methods are callable.
- CORS behavior unchanged.

### Remote verification

After deployment:

```text
GET /v1/health
GET /v1/tools
GET /v1/tools/index?group=biome
GET /openapi.json
GET /.well-known/structuresmith.json
POST each published biome route with valid request
POST selected invalid requests and confirm structured rejection
```

### Gate: `BIOME_PUBLIC_SERVICEABILITY`

Public documentation must not claim deployed availability until remote verification passes.

---

## Stage 12 - Structure/Biome Context Integration

### Goal

Allow structure generation to consume biome profiles and biome planning to understand structure constraints without creating a circular subsystem.

### Implementation tasks

- Define normalized context exchange record.
- Add helper to map `BiomeProfile` -> existing `SiteContext` fields.
- Add optional structure affinity/exclusion data to biome planning.
- Add tests for coast, wetland, slope, climate, and exclusion mapping.

### Verification

- Existing structure requests without biome integration behave identically.
- Added biome context enriches but does not overwrite explicit caller context unless a merge policy says so.
- Conflicts are reported, not silently resolved.
- No import cycle introduced.

### Gate: `WORLD_CONTEXT_INTEROP`

---

## Stage 13 - Family and Transition Generation

### Goal

Support coherent multi-biome ecological families.

### Implementation tasks

- Implement family base + variant delta model.
- Implement family coverage budget.
- Implement transition graph validation.
- Implement redundancy checks among siblings.
- Implement family generation tool.

### Verification

- Variant deltas preserve family identity.
- Total coverage respects family budget.
- Transition graph has no impossible forbidden/preferred contradictions.
- Sibling redundancy thresholds produce advisory/blocking findings.

### Gate: `BIOME_FAMILY_COHERENCE`

---

## Stage 14 - Additive Existing-Biome Provider

### Goal

Support one proven loader/version mechanism for extending an upstream biome without replacement.

### Implementation tasks

- Select one provider only after confirming target API semantics.
- Implement supported operation subset.
- Prove no replacement flag/path is emitted.
- Add runtime fixture mod/datapack.

### Required destructive regression tests

Attempts to:

```text
clear features
replace entire biome JSON
remove upstream spawns
disable native biome source
replace provider table
```

must all fail before artifact creation.

### Runtime verification

Confirm added feature/spawn/etc. appears while original upstream behavior remains present.

### Gate: `ADDITIVE_UPSTREAM_RUNTIME`

This gate must be provider/version specific. Passing Forge 1.x does not certify NeoForge, Fabric, TerraBlender, or another version.

---

## Stage 15 - Tier B / Tier C Simulation and Performance Characterization

### Goal

Increase confidence from analytical estimates to provider emulation and runtime sampling.

### Implementation tasks

- Add provider emulation only where source behavior is sufficiently defined.
- Add runtime sample-world harness.
- Record chunk/region sampling strategy.
- Measure generation time and worldgen errors.
- Compare analytical estimates with runtime results.

### Verification

- Runtime results include seed and sample coordinates.
- Divergence between Tier A and runtime is quantified.
- Metrics are recalibrated if static estimates are systematically biased.
- Performance budget has measured evidence.

### Gate: `BIOME_RUNTIME_SIMULATION`

---

## Stage 16 - Frontend Workbench

### Goal

Expose the capability to human users without weakening API validation.

### Implementation tasks

- Add Biome Expander navigation surface.
- Add staged form state.
- Add profile diff display.
- Add metric table/chart views.
- Add simulation summary.
- Add provider/export preview tree.
- Add reason-code display.
- Add resume/snapshot selection.

### Verification

- Every UI action calls the public API rather than duplicating worldgen logic in JavaScript.
- UI cannot bypass blocking validation.
- Failed API call preserves entered values.
- Existing structure dashboard remains functional.
- Accessibility and keyboard navigation checked.

### Gate: `BIOME_WORKBENCH`

---

## Stage 17 - Documentation, Examples, and Release Hardening

### Goal

Make the capability understandable to humans and tool-calling AIs and freeze a support matrix.

### Documentation deliverables

```text
docs/BIOME_EXPANSION_MODULARITY_INTEGRATION_PLAN.md
docs/BIOME_EXPANDER.md
docs/BIOME_PROVIDER_CONTRACT.md
docs/BIOME_METRICS.md
docs/BIOME_RUNTIME_VALIDATION.md
docs/API.md updates
README capability summary
examples/biomes/... request/response fixtures
```

### Verification

- Documentation claims match provider support matrix.
- Every public example validates against JSON Schema.
- Every example tool exists in public catalog.
- Unsupported versions are clearly marked.
- No runtime-unverified provider is described as validated.

### Final release gate: `BIOME_EXPANDER_RELEASE`

Requires all release-target stages PASS, existing Continuity Works regression suite PASS, public serviceability PASS, remote endpoint verification PASS, and at least one end-to-end fresh-world runtime test for every provider/version combination claimed as supported.

---

## 26. Stage Verification Record Format

Every stage should produce a machine-readable verification record resembling:

```json
{
  "gate": "BIOME_PATCH_SAFETY",
  "stage": 4,
  "status": "PASS",
  "commit": "<git sha>",
  "inventory_fingerprint": "<hash or null>",
  "tests": {
    "passed": 42,
    "failed": 0,
    "skipped": 1
  },
  "findings": [],
  "artifacts": [],
  "verified_at": "<UTC timestamp>",
  "verification_class": "static",
  "next_gate": "BIOME_STATIC_AUDIT"
}
```

Recommended status values:

```text
PASS
PASS_WITH_WARNINGS
FAIL
BLOCKED
STALE
NOT_RUN
```

A warning must include an explicit reason code and explain whether it affects promotion.

---

## 27. Failure and Recovery Rules

The implementation should follow a fail-safe incremental recovery policy.

1. Preserve any already-valid stage output when a later stage fails.
2. Record the exact failed gate, test, provider, input fingerprint, and reason code.
3. Apply the smallest repair that restores the failed contract.
4. Re-run the failed gate and all directly dependent gates.
5. Do not broadly rewrite working upstream modules simply to avoid fixing a biome-specific defect.
6. If an environment fingerprint changed, revalidate only environment-dependent stages before recomputing stable semantic planning.
7. Runtime failure never authorizes a destructive compatibility fallback.

---

## 28. Testing Strategy

### 28.1 Unit tests

Cover normalization, model serialization, patch legality, ownership rules, metrics, provider selection, path generation, reason codes, and deterministic simulation.

### 28.2 Golden fixtures

Keep known request -> profile/plan/patch/export examples. Golden output should focus on semantic stability and avoid fields that legitimately vary by timestamp or commit.

### 28.3 Property tests

High-value properties include:

```text
upstream patch never contains replacement operation
same seed/input produces same analytical simulation
family member weights never exceed family budget unless explicitly allowed
unknown IDs never become exact without evidence
provider export never escapes allowed output root
```

### 28.4 Regression tests

Every biome milestone runs the complete existing structure/content suite. Biome support is not acceptable if it destabilizes structure generation.

### 28.5 Runtime matrix

Track runtime verification by exact tuple:

```text
minecraft_version
loader
loader_version
provider
provider_version
representative mod set
```

Never collapse runtime evidence into a generic "Forge supported" statement.

---

## 29. Security and Path-Safety Requirements

Biome export accepts user-controlled namespaces, IDs, and artifact names, so path validation is mandatory.

- Reject `..`, absolute paths, drive prefixes, NULs, and separator injection in resource IDs.
- Normalize namespaced IDs before output mapping.
- Export only beneath a declared artifact root.
- Never write directly into installed mod JARs.
- Never modify third-party source files in place as a compatibility mechanism.
- Treat uploaded/extracted datapacks as untrusted input.
- Limit recursive resource expansion and file-size consumption.
- Bound simulation seed/sample counts through schema limits.

---

## 30. Performance Budgets

Phase-one static operations should remain lightweight enough for API use.

Recommended default limits:

```text
profile referenced-resource expansion: bounded depth
compare profiles per request: <= 32 by default
simulation seeds: <= 100 by default
simulation grid/sample cells: bounded configurable maximum
family members: <= 32 by default
patch operations: <= 512 by default
```

Higher limits may be allowed through explicit server configuration, not unbounded user input.

Cache opportunities:

```text
inventory fingerprints
parsed resource JSON by file hash
resolved registry IDs
normalized biome profiles by source hash
metric vectors by profile fingerprint
simulation results by plan+seed+provider fingerprint
```

Caches are acceleration only; snapshots remain the durable provenance mechanism.

---

## 31. Versioning Strategy

Three versions must be tracked independently:

```text
Continuity Works package version
tool schema version
biome model/provider contract version
```

A provider must also declare its supported Minecraft/loader matrix. Tool schemas should be backward-compatible within the existing public API version where practical. Breaking request/response semantics require either explicit schema-version negotiation or a future API version, not silent reinterpretation.

---

## 32. Provider Capability Matrix Format

Each provider should declare something like:

```json
{
  "provider_id": "continuityworks:vanilla_datapack_biome",
  "provider_contract": "1.0",
  "minecraft_versions": ["1.20.1"],
  "loaders": ["vanilla", "forge", "fabric", "neoforge"],
  "operations": ["create_biome", "create_family_member"],
  "upstream_overlay_operations": [],
  "distribution_support": "limited",
  "runtime_validation": {
    "1.20.1/vanilla": "passed"
  }
}
```

A biome modifier provider might support `add_feature` and `add_spawn` against upstream targets but not `adjust_owned_distribution`. The provider registry should select by declared capability rather than by provider name heuristics.

---

## 33. Example End-to-End Flow: Add a Rare Fungal Feature

User intent:

```text
Add rare luminous fungal clusters to cold old-growth forests without changing existing trees or biome distribution.
```

Execution:

```text
biome_inventory
 -> biome_profile(target forest biomes)
 -> registry resolve fungal feature/block IDs
 -> biome_plan(scope=micro, layers=[features])
 -> biome_patch_build(add_feature)
 -> compatibility gate verifies append-only provider exists
 -> biome_metrics checks feature pressure
 -> provider preview
 -> export
 -> static validation
 -> fresh-world runtime test
```

The plan preserve list includes existing vegetation and distribution. Any provider that requires replacing the entire biome JSON is rejected as incompatible with the request and project policy.

---

## 34. Example End-to-End Flow: Create a Volcanic Biome Family

User intent:

```text
Create a volcanic family with basalt lowlands, ash forest, volcanic highlands, and rare caldera wetlands occupying about 4% of the overworld collectively.
```

Execution:

```text
inventory
 -> new family plan
 -> shared climate envelope
 -> family palette/resource roles
 -> four member deltas
 -> transition graph
 -> family distribution budget = 0.04
 -> redundancy audit
 -> resource drift audit
 -> analytical simulation across fixed seeds
 -> adjust weights within plan
 -> provider resolution
 -> export previews
 -> materialize owned resources
 -> runtime fresh-world test
```

A failure where each member independently targets 4% produces `FAMILY_COVERAGE_EXCEEDED` and blocks export.

---

## 35. Example End-to-End Flow: Structure-Aware Harbor Biome Planning

User intent:

```text
Create a cold industrial coast variant suitable for large harbor structures.
```

Biome Expander profiles coastal candidates and produces terrain/hydrology constraints. The structure capability supplies requirements such as coastline, minimum flat apron, water depth, road connector, and structure exclusion radius. Biome Expander uses those requirements to score candidate transition/distribution contexts but does not author the harbor NBT. The structure generator consumes the resulting normalized site context.

This demonstrates why the two capabilities should interoperate without merging into one subsystem.

---

## 36. Documentation and Human-Readable Explanations

Each tool should document:

```text
what it reads
what it writes
whether it is static or runtime
whether it can modify upstream behavior
what provider is required
what version assumptions apply
what metrics mean
what can block the request
what snapshot is created
```

The human guide should include a specific section titled "What Biome Expander Will Not Do" explaining that it does not silently replace third-party biome definitions or claim runtime validation from static analysis.

---

## 37. Suggested Presets

Presets should reduce AI prompt size while preserving deliberate gates.

```text
biome.inspect_existing
biome.add_small_feature
biome.create_single_owned
biome.create_family
biome.plan_transition
biome.analyze_distribution
biome.audit_performance
biome.audit_compatibility
```

Presets should never set destructive flags because such flags are not part of the compatibility contract.

---

## 38. Semantic Icon Assignment

Follow the existing tool metadata approach. Candidate Minecraft icons:

```text
biome_inventory            minecraft:knowledge_book
biome_profile              minecraft:filled_map
biome_compare              minecraft:spyglass
biome_plan                 minecraft:map
biome_patch_build          minecraft:grass_block
biome_metrics              minecraft:recovery_compass
biome_audit                minecraft:compass
biome_simulate             minecraft:clock
biome_generate             minecraft:oak_sapling
biome_export               minecraft:chest
biome_family_generate      minecraft:azalea
biome_transition_generate  minecraft:moss_block
biome_distribution_plan    minecraft:cartography_table
biome_balance              minecraft:sculk_sensor
biome_provider_probe       minecraft:comparator
```

Exact item choices can be adjusted, but assignment should remain deterministic and version-aware where required.

---

## 39. Acceptance Criteria for Biome Expander v0.1

A realistic v0.1 should not attempt every provider. It is complete when all of the following are true:

- Loader-neutral biome models exist and are tested.
- Biome/worldgen inventory and registry probing work on fixtures.
- Existing biomes can be profiled read-only with provenance.
- Plans and append-only patches can be produced.
- Destructive upstream operations are rejected.
- Static metrics and audits exist with documented confidence.
- Tier A deterministic simulation exists and is clearly labeled analytical.
- At least one provider can materialize a Continuity Works-owned biome resource for a declared target version.
- That provider has passed a fresh-world runtime validation.
- Core biome tools are present in `/v1/tools` and progressive disclosure.
- Published biome routes pass local serviceability and remote endpoint checks.
- Existing structure/content capabilities show no regression.
- Snapshot/resume works across biome planning and export.
- Documentation and examples match actual support.

---

## 40. Acceptance Criteria for Biome Expander v0.2+

Subsequent releases can add:

- coherent family generation,
- richer transition planning,
- additive modification provider for one loader/version,
- TerraBlender distribution provider,
- Tier B provider emulation,
- Tier C runtime sampling automation,
- frontend biome workbench,
- more advanced ecology/resource balancing,
- cross-provider compatibility diagnostics,
- broader Minecraft version support.

Each new provider is independently verified and cannot inherit validation status from another provider.

---

## 41. Implementation Order Summary

```text
0  baseline and invariant capture
1  domain models
2  inventory/registry extension
3  read-only profile
4  planning + patch safety
5  metrics + static audit
6  analytical simulation
7  provider registry + preview
8  first owned-resource exporter
9  first runtime validation
10 tool catalog
11 public routes/serviceability
12 structure context bridge
13 family/transition engine
14 first additive upstream provider
15 higher-confidence simulation/performance
16 frontend workbench
17 documentation/release hardening
```

This order deliberately postpones broad compatibility materialization until the semantic core, safety rules, profile layer, metrics, and provider contracts are proven.

---

## 42. Immediate Implementation Backlog

The first implementation batch should be narrow enough to validate architecture but large enough to establish the real module.

### Batch A

```text
create src/structure_capability/biomes/
add models.py
add reason_codes.py
add capability.py skeleton
compose capability into StructureCapability
add model unit tests
```

No public tools yet.

### Batch B

```text
extend mod/inventory detection for biome + feature resources
extend registry probe kinds
add ownership classifier
add inventory fingerprint
add fixtures/tests
```

### Batch C

```text
implement biome_profile
implement provenance/confidence
snapshot profile
add profile fixtures
```

### Batch D

```text
implement biome_plan
implement BiomePatch builder
implement destructive-operation gates
add safety tests
```

### Batch E

```text
implement static metrics/audit
implement Tier A simulation
add deterministic tests
```

Only after Batches A-E pass should the first provider and public route work begin.

---

## 43. Release Verification Checklist

Before any Biome Expander release is described as usable:

- [ ] Existing Continuity Works tests pass.
- [ ] Biome model contract gate passes.
- [ ] Registry/inventory gate passes.
- [ ] Read-only profile gate passes.
- [ ] Patch safety gate passes.
- [ ] Static audit gate passes.
- [ ] Simulation gate passes for claimed simulation tier.
- [ ] Provider resolution gate passes.
- [ ] Static export gate passes for every claimed provider/version.
- [ ] Fresh-world runtime gate passes for every claimed runtime-supported provider/version.
- [ ] Tool catalog schemas validate.
- [ ] Publication matrix is synchronized.
- [ ] Local `PUBLIC_SERVICEABILITY` passes.
- [ ] Remote health/tools/OpenAPI/discovery routes are verified after deployment.
- [ ] Frontend, if shipped, cannot bypass API gates.
- [ ] Documentation does not overclaim unsupported providers or versions.
- [ ] Generated artifacts contain provenance and snapshot references.
- [ ] No third-party resource replacement path exists in compatibility output.

---

## 44. Final Architectural Position

Biome Expander should become a peer capability within Continuity Works, integrated through the existing `StructureCapability` facade and public service rather than created as a separate application. Its core value is not the number of biome JSON files it can generate. Its value is that it gives human and AI clients a deliberate, inspectable, version-aware, mod-aware, measurable, reversible, and non-destructive way to reason about world ecology.

The stable contract is:

```text
PROFILE before mutation.
PLAN before export.
PATCH only declared layers.
PRESERVE upstream authority.
MEASURE consequences.
SIMULATE distribution.
RESOLVE a real provider.
SNAPSHOT every verified boundary.
RUNTIME-TEST before promotion.
DO NOT ADVANCE through a failed gate.
```

That contract should remain true even as the number of supported loaders, versions, biome mods, metrics, and frontend tools grows.

---

## Appendix A - Proposed `BiomePlan` Response Skeleton

```json
{
  "plan_id": "BX-0047",
  "operation": "create_family",
  "scope_level": "family",
  "target_version": "1.20.1",
  "inventory_fingerprint": "...",
  "ownership": "continuity_works_owned",
  "layers_affected": [
    "climate",
    "terrain",
    "surface",
    "vegetation",
    "features",
    "fauna",
    "distribution",
    "transitions"
  ],
  "preserve_contract": {
    "upstream_authority": true,
    "replacement_allowed": false
  },
  "patches": [],
  "metric_targets": {
    "family_world_share_target": 0.04,
    "minimum_transition_quality": 75,
    "maximum_compatibility_risk": 30
  },
  "provider_candidates": [],
  "status": "READY_FOR_PATCH",
  "findings": [],
  "snapshot": {}
}
```

## Appendix B - Proposed Metric Record

```json
{
  "name": "TransitionQuality",
  "value": 88.0,
  "scale": "0-100",
  "direction": "higher_is_better",
  "method": "normalized_neighbor_compatibility_v1",
  "confidence": 0.81,
  "threshold": 75.0,
  "status": "PASS",
  "evidence_source": [
    "target climate envelope",
    "neighbor climate envelope",
    "transition rules"
  ]
}
```

## Appendix C - Proposed Provider Probe Response

```json
{
  "request": {
    "operation": "add_feature",
    "target": "minecraft:old_growth_pine_taiga",
    "target_version": "1.20.1"
  },
  "candidates": [
    {
      "provider_id": "continuityworks:forge_biome_modifier",
      "status": "SUPPORTED",
      "operations": ["add_feature"],
      "runtime_validation": "required"
    }
  ],
  "rejected": [
    {
      "provider_id": "continuityworks:vanilla_datapack_biome",
      "reason_code": "PROVIDER_OPERATION_UNSUPPORTED",
      "message": "This provider creates owned biome resources but does not append features to an upstream biome."
    }
  ]
}
```

## Appendix D - Definition of Done for Any New Compatibility Adapter

A new adapter is not done until:

1. Its upstream integration point is documented.
2. Its supported versions are explicit.
3. Its operation subset is explicit.
4. It cannot emit replacement/disable/clear behavior against upstream systems.
5. Static fixtures pass.
6. Invalid/destructive requests fail before artifact creation.
7. A fresh-world runtime test demonstrates the additive behavior.
8. Existing native behavior is shown to remain present.
9. The provider support matrix records the exact tested tuple.
10. Documentation uses "runtime validated" only for tuples that actually passed.

## Appendix E - Repository Naming Note

The project is Continuity Works, while the current Python package, public capability metadata, and several existing docs still use the historical StructureSmith/`structure_capability` identifiers. Biome Expander should integrate with those existing implementation identifiers for this task rather than performing an unrelated project-wide rename. A later naming migration can be planned separately without coupling it to biome functionality.
