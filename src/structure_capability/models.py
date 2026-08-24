from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
from .grading import RebuildGrade

class PhysicalClearance(str, Enum):
    MICRO = "micro"
    PERSON = "person"
    PUBLIC_CIRCULATION = "public_circulation"
    CART = "cart"
    VEHICLE = "vehicle"
    SUBMERSIBLE = "submersible"
    INDUSTRIAL = "industrial"
    MEGASTRUCTURE = "megastructure"

class AccessClearance(str, Enum):
    PUBLIC = "public"
    STAFF = "staff"
    CONTROLLED = "controlled"
    RESTRICTED = "restricted"
    SECURE = "secure"
    BLACKSITE = "blacksite"

@dataclass
class SiteContext:
    dimension: str = "minecraft:overworld"
    biomes: list[str] = field(default_factory=list)
    biome_tags: list[str] = field(default_factory=list)
    terrain: str = "unknown"
    fluid: str | None = None
    sea_level: int | None = None
    y_min: int | None = None
    y_max: int | None = None
    slope_class: str | None = None
    climate: dict[str, Any] = field(default_factory=dict)
    orientation: str | None = None
    approach_vectors: list[str] = field(default_factory=list)
    required_connectors: list[dict[str, Any]] = field(default_factory=list)
    nearby_features: list[str] = field(default_factory=list)
    exclusion_zones: list[dict[str, Any]] = field(default_factory=list)
    protected_regions: list[dict[str, Any]] = field(default_factory=list)
    placement: dict[str, Any] = field(default_factory=dict)

@dataclass
class PurposeProfile:
    kind: str = "unspecified"
    original_function: str | None = None
    current_function: str | None = None
    required_zones: list[str] = field(default_factory=list)
    required_routes: list[str] = field(default_factory=list)
    required_utilities: list[str] = field(default_factory=list)
    required_exterior: list[str] = field(default_factory=list)
    forbidden_features: list[str] = field(default_factory=list)

@dataclass
class ThemeProfile:
    name: str = "neutral"
    culture: str | None = None
    institution: str | None = None
    palette_roles: dict[str, list[str]] = field(default_factory=dict)
    silhouette_rules: list[str] = field(default_factory=list)
    facade_rules: list[str] = field(default_factory=list)
    interior_rules: list[str] = field(default_factory=list)
    technology_language: list[str] = field(default_factory=list)
    damage_language: list[str] = field(default_factory=list)
    signage_language: list[str] = field(default_factory=list)
    forbidden_assets: list[str] = field(default_factory=list)

@dataclass
class StructureRequest:
    structure_id: str
    structure_type: str = "building"
    target_version: str = "1.20.1"
    scale: float = 1.0
    operation: str = "plan"
    grade: RebuildGrade = RebuildGrade.AUDIT_ONLY
    source: str | None = None
    purpose: PurposeProfile = field(default_factory=PurposeProfile)
    theme: ThemeProfile = field(default_factory=ThemeProfile)
    context: SiteContext = field(default_factory=SiteContext)
    physical_clearance: PhysicalClearance = PhysicalClearance.PERSON
    access_clearance: AccessClearance = AccessClearance.PUBLIC
    preserve: list[str] = field(default_factory=list)
    mutable: list[str] = field(default_factory=list)
    integration_contracts: dict[str, Any] = field(default_factory=dict)
    generation: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StructureRequest":
        return cls(
            structure_id=d["structure_id"],
            structure_type=str(d.get("structure_type", "building")),
            target_version=str(d.get("target_version", "1.20.1")),
            scale=float(d.get("scale", 1.0)),
            operation=d.get("operation", "plan"),
            grade=RebuildGrade.parse(d.get("grade", d.get("operation", 0) if isinstance(d.get("operation"), int) else 0)),
            source=d.get("source"),
            purpose=PurposeProfile(**d.get("purpose", {})),
            theme=ThemeProfile(**d.get("theme", {})),
            context=SiteContext(**d.get("context", {})),
            physical_clearance=PhysicalClearance(d.get("physical_clearance", "person")),
            access_clearance=AccessClearance(d.get("access_clearance", "public")),
            preserve=list(d.get("preserve", [])),
            mutable=list(d.get("mutable", [])),
            integration_contracts=dict(d.get("integration_contracts", {})),
            generation=dict(d.get("generation", {})),
            metadata=dict(d.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["grade"] = int(self.grade)
        out["physical_clearance"] = self.physical_clearance.value
        out["access_clearance"] = self.access_clearance.value
        return out
