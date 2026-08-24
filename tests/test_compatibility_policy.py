import tempfile
import unittest

from structure_capability import StructureCapability
from structure_capability.compatibility import compatibility_policy, validate_compatibility_request
from structure_capability.generators import InfrastructureGenerator


class CompatibilityPolicyTests(unittest.TestCase):
    def test_global_policy_is_append_only_and_non_destructive(self):
        policy = compatibility_policy()
        self.assertEqual(policy["mode"], "append_only")
        self.assertTrue(policy["non_destructive"])
        self.assertEqual(policy["base_authority"], "preserved")
        self.assertIn("extend_tables", policy["allowed_operations"])
        self.assertIn("replace_existing", policy["forbidden_operations"])

    def test_additive_strategies_are_accepted(self):
        validate_compatibility_request(
            {"mode": "append_only", "table_strategy": "append"},
            {"integration_mode": "additive", "selector_strategy": "extend"},
        )

    def test_destructive_modes_and_flags_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "append_only"):
            validate_compatibility_request({"mode": "replace"})
        with self.assertRaisesRegex(ValueError, "forbidden"):
            validate_compatibility_request({"replace_existing": True})
        with self.assertRaisesRegex(ValueError, "replacement strategies"):
            validate_compatibility_request({"table_strategy": "replace"})

    def test_public_infrastructure_generator_enforces_policy(self):
        generator = InfrastructureGenerator()
        accepted = generator.generate({
            "module_type": "inner_city_road",
            "lost_cities": {
                "enabled": True,
                "integration_mode": "append_only",
                "table_strategy": "append",
            },
        })
        self.assertEqual(accepted["fitness"]["status"], "PASS")

        with self.assertRaisesRegex(ValueError, "forbidden"):
            generator.generate({
                "module_type": "inner_city_road",
                "lost_cities": {"enabled": True, "replace_existing": True},
            })

        with self.assertRaisesRegex(ValueError, "append_only"):
            generator.generate({
                "module_type": "highway",
                "compatibility": {"mode": "override"},
            })

    def test_capability_advertises_non_destructive_policy_and_lost_cities_reference(self):
        with tempfile.TemporaryDirectory() as td:
            capabilities = StructureCapability(td).capabilities()
        self.assertEqual(capabilities["compatibility_policy"]["mode"], "append_only")
        reference = capabilities["infrastructure_layout"]["lost_cities_reference"]
        self.assertEqual(reference["repository"], "McJtyMods/LostCities")
        self.assertEqual(reference["branch"], "1.20")
        self.assertFalse(reference["replacement_allowed"])
        self.assertIn("railways", reference["native_systems_preserved"])


if __name__ == "__main__":
    unittest.main()
