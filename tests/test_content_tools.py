import json
import tempfile
import unittest
from pathlib import Path

from structure_capability import StructureCapability


class MinecraftContentToolTests(unittest.TestCase):
    def test_book_1201_uses_legacy_book_nbt(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_book_generate({
                "target_version": "1.20.1", "title": "Field Notes", "author": "Atlas",
                "pages": ["Page one", {"text": "Page two", "bold": True}],
            })
            self.assertEqual(out["format"], "legacy_written_book_nbt")
            self.assertIn("tag", out["item_stack"])
            self.assertEqual(out["gate"]["status"], "PASS")

    def test_book_1205_uses_written_book_component(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_book_generate({
                "target_version": "1.20.5", "title": "Containment Log", "author": "VCF", "pages": ["Entry 1"]
            })
            self.assertEqual(out["format"], "item_components_1_20_5_plus")
            self.assertIn("minecraft:written_book_content", out["item_stack"]["components"])

    def test_loot_table_121_uses_singular_directory_and_guarantees(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_loot_table_generate({
                "target_version": "1.21", "table_id": "test:evidence/cache",
                "items": [{"id": "minecraft:iron_ingot", "weight": 3}],
                "guaranteed": [{"id": "minecraft:paper", "count": 1}],
            })
            self.assertEqual(out["path"], "data/test/loot_table/evidence/cache.json")
            self.assertEqual(len(out["json"]["pools"]), 2)
            self.assertEqual(out["gate"]["status"], "PASS")

    def test_recipe_1205_uses_item_stack_result(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_recipe_generate({
                "target_version": "1.20.5", "recipe_id": "test:compressed_stone", "type": "crafting_shaped",
                "pattern": ["###", "###", "###"], "key": {"#": {"item": "minecraft:cobblestone"}},
                "result": {"id": "minecraft:stone", "count": 2},
            })
            self.assertEqual(out["path"], "data/test/recipes/compressed_stone.json")
            self.assertEqual(out["json"]["result"]["id"], "minecraft:stone")
            self.assertEqual(out["json"]["result"]["count"], 2)

    def test_recipe_121_uses_singular_directory(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_recipe_generate({
                "target_version": "1.21", "recipe_id": "test:stone_mix", "type": "crafting_shapeless",
                "ingredients": ["minecraft:stone", "minecraft:gravel"], "result": "minecraft:cobblestone",
            })
            self.assertEqual(out["path"], "data/test/recipe/stone_mix.json")

    def test_inventory_discovers_mod_resource_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            item_model = root / "assets" / "examplemod" / "models" / "item" / "widget.json"
            recipe = root / "data" / "examplemod" / "recipes" / "widget.json"
            item_model.parent.mkdir(parents=True)
            recipe.parent.mkdir(parents=True)
            item_model.write_text(json.dumps({"parent": "item/generated"}))
            recipe.write_text(json.dumps({"type": "minecraft:crafting_shapeless"}))
            cap = StructureCapability(root)
            item_probe = cap.minecraft_registry_probe({"id": "examplemod:widget", "kind": "item"})
            recipe_probe = cap.minecraft_registry_probe({"id": "examplemod:widget", "kind": "recipe"})
            self.assertEqual(item_probe["probe"]["level"], "candidate")
            self.assertEqual(recipe_probe["probe"]["level"], "exact")

    def test_strict_unknown_mod_id_blocks_materialization(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_recipe_generate({
                "target_version": "1.20.1", "recipe_id": "test:bad_mod_recipe",
                "type": "crafting_shapeless", "id_policy": "strict",
                "ingredients": ["missingmod:widget"], "result": "minecraft:stone",
            })
            self.assertEqual(out["gate"]["status"], "FAIL")
            self.assertFalse(out["materialization_allowed"])

    def test_icon_can_force_svg_badge(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            out = cap.minecraft_icon_assign({"subject": "recipe", "mode": "badge", "label": "RX"})
            self.assertEqual(out["icon"]["kind"], "svg_badge")
            self.assertIn("<svg", out["icon"]["fallback_svg"])


if __name__ == "__main__":
    unittest.main()
