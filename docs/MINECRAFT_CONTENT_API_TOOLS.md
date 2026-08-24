# Minecraft Content API Tools

StructureSmith exposes books, loot tables, recipes, registry probing, and icon assignment as deliberate AI/tool-calling capabilities rather than helper snippets. They are reachable through the portable `/v1/tools` catalog and direct HTTP endpoints.

## Design contract

Every content authoring call accepts a Minecraft Java target version and returns an artifact plus a deterministic `gate` report. Gates expose stable reason codes for version resolution, registry-ID confidence, feature support, packaging layout, and output limits. They are deliberately inspectable validation logic; they do **not** expose or depend on hidden chain-of-thought.

Mod awareness is local-first. StructureSmith scans installed Forge/NeoForge/Fabric JAR metadata, namespaces, datapack/resource-pack trees, recipes, loot tables, structure definitions, item tags, and item model/texture candidates. A non-vanilla resource ID can therefore be classified as `exact`, `candidate`, `namespace`, or `unknown`. Callers choose `id_policy: strict | namespace | permissive` to decide whether namespace-only or unknown IDs block materialization.

## Tools and endpoints

| Tool | Endpoint | Purpose |
| --- | --- | --- |
| `minecraft_registry_probe` | `POST /v1/minecraft/registry/probe` | Validate a vanilla/modded resource location against the scanned project. |
| `minecraft_book_generate` | `POST /v1/minecraft/book` | Assemble a written-book item payload. |
| `minecraft_loot_table_generate` | `POST /v1/minecraft/loot-table` | Materialize weighted and guaranteed loot pools. |
| `minecraft_recipe_generate` | `POST /v1/minecraft/recipe` | Materialize shaped, shapeless, cooking, and stonecutting recipes. |
| `minecraft_icon_assign` | `POST /v1/minecraft/icon` | Assign a semantic Minecraft item icon or deterministic SVG fallback. |

## Version adaptation

The content layer treats format changes as explicit compatibility boundaries.

- Written books before 1.20.5 emit the legacy title/author/pages NBT-shaped payload. Minecraft 1.20.5+ emits `minecraft:written_book_content` in the item component map.
- Recipe result item stacks switch to the component-capable 1.20.5+ item-stack representation. Cooking recipes also switch from a plain result ID to an item-stack object on that boundary.
- Minecraft 1.21+ uses singular datapack resource folders such as `recipe` and `loot_table`; earlier datapack versions use `recipes` and `loot_tables`.
- Minecraft 1.21.2+ recipe ingredients use the simplified item/tag representation. Earlier recipes retain the legacy `{item: ...}` / `{tag: ...}` form.
- Custom recipe datapack generation is gated out for pre-1.13 targets rather than fabricating compatibility.

The generator is conservative: advanced loot predicates/functions, custom recipe serializers, and loader-specific recipe types remain provider-extension territory until a provider explicitly declares and validates them.

## Icon assignment

The tool catalog includes StructureSmith extension metadata describing a semantic icon and a vanilla fallback item for each deliberate tool. Runtime icon assignment prefers a discoverable Minecraft item ID. When an item icon cannot be established, the API returns a deterministic lightweight SVG badge generated from the semantic subject and short label. This provides a no-network fallback without pretending to author detailed texture art.

## Example: guaranteed evidence loot

```json
{
  "target_version": "1.20.1",
  "table_id": "infinite_domain:chests/atlas_evidence",
  "items": [
    {"id": "minecraft:iron_ingot", "weight": 5, "min_count": 1, "max_count": 3}
  ],
  "guaranteed": [
    {"id": "minecraft:paper", "count": 1}
  ],
  "id_policy": "namespace"
}
```

The guaranteed item is emitted into its own one-roll pool, so it is not merely given a high weight; it is structurally guaranteed by the generated table.
