# Tool selection — current published capability

**Do not treat this list as a frozen schema.** First confirm the executing service and fetch `GET /v1/tools/index`, then `GET /v1/tools/{tool_name}` or `GET /v1/tools` for current input schemas and publication metadata. The documented catalog schema version 1.4 contains 18 tools.

| Need | Published tool |
| --- | --- |
| Identity, available features | `structure_capabilities` |
| Scan project artifacts and registries | `structure_inventory` |
| Inspect an existing structure | `structure_audit` |
| Plan a context-sensitive rebuild | `structure_plan` |
| Generate or refit structures | `structure_generate` |
| Purpose-fit modular dungeon layout | `dungeon_layout` |
| Roads, highways, civic and industrial layouts | `infrastructure_layout` |
| Aerospace support campus | `aerospace_support_campus_generate` |
| Minecraft release formats and metadata | `minecraft_version` |
| Verify vanilla/mod registry IDs | `minecraft_registry_probe` |
| Written Minecraft books | `minecraft_book_generate` |
| Version-correct loot tables | `minecraft_loot_table_generate` |
| Shaped, shapeless, cooking, stonecutting recipes | `minecraft_recipe_generate` |
| Advancements | `minecraft_advancement_generate` |
| Item/block/fluid/entity/function/game event tags | `minecraft_tag_generate` |
| Datapack manifests | `minecraft_datapack_manifest_generate` |
| Compose structure and content artifacts | `minecraft_content_package_generate` |
| Semantic item icons or lightweight SVG fallback | `minecraft_icon_assign` |

## Routing

Use the **canonical endpoint** and HTTP method published for each tool under `x-continuity-works-tool`; source authority is `structure_capability.publication.PUBLIC_CAPABILITIES`. `POST /v1/resolve` is a discovery/selection helper, not permission to invent a route. `/openapi.json` is authoritative for request and response validation. Do not infer endpoints by snake-case conversion.

Recommended progression:

1. `GET /v1/health`: verify identity, service health, and build where supplied.
2. `GET /v1/tools/index`: shortlist the smallest relevant operation.
3. `GET /v1/tools/{tool_name}`: get the chosen tool schema.
4. Optionally retrieve a preset and resolve version/mod constraints.
5. Invoke the **exact** published endpoint with schema-valid arguments.
6. Inspect explicit gate results and emitted artifacts. If blocked, repair the cause rather than bypass the gate.

Use a local `StructureCapability(project_root=...)` when running Python directly. Refer to [API reference](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/API.md), [content authoring](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/MINECRAFT_CONTENT_API_TOOLS.md), and [public serviceability](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/PUBLIC_SERVICEABILITY.md) for detailed contracts.

### Example of a documented route

```http
POST /v1/infrastructure/layout
Content-Type: application/json

{
  "module_type": "inner_city_road",
  "seed": 9001,
  "world_seed": 20260824,
  "road": {"width": 6, "terrain_padding": 5},
  "purpose": {"depth": 3}
}
```

The hard city-road module is 5 blocks of integration padding + 6 roadbed + 5 padding. Do not treat the sample as the schema for every infrastructure type.
