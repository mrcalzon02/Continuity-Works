#!/usr/bin/env python3
"""Build and verify the single Continuity Works Forge 1.20.1 release JAR.

This replaces the rc.1 outer ZIP workflow. The command fails closed: it does not
produce or bless a distribution artifact unless the unified Forge project builds
and the resulting archive contains both runtime subsystems and their required
worldgen/protection resources.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

VERSION = "0.3.0-rc.2"
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
PROJECT = REPO_ROOT / "modules" / "continuityworks_runtime" / "forge-1.20.1"
DIST = HERE / "dist"
EXPECTED_NAME = f"ContinuityWorks-Forge-1.20.1-{VERSION}.jar"
OUTPUT = DIST / EXPECTED_NAME


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Validate/copy an existing unified build/libs JAR without invoking Gradle.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def gradle_command() -> list[str]:
    gradle = shutil.which("gradle")
    if gradle:
        return [gradle, "-p", str(PROJECT), "clean", "jarJar", "reobfJarJar"]
    raise SystemExit(
        "No Gradle executable is available. Build in a Forge-capable environment "
        "or use the repository JitPack configuration; no GitHub Actions are required."
    )


def run_build() -> None:
    command = gradle_command()
    print(f"[build] {' '.join(command)}")
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def select_jar() -> Path:
    libs = PROJECT / "build" / "libs"
    require(libs, "unified Forge build output directory")
    candidates = [
        path
        for path in libs.glob("*.jar")
        if not any(token in path.name.lower() for token in ("sources", "javadoc", "dev", "slim"))
    ]
    if not candidates:
        raise SystemExit(f"No runtime JAR found in {libs}")
    candidates.sort(key=lambda path: (path.stat().st_size, path.name), reverse=True)
    selected = candidates[0]
    if selected.stat().st_size == 0:
        raise SystemExit(f"Runtime JAR is empty: {selected}")
    return selected


def validate_jar(path: Path) -> dict[str, int]:
    if not zipfile.is_zipfile(path):
        raise SystemExit(f"Not a readable JAR/ZIP archive: {path}")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {
            "META-INF/mods.toml",
            "continuityworks_spawn_protection.mixins.json",
            "io/continuityworks/biomes/ContinuityWorksBiomeTemplates.class",
            "io/continuityworks/spawnprotection/ContinuityWorksSpawnProtection.class",
            "data/continuityworks_biomes/structures/abyssal/fracture_vent_field.nbt",
            "data/continuityworks_biomes/structures/abyssal/hadal_vent_complex.nbt",
        }
        missing = sorted(required - names)
        if missing:
            raise SystemExit("Unified JAR is missing required entries: " + ", ".join(missing))

        mods_toml = archive.read("META-INF/mods.toml").decode("utf-8", errors="strict")
        for mod_id in ("continuityworks_biomes", "continuityworks_spawn_protection"):
            if f'modId="{mod_id}"' not in mods_toml:
                raise SystemExit(f"mods.toml does not declare {mod_id}")

        biome_defs = [
            name
            for name in names
            if name.startswith("data/continuityworks_biomes/worldgen/biome/")
            and name.endswith(".json")
        ]
        if len(biome_defs) < 128:
            raise SystemExit(
                f"Expected at least 128 generated Continuity Works biome definitions; found {len(biome_defs)}"
            )

        mixin_classes = [
            name
            for name in names
            if name.startswith("io/continuityworks/spawnprotection/mixin/")
            and name.endswith(".class")
        ]
        if len(mixin_classes) < 3:
            raise SystemExit(
                f"Expected Structure Spawn Protection mixin classes; found {len(mixin_classes)}"
            )

        nested_jars = [name for name in names if name.startswith("META-INF/jarjar/")]
        if not nested_jars:
            raise SystemExit("Jar-in-Jar metadata is absent; TerraBlender embedding was not materialized")

        return {
            "entries": len(names),
            "biome_definitions": len(biome_defs),
            "spawn_protection_mixin_classes": len(mixin_classes),
            "materialized_nbt_structures": 2,
        }


def publish_local_copy(source: Path) -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    shutil.copy2(source, OUTPUT)
    if OUTPUT.stat().st_size == 0:
        raise SystemExit("Copied release JAR is empty")


def main() -> int:
    args = parse_args()
    require(PROJECT, "unified Forge project")
    require(PROJECT / "build.gradle", "unified Forge build file")
    require(PROJECT / "src/main/resources/META-INF/mods.toml", "unified mods.toml")

    if not args.skip_build:
        run_build()

    built = select_jar()
    metrics = validate_jar(built)
    publish_local_copy(built)
    copied_metrics = validate_jar(OUTPUT)
    if metrics != copied_metrics:
        raise SystemExit("Release-copy verification diverged from built JAR")

    print(f"[success] Forge release JAR: {OUTPUT}")
    print(f"[bytes] {OUTPUT.stat().st_size}")
    print(f"[sha256] {sha256(OUTPUT)}  {OUTPUT.name}")
    print(f"[contents] {metrics}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(
            f"Build failed with exit code {exc.returncode}: {' '.join(map(str, exc.cmd))}",
            file=sys.stderr,
        )
        raise SystemExit(exc.returncode)
