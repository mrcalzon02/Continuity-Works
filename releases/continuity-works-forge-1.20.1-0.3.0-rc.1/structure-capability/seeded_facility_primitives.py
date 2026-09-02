from __future__ import annotations

class SeededFacilityGenerationError(ValueError):
    pass


class _Plan:
    def __init__(self, size, palette):
        self.size, self.palette, self.blocks = list(size), dict(palette), {}

    def _block(self, role):
        block = role if role.startswith("minecraft:") else self.palette.get(role)
        if not isinstance(block, str) or not block.startswith("minecraft:"):
            raise SeededFacilityGenerationError(f"Invalid vanilla material role: {role}")
        return block

    def put(self, x, y, z, role):
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]):
            raise SeededFacilityGenerationError(f"Block {(x, y, z)} outside {self.size}")
        self.blocks[(x, y, z)] = self._block(role)

    def box(self, a, b, role, hollow=False):
        for x in range(a[0], b[0] + 1):
            for y in range(a[1], b[1] + 1):
                for z in range(a[2], b[2] + 1):
                    if not hollow or x in (a[0], b[0]) or y in (a[1], b[1]) or z in (a[2], b[2]):
                        self.put(x, y, z, role)

    def line(self, a, b, role):
        d = tuple(b[i] - a[i] for i in range(3))
        n = max(abs(v) for v in d)
        if not n:
            self.put(*a, role)
            return
        for step in range(n + 1):
            t = step / n
            self.put(*(int(round(a[i] + d[i] * t)) for i in range(3)), role)

    def cyl(self, cx, cz, radius, y0, y1, role):
        for x in range(cx - radius, cx + radius + 1):
            for z in range(cz - radius, cz + radius + 1):
                if (x - cx) ** 2 + (z - cz) ** 2 > radius**2:
                    continue
                edge = any(
                    (nx - cx) ** 2 + (nz - cz) ** 2 > radius**2
                    for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))
                )
                for y in range(y0, y1 + 1):
                    if edge or y in (y0, y1):
                        self.put(x, y, z, role)

    def fence(self, gate_x):
        w, d = self.size[0], self.size[2]
        gap = set(range(gate_x - 2, gate_x + 3))
        for x in range(1, w - 1):
            if x not in gap:
                self.put(x, 1, 1, "fence")
            self.put(x, 1, d - 2, "fence")
        for z in range(1, d - 1):
            self.put(1, 1, z, "fence")
            self.put(w - 2, 1, z, "fence")

    def structure(self):
        return {
            "size": self.size,
            "blocks": [{"pos": list(p), "block": b} for p, b in sorted(self.blocks.items())],
        }



class FacilityGrammarHelpers:
    @staticmethod
    def _idx(scale, tiers):
        if scale not in tiers:
            raise SeededFacilityGenerationError(f"Scale {scale!r} not in {tiers}")
        return tiers.index(scale)

    @staticmethod
    def _building(p, x, z, w, d, h=4, glass=False):
        p.box((x, 1, z), (x + w - 1, h, z + d - 1), "primary_wall", hollow=True)
        p.box((x, h, z), (x + w - 1, h, z + d - 1), "roof")
        if glass:
            for xx in range(x + 2, x + w - 2):
                p.put(xx, 2, z, "glass")
                p.put(xx, 3, z, "glass")

    @staticmethod
    def _gantry(p, x, z, w=8, d=7, h=5):
        for xx in (x, x + w):
            for zz in (z, z + d):
                p.line((xx, 1, zz), (xx, h, zz), "metal")
        p.line((x, h, z), (x + w, h, z), "metal")
        p.line((x, h, z + d), (x + w, h, z + d), "metal")
        p.line((x, h, z), (x, h, z + d), "pipe")
        p.line((x + w, h, z), (x + w, h, z + d), "pipe")
