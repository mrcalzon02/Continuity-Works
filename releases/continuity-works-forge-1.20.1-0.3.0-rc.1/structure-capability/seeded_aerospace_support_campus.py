from __future__ import annotations

import hashlib
import json
import random
from copy import deepcopy

from .aerospace_support_network import AerospaceSupportNetworkValidator
from .facility_library import FacilityLibrary


class SeededAerospaceSupportCampusError(ValueError):
    pass


class SeededAerospaceSupportCampusGenerator:
    """Deterministically synthesize typed aerospace support campus site graphs."""

    CONTRACT = "continuityworks:seeded_aerospace_support_campus/v1"
    SCALES = ("micro", "light", "standard", "heavy", "superheavy", "megastructure")
    ORIENTATIONS = ("north", "east", "south", "west")
    SPACING = ("compact", "distributed")
    TERRAIN = {
        "micro": ("flat", "gentle_grade"),
        "light": ("flat", "gentle_grade", "cut_and_fill"),
        "standard": ("flat", "graded", "cut_and_fill"),
        "heavy": ("graded", "terraced", "cut_and_fill"),
        "superheavy": ("graded", "terraced", "engineered_plateau"),
        "megastructure": ("engineered_plateau", "terraced", "deep_cut"),
    }

    TEMPLATES = {
        "micro": {
            "facilities": [
                ("service", "continuityworks:archetype/utility_component_service_shed", (10, 10)),
                ("maintenance", "continuityworks:archetype/microcraft_maintenance_bay", (40, 10)),
            ],
            "extras": [
                {"id": "service_road", "kind": "infrastructure", "source_module": "local_road_segment_6w", "site_pos": (10, 30), "sockets": [
                    {"id": "a", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "b", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
                {"id": "maintenance_road", "kind": "infrastructure", "source_module": "local_road_segment_6w", "site_pos": (40, 30), "sockets": [
                    {"id": "a", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "b", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
                {"id": "utility_grid", "kind": "external_anchor", "site_pos": (0, 10), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "refit_support", "kind": "external_anchor", "site_pos": (55, 10), "sockets": [{"id": "bay", "profile": "maintenance_bay_interface", "group": "maintenance", "flow": "bidirectional", "required": True}]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (25, 55), "sockets": [
                    {"id": "service_road", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "maintenance_road", "profile": "local_road_6w", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
            ],
            "edges": [
                ("service", "road", "service_road", "a"),
                ("service_road", "b", "pad", "service_road"),
                ("service", "utility", "utility_grid", "service"),
                ("maintenance", "road", "maintenance_road", "a"),
                ("maintenance_road", "b", "pad", "maintenance_road"),
                ("maintenance", "refit", "refit_support", "bay"),
            ],
        },
        "light": {
            "facilities": [
                ("assembly", "continuityworks:archetype/small_assembly_bay", (10, 10)),
                ("transfer", "continuityworks:archetype/component_transfer_gantry", (45, 10)),
            ],
            "extras": [
                {"id": "supplier", "kind": "external_anchor", "site_pos": (0, 10), "sockets": [{"id": "out", "profile": "vehicle_transfer_interface", "group": "logistics", "flow": "outbound", "required": True}]},
                {"id": "utility_grid", "kind": "external_anchor", "site_pos": (10, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "checkpoint", "kind": "infrastructure", "source_module": "road_checkpoint_gate", "site_pos": (70, 10), "sockets": [
                    {"id": "campus", "profile": "checkpoint_road_interface", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "launch", "profile": "checkpoint_road_interface", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
                {"id": "apron", "kind": "infrastructure", "source_module": "pad_access_apron", "site_pos": (90, 10), "sockets": [
                    {"id": "road", "profile": "launch_support_road_8w", "group": "launch_support", "flow": "bidirectional", "required": True},
                    {"id": "queue", "profile": "pad_queue_interface", "group": "launch_support", "flow": "bidirectional", "required": True},
                ]},
                {"id": "queue", "kind": "infrastructure", "source_module": "queue_alignment_segment", "site_pos": (110, 10), "sockets": [
                    {"id": "in", "profile": "queue_alignment_interface", "group": "staging", "flow": "bidirectional", "required": True},
                    {"id": "out", "profile": "queue_alignment_interface", "group": "staging", "flow": "bidirectional", "required": True},
                ]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (130, 10), "sockets": [{"id": "queue", "profile": "pad_queue_interface", "group": "launch_support", "flow": "bidirectional", "required": True}]},
            ],
            "edges": [
                ("assembly", "parts_in", "supplier", "out"),
                ("assembly", "vehicle_out", "transfer", "component_in"),
                ("assembly", "utility", "utility_grid", "service"),
                ("transfer", "launch_feed", "checkpoint", "campus"),
                ("checkpoint", "launch", "apron", "road"),
                ("apron", "queue", "queue", "in"),
                ("queue", "out", "pad", "queue"),
            ],
        },
        "standard": {
            "facilities": [
                ("factory", "continuityworks:archetype/precision_components_factory", (10, 10)),
                ("assembly", "continuityworks:archetype/dual_bay_assembly_hall", (50, 10)),
            ],
            "extras": [
                {"id": "factory_supplier", "kind": "external_anchor", "site_pos": (0, 0), "sockets": [{"id": "out", "profile": "heavy_logistics_10w", "group": "logistics", "flow": "outbound", "required": True}]},
                {"id": "assembly_supplier", "kind": "external_anchor", "site_pos": (50, 0), "sockets": [{"id": "out", "profile": "heavy_logistics_10w", "group": "logistics", "flow": "outbound", "required": True}]},
                {"id": "vehicle_staging", "kind": "external_anchor", "site_pos": (80, 0), "sockets": [{"id": "in", "profile": "component_transfer_interface", "group": "logistics", "flow": "inbound", "required": True}]},
                {"id": "factory_utility", "kind": "external_anchor", "site_pos": (10, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "assembly_utility", "kind": "external_anchor", "site_pos": (60, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "turnout", "kind": "infrastructure", "source_module": "industrial_turnout_loop", "site_pos": (35, 35), "sockets": [
                    {"id": "west", "profile": "industrial_road_8w", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "east", "profile": "industrial_road_8w", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "north", "profile": "industrial_road_8w", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
                {"id": "checkpoint", "kind": "infrastructure", "source_module": "road_checkpoint_gate", "site_pos": (35, 55), "sockets": [
                    {"id": "campus", "profile": "checkpoint_road_interface", "group": "frontage", "flow": "bidirectional", "required": True},
                    {"id": "launch", "profile": "checkpoint_road_interface", "group": "frontage", "flow": "bidirectional", "required": True},
                ]},
                {"id": "apron", "kind": "infrastructure", "source_module": "pad_access_apron", "site_pos": (35, 75), "sockets": [
                    {"id": "road", "profile": "launch_support_road_8w", "group": "launch_support", "flow": "bidirectional", "required": True},
                    {"id": "queue", "profile": "pad_queue_interface", "group": "launch_support", "flow": "bidirectional", "required": True},
                ]},
                {"id": "queue", "kind": "infrastructure", "source_module": "queue_alignment_segment", "site_pos": (35, 95), "sockets": [
                    {"id": "in", "profile": "queue_alignment_interface", "group": "staging", "flow": "bidirectional", "required": True},
                    {"id": "out", "profile": "queue_alignment_interface", "group": "staging", "flow": "bidirectional", "required": True},
                ]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (35, 115), "sockets": [{"id": "queue", "profile": "pad_queue_interface", "group": "launch_support", "flow": "bidirectional", "required": True}]},
            ],
            "edges": [
                ("factory", "freight", "factory_supplier", "out"),
                ("factory", "utility", "factory_utility", "service"),
                ("assembly", "parts_in", "assembly_supplier", "out"),
                ("assembly", "vehicles_out", "vehicle_staging", "in"),
                ("assembly", "utility", "assembly_utility", "service"),
                ("factory", "road", "turnout", "west"),
                ("assembly", "road", "turnout", "east"),
                ("turnout", "north", "checkpoint", "campus"),
                ("checkpoint", "launch", "apron", "road"),
                ("apron", "queue", "queue", "in"),
                ("queue", "out", "pad", "queue"),
            ],
        },
        "heavy": {
            "facilities": [
                ("marshalling", "continuityworks:archetype/heavy_component_marshalling_yard", (10, 20)),
                ("integration", "continuityworks:archetype/vertical_integration_support_tower", (65, 5)),
                ("launch_queue", "continuityworks:archetype/launch_queue_preparation_yard", (65, 45)),
            ],
            "extras": [
                {"id": "supplier", "kind": "external_anchor", "site_pos": (0, 20), "sockets": [{"id": "out", "profile": "heavy_logistics_10w", "group": "logistics", "flow": "outbound", "required": True}]},
                {"id": "utility_grid", "kind": "external_anchor", "site_pos": (65, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "crawler_junction", "kind": "infrastructure", "source_module": "heavy_crawlerway_junction", "site_pos": (40, 25), "sockets": [
                    {"id": "north", "profile": "crawler_lane_9x5", "group": "heavy_transport", "flow": "bidirectional", "required": True},
                    {"id": "east", "profile": "crawler_lane_9x5", "group": "heavy_transport", "flow": "bidirectional", "required": True},
                    {"id": "south", "profile": "crawler_lane_9x5", "group": "heavy_transport", "flow": "bidirectional", "required": True},
                ]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (100, 25), "sockets": [
                    {"id": "service", "profile": "launch_mount_service_axis", "group": "launch_support", "flow": "bidirectional", "required": True},
                    {"id": "queue", "profile": "pad_queue_interface", "group": "launch_support", "flow": "bidirectional", "required": True},
                ]},
            ],
            "edges": [
                ("marshalling", "freight", "supplier", "out"),
                ("marshalling", "crawler", "crawler_junction", "north"),
                ("crawler_junction", "east", "integration", "crawler"),
                ("crawler_junction", "south", "launch_queue", "crawler_in"),
                ("integration", "utility", "utility_grid", "service"),
                ("integration", "launch_feed", "pad", "service"),
                ("launch_queue", "pad_feed", "pad", "queue"),
            ],
        },
        "superheavy": {
            "facilities": [
                ("factory", "continuityworks:archetype/mega_vehicle_production_factory", (10, 20)),
                ("spine", "continuityworks:archetype/superheavy_transfer_spine", (70, 20)),
                ("integration", "continuityworks:archetype/superheavy_vehicle_integration_factory", (130, 20)),
            ],
            "extras": [
                {"id": "supplier", "kind": "external_anchor", "site_pos": (0, 20), "sockets": [{"id": "out", "profile": "heavy_logistics_10w", "group": "logistics", "flow": "outbound", "required": True}]},
                {"id": "factory_utility", "kind": "external_anchor", "site_pos": (10, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "integration_utility", "kind": "external_anchor", "site_pos": (130, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (190, 20), "sockets": [{"id": "service", "profile": "launch_mount_service_axis", "group": "launch_support", "flow": "bidirectional", "required": True}]},
            ],
            "edges": [
                ("factory", "freight", "supplier", "out"),
                ("factory", "utility", "factory_utility", "service"),
                ("factory", "transport", "spine", "spine_a"),
                ("spine", "spine_b", "integration", "launch_spine"),
                ("spine", "launch_branch", "pad", "service"),
                ("integration", "utility", "integration_utility", "service"),
            ],
        },
        "megastructure": {
            "facilities": [
                ("campus", "continuityworks:archetype/mega_enclosed_assembly_campus", (10, 20)),
                ("transfer", "continuityworks:archetype/colossal_transfer_hall", (100, 20)),
                ("underground", "continuityworks:archetype/underground_vehicle_staging_integration_complex", (190, 20)),
            ],
            "extras": [
                {"id": "campus_utility", "kind": "external_anchor", "site_pos": (10, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "transfer_utility", "kind": "external_anchor", "site_pos": (100, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "underground_utility", "kind": "external_anchor", "site_pos": (190, 0), "sockets": [{"id": "service", "profile": "power_service_corridor_3x3", "group": "utility", "flow": "bidirectional", "required": True}]},
                {"id": "pad", "kind": "launch_anchor", "site_pos": (280, 20), "sockets": [{"id": "service", "profile": "launch_mount_service_axis", "group": "launch_support", "flow": "bidirectional", "required": True}]},
            ],
            "edges": [
                ("campus", "transport", "transfer", "inbound"),
                ("transfer", "outbound", "underground", "transport"),
                ("underground", "launch", "pad", "service"),
                ("campus", "utility", "campus_utility", "service"),
                ("transfer", "utility", "transfer_utility", "service"),
                ("underground", "utility", "underground_utility", "service"),
            ],
        },
    }

    def __init__(self, facility_library=None, network_validator=None):
        self.facilities = facility_library or FacilityLibrary()
        self.network = network_validator or AerospaceSupportNetworkValidator(
            structure_library=self.facilities.structures
        )
        self._reference_by_archetype: dict[str, str] = {}
        for entry in self.facilities.entries(
            kind="facility_reference", category="aerospace_support"
        ):
            reference = self.facilities.load(entry["id"])
            self._reference_by_archetype.setdefault(reference["archetype_id"], entry["id"])

    @classmethod
    def _rng(cls, seed, scale):
        if isinstance(seed, bool) or not isinstance(seed, (int, str)) or not str(seed):
            raise SeededAerospaceSupportCampusError(
                "Seed must be a non-empty integer or string"
            )
        if scale not in cls.SCALES:
            raise SeededAerospaceSupportCampusError(f"Unsupported campus scale: {scale}")
        text = str(seed)
        digest = hashlib.sha256(f"{cls.CONTRACT}|{scale}|{text}".encode()).hexdigest()
        return text, digest, random.Random(int(digest[:32], 16))

    def generate(self, scale, seed, corporate_language_id=None):
        seed_text, seed_digest, rng = self._rng(seed, scale)
        template = deepcopy(self.TEMPLATES[scale])
        archetype_ids = [item[1] for item in template["facilities"]]
        common_operators = None
        for archetype_id in archetype_ids:
            archetype = self.facilities.load(archetype_id)
            allowed = set(archetype.get("allowed_corporate_languages", []))
            common_operators = allowed if common_operators is None else common_operators & allowed
        choices = sorted(common_operators or set())
        if not choices:
            raise SeededAerospaceSupportCampusError(
                f"No common operator language for {scale} campus template"
            )
        operator = corporate_language_id or rng.choice(choices)
        if operator not in choices:
            raise SeededAerospaceSupportCampusError(
                f"{operator} is not compatible with every {scale} campus facility"
            )

        orientation = rng.choice(self.ORIENTATIONS)
        spacing = rng.choice(self.SPACING)
        terrain = rng.choice(self.TERRAIN[scale])

        nodes = []
        positions = {}
        for node_id, archetype_id, pos in template["facilities"]:
            node = self._facility_node(node_id, archetype_id, operator, rng)
            nodes.append(node)
            positions[node_id] = pos
        for extra in template["extras"]:
            node = deepcopy(extra)
            positions[node["id"]] = tuple(node.pop("site_pos"))
            nodes.append(node)

        self._apply_positions(nodes, positions, orientation, spacing)
        edges = [
            {
                "a": {"node": a_node, "socket": a_socket},
                "b": {"node": b_node, "socket": b_socket},
            }
            for a_node, a_socket, b_node, b_socket in template["edges"]
        ]
        graph = {
            "contract": self.network.CONTRACT,
            "generation_contract": self.CONTRACT,
            "graph_id": f"continuityworks:seeded/aerospace_support/{scale}/{seed_digest[:16]}",
            "seed": seed_text,
            "seed_digest": seed_digest,
            "scale": scale,
            "corporate_language_id": operator,
            "site_context": {
                "orientation": orientation,
                "spacing": spacing,
                "terrain": terrain,
            },
            "nodes": nodes,
            "edges": edges,
        }
        validation = self.network.validate_graph(graph)
        fingerprint = self.graph_fingerprint(graph)
        graph["campus_fingerprint"] = fingerprint
        return {
            "graph": graph,
            "report": {
                "gate": "SEEDED_AEROSPACE_SUPPORT_CAMPUS",
                "status": validation["status"],
                "generation_contract": self.CONTRACT,
                "seed": seed_text,
                "seed_digest": seed_digest,
                "scale": scale,
                "corporate_language_id": operator,
                "facility_archetypes": archetype_ids,
                "node_count": validation["node_count"],
                "edge_count": validation["edge_count"],
                "launch_anchor_count": validation["launch_anchor_count"],
                "site_context": graph["site_context"],
                "campus_fingerprint": fingerprint,
                "network_findings": validation["findings"],
            },
        }

    def _facility_node(self, node_id, archetype_id, operator, rng):
        archetype = self.facilities.load(archetype_id)
        support = archetype.get("support_network", {})
        vessel = archetype.get("vessel_state_support", {})
        classes = list(vessel.get("classes", []))
        states = list(vessel.get("states", []))
        if not classes or not states:
            raise SeededAerospaceSupportCampusError(
                f"Missing vessel state support: {archetype_id}"
            )
        return {
            "id": node_id,
            "kind": "facility",
            "archetype_id": archetype_id,
            "reference_id": self._reference_by_archetype.get(archetype_id),
            "corporate_language_id": operator,
            "scale": archetype["scale_tiers"][0],
            "support_design_mode": archetype.get("support_design_mode"),
            "vessel_class": rng.choice(classes),
            "vessel_state": rng.choice(states),
            "requirements": deepcopy(support.get("requirements", {})),
            "sockets": [
                {
                    "id": socket["id"],
                    "profile": socket["profile"],
                    "group": socket["group"],
                    "flow": socket.get("flow", "bidirectional"),
                    "required": False,
                }
                for socket in support.get("sockets", [])
            ],
        }

    @staticmethod
    def _apply_positions(nodes, positions, orientation, spacing):
        factor = 1 if spacing == "compact" else 2

        def rotate(x, z):
            if orientation == "north":
                return x, z
            if orientation == "east":
                return z, -x
            if orientation == "south":
                return -x, -z
            return -z, x

        rotated = {
            node_id: rotate(pos[0] * factor, pos[1] * factor)
            for node_id, pos in positions.items()
        }
        min_x = min(x for x, _ in rotated.values())
        min_z = min(z for _, z in rotated.values())
        normalized = {
            node_id: [x - min_x, z - min_z]
            for node_id, (x, z) in rotated.items()
        }
        for node in nodes:
            node["site_pos"] = normalized[node["id"]]

    @staticmethod
    def graph_fingerprint(graph):
        data = deepcopy(graph)
        data.pop("campus_fingerprint", None)
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
