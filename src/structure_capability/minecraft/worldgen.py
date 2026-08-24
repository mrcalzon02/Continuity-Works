from __future__ import annotations

def jigsaw_structure(*, biome_selector, start_pool, step="surface_structures",
                     terrain_adaptation="bury", heightmap=None, absolute_y=0,
                     max_distance=80):
    out = {
        "type": "minecraft:jigsaw",
        "biomes": biome_selector,
        "step": step,
        "spawn_overrides": {},
        "terrain_adaptation": terrain_adaptation,
        "start_pool": start_pool,
        "size": 1,
        "start_height": {"absolute": absolute_y},
        "max_distance_from_center": max_distance,
        "use_expansion_hack": False,
    }
    if heightmap:
        out["project_start_to_heightmap"] = heightmap
    return out

def random_spread_structure_set(structure_id, spacing, separation, salt):
    if separation >= spacing:
        raise ValueError("separation must be lower than spacing")
    return {
        "structures": [{"structure": structure_id, "weight": 1}],
        "placement": {
            "type": "minecraft:random_spread",
            "spacing": spacing,
            "separation": separation,
            "salt": salt,
        },
    }

def validate_geospatial_worldgen(structure, structure_set):
    findings = []
    biomes = structure.get("biomes")
    if not biomes:
        findings.append(("error", "NO_BIOME_SELECTOR"))
    placement = structure_set.get("placement", {})
    if placement.get("type") == "minecraft:random_spread":
        if placement.get("separation", 0) >= placement.get("spacing", 0):
            findings.append(("error", "INVALID_RANDOM_SPREAD"))
    return findings
