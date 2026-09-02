from __future__ import annotations


def adapt_donjon_options(options: dict, *, cell_scale_blocks: int = 3, triple_fold: bool = True) -> dict:
    """Translate classic donjon dungeon.pl option vocabulary to native_modular_v1.

    This adapter contains no donjon implementation code. It exists so callers can
    migrate familiar option sets while adding Minecraft-specific modularity,
    purpose, scale, fitness and theming constraints.
    """
    if cell_scale_blocks < 1:
        raise ValueError("cell_scale_blocks must be positive")
    shape_map = {
        "none": "rectangle", "box": "ring", "cross": "cross", "round": "round",
    }
    corridor_map = {"straight": "straight", "bent": "bent", "labyrinth": "labyrinth"}
    room_map = {"packed": "packed", "scattered": "scattered"}

    layout_name = str(options.get("dungeon_layout", "None")).lower()
    corridor_name = str(options.get("corridor_layout", "Bent")).lower()
    room_name = str(options.get("room_layout", "Scattered")).lower()
    remove_deadends = int(options.get("remove_deadends", 50))
    dead_end_policy = "none" if remove_deadends >= 80 else "some" if remove_deadends >= 25 else "many"

    n_rows = max(9, int(options.get("n_rows", 39)))
    n_cols = max(9, int(options.get("n_cols", 39)))
    preferred_width = (n_cols - (n_cols % 2)) * cell_scale_blocks
    preferred_depth = (n_rows - (n_rows % 2)) * cell_scale_blocks
    meso = cell_scale_blocks
    macro = meso * 3

    room_min = max(1, int(options.get("room_min", 3)))
    room_max = max(room_min, int(options.get("room_max", 9)))
    return {
        "seed": int(options.get("seed", 0)),
        "layout_shape": shape_map.get(layout_name, "rectangle"),
        "room_layout": room_map.get(room_name, "scattered"),
        "corridor_style": corridor_map.get(corridor_name, "bent"),
        "dead_end_policy": dead_end_policy,
        "stair_count": max(0, int(options.get("add_stairs", 0))),
        "size": {
            "min_width": max(24, preferred_width // 2),
            "min_depth": max(24, preferred_depth // 2),
            "max_width": max(preferred_width, preferred_width * 2),
            "max_depth": max(preferred_depth, preferred_depth * 2),
            "preferred_width": preferred_width,
            "preferred_depth": preferred_depth,
        },
        "modularity": {
            "triple_fold": bool(triple_fold),
            "macro_module": macro,
            "meso_module": meso,
            "micro_module": 1,
            "connector_width": min(3, meso),
            "room_min_modules": room_min,
            "room_max_modules": room_max,
        },
        "metadata": {
            "compatibility_adapter": "donjon_option_vocabulary_v1",
            "classic_options": dict(options),
            "cell_scale_blocks": cell_scale_blocks,
        },
    }
