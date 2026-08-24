import tempfile
import unittest

from structure_capability import StructureCapability
from structure_capability.request_resolution import CapabilityResolver


class RequestResolutionTests(unittest.TestCase):
    def test_compact_index_does_not_embed_full_schemas(self):
        resolver = CapabilityResolver()
        index = resolver.index()
        self.assertGreater(index["count"], 5)
        self.assertTrue(any(x["name"] == "structure_generate" for x in index["tools"]))
        self.assertFalse(any("parameters" in x for x in index["tools"]))

    def test_exact_contract_only_returns_selected_tool(self):
        resolver = CapabilityResolver()
        contract = resolver.contract("minecraft_book_generate")
        self.assertEqual(contract["name"], "minecraft_book_generate")
        self.assertIn("title", contract["parameters"]["required"])
        self.assertIn("content.written_book", contract["preset_ids"])

    def test_modular_structure_preset_requires_only_unique_identity(self):
        resolver = CapabilityResolver()
        result = resolver.resolve(
            "structure_generate",
            {"structure_id": "example:lab", "generation": {"layout": {"seed": 42}}},
            preset_id="structure.modular_dungeon_nbt",
        )
        self.assertTrue(result["ready"])
        self.assertEqual(result["request"]["generation"]["kind"], "dungeon")
        self.assertEqual(result["request"]["generation"]["layout"]["seed"], 42)
        self.assertEqual(result["request"]["generation"]["layout"]["modularity"]["macro_module"], 12)

    def test_book_preset_reports_only_missing_book_variables(self):
        resolver = CapabilityResolver()
        result = resolver.resolve(
            "minecraft_book_generate",
            {"title": "Field Notes"},
            preset_id="content.written_book",
        )
        self.assertFalse(result["ready"])
        self.assertEqual(set(result["missing"]), {"author", "pages"})
        self.assertIn("author", result["required_inputs"])
        self.assertIn("pages", result["required_inputs"])
        self.assertEqual(result["request"]["target_version"], "1.20.1")

    def test_loot_preset_requires_weighted_or_guaranteed_content(self):
        resolver = CapabilityResolver()
        result = resolver.resolve(
            "minecraft_loot_table_generate",
            {"table_id": "example:test"},
            preset_id="content.chest_loot",
        )
        self.assertFalse(result["ready"])
        self.assertIn("items|guaranteed", result["missing"])
        self.assertEqual(result["requires_any"][0]["one_of"], ["items", "guaranteed"])

    def test_structure_capability_exposes_progressive_disclosure(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            self.assertEqual(cap.tool_index()["mode"], "compact_index")
            resolved = cap.resolve_tool_request({
                "tool": "dungeon_layout",
                "preset_id": "layout.modular_dungeon",
                "overrides": {"seed": 7, "purpose": "crypt"},
            })
            self.assertTrue(resolved["ready"])
            self.assertEqual(resolved["request"]["seed"], 7)


if __name__ == "__main__":
    unittest.main()
