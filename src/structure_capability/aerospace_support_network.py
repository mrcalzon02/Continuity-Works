from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from .structure_library import StructureLibrary


class AerospaceSupportNetworkError(ValueError):
    pass


class AerospaceSupportNetworkValidator:
    """Validate typed jigsaw/site graphs for aerospace support campuses."""

    CONTRACT = "continuityworks:aerospace_support_site_graph/v1"
    HEAVY_PROFILES = {
        "heavy_logistics_10w",
        "freight_yard_interface",
        "crawler_lane_9x5",
        "pad_queue_interface",
        "launch_mount_service_axis",
        "superheavy_crawler_lane_15x8",
        "transport_spine_interface",
    }
    SUPERHEAVY_PROFILES = {
        "superheavy_crawler_lane_15x8",
        "transport_spine_interface",
    }

    def __init__(
        self,
        repo_root: str | Path | None = None,
        *,
        structure_library: StructureLibrary | None = None,
    ):
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]
        self.repo_root = Path(repo_root).resolve()
        self.structure_library = structure_library or StructureLibrary(
            self.repo_root / "library"
        )
        self.support_root = self.repo_root / "facility_library" / "aerospace_orbital"
        self.program = self._read_json(self.support_root / "support_program.json")
        self.network_modules = self._read_json(
            self.support_root / "network_modules.json"
        )

    @staticmethod
    def _read_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise AerospaceSupportNetworkError(f"Expected object: {path}")
        return value

    def validate_program(self) -> dict:
        findings: list[dict[str, str]] = []

        def fail(code: str, detail: str) -> None:
            findings.append({"status": "FAIL", "code": code, "detail": detail})

        profiles = self.structure_library.connector_contract.get("profiles", {})
        if self.structure_library.connector_contract.get("version", 0) < 4:
            fail(
                "CONNECTOR_CONTRACT_TOO_OLD",
                str(self.structure_library.connector_contract.get("version")),
            )

        proposed = set(self.program.get("proposed_connector_contract_v4_additions", []))
        missing_profiles = sorted(proposed - set(profiles))
        if missing_profiles:
            fail("MISSING_V4_PROFILES", ", ".join(missing_profiles))

        modules = self.network_modules.get("modules")
        if not isinstance(modules, list) or not modules:
            fail("NETWORK_MODULES_MISSING", "network_modules.json")
            modules = []

        ids: set[str] = set()
        planned = set(self.program.get("planned_network_modules", []))
        for item in modules:
            module_id = item.get("id")
            if not module_id or module_id in ids:
                fail("DUPLICATE_NETWORK_MODULE", str(module_id))
                continue
            ids.add(module_id)
            size = item.get("size")
            if not isinstance(size, list) or len(size) != 3 or any(
                not isinstance(v, int) or v <= 0 for v in size
            ):
                fail("INVALID_NETWORK_MODULE_SIZE", str(module_id))
            for socket in item.get("sockets", []):
                profile = socket.get("profile")
                group = socket.get("group")
                if profile not in profiles:
                    fail("UNKNOWN_SOCKET_PROFILE", f"{module_id}: {profile}")
                allowed = set(self.program.get("socket_groups", {}).get(group, []))
                if profile not in allowed:
                    fail(
                        "SOCKET_GROUP_PROFILE_MISMATCH",
                        f"{module_id}:{socket.get('id')} {group}/{profile}",
                    )
                self._validate_socket_boundary(item, socket, fail)
        missing_modules = sorted(planned - ids)
        if missing_modules:
            fail("MISSING_PLANNED_NETWORK_MODULE", ", ".join(missing_modules))

        road = self.network_modules.get("road_baseline", {})
        if road.get("local_road_width_blocks") != 6:
            fail("LOCAL_ROAD_WIDTH_DRIFT", str(road.get("local_road_width_blocks")))
        if road.get("terrain_padding_each_side_blocks") != 5:
            fail(
                "ROAD_TERRAIN_PADDING_DRIFT",
                str(road.get("terrain_padding_each_side_blocks")),
            )

        return {
            "gate": "AEROSPACE_SUPPORT_NETWORK_PROGRAM",
            "status": "FAIL" if findings else "PASS",
            "connector_contract_version": self.structure_library.connector_contract.get(
                "version"
            ),
            "connector_profiles": len(profiles),
            "network_modules": len(modules),
            "findings": findings,
        }

    @staticmethod
    def _validate_socket_boundary(item: dict, socket: dict, fail) -> None:
        size = item.get("size")
        center = socket.get("center")
        face = socket.get("face")
        if not isinstance(size, list) or len(size) != 3:
            return
        if not isinstance(center, list) or len(center) != 3:
            fail("INVALID_SOCKET_CENTER", f"{item.get('id')}:{socket.get('id')}")
            return
        x, y, z = center
        w, h, d = size
        if not (0 <= x < w and 0 <= y < h and 0 <= z < d):
            fail("SOCKET_OUT_OF_BOUNDS", f"{item.get('id')}:{socket.get('id')}")
            return
        boundary_ok = {
            "north": z == 0,
            "south": z == d - 1,
            "west": x == 0,
            "east": x == w - 1,
            "down": y == 0,
            "up": y == h - 1,
        }.get(face, False)
        if not boundary_ok:
            fail("SOCKET_NOT_ON_FACE", f"{item.get('id')}:{socket.get('id')}:{face}")

    def validate_graph(self, graph: dict[str, Any]) -> dict:
        findings: list[dict[str, str]] = []

        def fail(code: str, detail: str) -> None:
            findings.append({"status": "FAIL", "code": code, "detail": detail})

        if graph.get("contract") != self.CONTRACT:
            fail("SITE_GRAPH_CONTRACT_MISMATCH", str(graph.get("contract")))

        nodes_raw = graph.get("nodes", [])
        edges = graph.get("edges", [])
        nodes: dict[str, dict] = {}
        sockets: dict[tuple[str, str], dict] = {}
        for node in nodes_raw:
            node_id = node.get("id")
            if not node_id or node_id in nodes:
                fail("DUPLICATE_OR_MISSING_NODE", str(node_id))
                continue
            nodes[node_id] = node
            seen: set[str] = set()
            for socket in node.get("sockets", []):
                socket_id = socket.get("id")
                if not socket_id or socket_id in seen:
                    fail("DUPLICATE_OR_MISSING_SOCKET", f"{node_id}:{socket_id}")
                    continue
                seen.add(socket_id)
                profile = socket.get("profile")
                if profile not in self.structure_library.connector_contract.get(
                    "profiles", {}
                ):
                    fail("UNKNOWN_SOCKET_PROFILE", f"{node_id}:{socket_id}:{profile}")
                sockets[(node_id, socket_id)] = socket

        adjacency: dict[str, set[str]] = defaultdict(set)
        connected_sockets: set[tuple[str, str]] = set()
        for index, edge in enumerate(edges):
            try:
                left = (edge["a"]["node"], edge["a"]["socket"])
                right = (edge["b"]["node"], edge["b"]["socket"])
            except Exception:
                fail("INVALID_EDGE", str(index))
                continue
            if left not in sockets or right not in sockets:
                fail("UNKNOWN_EDGE_ENDPOINT", f"{index}:{left}->{right}")
                continue
            if left in connected_sockets or right in connected_sockets:
                fail("SOCKET_REUSED", f"{index}:{left}->{right}")
                continue
            lp = sockets[left].get("profile")
            rp = sockets[right].get("profile")
            if not self.structure_library.profiles_compatible(lp, rp):
                fail("INCOMPATIBLE_SOCKET_PROFILES", f"{index}:{lp}<->{rp}")
                continue
            connected_sockets.add(left)
            connected_sockets.add(right)
            adjacency[left[0]].add(right[0])
            adjacency[right[0]].add(left[0])

        for key, socket in sockets.items():
            if socket.get("required", False) and key not in connected_sockets:
                fail("REQUIRED_SOCKET_UNCONNECTED", f"{key[0]}:{key[1]}")

        launch_anchors = {
            node_id
            for node_id, node in nodes.items()
            if node.get("kind") == "launch_anchor"
        }
        if not launch_anchors:
            fail("NO_LAUNCH_ANCHOR", "site graph has no launch_anchor node")

        for node_id, node in nodes.items():
            requirements = node.get("requirements", {})
            if not node.get("isolated", False) and node.get("kind") != "external_anchor":
                if not adjacency.get(node_id):
                    fail("NETWORK_ISOLATION", node_id)

            connected = {
                socket_id: sockets[(node_id, socket_id)]
                for (nid, socket_id) in connected_sockets
                if nid == node_id
            }

            if requirements.get("utility"):
                if not any(s.get("group") == "utility" for s in connected.values()):
                    fail("UTILITY_ATTACHMENT_MISSING", node_id)

            if requirements.get("inbound_logistics"):
                if not any(
                    s.get("group") in {"logistics", "heavy_transport"}
                    and s.get("flow") in {"inbound", "bidirectional"}
                    for s in connected.values()
                ):
                    fail("INBOUND_LOGISTICS_MISSING", node_id)

            if requirements.get("outbound_logistics"):
                if not any(
                    s.get("group") in {"logistics", "heavy_transport"}
                    and s.get("flow") in {"outbound", "bidirectional"}
                    for s in connected.values()
                ):
                    fail("OUTBOUND_LOGISTICS_MISSING", node_id)

            scale = node.get("scale")
            if requirements.get("heavy_route") or scale == "heavy":
                profiles = {s.get("profile") for s in connected.values()}
                if not profiles.intersection(self.HEAVY_PROFILES):
                    fail("HEAVY_ROUTE_UNDERSIZED", node_id)
            if requirements.get("superheavy_route") or scale in {
                "superheavy",
                "megastructure",
            }:
                profiles = {s.get("profile") for s in connected.values()}
                if not profiles.intersection(self.SUPERHEAVY_PROFILES):
                    fail("SUPERHEAVY_ROUTE_MISSING", node_id)

            if requirements.get("launch_route"):
                if not self._reaches_any(node_id, launch_anchors, adjacency):
                    fail("LAUNCH_ANCHOR_UNREACHABLE", node_id)

        return {
            "gate": "AEROSPACE_SUPPORT_SITE_GRAPH",
            "status": "FAIL" if findings else "PASS",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "launch_anchor_count": len(launch_anchors),
            "findings": findings,
        }

    @staticmethod
    def _reaches_any(
        start: str, targets: set[str], adjacency: dict[str, set[str]]
    ) -> bool:
        if start in targets:
            return True
        queue: deque[str] = deque([start])
        seen = {start}
        while queue:
            current = queue.popleft()
            for nxt in adjacency.get(current, set()):
                if nxt in targets:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False
