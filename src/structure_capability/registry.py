from __future__ import annotations
from dataclasses import dataclass, field

VANILLA_ROLE_DEFAULTS = {
    "foundation": ["minecraft:stone_bricks", "minecraft:deepslate_tiles"],
    "structural": ["minecraft:stone_bricks", "minecraft:bricks", "minecraft:polished_andesite"],
    "industrial_structural": ["minecraft:deepslate_tiles", "minecraft:iron_block", "minecraft:cut_copper"],
    "glass": ["minecraft:glass", "minecraft:tinted_glass"],
    "wood": ["minecraft:oak_planks", "minecraft:spruce_planks"],
    "metal": ["minecraft:iron_block", "minecraft:cut_copper", "minecraft:weathered_cut_copper"],
    "roof": ["minecraft:stone_brick_slab", "minecraft:deepslate_tile_slab"],
    "rail": ["minecraft:iron_bars"],
    "light": ["minecraft:lantern", "minecraft:sea_lantern", "minecraft:redstone_lamp"],
    "waterproof": ["minecraft:prismarine_bricks", "minecraft:dark_prismarine"],
    "geology_basaltic": ["minecraft:basalt", "minecraft:smooth_basalt", "minecraft:blackstone"],
    "sediment": ["minecraft:sand", "minecraft:gravel", "minecraft:clay", "minecraft:mud"],
}

@dataclass
class RegistryResolver:
    inventory: object | None = None
    role_defaults: dict[str, list[str]] = field(default_factory=lambda: dict(VANILLA_ROLE_DEFAULTS))

    def probe(self, registry_id: str, kind: str | None = None) -> dict:
        if registry_id.startswith("minecraft:"):
            return {"id": registry_id, "kind": kind, "level": "vanilla", "namespace_known": True, "evidence": ["minecraft namespace"]}
        if self.inventory and hasattr(self.inventory, "probe"):
            return self.inventory.probe(registry_id, kind=kind)
        return {"id": registry_id, "kind": kind, "level": "unknown", "namespace_known": False, "evidence": []}

    def verified(self, registry_id: str) -> bool:
        return self.probe(registry_id).get("level") != "unknown"

    def resolve(self, requested: str | None = None, role: str | None = None) -> str:
        if requested and self.verified(requested):
            return requested
        choices = self.role_defaults.get(role or "structural", ["minecraft:stone_bricks"])
        return choices[0]

    def resolve_palette(self, profile: dict[str, list[str]]) -> dict[str, str]:
        resolved = {}
        for role, candidates in profile.items():
            chosen = next((x for x in candidates if self.verified(x)), None)
            resolved[role] = chosen or self.resolve(role=role)
        return resolved
