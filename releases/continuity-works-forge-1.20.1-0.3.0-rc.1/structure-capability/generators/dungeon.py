from __future__ import annotations
from dataclasses import dataclass, field, asdict
from collections import deque
from math import ceil, gcd
import random
from typing import Any


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else max(a, b)


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def _quantize_up(n: int, q: int) -> int:
    return int(ceil(n / q) * q)

def _quantize_within(preferred: int, lo: int, hi: int, q: int) -> int | None:
    q = max(1, int(q))
    up = _quantize_up(preferred, q)
    if lo <= up <= hi:
        return up
    down = (preferred // q) * q
    if lo <= down <= hi:
        return down
    minimum = _quantize_up(lo, q)
    return minimum if minimum <= hi else None


PURPOSE_DEFAULTS: dict[str, dict[str, Any]] = {
    "generic_dungeon": {
        "min_footprint": [32, 32], "max_footprint": [160, 160],
        "zones": ["entry", "circulation", "encounter", "reward"], "room_count": [6, 18],
    },
    "crypt": {
        "min_footprint": [28, 28], "max_footprint": [128, 128],
        "zones": ["entry", "burial", "ritual", "guardian", "reward"], "room_count": [5, 14],
    },
    "fortress": {
        "min_footprint": [48, 48], "max_footprint": [192, 192],
        "zones": ["entry", "defense", "barracks", "command", "storage"], "room_count": [8, 24],
    },
    "laboratory": {
        "min_footprint": [40, 32], "max_footprint": [160, 128],
        "zones": ["entry", "reception", "laboratory", "utilities", "storage", "secure_core"], "room_count": [7, 20],
    },
    "warehouse": {
        "min_footprint": [48, 32], "max_footprint": [192, 160],
        "zones": ["entry", "loading", "storage", "service", "office"], "room_count": [5, 14],
    },
    "temple": {
        "min_footprint": [36, 36], "max_footprint": [160, 160],
        "zones": ["entry", "processional", "assembly", "sanctum", "service"], "room_count": [5, 16],
    },
    "residence": {
        "min_footprint": [20, 20], "max_footprint": [96, 96],
        "zones": ["entry", "living", "sleeping", "service", "storage"], "room_count": [4, 12],
    },
}


@dataclass
class SizeConstraints:
    min_width: int = 24
    min_depth: int = 24
    max_width: int = 160
    max_depth: int = 160
    preferred_width: int | None = None
    preferred_depth: int | None = None
    floors: int = 1
    floor_height: int = 5


@dataclass
class ModularityProfile:
    triple_fold: bool = True
    macro_module: int = 12
    meso_module: int = 4
    micro_module: int = 1
    connector_width: int = 3
    room_min_modules: int = 2
    room_max_modules: int = 5
    allow_repetition: bool = True
    allow_mirroring: bool = True
    allow_rotation: bool = True

    def quantum(self) -> int:
        values = [self.meso_module, self.micro_module]
        if self.triple_fold:
            values.append(self.macro_module)
        q = 1
        for value in values:
            q = _lcm(q, max(1, int(value)))
        return q


@dataclass
class DungeonLayoutRequest:
    seed: int = 0
    purpose: str = "generic_dungeon"
    size: SizeConstraints = field(default_factory=SizeConstraints)
    modularity: ModularityProfile = field(default_factory=ModularityProfile)
    required_zones: list[str] = field(default_factory=list)
    room_count: int | None = None
    scale: float = 1.0
    layout_shape: str = "rectangle"
    room_layout: str = "scattered"
    corridor_style: str = "bent"
    dead_end_policy: str = "some"
    verticality: str = "flat"
    stair_count: int = 0
    theme: dict[str, Any] = field(default_factory=dict)
    purpose_constraints: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DungeonLayoutRequest":
        size = SizeConstraints(**data.get("size", {}))
        modularity = ModularityProfile(**data.get("modularity", {}))
        return cls(
            seed=int(data.get("seed", 0)),
            purpose=str(data.get("purpose", "generic_dungeon")),
            size=size,
            modularity=modularity,
            required_zones=list(data.get("required_zones", [])),
            room_count=data.get("room_count"),
            scale=float(data.get("scale", 1.0)),
            layout_shape=str(data.get("layout_shape", "rectangle")).lower(),
            room_layout=str(data.get("room_layout", "scattered")).lower(),
            corridor_style=str(data.get("corridor_style", "bent")).lower(),
            dead_end_policy=str(data.get("dead_end_policy", "some")).lower(),
            verticality=str(data.get("verticality", "flat")),
            stair_count=max(0, int(data.get("stair_count", 0))),
            theme=dict(data.get("theme", {})),
            purpose_constraints=dict(data.get("purpose_constraints", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self):
        return asdict(self)


class DungeonGenerator:
    """Original, dependency-free dungeon layout generator.

    The engine deliberately uses generic room packing and Manhattan routing rather
    than copying donjon's CC BY-NC implementation. The upstream source can be kept
    as an isolated reference/optional provider without imposing its license on this
    native engine.
    """

    def generate(self, request: DungeonLayoutRequest | dict[str, Any]) -> dict[str, Any]:
        req = request if isinstance(request, DungeonLayoutRequest) else DungeonLayoutRequest.from_dict(request)
        if not 0.25 <= req.scale <= 4.0:
            raise ValueError("scale must be between 0.25 and 4.0")
        if req.corridor_style not in {"straight", "bent", "labyrinth"}:
            raise ValueError("corridor_style must be straight, bent, or labyrinth")
        if req.layout_shape not in {"rectangle", "cross", "round", "ring"}:
            raise ValueError("layout_shape must be rectangle, cross, round, or ring")
        if req.room_layout not in {"scattered", "packed"}:
            raise ValueError("room_layout must be scattered or packed")
        if req.dead_end_policy not in {"many", "some", "none"}:
            raise ValueError("dead_end_policy must be many, some, or none")

        purpose = dict(PURPOSE_DEFAULTS.get(req.purpose, PURPOSE_DEFAULTS["generic_dungeon"]))
        purpose.update(req.purpose_constraints)
        self._validate_purpose_profile(purpose)
        size, size_resolution = self._resolve_size(req, purpose)
        module = req.modularity.meso_module
        grid_w, grid_d = max(5, size[0] // module), max(5, size[1] // module)
        rng = random.Random(req.seed)
        grid = [["#" for _ in range(grid_w)] for _ in range(grid_d)]
        self._apply_layout_mask(grid, req.layout_shape)

        purpose_min_rooms, purpose_max_rooms = purpose["room_count"]
        target = req.room_count or int(round(((purpose_min_rooms + purpose_max_rooms) / 2) * req.scale))
        if req.room_layout == "packed" and req.room_count is None:
            target = int(round(target * 1.2))
        target = _clamp(target, 3, max(3, (grid_w * grid_d) // 8))
        rooms = self._place_rooms(rng, grid, target, req.modularity, req.room_layout)
        if len(rooms) < 2:
            raise ValueError("Resolved footprint is too small to place a usable dungeon under current modularity constraints")

        required_zones = list(dict.fromkeys(req.required_zones or purpose["zones"]))
        self._assign_zones(rooms, required_zones)
        corridors = self._connect_rooms(rng, grid, rooms, req.corridor_style, req.dead_end_policy)
        doors = self._derive_doors(grid, rooms)
        stairs = self._derive_stairs(rooms, req.size.floors, req.verticality, req.stair_count)
        layout = {
            "engine": "native_modular_v1",
            "seed": req.seed,
            "purpose": req.purpose,
            "layout_shape": req.layout_shape,
            "room_layout": req.room_layout,
            "corridor_style": req.corridor_style,
            "dead_end_policy": req.dead_end_policy,
            "purpose_constraints": req.purpose_constraints,
            "theme": req.theme,
            "metadata": req.metadata,
            "footprint_blocks": [grid_w * module, grid_d * module],
            "floors": req.size.floors,
            "floor_height": req.size.floor_height,
            "grid_module_blocks": module,
            "grid_size": [grid_w, grid_d],
            "modularity": {
                **asdict(req.modularity),
                "resolved_quantum": req.modularity.quantum(),
                "layers": {
                    "macro": "site/program composition",
                    "meso": "rooms/circulation",
                    "micro": "block/detail construction",
                },
            },
            "size_resolution": size_resolution,
            "required_zones": required_zones,
            "rooms": rooms,
            "corridors": corridors,
            "doors": doors,
            "stairs": stairs,
            "grid": ["".join(row) for row in grid],
        }
        layout["fitness"] = evaluate_dungeon_layout(layout, req)
        return layout

    def _apply_layout_mask(self, grid, shape):
        if shape == "rectangle":
            return
        h, w = len(grid), len(grid[0])
        cx, cz = (w - 1) / 2.0, (h - 1) / 2.0
        rx, rz = max(1.0, w / 2.0), max(1.0, h / 2.0)
        for z in range(h):
            for x in range(w):
                nx, nz = abs(x - cx) / rx, abs(z - cz) / rz
                keep = True
                if shape == "round":
                    keep = (nx * nx + nz * nz) <= 0.90
                elif shape == "cross":
                    keep = nx <= 0.34 or nz <= 0.34
                elif shape == "ring":
                    r2 = nx * nx + nz * nz
                    keep = 0.20 <= r2 <= 0.92
                if not keep:
                    grid[z][x] = "X"

    def _validate_purpose_profile(self, purpose):
        for key in ("min_footprint", "max_footprint", "room_count"):
            value = purpose.get(key)
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError(f"purpose constraint {key} must contain exactly two integers")
        if int(purpose["min_footprint"][0]) > int(purpose["max_footprint"][0]) or int(purpose["min_footprint"][1]) > int(purpose["max_footprint"][1]):
            raise ValueError("purpose min_footprint cannot exceed max_footprint")
        if int(purpose["room_count"][0]) > int(purpose["room_count"][1]):
            raise ValueError("purpose room_count minimum cannot exceed maximum")
        if "zones" not in purpose or not isinstance(purpose["zones"], list):
            raise ValueError("purpose constraint zones must be a list")

    def _resolve_size(self, req, purpose):
        pmin_w, pmin_d = purpose["min_footprint"]
        pmax_w, pmax_d = purpose["max_footprint"]
        s = req.size
        minimum_w = max(s.min_width, int(round(pmin_w * req.scale)))
        minimum_d = max(s.min_depth, int(round(pmin_d * req.scale)))
        maximum_w = min(s.max_width, max(minimum_w, int(round(pmax_w * req.scale))))
        maximum_d = min(s.max_depth, max(minimum_d, int(round(pmax_d * req.scale))))
        if maximum_w < minimum_w or maximum_d < minimum_d:
            raise ValueError("Explicit size constraints conflict with purpose/scale constraints")
        preferred_w = s.preferred_width or minimum_w
        preferred_d = s.preferred_depth or minimum_d
        quantum = req.modularity.quantum()
        preferred_w = _clamp(preferred_w, minimum_w, maximum_w)
        preferred_d = _clamp(preferred_d, minimum_d, maximum_d)
        width = _quantize_within(preferred_w, minimum_w, maximum_w, quantum)
        depth = _quantize_within(preferred_d, minimum_d, maximum_d, quantum)
        if width is None or depth is None:
            # Fall back to meso quantization if strict triple-fold quantization
            # cannot fit the envelope; keep the preferred scale instead of
            # collapsing all the way to the minimum footprint.
            q = max(1, req.modularity.meso_module)
            width = _quantize_within(preferred_w, minimum_w, maximum_w, q)
            depth = _quantize_within(preferred_d, minimum_d, maximum_d, q)
        if width is None or depth is None:
            raise ValueError("No modular footprint can satisfy the resolved purpose and size envelope")
        return (width, depth), {
            "purpose_min": [pmin_w, pmin_d], "purpose_max": [pmax_w, pmax_d],
            "resolved_min": [minimum_w, minimum_d], "resolved_max": [maximum_w, maximum_d],
            "resolved": [width, depth], "scale": req.scale, "quantum": quantum,
        }

    def _place_rooms(self, rng, grid, target, modularity, room_layout):
        h, w = len(grid), len(grid[0])
        rooms = []
        attempts = target * 50
        for _ in range(attempts):
            if len(rooms) >= target:
                break
            rw = rng.randint(modularity.room_min_modules, modularity.room_max_modules)
            rd = rng.randint(modularity.room_min_modules, modularity.room_max_modules)
            if rw >= w - 2 or rd >= h - 2:
                continue
            x = rng.randint(1, w - rw - 1)
            z = rng.randint(1, h - rd - 1)
            # Even packed rooms retain one meso wall/service bay between room
            # cells so later materialization does not accidentally merge rooms.
            margin = 1
            if any(grid[zz][xx] != "#" for zz in range(max(0,z-margin), min(h,z+rd+margin)) for xx in range(max(0,x-margin), min(w,x+rw+margin))):
                continue
            rid = len(rooms) + 1
            for zz in range(z, z + rd):
                for xx in range(x, x + rw):
                    grid[zz][xx] = "R"
            rooms.append({
                "id": rid, "x": x, "z": z, "width_modules": rw, "depth_modules": rd,
                "center": [x + rw // 2, z + rd // 2], "zone": None,
            })
        return rooms

    def _assign_zones(self, rooms, zones):
        for i, room in enumerate(rooms):
            room["zone"] = zones[i] if i < len(zones) else (zones[-1] if zones else "general")

    def _connect_rooms(self, rng, grid, rooms, style, dead_end_policy):
        remaining = set(range(1, len(rooms)))
        connected = {0}
        edges = []
        while remaining:
            best = None
            for a in connected:
                ax, az = rooms[a]["center"]
                for b in remaining:
                    bx, bz = rooms[b]["center"]
                    d = abs(ax-bx) + abs(az-bz)
                    if best is None or d < best[0]:
                        best = (d, a, b)
            _, a, b = best
            edges.append((a, b))
            connected.add(b); remaining.remove(b)

        # Dead-end policy operates on the room graph. "none" aggressively adds
        # cycles around leaf rooms, while "some" adds a smaller number of loops.
        extra_target = 0
        if dead_end_policy == "none":
            extra_target = max(1, len(rooms) // 2)
        elif dead_end_policy == "some":
            extra_target = max(0, len(rooms) // 5)
        if style == "labyrinth":
            extra_target += max(1, len(rooms) // 3)

        existing = {tuple(sorted(e)) for e in edges}
        candidates = []
        for a in range(len(rooms)):
            for b in range(a + 1, len(rooms)):
                if (a, b) in existing:
                    continue
                ax,az=rooms[a]["center"]; bx,bz=rooms[b]["center"]
                candidates.append((abs(ax-bx)+abs(az-bz), rng.random(), a, b))
        candidates.sort()
        for _, _, a, b in candidates[:extra_target]:
            edges.append((a,b))

        segments = []
        for a,b in edges:
            path = self._route(grid, rooms[a]["center"], rooms[b]["center"], style, rng)
            if not path:
                raise ValueError(f"Layout mask prevents routing between rooms {a+1} and {b+1}")
            segments.append({"from_room": a+1, "to_room": b+1, "path": path})
        return segments

    def _route(self, grid, start, end, style, rng):
        from collections import deque
        sx, sz = start; tx, tz = end
        q = deque([(sx,sz)])
        parent = {(sx,sz): None}
        while q:
            x,z = q.popleft()
            if (x,z) == (tx,tz):
                break
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            if style == "labyrinth":
                rng.shuffle(dirs)
            else:
                # Prefer motion that closes the largest target delta. For bent
                # corridors randomly choose the first axis when deltas tie.
                x_first = abs(tx-x) > abs(tz-z) or (abs(tx-x) == abs(tz-z) and (style == "straight" or rng.random() < .5))
                primary = [(1 if tx>x else -1,0)] if tx != x else []
                secondary = [(0,1 if tz>z else -1)] if tz != z else []
                ordered = (primary + secondary) if x_first else (secondary + primary)
                dirs = ordered + [d for d in dirs if d not in ordered]
            for dx,dz in dirs:
                nx,nz=x+dx,z+dz
                if not (0 <= nz < len(grid) and 0 <= nx < len(grid[0])):
                    continue
                if grid[nz][nx] == "X" or (nx,nz) in parent:
                    continue
                parent[(nx,nz)] = (x,z)
                q.append((nx,nz))
        if (tx,tz) not in parent:
            return []
        path=[]; cur=(tx,tz)
        while cur is not None:
            path.append([cur[0],cur[1]])
            cur=parent[cur]
        path.reverse()
        for x,z in path:
            if grid[z][x] == "#":
                grid[z][x] = "."
        return path

    def _derive_doors(self, grid, rooms):
        doors = []
        for room in rooms:
            x0,z0,w,d = room["x"],room["z"],room["width_modules"],room["depth_modules"]
            candidates = []
            for x in range(x0, x0+w):
                candidates += [(x,z0),(x,z0+d-1)]
            for z in range(z0, z0+d):
                candidates += [(x0,z),(x0+w-1,z)]
            for x,z in candidates:
                for nx,nz in ((x+1,z),(x-1,z),(x,z+1),(x,z-1)):
                    if 0 <= nz < len(grid) and 0 <= nx < len(grid[0]) and grid[nz][nx] == ".":
                        doors.append({"room":room["id"],"at":[x,z],"outside":[nx,nz]})
                        break
                if doors and doors[-1]["room"] == room["id"]:
                    break
        return doors

    def _derive_stairs(self, rooms, floors, verticality, stair_count):
        stairs = []
        if floors > 1 and verticality != "flat":
            anchors = rooms[:min(len(rooms), max(1, floors-1))]
            stairs.extend({"kind":"inter_floor", "room":r["id"], "at":r["center"], "connects_floors":[i,i+1]} for i,r in enumerate(anchors))
        if stair_count and rooms:
            for i in range(stair_count):
                r = rooms[(i * max(1, len(rooms)//max(1, stair_count))) % len(rooms)]
                stairs.append({"kind":"external_up" if i % 2 == 0 else "external_down", "room":r["id"], "at":r["center"]})
        return stairs


def evaluate_dungeon_layout(layout: dict[str, Any], request: DungeonLayoutRequest) -> dict[str, Any]:
    findings = []
    width, depth = layout["footprint_blocks"]
    s = request.size
    if not (s.min_width <= width <= s.max_width and s.min_depth <= depth <= s.max_depth):
        findings.append({"severity":"error","code":"SIZE_OUTSIDE_EXPLICIT_CONSTRAINTS"})
    zones = {r.get("zone") for r in layout.get("rooms", [])}
    missing = [z for z in layout.get("required_zones", []) if z not in zones]
    if missing:
        findings.append({"severity":"error","code":"MISSING_REQUIRED_ZONES","zones":missing})
    if len(layout.get("rooms", [])) < 3:
        findings.append({"severity":"error","code":"INSUFFICIENT_PROGRAM_ROOMS"})
    if len(layout.get("corridors", [])) < max(0, len(layout.get("rooms", []))-1):
        findings.append({"severity":"error","code":"DISCONNECTED_ROOM_GRAPH"})
    if request.modularity.connector_width < 2:
        findings.append({"severity":"warning","code":"NARROW_CONNECTOR","message":"Connector width below two blocks can constrain multiplayer circulation."})
    if request.modularity.connector_width > request.modularity.meso_module:
        findings.append({"severity":"error","code":"CONNECTOR_EXCEEDS_MESO_MODULE","message":"Connector width cannot exceed the meso room/circulation module."})
    if request.modularity.connector_width % max(1, request.modularity.micro_module):
        findings.append({"severity":"error","code":"CONNECTOR_MICRO_ALIGNMENT_FAILED"})
    q = request.modularity.meso_module
    if width % q or depth % q:
        findings.append({"severity":"error","code":"MESO_MODULE_ALIGNMENT_FAILED"})
    return {
        "status": "FAIL" if any(f["severity"] == "error" for f in findings) else "PASS",
        "findings": findings,
        "metrics": {
            "room_count": len(layout.get("rooms", [])),
            "corridor_count": len(layout.get("corridors", [])),
            "door_count": len(layout.get("doors", [])),
            "required_zone_coverage": len(layout.get("required_zones", [])) - len(missing),
            "required_zone_total": len(layout.get("required_zones", [])),
            "footprint_area": width * depth,
        },
    }
