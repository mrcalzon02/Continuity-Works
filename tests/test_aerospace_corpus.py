import hashlib
import json
import unittest
from pathlib import Path

from structure_capability.facility_library import FacilityLibrary


class AerospaceCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.library = FacilityLibrary(cls.repo / "facility_library", cls.repo / "library")
        cls.corpus = json.loads((cls.repo / "facility_library" / "aerospace_orbital" / "corpus.json").read_text(encoding="utf-8"))
        cls.design = json.loads((cls.repo / "facility_library" / "aerospace_orbital" / "design_language.json").read_text(encoding="utf-8"))

    def test_two_distinct_complete_facilities_per_scale(self):
        minimum = self.corpus["minimum_distinct_facilities_per_scale"]
        self.assertEqual(minimum, 2)
        self.assertEqual(self.corpus["minimum_complete_references_per_scale"], 2)
        expected_tiers = {"micro", "light", "standard", "heavy", "superheavy", "megastructure"}
        self.assertEqual(set(self.corpus["tiers"]), expected_tiers)
        for scale, tier in self.corpus["tiers"].items():
            with self.subTest(scale=scale):
                self.assertGreaterEqual(len(set(tier["archetypes"])), minimum)
                self.assertGreaterEqual(len(set(tier["references"])), 2)
                for archetype_id in tier["archetypes"]:
                    archetype = self.library.load(archetype_id)
                    self.assertIn(scale, archetype["scale_tiers"])
                referenced_archetypes = {self.library.load(ref)["archetype_id"] for ref in tier["references"]}
                self.assertEqual(referenced_archetypes, set(tier["archetypes"]))

    def test_every_aerospace_reference_is_an_actual_materializable_structure(self):
        fingerprints = set()
        for tier in self.corpus["tiers"].values():
            for reference_id in tier["references"]:
                reference = self.library.load(reference_id)
                self.assertTrue(reference["aerospace_reference"]["actual_structure_commitment"])
                recognition = self.library.evaluate_reference(reference_id)
                self.assertEqual(recognition["status"], "PASS", recognition)
                compiled = self.library.compile_reference(reference_id)
                self.assertGreater(len(compiled["blocks"]), 500)
                payload = json.dumps(compiled["blocks"], separators=(",", ":"), sort_keys=True).encode("utf-8")
                fingerprint = hashlib.sha256(payload).hexdigest()
                self.assertNotIn(fingerprint, fingerprints)
                fingerprints.add(fingerprint)

    def test_scale_is_compositional_not_uniform_scaling(self):
        for archetype_id in [entry["id"] for entry in self.library.entries(kind="archetype", category="aerospace_orbital")]:
            archetype = self.library.load(archetype_id)
            response = archetype["scale_response"]
            self.assertTrue(response["composition_changes_with_scale"])
            self.assertTrue(response["simple_uniform_scaling_forbidden"])
            self.assertIn(archetype["aerospace_design_mode"], self.design["modes"])

    def test_system_design_modes_cover_corpus(self):
        required = set(self.corpus["required_design_modes"])
        self.assertTrue(required.issubset(set(self.design["modes"])))
        used = {self.library.load(entry["id"])["aerospace_design_mode"] for entry in self.library.entries(kind="archetype", category="aerospace_orbital")}
        self.assertTrue(required.issubset(used))

    def test_megastructure_references_include_placement_datum(self):
        for reference_id in self.corpus["tiers"]["megastructure"]["references"]:
            reference = self.library.load(reference_id)
            self.assertIn("placement_guidance", reference)
            self.assertGreater(reference["placement_guidance"]["placement_datum_y"], 0)


if __name__ == "__main__":
    unittest.main()
