from __future__ import annotations
import base64
from .structure_builder import StructureBuilder
from ..versioning import resolve_minecraft_version


def _build_open_mask(layout: dict) -> list[list[bool]]:
    grid = layout["grid"]
    module = int(layout["grid_module_blocks"])
    width, depth = map(int, layout["footprint_blocks"])
    corridor_width = int(layout.get("modularity", {}).get("connector_width", module))
    corridor_width = max(1, min(module, corridor_width))
    offset = (module - corridor_width) // 2
    end = offset + corridor_width
    mask = [[False for _ in range(width)] for _ in range(depth)]

    for gz, row in enumerate(grid):
        for gx, cell in enumerate(row):
            x0, z0 = gx * module, gz * module
            if cell == "R":
                for z in range(z0, z0 + module):
                    for x in range(x0, x0 + module):
                        mask[z][x] = True
                continue
            if cell != ".":
                continue
            for z in range(z0 + offset, z0 + end):
                for x in range(x0 + offset, x0 + end):
                    mask[z][x] = True
            neighbors = {
                "north": gz > 0 and grid[gz - 1][gx] in {"R", "."},
                "south": gz + 1 < len(grid) and grid[gz + 1][gx] in {"R", "."},
                "west": gx > 0 and row[gx - 1] in {"R", "."},
                "east": gx + 1 < len(row) and row[gx + 1] in {"R", "."},
            }
            if neighbors["north"]:
                for z in range(z0, z0 + end):
                    for x in range(x0 + offset, x0 + end): mask[z][x] = True
            if neighbors["south"]:
                for z in range(z0 + offset, z0 + module):
                    for x in range(x0 + offset, x0 + end): mask[z][x] = True
            if neighbors["west"]:
                for z in range(z0 + offset, z0 + end):
                    for x in range(x0, x0 + end): mask[z][x] = True
            if neighbors["east"]:
                for z in range(z0 + offset, z0 + end):
                    for x in range(x0 + offset, x0 + module): mask[z][x] = True
    return mask


def _compile_region(layout: dict, open_mask: list[list[bool]], *,
                    x0: int, x1: int, z0: int, z1: int,
                    floor_start: int, floor_end: int,
                    data_version: int, registry_resolver=None,
                    palette: dict | None = None) -> tuple[dict, bytes] | None:
    palette = dict(palette or {})
    floor_block = palette.get("floor", "minecraft:stone_bricks")
    wall_block = palette.get("wall", "minecraft:stone_bricks")
    roof_block = palette.get("roof", "minecraft:stone_brick_slab")
    floor_height = int(layout.get("floor_height", 5))
    region_w, region_d = x1 - x0, z1 - z0
    region_h = (floor_end - floor_start) * floor_height
    if not any(open_mask[z][x] for z in range(z0, z1) for x in range(x0, x1)):
        return None

    builder = StructureBuilder((region_w, region_h, region_d), data_version=data_version, registry_resolver=registry_resolver)
    global_depth, global_width = len(open_mask), len(open_mask[0])
    for global_floor in range(floor_start, floor_end):
        local_floor = global_floor - floor_start
        ly0 = local_floor * floor_height
        ly_roof = ly0 + floor_height - 1
        for gz in range(z0, z1):
            for gx in range(x0, x1):
                if not open_mask[gz][gx]:
                    continue
                lx, lz = gx - x0, gz - z0
                builder.set(lx, ly0, lz, floor_block)
                builder.set(lx, ly_roof, lz, roof_block)
                neighbors = ((gx,gz-1),(gx,gz+1),(gx-1,gz),(gx+1,gz))
                if any(nx < 0 or nz < 0 or nx >= global_width or nz >= global_depth or not open_mask[nz][nx] for nx,nz in neighbors):
                    for ly in range(ly0 + 1, ly_roof):
                        builder.set(lx, ly, lz, wall_block)

    data = builder.bytes()
    meta = {
        "size": [region_w, region_h, region_d],
        "offset": [x0, floor_start * floor_height, z0],
        "block_count": len(builder.blocks),
        "palette_entries": len(builder.palette),
        "git_blob_sha1": builder.git_blob_sha1(),
        "bytes": len(data),
    }
    return meta, data


