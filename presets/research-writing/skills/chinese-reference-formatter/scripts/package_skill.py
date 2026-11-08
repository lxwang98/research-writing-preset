#!/usr/bin/env python3
"""Build a portable, versioned skill ZIP from an explicit file list."""

import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = (
    "SKILL.md",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "agents/openai.yaml",
    "references/chinese-reference-rules.md",
    "scripts/format_reference.py",
    "examples/metadata.json",
)


def package_skill(output_dir: Path, expected_version: str = "") -> Path:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    name = re.search(r"^name: ([a-z0-9-]+)$", text, re.M).group(1)
    version = re.search(r'^  version: "(\d+\.\d+\.\d+)"$', text, re.M).group(1)
    if expected_version and expected_version != version:
        raise ValueError(
            f"Requested version {expected_version!r} does not match SKILL.md {version!r}."
        )
    # Read everything before writing an archive, so missing files fail atomically.
    contents = [
        (relative, (ROOT / relative).read_bytes()) for relative in PACKAGE_FILES
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{name}-{version}.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for relative, content in contents:
            info = ZipInfo(f"{name}/{relative}")
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, content)
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument(
        "--version",
        default="",
        help="Require this version (used for release tag validation).",
    )
    args = parser.parse_args()
    try:
        print(package_skill(args.output_dir, args.version))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
