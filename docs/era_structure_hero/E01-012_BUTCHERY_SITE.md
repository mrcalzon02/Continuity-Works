# E01-012 — Butchery Site

Status: HERO_SPEC_COMPLETE
Era: Lower Paleolithic / Early Human
Primary family: `continuityworks:early_human_carcass_processing`
Default unrelated-structure exclusion: 500 blocks minimum
Compatibility policy: additive/non-destructive; same-parent reservation only for compatible family composition

## Purpose

Represent a temporary or repeatedly used carcass-processing locus where a small-to-medium animal is dismembered, defleshed, sorted, and partially transported. The site is not a settlement, hunting blind, slaughterhouse, storage facility, ritual precinct, or generic refuse scatter. Its identity is created by the spatial relationship between a carcass-processing center, cut/impact work positions, bone and offcut discard, selected transport portions, tool-use traces, and a clear outward carry route.

## Historical and technological context

Technology is limited to Lower Paleolithic behaviors: stone flakes/choppers, hammerstones, expedient anvils, wooden implements where plausible, direct percussion, marrow access, tendon/hide removal, and opportunistic fire use only when independently justified. No metal, masonry, permanent tables, racks, formal drainage, fencing, pens, carts, engineered smokehouses, storage buildings, or later industrial butchery systems are permitted.

The archetype should read archaeologically as a task-specific activity area whose organization emerges from carcass anatomy, worker positions, discard direction, and transport decisions rather than from architecture.

## Footprint and scale classes

- **Small:** 17×5×15 nominal envelope. One primary carcass locus, 1–2 work positions, light bone/offcut scatter, one selected transport cache, short carry route.
- **Medium:** 27×6×23 nominal envelope. One primary carcass locus with differentiated limb/axial processing zones, 2–4 work positions, marrow-break cluster, hide/offcut edge, selected transport portions, longer carry route.
- **Large:** 39×7×33 nominal envelope. Large but still single-carcass or tightly grouped processing event, 4–7 work positions, multiple anatomical discard fans, stronger marrow-processing evidence, larger selected-portion staging, possible secondary fire association, and broader trampling/circulation.

E01-012 must remain below the scale/biomass signature of E01-013 Large-Carcass Processing Site.

## Architectural program

This is an open-air task landscape, not a building. Required spatial program:

1. Primary carcass-processing center.
2. Anatomically biased work positions around that center.
3. Limb/axial bone discard zones with directional scatter rather than uniform debris.
4. Cut/impact tool-use trace zones adjacent to processing positions.
5. Marrow-breaking/anvil zone, stronger in medium and large variants.
6. Hide/offcut handling edge placed down-slope or peripheral where practical.
7. Selected transport portion staging on the cleaner side of the site.
8. Outward carry route from staging toward the structure boundary.
9. Clear circulation cells between the dirty processing core and selected transport staging.
10. Optional small hearth association only for conditions/cultures where immediate consumption or brief heat treatment is plausible; hearth must never dominate site identity.

## Procedural generation logic

Use deterministic named random streams derived from world seed plus catalog ID. Generation order:

1. Resolve scale, terrain plane, biome palette, and carcass orientation.
2. Place a non-rectilinear central carcass footprint represented through semantic block proxies.
3. Generate 1–7 work positions around anatomical sectors according to scale.
4. Project directional bone/offcut fans away from work positions; avoid isotropic random scatter.
5. Place impact/anvil and marrow-break proxies near high-value bone sectors.
6. Keep selected transport staging on the cleaner opposite side of the processing core.
7. Generate a sparse carry route from staging to the site edge.
8. Reserve circulation cells; debris should not completely choke access between work positions and staging.
9. Add condition-specific chronology/weathering transforms after the primary task topology exists.
10. Emit deterministic fingerprint and qualification metadata.

The generator must fail qualification if carcass-processing relationships cannot be read from the resulting topology.

## Biome and environmental adaptation

- **Temperate:** coarse dirt/grass-edge footing; moderate weathering and moss only in abandoned states.
- **Boreal:** podzol/coarse-dirt character, darker stone tool proxies, limited organic persistence.
- **Tundra:** gravel/stone footing, minimal vegetation reclaim, stronger exposed-bone persistence proxy.
- **Savanna:** dry coarse dirt, broad trampling, sparse vegetation reclaim.
- **Arid:** sand/sandstone footing, no moss; wind-reworked discard in degraded states.
- **Tropical:** dirt/mud-like footing proxy, rapid organic disappearance, stronger reclaim in abandoned states.
- **Coastal:** gravel/sand footing, possible shell/gravel contamination but never enough to redefine the site.

