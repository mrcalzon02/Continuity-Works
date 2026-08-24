from __future__ import annotations
from pathlib import Path
import gzip, io, struct

class NBTReader:
    def __init__(self, data: bytes):
        self.f = io.BytesIO(data)

    def read(self, n):
        b = self.f.read(n)
        if len(b) != n:
            raise EOFError("Unexpected end of NBT")
        return b

    def u8(self): return self.read(1)[0]
    def i8(self): return struct.unpack(">b", self.read(1))[0]
    def i16(self): return struct.unpack(">h", self.read(2))[0]
    def i32(self): return struct.unpack(">i", self.read(4))[0]
    def i64(self): return struct.unpack(">q", self.read(8))[0]
    def f32(self): return struct.unpack(">f", self.read(4))[0]
    def f64(self): return struct.unpack(">d", self.read(8))[0]
    def string(self):
        n = struct.unpack(">H", self.read(2))[0]
        return self.read(n).decode("utf-8")

    def payload(self, tag):
        if tag == 0: return None
        if tag == 1: return self.i8()
        if tag == 2: return self.i16()
        if tag == 3: return self.i32()
        if tag == 4: return self.i64()
        if tag == 5: return self.f32()
        if tag == 6: return self.f64()
        if tag == 7:
            return list(self.read(self.i32()))
        if tag == 8: return self.string()
        if tag == 9:
            item = self.u8()
            return [self.payload(item) for _ in range(self.i32())]
        if tag == 10:
            out = {}
            while True:
                t = self.u8()
                if t == 0: break
                name = self.string()
                out[name] = self.payload(t)
            return out
        if tag == 11:
            return [self.i32() for _ in range(self.i32())]
        if tag == 12:
            return [self.i64() for _ in range(self.i32())]
        raise ValueError(f"Unsupported NBT tag {tag}")

    def root(self):
        tag = self.u8()
        if tag != 10:
            raise ValueError(f"NBT root must be compound, got {tag}")
        name = self.string()
        return name, self.payload(10)

def load_nbt(path_or_bytes):
    data = Path(path_or_bytes).read_bytes() if isinstance(path_or_bytes, (str, Path)) else bytes(path_or_bytes)
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return NBTReader(data).root()[1]

def load_structure_nbt(path_or_bytes):
    root = load_nbt(path_or_bytes)
    required = ("size", "palette", "blocks")
    missing = [k for k in required if k not in root]
    if missing:
        raise ValueError(f"Not a standard structure NBT; missing {missing}")
    return root
