# Minecraft Content API Tools

StructureSmith exposes Minecraft content authoring as deliberate AI/tool-calling capabilities rather than helper snippets. The content layer now covers registry probing, written books, loot tables, recipes, advancements, tags, datapack manifests, semantic icons, and a package composer that can call the authoritative structure generator and return linked structure/content artifacts under one aggregate gate.

## Design contract

Every content authoring call accepts a Minecraft Java target version and returns an artifact plus a deterministic `gate` report. Gates expose stable reason codes for version resolution, registry-ID confidence, feature support, packaging layout, linking, and materialization. They are deliberately inspectable validation logic; they do **not** expose or depend on hidden chain-of-thought.

Mod awareness is local-first. StructureSmith scans installed Forge/NeoForge/Fabric JAR metadata, namespaces, datapack/resource-pack trees, recipes, loot tables, structure definitions, item tags, and item model/texture candidates. A non-vanilla resource ID can therefore be classified as `exact`, `candidate`, `namespace`, or `unknown`. Callers choose `id_policy: strict | namespace | permissive` to decide whether namespace-only or unknown IDs block materialization.

## Tools and endpoints

| Tool | Endpoint | Purpose |
| --- | --- | --- |
| `minecraft_registry_probe` | `POST /v1/minecraft/registry/probe` | Validate a vanilla/modded resource location against the scanned project. |
| `minecraft_book_generate` | `POST /v1/minecraft/book` | Assemble a written-book item payload and loot-compatible representation. |
| `minecraft_loot_table_generate` | `POST /v1/minecraft/loot-table` | Materialize weighted and guaranteed loot pools, including version-aware item data. |
| `minecraft_recipe_generate` | `POST /v1/minecraft/recipe` | Materialize shaped, shapeless, cooking, and stonecutting recipes. |
| `minecraft_advancement_generate` | `POST /v1/minecraft/advancement` | Materialize criteria, display metadata, rewards, and version-aware advancement paths/icons. |
| `minecraft_tag_generate` | `POST /v1/minecraft/tag` | Materialize item/block/fluid/entity/function/game-event tags with version-aware directories. |
| `minecraft_datapack_manifest_generate` | `POST /v1/minecraft/datapack-manifest` | Generate a gated `pack.mcmeta` without guessing an unknown pack format. |
| `minecraft_content_package_generate` | `POST /v1/minecraft/content-package` | Compose structure and content artifacts, cross-link them, and return one aggregate gate. |
| `minecraft_icon_assign` | `POST /v1/minecraft/icon` | Assign a semantic Minecraft item icon or deterministic SVG fallback. |

The portable `/v1/tools` catalog is schema version **1.3** and exposes 17 deliberate tools in total, including the existing structure, dungeon, infrastructure, and Minecraft-version capabilities.

## Version adaptation

The content layer treats format changes as explicit compatibility boundaries.

- Written books before 1.20.5 emit legacy title/author/pages NBT-shaped data. Minecraft 1.20.5+ emits `minecraft:written_book_content` in the item component map.
- The old 100-page written-book ceiling is enforced only before 1.20.5. Minecraft 1.20.5+ is not falsely rejected by that obsolete limit.
- A generated book also returns a loot-compatible item description. Before 1.20.5 that uses legacy SNBT; on 1.20.5+ it carries item components.
- Loot entries can therefore materialize legacy custom NBT with `minecraft:set_nbt` on older targets or item components with `minecraft:set_components` on 1.20.5+.
- Recipe result item stacks switch to the component-capable 1.20.5+ item-stack representation. Cooking recipes also switch from a plain result ID to an item-stack object on that boundary.
- Advancement display icons switch from the older `item` field to the 1.20.5+ item-stack `id` representation.
- Minecraft 1.21+ uses singular datapack resource folders such as `advancement`, `recipe`, `loot_table`, and singular tag registry directories such as `tags/item` and `tags/function`.
- Minecraft 1.21.2+ recipe ingredients use the simplified item/tag representation. Earlier recipes retain the legacy `{item: ...}` / `{tag: ...}` form.
- Custom recipe and tag datapack generation is gated out for pre-1.13 targets rather than fabricating compatibility.

