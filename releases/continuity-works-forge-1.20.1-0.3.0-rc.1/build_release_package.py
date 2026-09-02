#!/usr/bin/env python3
"""Build the Continuity Works Forge 1.20.1 release candidate package.

The builder fails closed: a distributable ZIP is only created after a usable JAR
has been found for both Forge projects. No GitHub Actions or external Python
packages are required.
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

VERSION = "0.3.0-rc.1"
PACKAGE_NAME = f"continuity-works-forge-1.20.1-{VERSION}"
HERE = Path(__file__).resolve().parent
BIOME_PROJECT = HERE / "biome-runtime"
PROTECTION_PROJECT = HERE / "structure-spawn-protection"
STRUCTURE_CAPABILITY = HERE / "structure-capability"
ERA_SPECS = HERE / "era-structure-specs"
DIST = HERE / "dist"
STAGE = DIST / PACKAGE_NAME
ZIP_PATH = DIST / f"{PACKAGE_NAME}.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Use existing build/libs outputs instead of invoking Gradle.",
    )
    return parser.parse_args()


def require_path(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {description}: {path}")


def gradle_command(project: Path) -> list[str]:
    own_sh = project / "gradlew"
    own_bat = project / "gradlew.bat"
    shared_sh = BIOME_PROJECT / "gradlew"
    shared_bat = BIOME_PROJECT / "gradlew.bat"

    if os.name == "nt":
        if own_bat.exists():
            return [str(own_bat), "clean", "build"]
        if shared_bat.exists():
            return [str(shared_bat), "-p", str(project), "clean", "build"]
    else:
        if own_sh.exists():
            return ["bash", str(own_sh), "clean", "build"]
        if shared_sh.exists():
            return ["bash", str(shared_sh), "-p", str(project), "clean", "build"]

    gradle = shutil.which("gradle")
    if gradle:
        return [gradle, "-p", str(project), "clean", "build"]

    raise SystemExit(
        f"No Gradle launcher is available for {project}. Install Gradle or retain "
        "the biome-runtime Gradle wrapper."
    )


def build_project(project: Path, label: str) -> None:
    command = gradle_command(project)
    print(f"[build] {label}: {' '.join(command)}")
    subprocess.run(command, cwd=project, check=True)


def select_runtime_jar(project: Path, label: str) -> Path:
    libs = project / "build" / "libs"
    require_path(libs, f"{label} build output directory")
    jars = [
        path
        for path in libs.glob("*.jar")
        if not any(token in path.name.lower() for token in ("sources", "javadoc", "dev", "slim"))
    ]
    if not jars:
        raise SystemExit(f"No runtime JAR found for {label} in {libs}")
    jars.sort(key=lambda path: (path.stat().st_size, path.name), reverse=True)
    selected = jars[0]
    if selected.stat().st_size == 0:
        raise SystemExit(f"Runtime JAR for {label} is empty: {selected}")
    print(f"[jar] {label}: {selected.name}")
    return selected


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stage_package(biome_jar: Path, protection_jar: Path) -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    mods = STAGE / "mods"
    structures = STAGE / "structures"
    mods.mkdir()
    structures.mkdir()

    shutil.copy2(biome_jar, mods / biome_jar.name)
    shutil.copy2(protection_jar, mods / protection_jar.name)
    shutil.copytree(STRUCTURE_CAPABILITY, structures / "structure-capability")
    shutil.copytree(ERA_SPECS, structures / "era-structure-specs")
    shutil.copy2(HERE / "README.md", STAGE / "README.md")
    shutil.copy2(HERE / "RELEASE_MANIFEST.json", STAGE / "RELEASE_MANIFEST.json")

    checksum_lines = []
    for jar in sorted(mods.glob("*.jar")):
        checksum_lines.append(f"{sha256(jar)}  mods/{jar.name}")
    (STAGE / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")


def write_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                arcname = Path(PACKAGE_NAME) / path.relative_to(STAGE)
                archive.write(path, arcname.as_posix())
    if not ZIP_PATH.exists() or ZIP_PATH.stat().st_size == 0:
        raise SystemExit("ZIP creation failed: output is missing or empty")


def main() -> int:
    args = parse_args()
    for path, description in (
        (BIOME_PROJECT, "biome runtime project"),
        (PROTECTION_PROJECT, "spawn protection project"),
        (STRUCTURE_CAPABILITY, "structure capability snapshot"),
        (ERA_SPECS, "era structure specification snapshot"),
        (HERE / "README.md", "release README"),
        (HERE / "RELEASE_MANIFEST.json", "release manifest"),
    ):
        require_path(path, description)

    if not args.skip_build:
        build_project(BIOME_PROJECT, "Continuity Works Biomes")
        build_project(PROTECTION_PROJECT, "Structure Spawn Protection")

    biome_jar = select_runtime_jar(BIOME_PROJECT, "Continuity Works Biomes")
    protection_jar = select_runtime_jar(PROTECTION_PROJECT, "Structure Spawn Protection")
    stage_package(biome_jar, protection_jar)
    write_zip()

    print(f"[success] Binary release package: {ZIP_PATH}")
    print(f"[sha256] {sha256(ZIP_PATH)}  {ZIP_PATH.name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Build failed with exit code {exc.returncode}: {' '.join(map(str, exc.cmd))}", file=sys.stderr)
        raise SystemExit(exc.returncode)
