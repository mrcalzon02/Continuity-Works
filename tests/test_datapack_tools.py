import tempfile
import unittest

from structure_capability import StructureCapability
from structure_capability.tooling import tool_catalog
from structure_capability.versioning import resolve_minecraft_version


class MinecraftDatapackToolTests(unittest.TestCase):
    def _capability(self, root):
        return StructureCapability(root)

    def test_book_page_limit_is_version_aware(self):
        pages = [f"Page {i}" for i in range(101)]
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            legacy = cap.minecraft_book_generate({
                "target_version": "1.20.1", "title": "Legacy", "author": "SS", "pages": pages,
            })
            modern = cap.minecraft_book_generate({
                "target_version": "1.20.5", "title": "Modern", "author": "SS", "pages": pages,
            })
            self.assertEqual(legacy["gate"]["status"], "FAIL")
            self.assertFalse(legacy["materialization_allowed"])
            self.assertNotEqual(modern["gate"]["status"], "FAIL")
            self.assertTrue(modern["materialization_allowed"])
            self.assertIn("BOOK_PAGE_LIMIT_REMOVED", {f["code"] for f in modern["gate"]["findings"]})

    def test_1205_release_metadata_is_exact(self):
        profile = resolve_minecraft_version("1.20.5")
        self.assertTrue(profile.exact_release_metadata)
        self.assertEqual(profile.data_version, 3837)
        self.assertEqual(profile.resource_pack_format, 32)
        self.assertEqual(profile.data_pack_format, 41)

    def test_book_has_loot_compatible_legacy_and_component_forms(self):
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            legacy = cap.minecraft_book_generate({
                "target_version": "1.20.1", "title": "Evidence", "author": "Atlas", "pages": ["A"],
            })
            modern = cap.minecraft_book_generate({
                "target_version": "1.20.5", "title": "Evidence", "author": "Atlas", "pages": ["A"],
            })
            self.assertIn("nbt", legacy["loot_entry"])
            self.assertNotIn("components", legacy["loot_entry"])
            self.assertIn("components", modern["loot_entry"])
            self.assertNotIn("nbt", modern["loot_entry"])

    def test_loot_table_adapts_custom_item_data(self):
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            legacy = cap.minecraft_loot_table_generate({
                "target_version": "1.20.1", "table_id": "test:legacy",
                "guaranteed": [{"id": "minecraft:paper", "nbt": "{CustomModelData:1}"}],
            })
            modern = cap.minecraft_loot_table_generate({
                "target_version": "1.20.5", "table_id": "test:modern",
                "guaranteed": [{"id": "minecraft:paper", "components": {"minecraft:custom_name": '{"text":"Evidence"}'}}],
            })
            legacy_functions = legacy["json"]["pools"][0]["entries"][0]["functions"]
            modern_functions = modern["json"]["pools"][0]["entries"][0]["functions"]
            self.assertEqual(legacy_functions[0]["function"], "minecraft:set_nbt")
            self.assertEqual(modern_functions[0]["function"], "minecraft:set_components")

    def test_advancement_icon_and_directory_are_version_aware(self):
        request = {
            "advancement_id": "test:discover/site",
            "display": {"title": "Found it", "description": "Enter the site", "icon": "minecraft:map"},
            "criteria": {"triggered": "minecraft:impossible"},
        }
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            legacy = cap.minecraft_advancement_generate({**request, "target_version": "1.20.1"})
            component = cap.minecraft_advancement_generate({**request, "target_version": "1.20.5"})
            singular = cap.minecraft_advancement_generate({**request, "target_version": "1.21"})
            self.assertIn("item", legacy["json"]["display"]["icon"])
            self.assertIn("id", component["json"]["display"]["icon"])
            self.assertEqual(singular["path"], "data/test/advancement/discover/site.json")

    def test_tag_directory_switches_to_singular_in_121(self):
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            old = cap.minecraft_tag_generate({
                "target_version": "1.20.1", "tag_id": "test:evidence", "registry": "item",
                "values": ["minecraft:paper"],
            })
            new = cap.minecraft_tag_generate({
                "target_version": "1.21", "tag_id": "test:evidence", "registry": "item",
                "values": ["minecraft:paper"],
            })
            self.assertEqual(old["path"], "data/test/tags/items/evidence.json")
            self.assertEqual(new["path"], "data/test/tags/item/evidence.json")

    def test_datapack_manifest_uses_exact_1205_format(self):
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            out = cap.minecraft_datapack_manifest_generate({
                "target_version": "1.20.5", "description": "StructureSmith test pack",
            })
            self.assertEqual(out["json"]["pack"]["pack_format"], 41)
            self.assertTrue(out["materialization_allowed"])

    def test_package_binds_generated_book_as_guaranteed_loot(self):
        with tempfile.TemporaryDirectory() as td:
            cap = self._capability(td)
            out = cap.minecraft_content_package_generate({
                "package_id": "test:quest_site",
                "target_version": "1.20.5",
                "books": [{"name": "evidence", "title": "Evidence", "author": "Atlas", "pages": ["Log entry"]}],
                "loot_tables": [{
                    "name": "evidence_chest",
                    "items": [{"id": "minecraft:iron_ingot", "weight": 2}],
                }],
                "bindings": [{
                    "type": "book_as_guaranteed_loot", "book": "evidence", "loot_table": "evidence_chest",
                }],
            })
            self.assertTrue(out["materialization_allowed"])
            self.assertEqual(out["links"][0]["status"], "linked")
            loot = out["artifacts"]["loot_tables"][0]
            self.assertEqual(len(loot["json"]["pools"]), 2)
            guaranteed_functions = loot["json"]["pools"][1]["entries"][0]["functions"]
            self.assertEqual(guaranteed_functions[0]["function"], "minecraft:set_components")

    def test_tool_catalog_v13_preserves_existing_generation_contracts(self):
        catalog = tool_catalog()
        tools = {tool["name"]: tool for tool in catalog["tools"]}
        self.assertEqual(catalog["schema_version"], "1.3")
        self.assertEqual(len(tools), 17)
        for name in (
            "minecraft_advancement_generate", "minecraft_tag_generate",
            "minecraft_datapack_manifest_generate", "minecraft_content_package_generate",
        ):
            self.assertIn(name, tools)
        generation = tools["structure_generate"]["parameters"]["properties"]["generation"]["properties"]
        self.assertIn("piece_limit", generation)
        road = tools["infrastructure_layout"]["parameters"]["properties"]["road"]["properties"]
        self.assertEqual(road["width"]["const"], 6)
        self.assertEqual(road["terrain_padding"]["const"], 5)


if __name__ == "__main__":
    unittest.main()
