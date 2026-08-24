# Local Mod Awareness and Adaptability

## Discovery sources

The default inventory scanner checks:
- `mods/*.jar`;
- NeoForge/Forge metadata (`META-INF/neoforge.mods.toml`, `META-INF/mods.toml`);
- Fabric metadata (`fabric.mod.json`);
- `data/<namespace>/...`;
- `assets/<namespace>/...`.

Projects may supplement exact registry IDs from generated registry dumps, game reports, KubeJS exports, data generators or project manifests.

## Registry safety

A namespace's presence proves only that the namespace exists. It does **not** prove a guessed block/item/entity exists. Therefore exact modded IDs should be supplied by a stronger registry provider whenever placement depends on them.

Policy:
1. exact verified ID available → use it;
2. no exact ID, but role can be represented in vanilla → use vanilla role fallback;
3. no safe fallback → mark capability requirement unresolved;
4. never invent an ID from a mod name.

## Capability-driven theming

Themes specify **roles** before block IDs:
- exterior structural;
- frame;
- glazing;
- waterproof skin;
- high-security wall;
- service pipe;
- power;
- light;
- floor;
- signage;
- damage material.

The registry resolver maps roles to verified local materials.

This allows the same cultural design to survive different modpacks without becoming a palette-swapped clone.
