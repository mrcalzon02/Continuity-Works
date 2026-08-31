from __future__ import annotations

import argparse
import json
from pathlib import Path

from structure_capability.facility_library import FacilityLibrary
from structure_capability.seeded_facility_generator import SeededFacilityGenerator


CASES = [
    ("gas_northstar_104729_small", "continuityworks:archetype/rural_gas_station", 104729, "continuityworks:corporate/northstar_fuel", "small"),
    ("gas_frontier_915071_small", "continuityworks:archetype/rural_gas_station", 915071, "continuityworks:corporate/frontier_cooperative", "small"),
    ("gas_auto_24061992_medium", "continuityworks:archetype/rural_gas_station", 24061992, None, "medium"),
    ("travel_northstar_77123_medium", "continuityworks:archetype/highway_travel_stop", 77123, "continuityworks:corporate/northstar_fuel", "medium"),
    ("travel_frontier_882451_large", "continuityworks:archetype/highway_travel_stop", 882451, "continuityworks:corporate/frontier_cooperative", "large"),
    ("travel_auto_alaska_highway_01", "continuityworks:archetype/highway_travel_stop", "alaska-highway-01", None, "large"),
    ("well_ironmesa_44021_small", "continuityworks:archetype/crude_oil_well_pad", 44021, "continuityworks:corporate/iron_mesa_energy", "small"),
    ("well_atlas_990177_medium", "continuityworks:archetype/crude_oil_well_pad", 990177, "continuityworks:corporate/atlas_basin_refining", "medium"),
    ("well_auto_pumpjack_delta", "continuityworks:archetype/crude_oil_well_pad", "pumpjack-delta-2", None, "medium"),
    ("tank_atlas_65311_medium", "continuityworks:archetype/bulk_tank_farm", 65311, "continuityworks:corporate/atlas_basin_refining", "medium"),
    ("tank_ironmesa_125771_large", "continuityworks:archetype/bulk_tank_farm", 125771, "continuityworks:corporate/iron_mesa_energy", "large"),
    ("tank_auto_grid_east", "continuityworks:archetype/bulk_tank_farm", "tank-grid-east", None, "large"),
    ("refinery_atlas_880301_medium", "continuityworks:archetype/compact_diesel_refinery", 880301, "continuityworks:corporate/atlas_basin_refining", "medium"),
    ("refinery_ironmesa_20260830_large", "continuityworks:archetype/compact_diesel_refinery", 20260830, "continuityworks:corporate/iron_mesa_energy", "large"),
    ("refinery_auto_diesel_process_a", "continuityworks:archetype/compact_diesel_refinery", "diesel-process-a", None, "large"),
    ("terminal_northstar_33791_medium", "continuityworks:archetype/truck_fuel_terminal", 33791, "continuityworks:corporate/northstar_fuel", "medium"),
    ("terminal_atlas_550701_large", "continuityworks:archetype/truck_fuel_terminal", 550701, "continuityworks:corporate/atlas_basin_refining", "large"),
    ("terminal_ironmesa_fleet_west", "continuityworks:archetype/truck_fuel_terminal", "fleet-terminal-west", "continuityworks:corporate/iron_mesa_energy", "large"),
]


def build_corpus(repo_root: Path) -> dict:
    facilities = FacilityLibrary(
        repo_root / "facility_library",
        structure_root=repo_root / "library",
    )
    generator = SeededFacilityGenerator(facilities)
    runs = []
    for run_id, archetype_id, seed, corporate_language_id, scale in CASES:
        full = generator.generate_run_record(
            run_id=run_id,
            archetype_id=archetype_id,
            seed=seed,
            corporate_language_id=corporate_language_id,
            scale=scale,
        )
        report = full["result"]
        runs.append({
            "run_id": run_id,
            "request": full["request"],
            "expected": {
                "status": report["status"],
                "corporate_language_id": report["corporate_language_id"],
                "scale": report["scale"],
                "size": report["size"],
                "block_count": report["block_count"],
                "structure_fingerprint": report["structure_fingerprint"],
                "variant": report["variant"],
            },
        })
    return {
        "contract": "continuityworks:seeded_facility_example_corpus/v1",
        "generation_contract": SeededFacilityGenerator.CONTRACT,
        "run_count": len(runs),
        "policy": {
            "deterministic_replay": True,
            "full_block_arrays_omitted": True,
            "fingerprint_algorithm": "sha256",
            "vanilla_only": True,
        },
        "runs": runs,
    }


def encode(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify deterministic seeded facility example runs."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed run corpus instead of rewriting it.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output = repo_root / "examples" / "seeded_facility_runs" / "runs.json"
    corpus = build_corpus(repo_root)
    encoded = encode(corpus)

    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != encoded:
            print(f"Seeded facility example drift: {output.relative_to(repo_root)}")
            return 1
        print(f"Seeded facility examples PASS ({corpus['run_count']} runs)")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded, encoding="utf-8")
    print(f"Wrote {corpus['run_count']} deterministic seeded facility runs to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
