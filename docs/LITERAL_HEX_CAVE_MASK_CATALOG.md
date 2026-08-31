# Literal Hex Cave Mask Catalog

## Fixed invariant

The hexagonal grid is literal cave geometry. It is never discarded as decorative noise, never replaced by generic Perlin/Worley output, and never reduced to a hidden organizational scaffold.

`LiteralHexCaveFeature` reconstructs true regular-hex cell edges in absolute world coordinates and physically carves those edges as corridors. Cell vertices also act as vertical connector shafts between warped horizontal lattice layers. Fractal, plasma, Worley, mirrored, Boolean, threshold and domain-warp operators only expose, conceal, widen, narrow, interrupt or distort the visibility of that literal lattice.

All 144 primary biomes receive a unique `CavePatternProfile` containing three named mask operators, independent weights, scale, literal hex radius, corridor width, layer spacing, layer thickness, threshold, radial symmetry count and deterministic salt. The primary operator cycles through the complete catalog so every listed method is actually used by the biome set rather than merely documented.

## Named operators

1. `MIRRORED_WORLEY_HEX_FIELD` — literal hex lattice under a mirrored Worley visibility field.
2. `KALEIDOSCOPIC_CELLULAR_GRID` — radial-folded cellular visibility over the continuous lattice.
3. `RECURSIVE_MIRROR_GRID` — large mirrored regions containing finer mirrored cellular subregions.
4. `WORLEY_VORONOI_OCCLUSION_MAP` — cell-center distance determines lattice visibility.
5. `DUAL_WORLEY_LAYER_MAP` — coarse cellular provinces plus fine cellular boundary breakup.
6. `INVERTED_CELLULAR_GRID` — a Worley field interferes with an inverted mirrored copy.
7. `MIRROR_SEAM_FRACTAL_MAP` — mirrored fractal density disrupted by a weaker asymmetric plasma field.
8. `FOUR_WAY_SYMMETRIC_CELLULAR_MAP` — horizontal and vertical cellular reflection.
9. `RADIALLY_MIRRORED_WORLEY_MAP` — Worley geometry repeated in radial kaleidoscope sectors.
10. `CELL_BOUNDARY_GRID_MASK` — lattice emphasized toward Voronoi boundaries.
11. `CELL_CENTER_GRID_MASK` — lattice emphasized around cellular centers.
12. `NESTED_CELLULAR_MAP` — coarse Worley cells select independently salted finer cellular maps.
13. `FRACTAL_WORLEY_HYBRID` — Worley provinces roughened by multi-octave fractal density.
14. `DOMAIN_WARPED_CELLULAR_GRID` — the cellular mask coordinates are warped before lattice masking.
15. `MIRRORED_DOMAIN_WARP_MAP` — warped mirrored field followed by weaker asymmetric breakup.
16. `CELLULAR_RIDGE_MAP` — nearest/second-nearest Worley difference produces branching ridges.
17. `CELLULAR_BASIN_MAP` — broad visibility basins centered on cellular seed points.
18. `INTERFERENCE_MIRROR_MAP` — original and mirrored cellular fields combined by difference/minimum interference.
19. `MULTI_AXIS_REFLECTION_FIELD` — horizontal, vertical and diagonal reflected cellular fields combined.
20. `OCTAVE_CELLULAR_MAP` — multiple Worley scales form hierarchical cellular detail.
21. `THRESHOLDED_CELLULAR_ARCHIPELAGO` — hard cellular/fractal threshold creates disconnected visible lattice islands.
22. `SOFT_CELLULAR_FOG_MAP` — smooth threshold causes the lattice to fade through cellular fog.
23. `CELLULAR_CRACK_NETWORK` — narrow Voronoi borders selectively expose the lattice.
24. `MIRRORED_CRACK_NETWORK` — mirrored cellular borders form symmetrical fracture systems.
25. `PLASMA_WORLEY_COMPOSITE` — plasma density and Worley survival masks are blended.
26. `FRACTAL_MIRROR_PLASMA_MAP` — recursively mirrored fractal/plasma field quantized into visibility bands.
27. `CELLULAR_XOR_MAP` — mirrored cellular masks use XOR-style visibility logic.
28. `CELLULAR_BOOLEAN_MAP` — cellular centers, boundaries and fractal regions use AND/OR/subtractive composition.
29. `CONCENTRIC_CELLULAR_MIRROR` — cellular masking repeats through mirrored radial rings.
30. `SYMMETRY_BROKEN_MIRROR_MAP` — strong mirrored cellular structure receives low-amplitude asymmetric plasma breakup.

## Relationship to the volumetric cave engine

The existing `BiomeCaveNetworkFeature` remains additive. It generates the organic chamber/tunnel/shaft volume. `LiteralHexCaveFeature` adds the intentionally recognizable hex-lattice corridors and connector nodes. A biome therefore receives both natural/noise-driven cave volume and explicit geometric network structure, with its own deterministic mask composition.

Both systems are restricted to recognized base geology and run before later structure placement. Formal Forge compile, game-load and fresh-world visual acceptance remain separate acceptance work and must not be inferred from source commit alone.
