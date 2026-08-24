# Geospatial and Locational Structural Awareness

Every production structure carries a placement contract.

## Required context dimensions

Where applicable record:
- dimension;
- biome IDs/tags;
- climatic family;
- land/water/fluid condition;
- sea level;
- target Y band;
- terrain class;
- local slope/cliff state;
- surface/subsurface placement;
- orientation;
- player/vehicle/submersible approach;
- road/rail/water/utility connectors;
- adjacent lots/features;
- protected/exclusion regions;
- terrain adaptation;
- projection/heightmap;
- spacing/separation/salt or equivalent distribution rule.

## Context fitness

Examples:
- ports face water and have cargo/service access;
- rail freight facilities connect to rail;
- markets have public approaches and service routes;
- industrial facilities have believable utility/load access;
- cliff structures anchor to rock rather than float;
- underwater structures have water-compatible entrances and approach clearance;
- faction-specific pools only bind to their geographic selectors;
- neutral geology may cross faction regions without mixing built cultures.

## Geospatial preservation

When rebuilding geometry, existing worldgen ownership is frozen unless the task explicitly changes it. A better building that no longer fits its biome, connector, lot, coastline or terrain is a regression.

## Terrain-sensitive generation

Prefer terrain/surface features for geology and NBT/structure templates for discrete built objects. Avoid using giant templates when a density/surface/placed-feature system better represents a continuous process.
