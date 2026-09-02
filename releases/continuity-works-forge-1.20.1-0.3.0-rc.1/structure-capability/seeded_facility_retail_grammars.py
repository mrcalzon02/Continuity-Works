from __future__ import annotations

from .seeded_facility_primitives import _Plan, FacilityGrammarHelpers


class RetailFacilityGrammars(FacilityGrammarHelpers):
    def _g_rural_gas_station(self, rng, pal, corp, scale):
        i = self._idx(scale, ["small", "medium"])
        size = [46 + 10 * i, 13, 38 + 6 * i]
        p = _Plan(size, pal)
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "ground")
        p.box((0, 0, 0), (size[0] - 1, 0, 5), "dark_metal")
        cw, cd, cy = 22 + 6 * i, 10 + 2 * i, 5
        x0, z0 = (size[0] - cw) // 2, 9
        p.box((x0, cy, z0), (x0 + cw - 1, cy, z0 + cd - 1), "roof")
        p.line((x0, cy, z0), (x0 + cw - 1, cy, z0), "accent_primary")
        p.line((x0, cy, z0 + cd - 1), (x0 + cw - 1, cy, z0 + cd - 1), "accent_secondary")
        for x in (x0 + 2, x0 + cw - 3):
            for z in (z0 + 1, z0 + cd - 2):
                p.line((x, 1, z), (x, cy, z), "metal")
        pumps = 2 + i + rng.randint(0, 1)
        for n in range(pumps):
            x = x0 + 4 + round(n * (cw - 9) / max(1, pumps - 1))
            z = z0 + cd // 2 - 1
            p.box((x, 1, z), (x + 1, 2, z + 2), "secondary_wall")
            p.put(x, 3, z + 1, "accent_primary")
        sw, sd = 18 + 5 * i + rng.randint(0, 2), 9 + 2 * i
        sx, sz = (size[0] - sw) // 2, size[2] - sd - 4
        self._building(p, sx, sz, sw, sd, 5, True)
        p.line((sx + 1, 4, sz), (sx + sw - 2, 4, sz), "accent_primary")
        px = 4 if rng.random() < .5 else size[0] - 6
        ph = 9 if corp.endswith("northstar_fuel") else 7
        p.box((px, 1, 2), (px + 1, ph, 3), "sign")
        p.box((px - 1, ph - 3, 1), (px + 2, ph - 1, 4), "accent_primary")
        service = bool(i or rng.random() < .45)
        if service:
            self._building(p, max(2, sx - 10), min(size[2] - 9, sz + 2), 7, 6)
        return {"plan": p, "signatures": ["fuel_canopy", "pump_islands", "storefront", "roadside_pylon", "parking", "rear_service", "brand_band"],
                "modules": {self.M["canopy"]: 1, self.M["pump"]: pumps, self.M["pylon"]: 1, self.M["room"]: 1, self.M["utility"]: int(service)},
                "variant": {"canopy_width": cw, "canopy_depth": cd, "pump_count": pumps, "store_width": sw, "store_depth": sd, "pylon_side": "west" if px < size[0] // 2 else "east", "rear_service": service}}

    def _g_highway_travel_stop(self, rng, pal, corp, scale):
        i = self._idx(scale, ["medium", "large"])
        size = [74 + 16 * i, 15, 56 + 10 * i]
        p = _Plan(size, pal)
        p.box((0, 0, 0), (size[0] - 1, 0, size[2] - 1), "ground")
        p.box((0, 0, 0), (size[0] - 1, 0, 6), "dark_metal")
        sw, sd = 28 + 8 * i + rng.randint(0, 4), 12 + 3 * i
        self._building(p, 6, size[2] - sd - 5, sw, sd, 6, True)
        p.line((7, 5, size[2] - sd - 5), (5 + sw, 5, size[2] - sd - 5), "accent_primary")
        x0, x1, z0, z1, cy = 7, 37 + 6 * i, 10, 24 + 2 * i, 6
        p.box((x0, cy, z0), (x1, cy, z1), "roof")
        p.line((x0, cy, z0), (x1, cy, z0), "accent_primary")
        pumps = 5 + 2 * i + rng.randint(0, 2)
        for n in range(pumps):
            x, z = x0 + 3 + (n % 4) * 7, z0 + 3 + (n // 4) * 6
            p.box((x, 1, z), (x + 1, 2, z + 2), "secondary_wall")
            p.put(x, 3, z + 1, "accent_primary")
        bays = 2 + i + rng.randint(0, 1)
        bx = max(x1 + 4, size[0] - 10 - bays * 9)
        for n in range(bays):
            self._gantry(p, bx + n * 9, 12, 7, 15)
        ph, px = 11, size[0] - 7
        p.box((px, 1, 2), (px + 1, ph, 3), "sign")
        p.box((px - 2, ph - 4, 1), (px + 3, ph - 1, 4), "accent_primary")
        rows = 2 + i
        for row in range(rows):
            for x in range(7, min(size[0] - 7, 54), 4):
                p.put(x, 0, 30 + row * 4, "secondary_wall")
        return {"plan": p, "signatures": ["fuel_canopy", "multiple_pump_islands", "large_storefront", "roadside_pylon", "truck_fueling_zone", "parking_field", "service_yard", "secondary_canopy"],
                "modules": {self.M["canopy"]: 1, self.M["pump"]: pumps, self.M["pylon"]: 1, self.M["room"]: 1, self.M["gantry"]: bays, self.M["utility"]: 1},
                "variant": {"pump_count": pumps, "truck_bays": bays, "store_width": sw, "store_depth": sd, "parking_rows": rows}}
