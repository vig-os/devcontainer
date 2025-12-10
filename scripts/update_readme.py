#!/usr/bin/env python3
"""Helpers for patching README metadata lines."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_PATTERN = re.compile(r"^- \*\*Version\*\*:.*$", re.MULTILINE)
SIZE_PATTERN = re.compile(r"^- \*\*Size\*\*:.*$", re.MULTILINE)


def update_version_line(
    readme_path: Path | str, version: str, release_url: str, release_date: str
) -> str:
    """Replace the version line with `[version](url), date`."""
    path = Path(readme_path)
    text = path.read_text()
    replacement = f"- **Version**: [{version}]({release_url}), {release_date}"
    updated_text, count = VERSION_PATTERN.subn(replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Version line not found in {path}")
    path.write_text(updated_text)
    return replacement


def update_size_line(readme_path: Path | str, size_mb: int) -> str:
    """Replace the size line with `~{size_mb} MB`."""
    path = Path(readme_path)
    text = path.read_text()
    replacement = f"- **Size**: ~{size_mb} MB"
    updated_text, count = SIZE_PATTERN.subn(replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Size line not found in {path}")
    path.write_text(updated_text)
    return replacement


def parse_args() -> tuple[str, argparse.Namespace]:
    parser = argparse.ArgumentParser(description="Patch README metadata lines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    version_parser = subparsers.add_parser(
        "version", help="Update the version line with link and date"
    )
    version_parser.add_argument("readme", type=Path)
    version_parser.add_argument("version")
    version_parser.add_argument("release_url")
    version_parser.add_argument("release_date")

    size_parser = subparsers.add_parser(
        "size", help="Update the size line with a value in MB"
    )
    size_parser.add_argument("readme", type=Path)
    size_parser.add_argument("size_mb", type=int)

    reset_parser = subparsers.add_parser(
        "reset-dev", help="Reset version line to development version"
    )
    reset_parser.add_argument("readme", type=Path)

    args = parser.parse_args()
    return args.command, args


def main() -> None:
    command, args = parse_args()
    if command == "version":
        update_version_line(
            args.readme, args.version, args.release_url, args.release_date
        )
    elif command == "size":
        update_size_line(args.readme, args.size_mb)
    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
