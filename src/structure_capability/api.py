from __future__ import annotations
from pathlib import Path
from .models import StructureRequest
from .mod_awareness import ModInventory
from .registry import RegistryResolver
from .snapshot import SnapshotStore
from .pipeline import StructurePipeline
from .generators import (
    DungeonGenerator,
    GeneratorRegistry,
    NativeDungeonProvider,
    InfrastructureGenerator,
    NativeInfrastructureProvider,
)
from .versioning import resolve_minecraft_version
from .tooling import tool_catalog

class StructureCapability:
    API_VERSION = "v1"

    def __init__(self, project_root=".", state_root=None):
        self.project_root = Path(project_root)
        self.inventory = ModInventory(self.project_root)
        self.inventory.scan()
        self.registry = RegistryResolver(self.inventory)
        state_root = state_root or self.project_root / ".structure-capability" / "snapshots"
        self.snapshots = SnapshotStore(state_root)
        self.pipeline = StructurePipeline(self.snapshots, self.registry)
        self.dungeons = DungeonGenerator()
        self.infrastructure = InfrastructureGenerator()
        self.generators = GeneratorRegistry()
        self.dungeon_provider = NativeDungeonProvider(self.dungeons)
        self.infrastructure_provider = NativeInfrastructureProvider(self.infrastructure)
        self.generators.register(self.dungeon_provider)
        self.generators.register(self.infrastructure_provider)

    def capabilities(self):
        return {
            "api_version": self.API_VERSION,
            "vanilla_first": True,
            "mod_awareness": ["jar metadata", "data/assets namespaces", "explicit registry IDs"],
            "operations": [
                "inventory", "audit", "plan", "generate", "resume", "dungeon_layout",
                "infrastructure_layout", "minecraft_version",
            ],
            "rebuild_grades": {
                "0": "AUDIT_ONLY",
                "1": "TOUCH_UP",
                "2": "REFIT",
                "3": "DETAIL_PASS",
                "4": "FUNCTIONAL_REBUILD",
                "5": "HEAVY_REBUILD",
                "6": "FULL_RECONTEXTUALIZATION",
            },
            "generators": self.generators.describe(),
            "dungeon_layout": {
                "engine": "native_modular_v1",
                "triple_fold_modularity": ["macro", "meso", "micro"],
                "purpose_sizing": True,
                "deterministic_seeded_generation": True,
                "donjon_reference": "isolated_cc_by_nc_optional_reference",
            },
            "infrastructure_layout": {
                "engine": "native_infrastructure_v1",
                "inner_city_cross_section": {"road_width": 6, "terrain_padding_each_side": 5},
                "highway_profiles": ["elevated_urban_water_crossing", "surface_highway"],
                "jigsaw_assembly": True,
                "lost_cities_contracts": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"],
                "purpose_depth_validation": True,
                "world_seed_determinism": True,
                "runtime_validation_required": True,
            },
            "minecraft_versions": {"initial_contract": "1.12.x+", "materialization": "provider_validated"},
            "ai_tool_calling": {"catalog_endpoint": "/v1/tools", "portable_json_schema": True},
            "independent_visual_review_required": True,
        }

    def tools(self):
        return tool_catalog()

    def register_generator(self, provider):
        self.generators.register(provider)
        return provider

    def inventory_project(self):
        return self.inventory.to_dict()

    def _request(self, request):
        return request if isinstance(request, StructureRequest) else StructureRequest.from_dict(request)

    def audit(self, request):
        return self.pipeline.audit(self._request(request))

    def plan(self, request):
        return self.pipeline.plan(self._request(request))

    def generate(self, request):
        req = self._request(request)
        result = self.pipeline.generate(req)
        provider = self.generators.resolve(req.generation.get("kind"))
        if not provider:
            return result

        generated = provider.generate(req, self.registry)
        result["generation"]["provider_id"] = generated["provider_id"]
        result["generation"]["status"] = generated["status"]
        result["generated_layout"] = generated["generated_layout"]
        if generated.get("structure_artifact"):
            result["structure_artifact"] = generated["structure_artifact"]

        planning_snapshot = result.get("snapshot")
        result["planning_snapshot"] = planning_snapshot
        generated_artifacts = {}
        if generated.get("artifact_bytes") is not None:
            prefix = req.structure_id.split(":")[-1]
            for name, data in generated["artifact_bytes"].items():
                generated_artifacts[f"{prefix}_{name}"] = data
        snapshot_artifact = dict(result.get("structure_artifact") or {})
        if snapshot_artifact.get("pieces"):
            snapshot_artifact["pieces"] = [dict(piece) for piece in snapshot_artifact["pieces"]]
            for piece in snapshot_artifact["pieces"]:
                piece.pop("nbt_base64", None)
        snapshot_artifact.pop("nbt_base64", None)
        snapshot_payload = {
            "request": req.to_dict(),
            "generation": result.get("generation"),
            "generated_layout": result.get("generated_layout"),
            "structure_artifact": snapshot_artifact or None,
        }
        final_snapshot = self.snapshots.create(
            req.structure_id, "generate", snapshot_payload,
            parent=planning_snapshot.get("snapshot_id") if planning_snapshot else None,
            generated_artifacts=generated_artifacts,
        )
        result["snapshot"] = final_snapshot
        return result

    def dungeon_layout(self, request):
        return self.dungeon_provider.layout(request)

    def infrastructure_layout(self, request):
        return self.infrastructure_provider.layout(request)

    def minecraft_version(self, version):
        return resolve_minecraft_version(version).to_dict()

    def resume(self, snapshot_id):
        return self.snapshots.load(snapshot_id)