Avoid biome transformations that overwrite terrain broadly. All placement is bounded and additive/non-destructive.

## Culture-variant hooks

Culture hooks may alter carcass orientation, worker spacing, preferred transport side, hearth probability, degree of marrow processing, discard-direction bias, and selected portion ratios. They must not introduce technology outside the era ceiling or convert the site into a permanent facility.

Supported behavioral profiles may include `expedient_field_dressing`, `transport_focused`, `marrow_intensive`, and `consumption_biased`.

## Material palette logic

Use vanilla blocks only as explicit semantic proxies:

- carcass/bone mass: bone block / calcite-role proxies;
- blood/organic stain: red terracotta or rooted/coarse dirt role proxies, never literal liquid blood;
- stone tools/hammerstones: flint is not a placeable block, so gravel/andesite/cobblestone role proxies are acceptable when metadata records their semantics;
- hide/offcut handling: brown/red carpet or wool only as semantic hide/offcut proxies and only in sparse trace quantities;
- ground/trampling: biome-appropriate coarse dirt, dirt, gravel, sand, podzol, or stone.

Metadata must state proxy semantics so vanilla materials are not misrepresented as literal archaeological substances.

## Condition variants

- **active:** strongest fresh processing topology; optional active hearth.
- **recent:** intact spatial organization with reduced active-fire evidence.
- **repeated:** overlapping discard lenses and stronger marrow-break accumulation while preserving one recognizable primary processing center.
- **abandoned:** organic proxies reduced, bone/tool traces remain.
- **weathered:** partial erosion and vegetation/sediment intrusion by biome.
- **scavenger_reworked:** bone/offcut traces dragged outward from the primary center while preserving enough topology to remain identifiable.
- **sediment_reworked:** part of the trace field covered/replaced by biome-appropriate sediment.
- **repurposed:** later compatible occupation traces may overlap only under the same parent reservation; original processing topology remains legible.

## Jigsaw and family relationships

Structure ID: `continuityworks:e01_012_butchery_site`
Start pool: `continuityworks:early_human/e01_012_butchery_site`
Family: `continuityworks:early_human_carcass_processing`

Compatible same-parent relationships may include hearth sites, knapping grounds, temporary shelters, hunting-event components, or transport staging when explicitly generated as one parent assemblage. Family compatibility never waives the 500-block rule for unrelated independently placed structures.

E01-013 Large-Carcass Processing Site is related but not interchangeable: E01-012 must remain smaller, simpler, and centered on ordinary carcass processing rather than megafaunal-scale spatial organization.

## Infrastructure dependencies

No infrastructure is required. Suitable generation requires only an open or lightly sheltered terrain patch with enough local relief tolerance for a carcass-processing floor and outward carry route. Existing roads, villages, Lost Cities content, mod structures, and terrain features are never replaced to make room for this site.

## Loot and occupancy hooks

Loot must remain sparse and task-specific. Acceptable hooks include low-probability stone-tool role items, bone fragments, raw-food proxies where gameplay integration allows, sinew/hide-role items supplied by compatible mods, or archaeology/evidence tokens. Do not create treasure-chest logic.

Occupancy hooks, if enabled by a consuming pack, should represent transient human activity, scavengers, or later abandonment. Continuity Works core generation should expose metadata/hooks rather than force hostile mobs or persistent NPC populations.

## Validation criteria

A generated E01-012 must satisfy all of the following:

- one dominant primary carcass-processing center;
- at least one work position and directional discard field;
- selected transport staging distinct from the dirty core;
- an outward carry route;
- debris does not fully block circulation;
- marrow/anvil evidence appears at medium/large scale;
- processing remains primary over hearth, shelter, or lithic manufacture;
- scale remains below E01-013 large-carcass requirements;
- no permanent architecture or later butchery infrastructure;
- block coordinates remain within declared bounds;
- deterministic replay produces identical fingerprint for identical inputs;
- different seeds produce meaningful topology variation;
- worldgen placement validates with minimum 500-block unrelated-structure and per-jigsaw-piece protection;
- same-parent family exception is explicit rather than implicit;
- replacement policy remains bounded/additive/non-destructive.

## Production-readiness requirements

Source completion alone is insufficient. Production admission requires observed unit-test execution, deterministic replay checks, representative visual review for all scales and major conditions, Minecraft-compatible template/NBT materialization where used by the runtime path, template-pool/load verification, world-generation placement acceptance in fresh worlds, exclusion-rule verification, terrain-integration review, additive compatibility testing against representative external structures, and confirmation that E01-012 remains visually and behaviorally distinct from E01-013.
