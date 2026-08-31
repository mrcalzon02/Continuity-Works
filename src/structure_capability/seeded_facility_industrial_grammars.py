from __future__ import annotations

from .seeded_facility_primitives import _Plan, FacilityGrammarHelpers


class IndustrialFacilityGrammars(FacilityGrammarHelpers):
    def _g_crude_oil_well_pad(self, rng, pal, corp, scale):
        i = self._idx(scale, ["small", "medium"])
        size = [50 + 12 * i, 14, 46 + 8 * i]
        p, gate = _Plan(size, pal), size[0] // 2
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "gravel")
        p.fence(gate)
        p.box((gate - 2, 0, 0), (gate + 2, 0, size[2] // 2), "ground")
        x, z = size[0] // 3, size[2] // 2
        p.box((x - 4, 0, z - 4), (x + 4, 0, z + 4), "foundation")
        for xx in (x - 2, x + 2):
            p.line((xx, 1, z), (xx, 7 + i, z), "dark_metal")
        p.line((x - 5, 7 + i, z), (x + 6, 7 + i, z), "metal")
        p.box((x + 5, 5 + i, z - 1), (x + 7, 7 + i, z + 1), "accent_primary")
        tanks, centers, tx = 1 + i + rng.randint(0, 1), [], size[0] - 10
        for n in range(tanks):
            tz = min(size[2] - 8, 12 + n * 12)
            p.cyl(tx, tz, 3, 1, 6, "tank")
            p.cyl(tx, tz, 3, 5, 5, "accent_secondary")
            centers.append([tx, tz])
        p.line((x + 2, 2, z), (tx - 4, 2, z), "pipe")
        for _, tz in centers:
            p.line((tx - 4, 2, z), (tx - 3, 2, tz), "pipe")
        self._building(p, 4, size[2] - 10, 8, 7)
        return {"plan": p, "signatures": ["pumpjack", "open_equipment_pad", "crude_storage", "visible_product_piping", "control_shed", "perimeter_fence", "service_road"],
                "modules": {self.M["pumpjack"]: 1, self.M["tank"]: tanks, self.M["pipe"]: 1, self.M["utility"]: 1},
                "variant": {"tank_count": tanks, "tank_centers": centers, "pumpjack_height": 8 + i, "gate_center": gate}}

    def _g_bulk_tank_farm(self, rng, pal, corp, scale):
        i = self._idx(scale, ["medium", "large"])
        size = [74 + 18 * i, 15, 60 + 14 * i]
        p, gate = _Plan(size, pal), size[0] // 2
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "ground")
        p.fence(gate)
        rows, cols, centers = 2 + i, 2 + i + rng.randint(0, 1), []
        for r in range(rows):
            for c in range(cols):
                x, z = 15 + c * 16, 18 + r * 16
                if x + 5 >= size[0] - 2 or z + 5 >= size[2] - 2:
                    continue
                p.cyl(x, z, 4, 1, 7, "tank")
                p.cyl(x, z, 4, 6, 6, "accent_secondary")
                centers.append([x, z])
        x0, x1 = min(x for x, _ in centers) - 6, max(x for x, _ in centers) + 6
        z0, z1 = min(z for _, z in centers) - 6, max(z for _, z in centers) + 6
        p.line((x0, 1, z0), (x1, 1, z0), "foundation"); p.line((x0, 1, z1), (x1, 1, z1), "foundation")
        p.line((x0, 1, z0), (x0, 1, z1), "foundation"); p.line((x1, 1, z0), (x1, 1, z1), "foundation")
        hx = min(size[0] - 10, x1 + 1)
        p.line((hx, 3, z0), (hx, 3, z1), "pipe")
        for x, z in centers:
            p.line((x + 4, 3, z), (hx, 3, z), "pipe")
        self._gantry(p, gate - 4, 5, 8, 8)
        self._building(p, size[0] - 13, size[2] - 10, 9, 7)
        return {"plan": p, "signatures": ["repeated_storage_tanks", "containment_perimeter", "pipe_header", "loading_point", "control_building", "security_fence", "service_lanes"],
                "modules": {self.M["tank"]: len(centers), self.M["pipe"]: 1, self.M["gantry"]: 1, self.M["utility"]: 1},
                "variant": {"tank_rows": rows, "tank_columns_requested": cols, "tank_count": len(centers), "tank_centers": centers, "containment_bounds": [x0, z0, x1, z1]}}

    def _g_compact_diesel_refinery(self, rng, pal, corp, scale):
        i = self._idx(scale, ["medium", "large"])
        size = [88 + 20 * i, 25 + 3 * i, 70 + 14 * i]
        p, gate = _Plan(size, pal), size[0] // 2
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "ground")
        p.fence(gate)
        count, columns = 2 + i + rng.randint(0, 1), []
        for n in range(count):
            x, z, h = 18 + n * 11, 24 + (n % 2) * 12, 14 + 3 * i + rng.randint(0, 3)
            p.cyl(x, z, 2, 1, h, "metal")
            for y in range(4, h, 4):
                p.cyl(x, z, 2, y, y, "accent_secondary")
            columns.append([x, z, h])
        rz = 45 + 4 * i
        p.line((10, 4, rz), (size[0] - 24, 4, rz), "pipe")
        p.line((10, 6, rz + 2), (size[0] - 24, 6, rz + 2), "pipe")
        for x, z, _ in columns:
            p.line((x, 4, z + 2), (x, 4, rz), "pipe")
        requested, centers, tx = 2 + i + rng.randint(0, 1), [], size[0] - 16
        for n in range(requested):
            z = 16 + n * 15
            if z + 5 >= size[2] - 3:
                break
            p.cyl(tx, z, 4, 1, 7, "tank"); p.cyl(tx, z, 4, 6, 6, "accent_primary")
            p.line((tx - 4, 3, z), (size[0] - 24, 3, rz), "pipe")
            centers.append([tx, z])
        fx, fz, top = size[0] - 8, size[2] - 8, size[1] - 3
        p.line((fx, 1, fz), (fx, top, fz), "dark_metal")
        for y in range(5, top, 5):
            p.put(fx, y, fz, "hazard")
        p.put(fx, top + 1, fz, "flare")
        bays = 1 + i + rng.randint(0, 1)
        for n in range(bays):
            self._gantry(p, 8 + n * 10, 6, 8, 8)
        self._building(p, 6, size[2] - 13, 12, 9, 5)
        return {"plan": p, "signatures": ["process_columns", "dense_pipe_network", "product_tanks", "flare_stack", "loading_gantry", "control_building", "utility_yard", "perimeter_security"],
                "modules": {self.M["column"]: count, self.M["pipe"]: 2, self.M["tank"]: len(centers), self.M["flare"]: 1, self.M["gantry"]: bays, self.M["utility"]: 1},
                "variant": {"process_column_count": count, "process_columns": columns, "tank_count": len(centers), "tank_centers": centers, "loading_bays": bays, "flare_position": [fx, fz], "pipe_rack_z": rz}}

    def _g_truck_fuel_terminal(self, rng, pal, corp, scale):
        i = self._idx(scale, ["medium", "large"])
        size = [80 + 20 * i, 16, 60 + 14 * i]
        p, gate = _Plan(size, pal), size[0] // 2
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "ground")
        p.fence(gate)
        requested, centers, tz = 3 + i + rng.randint(0, 1), [], size[2] - 15
        for n in range(requested):
            x = 12 + n * 15
            if x + 5 >= size[0] - 3:
                break
            p.cyl(x, tz, 4, 1, 7, "tank"); p.cyl(x, tz, 4, 6, 6, "accent_secondary")
            centers.append([x, tz])
        hz = tz - 7
        p.line((8, 3, hz), (size[0] - 10, 3, hz), "pipe")
        for x, z in centers:
            p.line((x, 3, z - 4), (x, 3, hz), "pipe")
        bays = 3 + i + rng.randint(0, 1)
        start = max(5, (size[0] - bays * 10) // 2)
        for n in range(bays):
            x = start + n * 10
            self._gantry(p, x, 13, 8, 11)
            p.line((x + 4, 0, 3), (x + 4, 0, 28), "secondary_wall")
        p.line((gate - 4, 1, 2), (gate - 4, 5, 2), "metal"); p.line((gate + 4, 1, 2), (gate + 4, 5, 2), "metal")
        p.line((gate - 4, 5, 2), (gate + 4, 5, 2), "accent_primary")
        p.line((gate - 4, 4, 2), (gate + 4, 4, 2), "hazard")
        self._building(p, size[0] - 15, 6, 10, 8)
        branded = int(corp.endswith("northstar_fuel"))
        if branded:
            p.box((4, 1, 3), (5, 7, 4), "sign"); p.box((3, 5, 2), (6, 7, 5), "accent_primary")
        return {"plan": p, "signatures": ["bulk_tanks", "multiple_loading_bays", "pipe_header", "controlled_vehicle_gate", "operations_building", "fleet_queue", "security_fence"],
                "modules": {self.M["tank"]: len(centers), self.M["pipe"]: 1, self.M["gantry"]: bays, self.M["utility"]: 1, self.M["pylon"]: branded},
                "variant": {"tank_count": len(centers), "tank_centers": centers, "loading_bays": bays, "gate_center": gate, "queue_lane_count": bays}}
