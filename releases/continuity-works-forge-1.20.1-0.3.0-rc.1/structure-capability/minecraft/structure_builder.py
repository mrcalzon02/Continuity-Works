from __future__ import annotations
import gzip, hashlib, io, struct

DATA_VERSION = 3955

def u16(n): return struct.pack(">H", n)
def i32(n): return struct.pack(">i", n)
def s(text):
    b = text.encode("utf-8")
    return u16(len(b)) + b
def tag_string(name, value): return b"\x08" + s(name) + s(value)
def tag_int(name, value): return b"\x03" + s(name) + i32(value)
def compound_payload(items): return b"".join(items) + b"\x00"
def tag_compound(name, items): return b"\x0a" + s(name) + compound_payload(items)
def tag_list(name, elem_type, payloads): return b"\x09" + s(name) + bytes([elem_type]) + i32(len(payloads)) + b"".join(payloads)
def list_compound_payload(items): return compound_payload(items)

class StructureBuilder:
    """Deterministic vanilla Minecraft structure-NBT builder."""

    def __init__(self, size, data_version=DATA_VERSION, registry_resolver=None):
        self.size = tuple(size)
        self.data_version = int(data_version)
        self.registry_resolver = registry_resolver
        self.palette, self.index, self.blocks = [], {}, {}

    def state(self, name, props=None):
        if self.registry_resolver and not self.registry_resolver.verified(name):
            raise ValueError(f"Unverified registry ID: {name}")
        key = (name, tuple(sorted((props or {}).items())))
        if key not in self.index:
            self.index[key] = len(self.palette)
            self.palette.append((name, dict(props or {})))
        return self.index[key]

    def set(self, x, y, z, name, props=None, nbt=None):
        self.blocks[(x, y, z)] = (self.state(name, props), nbt)

    def remove(self, x, y, z):
        self.blocks.pop((x, y, z), None)

    def cut(self, x1, y1, z1, x2, y2, z2):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    self.remove(x, y, z)

    def fill(self, x1, y1, z1, x2, y2, z2, name, props=None, nbt=None):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    self.set(x, y, z, name, props, nbt)

    def hollow_box(self, x1, y1, z1, x2, y2, z2, wall, floor=None, roof=None):
        floor, roof = floor or wall, roof or wall
        self.fill(x1, y1, z1, x2, y1, z2, floor)
        self.fill(x1, y2, z1, x2, y2, z2, roof)
        for y in range(y1 + 1, y2):
            for x in range(x1, x2 + 1):
                self.set(x, y, z1, wall); self.set(x, y, z2, wall)
            for z in range(z1 + 1, z2):
                self.set(x1, y, z, wall); self.set(x2, y, z, wall)

    def chest(self, x, y, z, loot, facing="north"):
        nbt = [tag_string("id", "minecraft:chest"), tag_string("LootTable", loot)]
        self.set(x, y, z, "minecraft:chest",
                 {"facing": facing, "type": "single", "waterlogged": "false"}, nbt)

    def raw(self):
        pal = []
        for name, props in self.palette:
            fields = [tag_string("Name", name)]
            if props:
                fields.append(tag_compound("Properties", [tag_string(k, v) for k, v in sorted(props.items())]))
            pal.append(list_compound_payload(fields))
        blocks = []
        for (x, y, z), (state, nbt) in sorted(self.blocks.items()):
            fields = [tag_int("state", state), tag_list("pos", 3, [i32(x), i32(y), i32(z)])]
            if nbt:
                fields.append(tag_compound("nbt", nbt))
            blocks.append(list_compound_payload(fields))
        root = [
            tag_int("DataVersion", self.data_version),
            tag_list("size", 3, [i32(v) for v in self.size]),
            tag_list("palette", 10, pal),
            tag_list("blocks", 10, blocks),
            tag_list("entities", 10, []),
        ]
        return b"\x0a\x00\x00" + compound_payload(root)

    def bytes(self):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(self.raw())
        return buf.getvalue()

    def git_blob_sha1(self):
        data = self.bytes()
        return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
