from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Deliberately retained only inside this non-user-facing validation guard.
# These literals identify retired public branding that must never ship again.
RETIRED_PUBLIC_BRANDS = ("StructureForge", "Structure Forge")
TEXT_SUFFIXES = {
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


def find_retired_branding(root: Path) -> list[tuple[Path, str]]:
    findings: list[tuple[Path, str]] = []
    retired = tuple(value.casefold() for value in RETIRED_PUBLIC_BRANDS)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        folded = text.casefold()
        for original, needle in zip(RETIRED_PUBLIC_BRANDS, retired):
            if needle in folded:
                findings.append((path.relative_to(root), original))
    return findings


def verify_static_branding(directory: str | Path) -> None:
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f"static artifact directory does not exist: {root}")
    findings = find_retired_branding(root)
    if findings:
        detail = ", ".join(f"{path} contains {brand!r}" for path, brand in findings)
        raise RuntimeError(f"retired Continuity Works branding leaked into rendered/static artifact: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail if retired StructureForge branding appears in a rendered Continuity Works static artifact."
    )
    parser.add_argument("--static-dir", required=True)
    args = parser.parse_args()
    try:
        verify_static_branding(args.static_dir)
    except (ValueError, RuntimeError) as exc:
        print(f"BRANDING_VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"Continuity Works branding verified: {args.static_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
