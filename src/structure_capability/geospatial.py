from __future__ import annotations
from dataclasses import dataclass

@dataclass
class GeospatialFinding:
    severity: str
    code: str
    message: str

def evaluate_context(context, purpose) -> list[GeospatialFinding]:
    findings = []
    placement = context.placement or {}
    if placement.get("requires_water") and context.fluid != "minecraft:water":
        findings.append(GeospatialFinding("error", "WATER_REQUIRED", "Placement requires water but site context is not water."))
    if placement.get("heightmap") == "OCEAN_FLOOR_WG" and context.fluid not in (None, "minecraft:water"):
        findings.append(GeospatialFinding("warning", "OCEAN_HEIGHTMAP_WITHOUT_WATER", "Ocean-floor projection is declared without water context."))
    if purpose.kind in {"dock", "port", "wharf"} and not (context.fluid == "minecraft:water" or "coast" in context.terrain):
        findings.append(GeospatialFinding("error", "PORT_WITHOUT_WATER", "Port/dock purpose requires coastline or water adjacency."))
    if purpose.kind in {"rail_depot", "freight_terminal"}:
        kinds = {c.get("kind") for c in context.required_connectors}
        if "rail" not in kinds:
            findings.append(GeospatialFinding("warning", "FREIGHT_WITHOUT_RAIL", "Freight/rail purpose has no rail connector contract."))
    if context.y_min is not None and context.y_max is not None and context.y_min > context.y_max:
        findings.append(GeospatialFinding("error", "INVALID_Y_RANGE", "y_min exceeds y_max."))
    return findings

def clearance_dimensions(clearance: str) -> tuple[int, int]:
    return {
        "micro": (1, 1),
        "person": (1, 2),
        "public_circulation": (3, 3),
        "cart": (2, 3),
        "vehicle": (4, 4),
        "submersible": (5, 5),
        "industrial": (6, 6),
        "megastructure": (10, 8),
    }.get(clearance, (1, 2))
