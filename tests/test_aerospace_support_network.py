import copy
import json
import unittest
from pathlib import Path

from structure_capability.aerospace_support_network import AerospaceSupportNetworkValidator


class AerospaceSupportNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.validator = AerospaceSupportNetworkValidator(cls.repo)
        cls.example = json.loads(
            (cls.repo / "facility_library" / "aerospace_orbital" / "examples" / "light_assembly_to_pad.site_graph.json").read_text(encoding="utf-8")
        )

    def test_phase_zero_program_is_complete(self):
        report = self.validator.validate_program()
        self.assertEqual(report["status"], "PASS", report["findings"])
        self.assertEqual(report["connector_contract_version"], 4)
        self.assertEqual(report["connector_profiles"], 41)
        self.assertEqual(report["network_modules"], 16)

    def test_reference_graph_reaches_launch_pad(self):
        report = self.validator.validate_graph(self.example)
        self.assertEqual(report["status"], "PASS", report["findings"])
        self.assertEqual(report["launch_anchor_count"], 1)

    def test_incompatible_profiles_fail(self):
        graph = copy.deepcopy(self.example)
        graph["nodes"][4]["sockets"][0]["profile"] = "local_road_6w"
        report = self.validator.validate_graph(graph)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("INCOMPATIBLE_SOCKET_PROFILES", {item["code"] for item in report["findings"]})

    def test_missing_utility_fails(self):
        graph = copy.deepcopy(self.example)
        graph["edges"] = [edge for edge in graph["edges"] if edge["a"]["socket"] != "utility"]
        graph["nodes"][0]["sockets"][3]["required"] = False
        report = self.validator.validate_graph(graph)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("UTILITY_ATTACHMENT_MISSING", {item["code"] for item in report["findings"]})

    def test_unreachable_launch_anchor_fails(self):
        graph = copy.deepcopy(self.example)
        graph["edges"] = graph["edges"][:3]
        for node in graph["nodes"]:
            for socket in node.get("sockets", []):
                if node["id"] not in {"assembly", "supplier", "staging", "utility_grid"}:
                    socket["required"] = False
        graph["nodes"][0]["sockets"][0]["required"] = False
        report = self.validator.validate_graph(graph)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("LAUNCH_ANCHOR_UNREACHABLE", {item["code"] for item in report["findings"]})

    def test_heavy_facility_rejects_local_road_only(self):
        graph = {
            "contract": self.validator.CONTRACT,
            "nodes": [
                {"id": "heavy", "kind": "facility", "scale": "heavy", "sockets": [{"id": "road", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True}]},
                {"id": "road", "kind": "external_anchor", "sockets": [{"id": "road", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True}]},
                {"id": "pad", "kind": "launch_anchor", "isolated": True, "sockets": []},
            ],
            "edges": [{"a": {"node": "heavy", "socket": "road"}, "b": {"node": "road", "socket": "road"}}],
        }
        report = self.validator.validate_graph(graph)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("HEAVY_ROUTE_UNDERSIZED", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