def compile_dungeon_layout_artifacts(layout: dict, *, target_version: str = "1.20.1",
                                     data_version: int | None = None, registry_resolver=None,
                                     palette: dict | None = None,
                                     materialization_mode: str = "auto",
                                     piece_limit: int | None = None,
                                     allow_oversize_nbt: bool = False,
                                     emit_binary: bool = False) -> tuple[dict, dict[str, bytes]]:
    """Compile a layout into one or more deterministic Minecraft structure NBTs.

    `auto` honors the vanilla structure-block size cap for the target family and
    fragments larger structures on meso-module boundaries. `single` refuses an
    oversized template unless allow_oversize_nbt is explicitly enabled.
    """
    version = resolve_minecraft_version(target_version)
    if not version.namespaced_ids:
        raise ValueError("Native NBT materialization currently requires Minecraft 1.13+; 1.12.x layout generation is supported but needs the legacy palette adapter")
    resolved_data_version = data_version if data_version is not None else version.data_version
    if resolved_data_version is None:
        raise ValueError("No verified DataVersion is bundled for this target; provide generation.data_version explicitly")
    mode = str(materialization_mode or "auto").lower()
    if mode not in {"auto", "single", "fragmented"}:
        raise ValueError("materialization_mode must be auto, single, or fragmented")

    width, depth = map(int, layout["footprint_blocks"])
    floor_height = int(layout.get("floor_height", 5))
    floors = int(layout.get("floors", 1))
    height = floors * floor_height
    limit = int(piece_limit or version.structure_block_limit)
    if limit < 8:
        raise ValueError("piece_limit must be at least 8 blocks")
    oversize = max(width, height, depth) > limit
    if mode == "single" and oversize and not allow_oversize_nbt:
        raise ValueError(f"Structure size {[width,height,depth]} exceeds the target vanilla structure-block limit of {limit}; use materialization_mode=fragmented/auto or explicitly allow oversize NBT")
    fragmented = mode == "fragmented" or (mode == "auto" and oversize)

    open_mask = _build_open_mask(layout)
    meso = int(layout["grid_module_blocks"])
    span = (limit // meso) * meso
    if span < meso:
        raise ValueError("piece_limit is smaller than the meso module")
    floors_per_piece = max(1, limit // floor_height)

    x_ranges = [(0,width)] if not fragmented else [(x,min(width,x+span)) for x in range(0,width,span)]
    z_ranges = [(0,depth)] if not fragmented else [(z,min(depth,z+span)) for z in range(0,depth,span)]
    f_ranges = [(0,floors)] if not fragmented else [(f,min(floors,f+floors_per_piece)) for f in range(0,floors,floors_per_piece)]

    pieces = []
    artifacts: dict[str, bytes] = {}
    index = 0
    for f0,f1 in f_ranges:
        for z0,z1 in z_ranges:
            for x0,x1 in x_ranges:
                compiled = _compile_region(
                    layout, open_mask, x0=x0, x1=x1, z0=z0, z1=z1,
                    floor_start=f0, floor_end=f1, data_version=resolved_data_version,
                    registry_resolver=registry_resolver, palette=palette,
                )
                if compiled is None:
                    continue
                meta, data = compiled
                name = f"piece_{index:03d}_x{x0}_y{f0*floor_height}_z{z0}.nbt"
                meta["name"] = name
                if emit_binary:
                    meta["nbt_base64"] = base64.b64encode(data).decode("ascii")
                pieces.append(meta)
                artifacts[name] = data
                index += 1

    if not pieces:
        raise ValueError("Layout materialization produced no non-empty pieces")
    resolved_palette = dict(palette or {})
    resolved_palette = {
        "floor": resolved_palette.get("floor", "minecraft:stone_bricks"),
        "wall": resolved_palette.get("wall", "minecraft:stone_bricks"),
        "roof": resolved_palette.get("roof", "minecraft:stone_brick_slab"),
    }
    aggregate = {
        "format": "minecraft_structure_nbt_piece_set" if len(pieces) > 1 else "minecraft_structure_nbt_gzip",
        "materialization_mode": "fragmented" if len(pieces) > 1 else "single",
        "target_version": version.to_dict(),
        "data_version": resolved_data_version,
        "overall_size": [width, height, depth],
        "piece_limit_blocks": limit,
        "piece_count": len(pieces),
        "pieces": pieces,
        "palette": resolved_palette,
        "connector_width_blocks": int(layout.get("modularity", {}).get("connector_width", layout["grid_module_blocks"])),
        "assembly": {
            "type": "fixed_offsets",
            "origin": [0,0,0],
            "note": "Pieces preserve global openings at shared boundaries. A later jigsaw/worldgen provider may convert these offsets into runtime assembly rules.",
        },
        "authoring_level": "architectural_skeleton",
    }
    return aggregate, artifacts


def compile_dungeon_layout_artifact(layout: dict, *, target_version: str = "1.20.1",
                                    data_version: int | None = None, registry_resolver=None,
                                    palette: dict | None = None) -> tuple[dict, bytes]:
    """Backward-compatible single-artifact helper for callers with in-limit layouts."""
    aggregate, artifacts = compile_dungeon_layout_artifacts(
        layout, target_version=target_version, data_version=data_version,
        registry_resolver=registry_resolver, palette=palette,
        materialization_mode="single", allow_oversize_nbt=True,
    )
    if len(artifacts) != 1:
        raise ValueError("single artifact helper unexpectedly produced multiple pieces")
    name, data = next(iter(artifacts.items()))
    piece = aggregate["pieces"][0]
    legacy = {
        "format": "minecraft_structure_nbt_gzip",
        "target_version": aggregate["target_version"],
        "data_version": aggregate["data_version"],
        "size": piece["size"],
        "block_count": piece["block_count"],
        "palette_entries": piece["palette_entries"],
        "git_blob_sha1": piece["git_blob_sha1"],
        "bytes": piece["bytes"],
        "palette": aggregate["palette"],
        "connector_width_blocks": aggregate["connector_width_blocks"],
        "authoring_level": aggregate["authoring_level"],
    }
    return legacy, data


def compile_dungeon_layout(layout: dict, *, target_version: str = "1.20.1",
                           data_version: int | None = None, registry_resolver=None,
                           palette: dict | None = None, emit_binary: bool = False) -> dict:
    result, data = compile_dungeon_layout_artifact(
        layout, target_version=target_version, data_version=data_version,
        registry_resolver=registry_resolver, palette=palette,
    )
    if emit_binary:
        result["nbt_base64"] = base64.b64encode(data).decode("ascii")
    return result
