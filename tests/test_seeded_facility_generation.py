import json
import unittest
from pathlib import Path

from structure_capability.facility_library import FacilityLibrary
from structure_capability.seeded_facility_generator import (
    SeededFacilityGenerationError,
    SeededFacilityGenerator,
)


class SeededFacilityGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        facilities = FacilityLibrary(
            cls.repo_root / "facility_library",
            structure_root=cls.repo_root / "library",
        )
        cls.generator = SeededFacilityGenerator(facilities)

    def test_same_seed_replays_identically(self):
        kwargs = {
            "archetype_id": "continuityworks:archetype/rural_gas_station",
            "seed": 777,
            "corporate_language_id": "continuityworks:corporate/northstar_fuel",
            "scale": "medium",
        }
        first = self.generator.generate(**kwargs)
        second = self.generator.generate(**kwargs)
        self.assertEqual(
            first["report"]["structure_fingerprint"],
            second["report"]["structure_fingerprint"],
        )
        self.assertEqual(first["structure"], second["structure"])

    def test_different_seeds_change_same_requested_facility(self):
        common = {
            "archetype_id": "continuityworks:archetype/rural_gas_station",
            "corporate_language_id": "continuityworks:corporate/northstar_fuel",
            "scale": "medium",
        }
        first = self.generator.generate(seed=777, **common)
        second = self.generator.generate(seed=778, **common)
        self.assertNotEqual(
            first["report"]["structure_fingerprint"],
            second["report"]["structure_fingerprint"],
        )

    def test_every_fuel_petroleum_archetype_generates_and_recognizes(self):
        archetypes = [
            "continuityworks:archetype/rural_gas_station",
            "continuityworks:archetype/highway_travel_stop",
            "continuityworks:archetype/crude_oil_well_pad",
            "continuityworks:archetype/bulk_tank_farm",
            "continuityworks:archetype/compact_diesel_refinery",
            "continuityworks:archetype/truck_fuel_terminal",
        ]
        for index, archetype_id in enumerate(archetypes):
            with self.subTest(archetype_id=archetype_id):
                result = self.generator.generate(archetype_id, seed=1000 + index)
                self.assertEqual(result["report"]["status"], "PASS")
                self.assertEqual(result["report"]["missing_signatures"], [])
                self.assertGreater(result["report"]["block_count"], 0)

    def test_auto_corporate_selection_is_allowed(self):
        archetype_id = "continuityworks:archetype/truck_fuel_terminal"
        archetype = self.generator.facilities.load(archetype_id)
        result = self.generator.generate(archetype_id, seed="auto-corporate")
        self.assertIn(
            result["report"]["corporate_language_id"],
            archetype["allowed_corporate_languages"],
        )

    def test_large_refinery_is_vanilla_and_in_bounds(self):
        result = self.generator.generate(
            "continuityworks:archetype/compact_diesel_refinery",
            seed=20260830,
            corporate_language_id="continuityworks:corporate/iron_mesa_energy",
            scale="large",
        )
        size = result["structure"]["size"]
        for block in result["structure"]["blocks"]:
            self.assertTrue(block["block"].startswith("minecraft:"))
            self.assertTrue(
                all(0 <= block["pos"][axis] < size[axis] for axis in range(3))
            )

    def test_invalid_scale_is_rejected(self):
        with self.assertRaises(SeededFacilityGenerationError):
            self.generator.generate(
                "continuityworks:archetype/rural_gas_station",
                seed=1,
                scale="large",
            )

    def test_committed_example_runs_replay_exactly(self):
        corpus_path = self.repo_root / "examples" / "seeded_facility_runs" / "runs.json"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        self.assertEqual(corpus["run_count"], 18)
        fingerprints = set()

        for expected in corpus["runs"]:
            with self.subTest(run_id=expected["run_id"]):
                request = expected["request"]
                actual = self.generator.generate_run_record(
                    run_id=expected["run_id"],
                    archetype_id=request["archetype_id"],
                    seed=request["seed"],
                    corporate_language_id=request["corporate_language_id"],
                    scale=request["scale"],
                )["result"]
                replay = {
                    "status": actual["status"],
                    "corporate_language_id": actual["corporate_language_id"],
                    "scale": actual["scale"],
                    "size": actual["size"],
                    "block_count": actual["block_count"],
                    "structure_fingerprint": actual["structure_fingerprint"],
                    "variant": actual["variant"],
                }
                self.assertEqual(replay, expected["expected"])
                fingerprints.add(replay["structure_fingerprint"])

        self.assertEqual(len(fingerprints), 18)


if __name__ == "__main__":
    unittest.main()
