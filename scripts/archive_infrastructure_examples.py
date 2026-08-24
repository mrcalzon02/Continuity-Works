from __future__ import annotations

import json
from pathlib import Path

from structure_capability.generators import InfrastructureGenerator

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "examples" / "infrastructure" / "archives"
WORLD_SEED = 20260824

EXAMPLES = [
    (
        "civic_urban.json",
        {
            "module_type": "civic_facility",
            "facility_kind": "civic_services_center",
            "variant": "urban",
            "seed": 1101,
            "world_seed": WORLD_SEED,
            "orientation": "north_south",
            "jigsaw": {"enabled": True, "pool": "structuresmith:infrastructure", "connector_width": 3, "max_depth": 8},
            "lost_cities": {"enabled": True, "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"], "tile_span_chunks": 2},
            "random_spawn": {"radius_blocks": 4096, "spacing_blocks": 256, "salt": 734287},
            "purpose": {"depth": 4},
        },
    ),
    (
        "civic_rural.json",
        {
            "module_type": "civic_facility",
            "facility_kind": "civic_services_center",
            "variant": "rural",
            "seed": 1102,
            "world_seed": WORLD_SEED,
            "orientation": "east_west",
            "jigsaw": {"enabled": True, "pool": "structuresmith:infrastructure", "connector_width": 3, "max_depth": 6},
            "lost_cities": {"enabled": True, "spawn_modes": ["randomized_coordinate", "sequential_jigsaw"], "tile_span_chunks": 2},
            "random_spawn": {"radius_blocks": 6144, "spacing_blocks": 384, "salt": 734288},
            "purpose": {"depth": 4},
        },
    ),
    (
        "industrial_urban.json",
        {
            "module_type": "industrial_facility",
            "facility_kind": "industrial_service_works",
            "variant": "urban",
            "seed": 2201,
            "world_seed": WORLD_SEED,
            "orientation": "north_south",
            "jigsaw": {"enabled": True, "pool": "structuresmith:infrastructure", "connector_width": 4, "max_depth": 8},
            "lost_cities": {"enabled": True, "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"], "tile_span_chunks": 3},
            "random_spawn": {"radius_blocks": 4096, "spacing_blocks": 256, "salt": 834287},
            "purpose": {"depth": 4},
        },
    ),
    (
        "industrial_rural.json",
        {
            "module_type": "industrial_facility",
            "facility_kind": "industrial_service_works",
            "variant": "rural",
            "seed": 2202,
            "world_seed": WORLD_SEED,
            "orientation": "east_west",
            "jigsaw": {"enabled": True, "pool": "structuresmith:infrastructure", "connector_width": 4, "max_depth": 6},
            "lost_cities": {"enabled": True, "spawn_modes": ["randomized_coordinate", "sequential_jigsaw"], "tile_span_chunks": 4},
            "random_spawn": {"radius_blocks": 8192, "spacing_blocks": 512, "salt": 834288},
            "purpose": {"depth": 4},
        },
    ),
]


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    generator = InfrastructureGenerator()
    manifest = {
        "schema": "structuresmith.infrastructure.example-archive.v1",
        "world_seed": WORLD_SEED,
        "runtime_scope": "deterministic static contract validation; fresh-world Lost Cities placement remains a runtime gate",
        "examples": [],
    }
    for filename, request in EXAMPLES:
        first = generator.generate(request)
        second = generator.generate(request)
        replay_verified = first["determinism"]["fingerprint"] == second["determinism"]["fingerprint"]
        if not replay_verified:
            raise RuntimeError(f"determinism failure for {filename}")
        if first["fitness"]["status"] != "PASS":
            raise RuntimeError(f"fitness failure for {filename}: {first['fitness']}")
        archive = {
            "request": request,
            "result": first,
            "archive_validation": {
                "deterministic_replay": replay_verified,
                "static_fitness": first["fitness"]["status"],
                "world_seed_authorized": first["spawn"]["world_seed_authorized"],
                "lost_cities_contract": first["lost_cities"]["adapter_status"],
                "fresh_world_runtime": first["runtime_validation"]["fresh_world_placement"],
            },
        }
        (ARCHIVE / filename).write_text(json.dumps(archive, indent=2, sort_keys=True) + "\n")
        manifest["examples"].append({
            "file": filename,
            "module_type": request["module_type"],
            "variant": request["variant"],
            "seed": request["seed"],
            "fingerprint": first["determinism"]["fingerprint"],
            "spawn_anchor": first["spawn"]["candidate_anchor"],
            "fitness": first["fitness"]["status"],
            "deterministic_replay": replay_verified,
        })
    (ARCHIVE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
