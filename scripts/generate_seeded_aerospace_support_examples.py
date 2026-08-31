from __future__ import annotations

import argparse
import json
from pathlib import Path

from structure_capability.aerospace_support_network import AerospaceSupportNetworkValidator
from structure_capability.facility_library import FacilityLibrary
from structure_capability.seeded_aerospace_support_campus import (
    SeededAerospaceSupportCampusGenerator,
)


def encode(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"


def build_corpus(repo_root: Path) -> dict:
    request_path = (
        repo_root
        / "examples"
        / "seeded_aerospace_support_campuses"
        / "requests.json"
    )
    requests = json.loads(request_path.read_text(encoding="utf-8"))
    facilities = FacilityLibrary(
        repo_root / "facility_library",
        structure_root=repo_root / "library",
    )
    network = AerospaceSupportNetworkValidator(
        repo_root,
        structure_library=facilities.structures,
    )
    generator = SeededAerospaceSupportCampusGenerator(facilities, network)

    runs = []
    for request in requests["requests"]:
        result = generator.generate(
            request["scale"],
            request["seed"],
            request.get("corporate_language_id"),
        )
        report = result["report"]
        graph = result["graph"]
        facility_nodes = [
            node for node in graph["nodes"] if node.get("kind") == "facility"
        ]
        runs.append({
            "run_id": request["run_id"],
            "request": {
                "scale": request["scale"],
                "seed": str(request["seed"]),
                "corporate_language_id": request.get("corporate_language_id"),
            },
            "expected": {
                "status": report["status"],
                "corporate_language_id": report["corporate_language_id"],
                "scale": report["scale"],
                "site_context": report["site_context"],
                "node_count": report["node_count"],
                "edge_count": report["edge_count"],
                "launch_anchor_count": report["launch_anchor_count"],
                "facility_archetypes": report["facility_archetypes"],
                "facility_states": [
                    {
                        "id": node["id"],
                        "archetype_id": node["archetype_id"],
                        "vessel_class": node["vessel_class"],
                        "vessel_state": node["vessel_state"],
                    }
                    for node in facility_nodes
                ],
                "campus_fingerprint": report["campus_fingerprint"],
            },
        })

    return {
        "contract": "continuityworks:seeded_aerospace_support_campus_example_corpus/v1",
        "generation_contract": SeededAerospaceSupportCampusGenerator.CONTRACT,
        "run_count": len(runs),
        "policy": {
            "deterministic_replay": True,
            "full_site_graphs_omitted": True,
            "fingerprint_algorithm": "sha256",
            "network_validation_required": True,
        },
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify deterministic aerospace support campus examples."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed compact run corpus instead of rewriting it.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output = (
        repo_root
        / "examples"
        / "seeded_aerospace_support_campuses"
        / "runs.json"
    )
    corpus = build_corpus(repo_root)
    encoded = encode(corpus)

    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != encoded:
            print(
                "Seeded aerospace support campus example drift: "
                f"{output.relative_to(repo_root)}"
            )
            return 1
        print(f"Seeded aerospace support campus examples PASS ({corpus['run_count']} runs)")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded, encoding="utf-8")
    print(
        f"Wrote {corpus['run_count']} deterministic aerospace support campus runs "
        f"to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
