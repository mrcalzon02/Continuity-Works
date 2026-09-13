from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Deliberately retained only inside this non-user-facing validation guard.
# Source and rendered/static guards reject every retired public identity.
RETIRED_PUBLIC_BRANDS = ("StructureForge", "Structure Forge", "StructureSmith")
RETIRED_SOURCE_BRANDS = RETIRED_PUBLIC_BRANDS
STATIC_TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".map",
    ".svg",
    ".txt",
    ".webmanifest",
    ".xml",
}
SOURCE_TEXT_SUFFIXES = STATIC_TEXT_SUFFIXES | {
    ".c",
    ".cfg",
    ".conf",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".jsx",
    ".kt",
    ".kts",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
SOURCE_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "releases",  # immutable historical release snapshots, not active source authority
    "venv",
}
# These two files must contain the retired literals so the guard can detect and test them.
SOURCE_LITERAL_ALLOWLIST = {
    Path("scripts/verify_branding.py"),
    Path("tests/test_branding_guard.py"),
}


def _find_branding_in_text(
    path: Path,
    relative_path: Path,
    brands: tuple[str, ...],
) -> list[tuple[Path, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    folded = text.casefold()
    findings: list[tuple[Path, str]] = []
    for original in brands:
        if original.casefold() in folded:
            findings.append((relative_path, original))
    return findings


def find_retired_branding(root: Path) -> list[tuple[Path, str]]:
    """Find retired branding in a rendered/static artifact."""
    findings: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in STATIC_TEXT_SUFFIXES:
            continue
        findings.extend(
            _find_branding_in_text(path, path.relative_to(root), RETIRED_PUBLIC_BRANDS)
        )
    return findings


def find_retired_source_branding(root: Path) -> list[tuple[Path, str]]:
    """Find retired pre-Continuity Works branding across active authoritative source."""
    findings: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in SOURCE_EXCLUDED_DIRS for part in relative.parts[:-1]):
            continue
        if relative in SOURCE_LITERAL_ALLOWLIST:
            continue
        findings.extend(_find_branding_in_text(path, relative, RETIRED_SOURCE_BRANDS))
    return findings


def _raise_on_findings(findings: list[tuple[Path, str]], *, surface: str) -> None:
    if findings:
        detail = ", ".join(f"{path} contains {brand!r}" for path, brand in findings)
        raise RuntimeError(f"retired Continuity Works branding leaked into {surface}: {detail}")


def verify_static_branding(directory: str | Path) -> None:
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f"static artifact directory does not exist: {root}")
    _raise_on_findings(find_retired_branding(root), surface="rendered/static artifact")


def verify_source_branding(directory: str | Path) -> None:
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f"source directory does not exist: {root}")
    _raise_on_findings(find_retired_source_branding(root), surface="authoritative source tree")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail if retired pre-Continuity Works branding appears in source or rendered artifacts."
    )
    parser.add_argument("--static-dir")
    parser.add_argument("--source-root")
    args = parser.parse_args()
    if not args.static_dir and not args.source_root:
        parser.error("at least one of --static-dir or --source-root is required")
    try:
        if args.source_root:
            verify_source_branding(args.source_root)
            print(f"Continuity Works source branding verified: {args.source_root}")
        if args.static_dir:
            verify_static_branding(args.static_dir)
            print(f"Continuity Works rendered branding verified: {args.static_dir}")
    except (ValueError, RuntimeError) as exc:
        print(f"BRANDING_VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
