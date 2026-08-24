import json, tempfile, unittest
from pathlib import Path
from structure_capability import StructureCapability, RebuildGrade
from structure_capability.minecraft.structure_builder import StructureBuilder
from structure_capability.minecraft.nbt import load_structure_nbt
from structure_capability.minecraft.worldgen import random_spread_structure_set
from structure_capability.generators import DungeonGenerator, adapt_donjon_options
from structure_capability.versioning import resolve_minecraft_version

class Tests(unittest.TestCase):
    def test_grade(self):
        self.assertEqual(RebuildGrade.parse("heavy-rebuild"), RebuildGrade.HEAVY_REBUILD)

    def test_deterministic_nbt(self):
        a = StructureBuilder((3,3,3)); a.set(1,1,1,"minecraft:stone")
        b = StructureBuilder((3,3,3)); b.set(1,1,1,"minecraft:stone")
        self.assertEqual(a.bytes(), b.bytes())
        self.assertEqual(a.git_blob_sha1(), b.git_blob_sha1())
        parsed = load_structure_nbt(a.bytes())
        self.assertEqual(parsed["size"], [3,3,3])
        self.assertEqual(len(parsed["blocks"]), 1)

    def test_structure_set_guard(self):
        with self.assertRaises(ValueError):
            random_spread_structure_set("x:y", 10, 10, 1)

    def test_plan_and_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            source = project / "s.json"
            source.write_text(json.dumps({"size":[2,2,2],"blocks":[{"block":"minecraft:stone","pos":[0,0,0]}]}))
            cap = StructureCapability(project)
            result = cap.plan({
                "structure_id":"test:site",
                "grade":"REFIT",
                "source":str(source),
                "purpose":{"kind":"warehouse","required_zones":["storage"]},
                "context":{"terrain":"urban_lot"}
            })
            self.assertEqual(result["plan"]["grade_name"], "REFIT")
            self.assertEqual(result["fitness"]["visual_gate"], "OPTIONAL_CLIENT_REVIEW")
            self.assertFalse(result["fitness"]["visual_review_required"])
            self.assertEqual(result["fitness"]["visual_review_owner"], "client")
            self.assertFalse(result["fitness"]["server_side_rendering"])
            self.assertTrue(result["snapshot"]["snapshot_id"])

    def test_visual_review_capability_is_client_owned_and_non_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            capabilities = cap.capabilities()
            self.assertFalse(capabilities["independent_visual_review_required"])
            self.assertFalse(capabilities["visual_review"]["required"])
            self.assertEqual(capabilities["visual_review"]["owner"], "client")
            self.assertFalse(capabilities["visual_review"]["server_side_rendering"])
            result = cap.generate({
                "structure_id":"test:client_rendered",
                "purpose":{"kind":"warehouse","required_zones":["storage"]},
                "context":{"terrain":"urban_lot"}
            })
            contract = result["generation"]["provider_contract"]
            self.assertFalse(contract["server_visual_review_required"])
            self.assertFalse(contract["server_side_rendering"])
            self.assertTrue(contract["client_rendering_responsibility"])
            self.assertTrue(contract["visual_review_advisory_only"])
            self.assertEqual(result["generation"]["status"], "READY_FOR_PROVIDER")

    def test_dungeon_layout_is_deterministic_and_fit(self):
        request = {
            "seed": 42, "purpose": "laboratory",
            "required_zones": ["entry", "laboratory", "utilities", "secure_core"],
            "size": {"min_width":48,"min_depth":40,"max_width":96,"max_depth":96,"preferred_width":72,"preferred_depth":60},
            "modularity": {"triple_fold":True,"macro_module":12,"meso_module":4,"micro_module":1,"connector_width":3},
        }
        gen = DungeonGenerator()
        a = gen.generate(request); b = gen.generate(request)
        self.assertEqual(a["grid"], b["grid"])
        self.assertEqual(a["rooms"], b["rooms"])
        self.assertEqual(a["fitness"]["status"], "PASS")
        self.assertEqual(a["footprint_blocks"], [72, 60])

    def test_dungeon_connector_fitness_gate(self):
        layout = DungeonGenerator().generate({
            "seed": 7, "purpose": "crypt",
            "size": {"min_width":48,"min_depth":48,"max_width":96,"max_depth":96},
            "modularity": {"meso_module":4,"micro_module":1,"macro_module":12,"connector_width":5},
        })
        self.assertEqual(layout["fitness"]["status"], "FAIL")
        self.assertIn("CONNECTOR_EXCEEDS_MESO_MODULE", {f["code"] for f in layout["fitness"]["findings"]})


    def test_donjon_option_adapter_and_shape_mask(self):
        translated = adapt_donjon_options({
            "seed": 9, "n_rows": 39, "n_cols": 39,
            "dungeon_layout": "Cross", "room_layout": "Packed",
            "corridor_layout": "Labyrinth", "remove_deadends": 100,
            "add_stairs": 2,
        })
        self.assertEqual(translated["layout_shape"], "cross")
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            layout = cap.dungeon_layout({"classic_donjon_options": {
                "seed": 9, "n_rows": 39, "n_cols": 39,
                "dungeon_layout": "Cross", "room_layout": "Packed",
                "corridor_layout": "Labyrinth", "remove_deadends": 100,
                "add_stairs": 2,
            }})
            self.assertEqual(layout["layout_shape"], "cross")
            self.assertEqual(layout["fitness"]["status"], "PASS")
            self.assertEqual(len(layout["stairs"]), 2)
            self.assertTrue(any("X" in row for row in layout["grid"]))

    def test_version_profile_known_data_version(self):
        profile = resolve_minecraft_version("1.20.1")
        self.assertEqual(profile.data_version, 3465)
        self.assertTrue(profile.exact_release_metadata)

    def test_oversize_dungeon_auto_fragments_to_target_limit(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            result = cap.generate({
                "structure_id":"test:large_lab", "target_version":"1.20.1",
                "purpose":{"kind":"laboratory","required_zones":["entry","laboratory","utilities","secure_core"]},
                "generation":{
                    "kind":"dungeon", "materialize_nbt":True,
                    "materialization_mode":"auto",
                    "layout":{
                        "seed":42,
                        "size":{"min_width":48,"min_depth":40,"max_width":96,"max_depth":96,"preferred_width":72,"preferred_depth":60},
                        "modularity":{"macro_module":12,"meso_module":4,"micro_module":1,"connector_width":3}
                    }
                }
            })
            artifact = result["structure_artifact"]
            self.assertEqual(result["generation"]["status"], "MATERIALIZED_PIECE_SET")
            self.assertEqual(artifact["overall_size"], [72, 5, 60])
            self.assertEqual(artifact["piece_limit_blocks"], 48)
            self.assertEqual(artifact["piece_count"], 4)
            self.assertEqual(len(result["snapshot"]["artifacts"]), 4)
            offsets = {tuple(piece["offset"]) for piece in artifact["pieces"]}
            self.assertEqual(offsets, {(0,0,0), (48,0,0), (0,0,48), (48,0,48)})
            for piece in artifact["pieces"]:
                self.assertLessEqual(max(piece["size"]), 48)
                snap = next(a for a in result["snapshot"]["artifacts"] if a["snapshot_path"].endswith(piece["name"]))
                parsed = load_structure_nbt(Path(td) / ".structure-capability" / "snapshots" / result["snapshot"]["snapshot_id"] / snap["snapshot_path"])
                self.assertEqual(parsed["DataVersion"], 3465)
                self.assertLessEqual(max(parsed["size"]), 48)

    def test_integrated_dungeon_generation_materializes_target_version(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            result = cap.generate({
                "structure_id":"test:dungeon", "target_version":"1.20.1",
                "purpose":{"kind":"crypt","required_zones":["entry","burial","reward"]},
                "generation":{
                    "kind":"dungeon", "materialize_nbt":True,
                    "layout":{
                        "seed":11,
                        "size":{"min_width":48,"min_depth":48,"max_width":96,"max_depth":96},
                        "modularity":{"macro_module":12,"meso_module":4,"micro_module":1,"connector_width":3}
                    }
                }
            })
            self.assertEqual(result["generated_layout"]["fitness"]["status"], "PASS")
            self.assertEqual(result["structure_artifact"]["data_version"], 3465)
            self.assertEqual(result["generation"]["status"], "MATERIALIZED_SKELETON")
            self.assertEqual(result["snapshot"]["stage"], "generate")
            self.assertEqual(result["snapshot"]["parent"], result["planning_snapshot"]["snapshot_id"])
            self.assertEqual(len(result["snapshot"]["artifacts"]), 1)
            artifact_path = Path(td) / ".structure-capability" / "snapshots" / result["snapshot"]["snapshot_id"] / result["snapshot"]["artifacts"][0]["snapshot_path"]
            parsed = load_structure_nbt(artifact_path)
            self.assertEqual(parsed["DataVersion"], 3465)
            self.assertGreater(len(parsed["blocks"]), 100)

if __name__ == "__main__":
    unittest.main()
