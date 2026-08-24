from __future__ import annotations
from dataclasses import dataclass, asdict
import re

# Verified common Java Edition release targets used heavily by modding projects.
# Unknown patch versions remain valid layout targets, but NBT materialization must
# receive an explicit DataVersion rather than guessing.
KNOWN_RELEASES = {
    "1.12.2": {"data_version": 1343, "resource_pack_format": 3, "data_pack_format": None},
    "1.16.5": {"data_version": 2586, "resource_pack_format": 6, "data_pack_format": 6},
    "1.18.2": {"data_version": 2975, "resource_pack_format": 8, "data_pack_format": 9},
    "1.19.2": {"data_version": 3120, "resource_pack_format": 9, "data_pack_format": 10},
    "1.19.4": {"data_version": 3337, "resource_pack_format": 13, "data_pack_format": 12},
    "1.20.1": {"data_version": 3465, "resource_pack_format": 15, "data_pack_format": 15},
    "1.21": {"data_version": 3953, "resource_pack_format": 34, "data_pack_format": 48},
    "1.21.1": {"data_version": 3955, "resource_pack_format": 34, "data_pack_format": 48},
}

@dataclass(frozen=True)
class MinecraftVersionProfile:
    requested: str
    normalized: str
    family: str
    namespaced_ids: bool
    flattening: bool
    structure_nbt: bool
    datapack_worldgen: bool
    jigsaw_worldgen: bool
    data_version: int | None = None
    resource_pack_format: int | None = None
    data_pack_format: int | None = None
    exact_release_metadata: bool = False
    structure_block_limit: int = 48
    notes: tuple[str, ...] = ()

    def to_dict(self):
        out = asdict(self)
        out["notes"] = list(self.notes)
        return out


def _parts(version: str) -> tuple[int, int, int]:
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", version)
    if not m:
        raise ValueError(f"Unsupported Minecraft version syntax: {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def resolve_minecraft_version(version: str | None) -> MinecraftVersionProfile:
    version = str(version or "1.20.1").strip()
    major, minor, patch = _parts(version)
    if major != 1 or minor < 12:
        raise ValueError("Initial compatibility contract supports Minecraft Java 1.12.x and newer 1.x releases")
    normalized = f"{major}.{minor}.{patch}"
    lookup_key = version if version in KNOWN_RELEASES else normalized
    metadata = KNOWN_RELEASES.get(lookup_key)
    flattening = minor >= 13
    datapack_worldgen = minor >= 16
    jigsaw_worldgen = minor >= 14
    if minor <= 12:
        family = "legacy_pre_flattening"
        notes = ["Legacy numeric/block-state compatibility adapter required for final materialization."]
    elif minor <= 15:
        family = "namespaced_pre_worldgen_datapack"
        notes = ["Namespaced block states supported; modern datapack worldgen JSON is not assumed."]
    elif minor <= 17:
        family = "early_datapack_worldgen"
        notes = ["Datapack worldgen supported; registry details should be validated against target runtime."]
    elif minor <= 20:
        family = "modern_1_18_to_1_20"
        notes = ["Modern height/worldgen assumptions supported; registry details remain target-version specific."]
    else:
        family = "modern_1_21_plus"
        notes = ["Modern structure NBT supported; validate changing registry/worldgen schemas at the target runtime."]
    if metadata is None:
        notes.append("Exact release metadata is not bundled for this patch; supply DataVersion explicitly before NBT materialization.")
    return MinecraftVersionProfile(
        requested=version,
        normalized=normalized,
        family=family,
        namespaced_ids=minor >= 13,
        flattening=flattening,
        structure_nbt=True,
        datapack_worldgen=datapack_worldgen,
        jigsaw_worldgen=jigsaw_worldgen,
        data_version=metadata.get("data_version") if metadata else None,
        resource_pack_format=metadata.get("resource_pack_format") if metadata else None,
        data_pack_format=metadata.get("data_pack_format") if metadata else None,
        exact_release_metadata=metadata is not None,
        structure_block_limit=32 if minor < 16 else 48,
        notes=tuple(notes),
    )
