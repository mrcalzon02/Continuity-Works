import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "structure_spawn_protection" / "forge-1.20.1"


class SpawnProtectionModuleLayoutTests(unittest.TestCase):
    def test_standalone_forge_module_declares_no_biome_dependency(self):
        build = (MODULE / "build.gradle").read_text(encoding="utf-8")
        mods = (MODULE / "src/main/resources/META-INF/mods.toml").read_text(encoding="utf-8")
        self.assertIn("ContinuityWorks-StructureSpawnProtection-Forge-1.20.1", build)
        self.assertNotIn("TerraBlender", build)
        self.assertNotIn("continuityworks_biomes", mods)

    def test_mixin_contract_is_required_and_contains_both_worldgen_hooks(self):
        config = json.loads((MODULE / "src/main/resources/continuityworks_spawn_protection.mixins.json").read_text())
        self.assertTrue(config["required"])
        self.assertEqual(config["injectors"]["defaultRequire"], 1)
        self.assertIn("ChunkGeneratorMixin", config["mixins"])
        self.assertIn("JigsawPlacementPlacerMixin", config["mixins"])

    def test_automatic_registry_scan_defaults_on_and_hard_minimum_is_500(self):
        config_java = (MODULE / "src/main/java/io/continuityworks/spawnprotection/config/SpawnProtectionConfig.java").read_text()
        self.assertIn("HARD_MINIMUM_RADIUS = 500", config_java)
        self.assertIn('define("autoIncludeRegisteredStructures", true)', config_java)
        self.assertIn('defineInRange("defaultExclusionRadius", HARD_MINIMUM_RADIUS', config_java)
        self.assertIn('defineInRange("defaultJigsawPieceRadius", HARD_MINIMUM_RADIUS', config_java)

    def test_public_adapter_api_enforces_same_minimum(self):
        api = (MODULE / "src/main/java/io/continuityworks/spawnprotection/api/SpawnProtectionApi.java").read_text()
        self.assertIn("External structure exclusion radius must be >= 500", api)
        self.assertIn("tryReserve", api)
        self.assertIn("commit", api)
        self.assertIn("rollback", api)

    def test_inclusion_tags_are_additive(self):
        tag_root = MODULE / "src/main/resources/data/continuityworks_spawn_protection/tags/worldgen/structure"
        for name in ("protected", "jigsaw_piece_protected", "ignored"):
            data = json.loads((tag_root / f"{name}.json").read_text())
            self.assertFalse(data["replace"])

    def test_biome_expander_enrollment_does_not_mutate_structure_definitions(self):
        runtime = ROOT / "examples/biome_expander/runtime_mod/1.20.1/src/main/resources/data"
        tag = json.loads((runtime / "continuityworks_spawn_protection/tags/worldgen/structure/protected.json").read_text())
        self.assertIn("continuityworks_biomes:abyssal/fracture_vent_field", tag["values"])
        self.assertIn("continuityworks_biomes:abyssal/hadal_vent_complex", tag["values"])
        profile = json.loads((runtime / "continuityworks_biomes/continuityworks_spawn_protection/profiles/abyssal_vents.json").read_text())
        self.assertGreaterEqual(profile["exclusion_radius"], 500)
        self.assertGreaterEqual(profile["jigsaw_piece_exclusion_radius"], 500)
        self.assertTrue(profile["protect_jigsaw_pieces"])


if __name__ == "__main__":
    unittest.main()
