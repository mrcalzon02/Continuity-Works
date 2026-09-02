from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .aerospace_support_network import AerospaceSupportNetworkValidator
from .facility_library import FacilityLibrary


class AerospaceSupportPlacementError(ValueError):
    pass


@dataclass(frozen=True)
class _Footprint:
    width: int
    height: int
    depth: int


class AerospaceSupportCampusPlacementPlanner:
    """Translate a validated support-campus graph into collision-safe block coordinates."""

    CONTRACT = "continuityworks:aerospace_support_placement/v1"
    ROTATIONS = {"north": 0, "east": 90, "south": 180, "west": 270}
    DEFAULT_CLEARANCE = {"compact": 12, "distributed": 28}
    ANCHOR_SIZE = {
        "external_anchor": _Footprint(9, 3, 9),
        "launch_anchor": _Footprint(25, 5, 25),
    }

    def __init__(
        self,
        facility_library: FacilityLibrary | None = None,
        network_validator: AerospaceSupportNetworkValidator | None = None,
    ):
        self.facilities = facility_library or FacilityLibrary()
        self.network = network_validator or AerospaceSupportNetworkValidator(
            structure_library=self.facilities.structures
        )
        self._network_modules = {
            item["id"]: item for item in self.network.network_modules.get("modules", [])
        }

    def plan(
        self,
        graph: dict[str, Any],
        *,
        origin: tuple[int, int, int] | list[int] = (0, 0, 0),
        clearance: int | None = None,
    ) -> dict[str, Any]:
        graph_report = self.network.validate_graph(graph)
        if graph_report["status"] != "PASS":
            raise AerospaceSupportPlacementError(
                f"Cannot place invalid support graph: {graph_report['findings']}"
            )
        origin = self._vec3(origin, "origin")
        if clearance is not None and (not isinstance(clearance, int) or clearance < 0):
            raise AerospaceSupportPlacementError("clearance must be a non-negative integer")
        spacing = graph.get("site_context", {}).get("spacing", "compact")
        gap = clearance if clearance is not None else self.DEFAULT_CLEARANCE.get(spacing, 12)
        orientation = graph.get("site_context", {}).get("orientation", "north")
        rotation = self.ROTATIONS.get(orientation)
        if rotation is None:
            raise AerospaceSupportPlacementError(f"Unsupported site orientation: {orientation}")

        nodes = {node["id"]: deepcopy(node) for node in graph.get("nodes", [])}
        physical = {
            node_id: self._physical_descriptor(node, rotation)
            for node_id, node in nodes.items()
        }
        origins = self._pack(nodes, physical, origin, gap)

        placements: dict[str, dict[str, Any]] = {}
        for node_id, node in nodes.items():
            desc = physical[node_id]
            node_origin = origins[node_id]
            size = desc["rotated_size"]
            sockets = self._world_sockets(node, desc, node_origin, rotation)
            placements[node_id] = {
                "node_id": node_id,
                "kind": node.get("kind"),
                "archetype_id": node.get("archetype_id"),
                "reference_id": node.get("reference_id"),
                "source_module": node.get("source_module"),
                "rotation_degrees": rotation,
                "origin": list(node_origin),
                "size": list(size),
                "bbox": {
                    "min": list(node_origin),
                    "max": [
                        node_origin[0] + size[0] - 1,
                        node_origin[1] + size[1] - 1,
                        node_origin[2] + size[2] - 1,
                    ],
                },
                "sockets": sockets,
            }

        overlap_findings = self._placement_overlaps(placements)
        routes = self._route_edges(graph, placements, gap)
        route_findings = [
            finding
            for route in routes
            for finding in route.get("findings", [])
        ]
        campus_bounds = self._bounds(placements, routes)

        plan = {
            "contract": self.CONTRACT,
            "source_graph_contract": graph.get("contract"),
            "source_generation_contract": graph.get("generation_contract"),
            "source_graph_id": graph.get("graph_id"),
            "source_campus_fingerprint": graph.get("campus_fingerprint"),
            "origin": list(origin),
            "rotation_degrees": rotation,
            "clearance_blocks": gap,
            "placements": [placements[key] for key in sorted(placements)],
            "routes": routes,
            "bounds": campus_bounds,
        }
        plan["placement_fingerprint"] = self.fingerprint(plan)
        findings = overlap_findings + route_findings
        return {
            "plan": plan,
            "report": {
                "gate": "AEROSPACE_SUPPORT_CAMPUS_PLACEMENT",
                "status": "FAIL" if findings else "PASS",
                "source_graph_status": graph_report["status"],
                "placement_count": len(placements),
                "route_count": len(routes),
                "rotation_degrees": rotation,
                "clearance_blocks": gap,
                "bounds": campus_bounds,
                "placement_fingerprint": plan["placement_fingerprint"],
                "findings": findings,
            },
        }

    def _physical_descriptor(self, node: dict, rotation: int) -> dict:
        kind = node.get("kind")
        if kind == "facility":
            reference_id = node.get("reference_id")
            if not reference_id:
                raise AerospaceSupportPlacementError(
                    f"Facility node has no reference_id: {node.get('id')}"
                )
            reference = self.facilities.load(reference_id)
            size = self._size(reference.get("size"), reference_id)
            sockets = deepcopy(
                reference.get("aerospace_support_reference", {}).get(
                    "network_sockets", []
                )
            )
            if not sockets:
                raise AerospaceSupportPlacementError(
                    f"Facility reference has no physical sockets: {reference_id}"
                )
            source = reference_id
        elif kind == "infrastructure":
            module_id = node.get("source_module")
            module = self._network_modules.get(module_id)
            if module is None:
                raise AerospaceSupportPlacementError(
                    f"Unknown network module: {node.get('id')} -> {module_id}"
                )
            size = self._size(module.get("size"), module_id)
            sockets = deepcopy(module.get("sockets", []))
            source = module_id
        elif kind in self.ANCHOR_SIZE:
            size_obj = self.ANCHOR_SIZE[kind]
            size = (size_obj.width, size_obj.height, size_obj.depth)
            sockets = self._anchor_sockets(node, size)
            source = kind
        else:
            raise AerospaceSupportPlacementError(
                f"Unsupported campus node kind: {node.get('id')} -> {kind}"
            )
        rotated_size = self._rotated_size(size, rotation)
        return {
            "source": source,
            "base_size": size,
            "rotated_size": rotated_size,
            "physical_sockets": sockets,
        }

    def _anchor_sockets(self, node: dict, size: tuple[int, int, int]) -> list[dict]:
        graph_sockets = node.get("sockets", [])
        if not graph_sockets:
            return []
        faces = ("north", "east", "south", "west")
        output = []
        for index, socket in enumerate(graph_sockets):
            face = faces[index % len(faces)]
            x = size[0] // 2
            y = min(size[1] - 1, 1)
            z = size[2] // 2
            if face == "north":
                z = 0
            elif face == "south":
                z = size[2] - 1
            elif face == "west":
                x = 0
            else:
                x = size[0] - 1
            output.append({
                "id": socket["id"],
                "profile": socket["profile"],
                "group": socket.get("group"),
                "face": face,
                "center": [x, y, z],
            })
        return output

    def _pack(self, nodes, physical, origin, gap):
        positions = {
            node_id: tuple(node.get("site_pos", [0, 0]))
            for node_id, node in nodes.items()
        }
        xs = sorted({pos[0] for pos in positions.values()})
        zs = sorted({pos[1] for pos in positions.values()})
        column_width = {
            x: max(
                physical[node_id]["rotated_size"][0]
                for node_id, pos in positions.items()
                if pos[0] == x
            )
            for x in xs
        }
        row_depth = {
            z: max(
                physical[node_id]["rotated_size"][2]
                for node_id, pos in positions.items()
                if pos[1] == z
            )
            for z in zs
        }
        x_origin = {}
        cursor = origin[0]
        previous = None
        for x in xs:
            if previous is not None:
                abstract_gap = max(0, int(x - previous) - 1)
                cursor += gap + min(48, abstract_gap // 2)
            x_origin[x] = cursor
            cursor += column_width[x]
            previous = x
        z_origin = {}
        cursor = origin[2]
        previous = None
        for z in zs:
            if previous is not None:
                abstract_gap = max(0, int(z - previous) - 1)
                cursor += gap + min(48, abstract_gap // 2)
            z_origin[z] = cursor
            cursor += row_depth[z]
            previous = z

        result = {}
        for node_id, (x, z) in positions.items():
            width, _, depth = physical[node_id]["rotated_size"]
            x_offset = (column_width[x] - width) // 2
            z_offset = (row_depth[z] - depth) // 2
            result[node_id] = (
                x_origin[x] + x_offset,
                origin[1],
                z_origin[z] + z_offset,
            )
        return result

    def _world_sockets(self, node, desc, origin, rotation):
        graph_sockets = node.get("sockets", [])
        physical = desc["physical_sockets"]
        assigned: set[int] = set()
        output = []
        for graph_socket in graph_sockets:
            index = self._match_socket(graph_socket, physical, assigned)
            if index is None:
                raise AerospaceSupportPlacementError(
                    f"No physical socket for {node.get('id')}:{graph_socket.get('id')} "
                    f"{graph_socket.get('profile')}/{graph_socket.get('group')}"
                )
            assigned.add(index)
            socket = physical[index]
            local = self._rotate_point(
                tuple(socket["center"]), desc["base_size"], rotation
            )
            output.append({
                "id": graph_socket["id"],
                "physical_socket_id": socket.get("id"),
                "profile": graph_socket["profile"],
                "group": graph_socket.get("group"),
                "flow": graph_socket.get("flow", "bidirectional"),
                "face": self._rotate_face(socket.get("face"), rotation),
                "world_center": [
                    origin[0] + local[0],
                    origin[1] + local[1],
                    origin[2] + local[2],
                ],
            })
        return output

    @staticmethod
    def _match_socket(graph_socket, physical, assigned):
        exact = [
            i for i, socket in enumerate(physical)
            if i not in assigned and socket.get("id") == graph_socket.get("id")
            and socket.get("profile") == graph_socket.get("profile")
        ]
        if exact:
            return exact[0]
        same_profile = [
            i for i, socket in enumerate(physical)
            if i not in assigned and socket.get("profile") == graph_socket.get("profile")
        ]
        if same_profile:
            return same_profile[0]
        return None

    def _route_edges(self, graph, placements, gap):
        node_map = {node["id"]: node for node in graph.get("nodes", [])}
        socket_map = {
            (placement["node_id"], socket["id"]): socket
            for placement in placements.values()
            for socket in placement["sockets"]
        }
        profiles = self.facilities.structures.connector_contract.get("profiles", {})
        routes = []
        for index, edge in enumerate(graph.get("edges", [])):
            left = edge["a"]
            right = edge["b"]
            left_socket = socket_map[(left["node"], left["socket"])]
            right_socket = socket_map[(right["node"], right["socket"])]
            start = tuple(left_socket["world_center"])
            end = tuple(right_socket["world_center"])
            lp = profiles[left_socket["profile"]]
            rp = profiles[right_socket["profile"]]
            width = max(int(lp.get("aperture", [1, 1])[0]), int(rp.get("aperture", [1, 1])[0]))
            height = max(int(lp.get("aperture", [1, 1])[1]), int(rp.get("aperture", [1, 1])[1]))
            group = left_socket.get("group") or right_socket.get("group")
            path, findings = self._route_path(
                start,
                end,
                placements,
                excluded={left["node"], right["node"]},
                half_width=max(0, (width - 1) // 2),
                margin=gap,
            )
            routes.append({
                "id": f"edge_{index:02d}",
                "a": deepcopy(left),
                "b": deepcopy(right),
                "profiles": [left_socket["profile"], right_socket["profile"]],
                "group": group,
                "width_blocks": width,
                "height_blocks": height,
                "path": [list(point) for point in path],
                "findings": findings,
            })
        return routes

    def _route_path(self, start, end, placements, *, excluded, half_width, margin):
        if start == end:
            return [start], []
        travel_y = max(start[1], end[1])
        start_surface = (start[0], travel_y, start[2])
        end_surface = (end[0], travel_y, end[2])
        candidates = [
            self._dedupe_path([start, start_surface, (end[0], travel_y, start[2]), end_surface, end]),
            self._dedupe_path([start, start_surface, (start[0], travel_y, end[2]), end_surface, end]),
        ]
        for path in candidates:
            if not self._path_intersections(path, placements, excluded, half_width):
                return path, []

        all_bounds = self._placement_union(placements)
        detours = [
            all_bounds["min"][0] - margin - half_width - 1,
            all_bounds["max"][0] + margin + half_width + 1,
        ]
        best = None
        for x in detours:
            path = self._dedupe_path([
                start,
                start_surface,
                (x, travel_y, start[2]),
                (x, travel_y, end[2]),
                end_surface,
                end,
            ])
            hits = self._path_intersections(path, placements, excluded, half_width)
            candidate = (len(hits), self._path_length(path), path, hits)
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        assert best is not None
        findings = []
        if best[0]:
            findings.append({
                "status": "FAIL",
                "code": "ROUTE_COLLISION",
                "detail": ", ".join(sorted(best[3])),
            })
        return best[2], findings

    def _path_intersections(self, path, placements, excluded, half_width):
        hits = set()
        for a, b in zip(path, path[1:]):
            if a[0] != b[0] and a[2] != b[2]:
                hits.add("NON_ORTHOGONAL_ROUTE")
                continue
            min_x = min(a[0], b[0]) - half_width
            max_x = max(a[0], b[0]) + half_width
            min_z = min(a[2], b[2]) - half_width
            max_z = max(a[2], b[2]) + half_width
            for node_id, placement in placements.items():
                if node_id in excluded:
                    continue
                bbox = placement["bbox"]
                if not (
                    max_x < bbox["min"][0]
                    or min_x > bbox["max"][0]
                    or max_z < bbox["min"][2]
                    or min_z > bbox["max"][2]
                ):
                    hits.add(node_id)
        return hits

    @staticmethod
    def _placement_overlaps(placements):
        findings = []
        ids = sorted(placements)
        for i, left_id in enumerate(ids):
            left = placements[left_id]["bbox"]
            for right_id in ids[i + 1:]:
                right = placements[right_id]["bbox"]
                separated = (
                    left["max"][0] < right["min"][0]
                    or right["max"][0] < left["min"][0]
                    or left["max"][2] < right["min"][2]
                    or right["max"][2] < left["min"][2]
                )
                if not separated:
                    findings.append({
                        "status": "FAIL",
                        "code": "PLACEMENT_OVERLAP",
                        "detail": f"{left_id}<->{right_id}",
                    })
        return findings

    @staticmethod
    def _placement_union(placements):
        return {
            "min": [
                min(p["bbox"]["min"][0] for p in placements.values()),
                min(p["bbox"]["min"][1] for p in placements.values()),
                min(p["bbox"]["min"][2] for p in placements.values()),
            ],
            "max": [
                max(p["bbox"]["max"][0] for p in placements.values()),
                max(p["bbox"]["max"][1] for p in placements.values()),
                max(p["bbox"]["max"][2] for p in placements.values()),
            ],
        }

    def _bounds(self, placements, routes):
        union = self._placement_union(placements)
        xs = [union["min"][0], union["max"][0]]
        ys = [union["min"][1], union["max"][1]]
        zs = [union["min"][2], union["max"][2]]
        for route in routes:
            for x, y, z in route["path"]:
                xs.append(x)
                ys.append(y)
                zs.append(z)
        return {"min": [min(xs), min(ys), min(zs)], "max": [max(xs), max(ys), max(zs)]}

    @staticmethod
    def _dedupe_path(path):
        output = []
        for point in path:
            if not output or output[-1] != point:
                output.append(point)
        return output

    @staticmethod
    def _path_length(path):
        return sum(
            abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
            for a, b in zip(path, path[1:])
        )

    @staticmethod
    def _size(value, label):
        if not isinstance(value, list) or len(value) != 3 or not all(
            isinstance(v, int) and v > 0 for v in value
        ):
            raise AerospaceSupportPlacementError(f"Invalid size for {label}: {value}")
        return tuple(value)

    @staticmethod
    def _vec3(value, label):
        if not isinstance(value, (tuple, list)) or len(value) != 3 or not all(
            isinstance(v, int) for v in value
        ):
            raise AerospaceSupportPlacementError(f"Invalid {label}: {value}")
        return tuple(value)

    @staticmethod
    def _rotated_size(size, rotation):
        if rotation in {0, 180}:
            return size
        return (size[2], size[1], size[0])

    @staticmethod
    def _rotate_point(point, size, rotation):
        x, y, z = point
        width, _, depth = size
        if rotation == 0:
            return x, y, z
        if rotation == 90:
            return depth - 1 - z, y, x
        if rotation == 180:
            return width - 1 - x, y, depth - 1 - z
        if rotation == 270:
            return z, y, width - 1 - x
        raise AerospaceSupportPlacementError(f"Unsupported rotation: {rotation}")

    @staticmethod
    def _rotate_face(face, rotation):
        if face in {"up", "down", None}:
            return face
        order = ["north", "east", "south", "west"]
        if face not in order:
            return face
        return order[(order.index(face) + rotation // 90) % 4]

    @staticmethod
    def fingerprint(plan):
        data = deepcopy(plan)
        data.pop("placement_fingerprint", None)
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