Exact release metadata now includes Minecraft Java 1.20.5 with DataVersion 3837, resource-pack format 32, and data-pack format 41. Unknown patch versions are still never assigned guessed release metadata.

## Advancements

`minecraft_advancement_generate` deliberately exposes the advancement pieces that other generated systems need:

- one or more named criteria with explicit triggers and optional conditions;
- optional parent advancement;
- optional display title, description, frame, icon, visibility, toast/chat behavior, and background;
- optional requirements matrix;
- rewards for experience, loot tables, recipes, or a function;
- optional telemetry flag;
- version-aware output path and icon representation.

An advancement with no criteria fails `ADVANCEMENT_CRITERIA_EMPTY` instead of emitting a knowingly unusable artifact.

## Tags

`minecraft_tag_generate` currently supports the datapack registries most useful to content composition:

`item`, `block`, `fluid`, `entity_type`, `function`, and `game_event`.

Values may be direct resource IDs, `#other:tag` references, or `{ "id": "...", "required": false }` objects. Item tags receive the same mod-aware ID confidence checks as other item-bearing content.

## Datapack manifest

`minecraft_datapack_manifest_generate` emits `pack.mcmeta`. If StructureSmith has exact metadata for the requested release, the data-pack format is selected from that release profile. If it does not, the caller must provide `pack_format`; StructureSmith fails `DATAPACK_FORMAT_UNKNOWN` rather than guessing.

This keeps a package's machine-readable compatibility claim separate from the looser ability to draft version-neutral content.

## Content package composition

`minecraft_content_package_generate` is the composition boundary for higher-level AI callers. A single request can contain:

- an optional full `structure` request, dispatched through the existing authoritative `StructureCapability.generate()` path;
- books;
- loot tables;
- recipes;
- advancements;
- tags;
- datapack-manifest settings;
- typed cross-artifact bindings.

The first supported binding is `book_as_guaranteed_loot`. It resolves a named generated book to a named generated loot table and injects the book into its own one-roll pool. This is specifically suitable for evidence books, quest logs, laboratory notes, and other items that must not disappear because of weighted RNG.

Example:

```json
{
  "package_id": "infinite_domain:atlas/ows_009",
  "target_version": "1.20.5",
  "books": [
    {
      "name": "evidence",
      "title": "Containment Log",
      "author": "Atlas",
      "pages": ["Entry one", "Entry two"]
    }
  ],
  "loot_tables": [
    {
      "name": "evidence_chest",
      "items": [
        {"id": "minecraft:iron_ingot", "weight": 4}
      ]
    }
  ],
  "bindings": [
    {
      "type": "book_as_guaranteed_loot",
      "book": "evidence",
      "loot_table": "evidence_chest"
    }
  ]
}
```

The response contains grouped child artifacts, a file manifest, resolved links, and an aggregate package gate. A failed child artifact fails the package; warnings remain visible as package warnings. `link_policy: strict` makes broken or missing bindings fail the package, while `warn` can be used during incomplete authoring passes.

When a `structure` request is included, the API does **not** create a second structure implementation. It calls the same authoritative generation/provider/snapshot path used by `structure_generate`, then attaches that result to the content package.

## Icon assignment

The tool catalog includes StructureSmith extension metadata describing a semantic icon and a vanilla fallback item for each deliberate tool. Runtime icon assignment prefers a discoverable Minecraft item ID. When an item icon cannot be established, the API returns a deterministic lightweight SVG badge generated from the semantic subject and short label. This provides a no-network fallback without pretending to author detailed texture art.

## Materialization boundary

The package composer is deliberately not a blanket claim that every possible mod serializer, loot predicate, advancement trigger condition, or command syntax is supported. Advanced loader-specific recipe serializers, arbitrary custom registry codecs, and command/function generation remain provider-extension territory until they have their own explicit version matrix and validation gates.
