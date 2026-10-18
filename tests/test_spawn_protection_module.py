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

    def test_mixinextras_is_bundled_for_exception_safe_generation_wrapping(self):
        build = (MODULE / "build.gradle").read_text(encoding="utf-8")
        self.assertIn("jarJar.enable()", build)
        self.assertIn("mixinextras-common:0.5.5", build)
        self.assertIn("mixinextras-forge:0.5.5", build)

    def test_automatic_registry_scan_defaults_on_and_hard_minimum_is_500(self):
        config_java = (MODULE / "src/main/java/io/continuityworks/spawnprotection/config/SpawnProtectionConfig.java").read_text()
        self.assertIn("HARD_MINIMUM_RADIUS = 500", config_java)
        self.assertIn('define("autoIncludeRegisteredStructures", true)', config_java)
        self.assertIn('defineInRange("defaultExclusionRadius", HARD_MINIMUM_RADIUS', config_java)
        self.assertIn('defineInRange("defaultJigsawPieceRadius", HARD_MINIMUM_RADIUS', config_java)

    def test_public_adapter_api_enforces_supported_radius_range(self):
        api = (MODULE / "src/main/java/io/continuityworks/spawnprotection/api/SpawnProtectionApi.java").read_text()
        self.assertIn("SpawnProtectionConfig.HARD_MINIMUM_RADIUS", api)
        self.assertIn("SpawnProtectionConfig.HARD_MAXIMUM_RADIUS", api)
        self.assertIn("External structure exclusion radius must be between ", api)
        self.assertIn("tryReserve", api)
        self.assertIn("commit", api)
        self.assertIn("rollback", api)

    def test_reservation_model_enforces_supported_persistent_radius_range(self):
        reservation = (MODULE / "src/main/java/io/continuityworks/spawnprotection/model/Reservation.java").read_text()
        self.assertIn("exclusionRadius == 0 && !provisional", reservation)
        self.assertIn("exclusionRadius 0 is reserved for provisional transient probes", reservation)
        self.assertIn("exclusionRadius != 0", reservation)
        self.assertIn("SpawnProtectionConfig.HARD_MINIMUM_RADIUS", reservation)
        self.assertIn("SpawnProtectionConfig.HARD_MAXIMUM_RADIUS", reservation)
        self.assertIn("persistent exclusionRadius must be 0 (transient probe) or between ", reservation)

    def test_generation_attempt_context_is_invocation_scoped_and_lifo(self):
        context = (MODULE / "src/main/java/io/continuityworks/spawnprotection/runtime/GenerationAttemptContext.java").read_text()
        mixin = (MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/ChunkGeneratorMixin.java").read_text()
        self.assertIn("new Frame(attempt)", context)
        self.assertIn("Generation attempt frames must end in LIFO order", context)
        self.assertIn("GenerationAttempt attempt = null;", mixin)
        self.assertNotIn("if (level == null) return;", mixin)
        self.assertIn("GenerationAttemptContext.begin(attempt);", mixin)
        self.assertIn("GenerationAttemptContext.end(attempt);", mixin)

    def test_forge_1201_structure_manager_level_is_resolved_from_real_accessor(self):
        config = json.loads(
            (MODULE / "src/main/resources/continuityworks_spawn_protection.mixins.json").read_text(encoding="utf-8")
        )
        accessor = (
            MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/StructureManagerLevelAccessor.java"
        ).read_text(encoding="utf-8")
        mixin = (
            MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/ChunkGeneratorMixin.java"
        ).read_text(encoding="utf-8")
        resolver = (
            MODULE / "src/main/java/io/continuityworks/spawnprotection/runtime/LevelResolver.java"
        ).read_text(encoding="utf-8")

        # Forge 1.20.1 StructureManager has a private level field; no
        # level() method, and its true backing level may be WorldGenRegion.
        self.assertIn("StructureManagerLevelAccessor", config["mixins"])
        self.assertIn("import net.minecraft.world.level.StructureManager;", accessor)
        self.assertIn("@Mixin(StructureManager.class)", accessor)
        self.assertIn('@Accessor("level")', accessor)
        self.assertIn("LevelAccessor continuityworks$getLevel()", accessor)
        self.assertIn("import net.minecraft.world.level.StructureManager;", mixin)
        self.assertNotIn("net.minecraft.world.level.levelgen.structure.StructureManager", mixin)
        self.assertNotIn("structureManager.level()", mixin)
        self.assertIn("LevelResolver.serverLevel(", mixin)
        self.assertIn(".continuityworks$getLevel()", mixin)
        self.assertIn("region.getLevel()", resolver)

    def test_generation_invocation_unwinds_on_thrown_exceptions(self):
        mixin = (MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/ChunkGeneratorMixin.java").read_text()
        self.assertIn('@WrapMethod(method = "tryGenerateStructure")', mixin)
        self.assertIn("Operation<Boolean> original", mixin)
        self.assertIn("boolean generated = original.call(", mixin)
        self.assertIn("finally {", mixin)
        self.assertIn("SpawnProtectionService.rollbackAttempt(attempt);", mixin)
        self.assertIn("GenerationAttemptContext.end(attempt);", mixin)
        self.assertNotIn('@Inject(method = "tryGenerateStructure"', mixin)

    def test_chunk_generator_mixin_calls_the_real_java_service_contract(self):
        # Static source-contract gate: the Forge module is not compiled by
        # the main Python frontend CI, so an obsolete Java method call can
        # otherwise survive every public-service validation.
        service = (MODULE / "src/main/java/io/continuityworks/spawnprotection/runtime/SpawnProtectionService.java").read_text(encoding="utf-8")
        attempt = (MODULE / "src/main/java/io/continuityworks/spawnprotection/runtime/GenerationAttempt.java").read_text(encoding="utf-8")
        mixin = (MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/ChunkGeneratorMixin.java").read_text(encoding="utf-8")
        self.assertIn(
            "beginAttempt(\n        ServerLevel level,\n        RegistryAccess registryAccess,\n        Structure structure,\n        ChunkPos chunkPos",
            service,
        )
        self.assertIn(
            "SpawnProtectionService.beginAttempt(\n                level,\n                registryAccess,\n                selectionEntry.structure().value(),\n                chunkPos\n            );",
            mixin,
        )
        self.assertNotIn("attempt.permitted()", mixin)
        self.assertNotIn("chunkPos.getMiddleBlockX()", mixin)
        self.assertNotIn("Registries.STRUCTURE", mixin)
        self.assertIn("boolean finish(StructureStart start)", attempt)
        self.assertIn("SpawnProtectionService.finishAttempt(attempt, start)", mixin)

    def test_generation_attempt_finish_owns_failed_transaction_cleanup(self):
        attempt = (MODULE / "src/main/java/io/continuityworks/spawnprotection/runtime/GenerationAttempt.java").read_text()
        mixin = (MODULE / "src/main/java/io/continuityworks/spawnprotection/mixin/ChunkGeneratorMixin.java").read_text()
        self.assertIn("boolean finished = false;", attempt)
        self.assertIn("finally {", attempt)
        self.assertIn("if (!finished) rollback();", attempt)
        self.assertIn("finished = true;", attempt)
        failed_finish = "if (!SpawnProtectionService.finishAttempt(attempt, start)) {\n                SpawnProtectionService.rollbackAttempt(attempt);"
        self.assertNotIn(failed_finish, mixin)

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