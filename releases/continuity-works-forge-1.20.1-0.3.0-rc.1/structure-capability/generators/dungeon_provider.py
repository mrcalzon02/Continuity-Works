from __future__ import annotations
from .dungeon import DungeonGenerator
from .donjon_compat import adapt_donjon_options
from ..minecraft.dungeon_compiler import compile_dungeon_layout_artifacts


class NativeDungeonProvider:
    aliases = ("dungeon", "dungeon_layout", "modular_dungeon")
    provider_id = "native_modular_v1"

    def __init__(self, generator: DungeonGenerator | None = None):
        self.generator = generator or DungeonGenerator()

    def describe(self):
        return {
            "provider_id": self.provider_id,
            "aliases": list(self.aliases),
            "structure_types": ["dungeon", "underground_complex", "interior_complex", "procedural_spatial_skeleton"],
            "features": [
                "deterministic_seed", "purpose_sizing", "functional_zones",
                "triple_fold_modularity", "shape_masks", "classic_donjon_option_adapter",
                "fitness_gate", "minecraft_nbt_skeleton_1_13_plus",
            ],
        }

    def normalize_layout_request(self, request: dict) -> dict:
        request = dict(request or {})
        if "classic_donjon_options" not in request:
            return request
        translated = adapt_donjon_options(
            dict(request.get("classic_donjon_options") or {}),
            cell_scale_blocks=int(request.get("cell_scale_blocks", 3)),
            triple_fold=bool(request.get("modularity", {}).get("triple_fold", True)),
        )
        for key, value in request.items():
            if key in {"classic_donjon_options", "cell_scale_blocks"}:
                continue
            if key in {"size", "modularity", "metadata"} and isinstance(value, dict):
                translated.setdefault(key, {}).update(value)
            else:
                translated[key] = value
        return translated

    def layout(self, request: dict):
        return self.generator.generate(self.normalize_layout_request(request))

    def generate(self, structure_request, registry_resolver):
        generation = structure_request.generation
        layout_request = dict(generation.get("layout", {}))
        layout_request.setdefault(
            "purpose",
            structure_request.purpose.kind if structure_request.purpose.kind != "unspecified" else "generic_dungeon",
        )
        layout_request.setdefault("scale", structure_request.scale)
        if structure_request.purpose.required_zones:
            layout_request.setdefault("required_zones", list(structure_request.purpose.required_zones))
        layout_request.setdefault("theme", structure_request.to_dict().get("theme", {}))
        layout = self.layout(layout_request)

        out = {
            "provider_id": self.provider_id,
            "status": "LAYOUT_READY" if layout["fitness"]["status"] == "PASS" else "BLOCKED_BY_FITNESS",
            "generated_layout": layout,
            "structure_artifact": None,
            "artifact_bytes": None,
        }
        if not bool(generation.get("materialize_nbt", False)):
            return out
        if layout["fitness"]["status"] != "PASS":
            return out

        palette = generation.get("palette")
        if not palette and structure_request.theme.palette_roles:
            resolved = registry_resolver.resolve_palette(structure_request.theme.palette_roles)
            palette = {
                "floor": resolved.get("floor") or resolved.get("foundation"),
                "wall": resolved.get("wall") or resolved.get("structural"),
                "roof": resolved.get("roof"),
            }
            palette = {k: v for k, v in palette.items() if v}
        artifact, artifact_bytes = compile_dungeon_layout_artifacts(
            layout,
            target_version=structure_request.target_version,
            data_version=generation.get("data_version"),
            registry_resolver=registry_resolver,
            palette=palette,
            materialization_mode=generation.get("materialization_mode", "auto"),
            piece_limit=generation.get("piece_limit"),
            allow_oversize_nbt=bool(generation.get("allow_oversize_nbt", False)),
            emit_binary=bool(generation.get("emit_binary", False)),
        )
        out.update(
            status="MATERIALIZED_PIECE_SET" if artifact["piece_count"] > 1 else "MATERIALIZED_SKELETON",
            structure_artifact=artifact,
            artifact_bytes=artifact_bytes,
        )
        return out
