from __future__ import annotations

from .infrastructure import InfrastructureGenerator


class NativeInfrastructureProvider:
    aliases = (
        "infrastructure", "road", "highway", "civic_facility", "industrial_facility",
        "native_infrastructure_v1",
    )
    provider_id = "native_infrastructure_v1"

    def __init__(self, generator: InfrastructureGenerator | None = None):
        self.generator = generator or InfrastructureGenerator()

    def describe(self):
        return {
            "provider_id": self.provider_id,
            "aliases": list(self.aliases),
            "structure_types": ["infrastructure", "road", "highway", "civic", "industrial"],
            "features": [
                "strict_inner_city_6_plus_5_plus_5_cross_section",
                "reference_driven_highway_profiles",
                "sequential_jigsaw_contracts",
                "lost_cities_tileable_grid_contract",
                "lost_cities_randomized_coordinate_contract",
                "lost_cities_sequential_jigsaw_contract",
                "purpose_depth_validation",
                "world_seed_determinism",
                "urban_rural_facility_variants",
            ],
            "runtime_note": "Lost Cities and fresh-world placement are emitted as integration contracts and require runtime validation in a compatible modded instance.",
        }

    def layout(self, request: dict):
        return self.generator.generate(request)

    def generate(self, structure_request, registry_resolver):
        generation = dict(structure_request.generation or {})
        layout_request = dict(generation.get("layout") or {})
        layout_request.setdefault("seed", int(generation.get("seed", 0)))
        layout_request.setdefault("world_seed", int(generation.get("world_seed", layout_request.get("seed", 0))))
        layout_request.setdefault("module_type", self._module_type(structure_request, layout_request))
        if structure_request.context.terrain in {"urban_lot", "city", "urban"}:
            layout_request.setdefault("variant", "urban")
        elif structure_request.context.terrain in {"rural", "field", "wilderness_edge"}:
            layout_request.setdefault("variant", "rural")
        purpose = dict(layout_request.get("purpose") or {})
        purpose.setdefault("depth", int(structure_request.metadata.get("purpose_depth", 3)))
        layout_request["purpose"] = purpose

        layout = self.layout(layout_request)
        return {
            "provider_id": self.provider_id,
            "status": "LAYOUT_READY" if layout["fitness"]["status"] == "PASS" else "BLOCKED_BY_FITNESS",
            "generated_layout": layout,
            "structure_artifact": None,
            "artifact_bytes": None,
        }

    @staticmethod
    def _module_type(structure_request, layout_request):
        if layout_request.get("module_type"):
            return layout_request["module_type"]
        kind = str(structure_request.purpose.kind or "").lower()
        stype = str(structure_request.structure_type or "").lower()
        if "highway" in {kind, stype}:
            return "highway"
        if "road" in {kind, stype} or stype == "infrastructure":
            return "inner_city_road"
        if kind == "civic" or stype == "civic":
            return "civic_facility"
        if kind == "industrial" or stype == "industrial":
            return "industrial_facility"
        return "inner_city_road"
