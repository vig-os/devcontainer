#!/usr/bin/env python3
"""Utility functions for build scripts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_PATTERN = re.compile(r"^- \*\*Version\*\*:.*$", re.MULTILINE)


def substitute_in_file(
    path: Path | str,
    pattern: str,
    replacement: str,
    *,
    regex: bool = False,
    global_replace: bool = True,
) -> None:
    """Apply substitution to file. Shared by sed_inplace and Sed transform."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    content = p.read_text()
    if regex:
        content = re.sub(pattern, replacement, content)
    else:
        if global_replace:
            content = content.replace(pattern, replacement)
        else:
            content = content.replace(pattern, replacement, 1)
    p.write_text(content)


def sed_inplace(pattern: str, file_path: Path | str) -> None:
    """Cross-platform sed in-place editing.

    Supports sed substitution patterns like: s|old|new|g
    The delimiter can be any character (typically |, /, #, etc.)
    Uses literal (non-regex) replacement.
    """
    path = Path(file_path)

    # Parse sed substitution pattern: s<delimiter><pattern><delimiter><replacement><delimiter>[flags]
    # Example: s|{{IMAGE_TAG}}|0.2.0|g
    if not pattern.startswith("s"):
        raise ValueError(
            f"Unsupported sed command: {pattern} (only 's' substitution is supported)"
        )

    if len(pattern) < 4:  # At minimum: s|a|b
        raise ValueError(
            f"Invalid sed pattern: {pattern} (expected format: s<delim><pattern><delim><replacement>[<delim><flags>])"
        )

    # Find the delimiter (first character after 's')
    delimiter = pattern[1]

    # Find all delimiter positions after 's'
    delim_positions = []
    pos = 1
    while True:
        pos = pattern.find(delimiter, pos + 1)
        if pos == -1:
            break
        delim_positions.append(pos)

    if len(delim_positions) < 2:
        raise ValueError(
            f"Invalid sed pattern: {pattern} (expected format: s<delim><pattern><delim><replacement>[<delim><flags>])"
        )

    search_pattern = pattern[2 : delim_positions[0]]
    replacement = pattern[delim_positions[0] + 1 : delim_positions[1]]
    flags = (
        pattern[delim_positions[1] + 1 :]
        if delim_positions[1] + 1 < len(pattern)
        else ""
    )
    global_replace = "g" in flags

    substitute_in_file(
        path, search_pattern, replacement, regex=False, global_replace=global_replace
    )


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


def parse_args() -> tuple[str, argparse.Namespace]:
    parser = argparse.ArgumentParser(description="Patch README metadata lines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    version_parser = subparsers.add_parser(
        "version", help="Update the README version line with link and date"
    )
    version_parser.add_argument("readme", type=Path)
    version_parser.add_argument("version")
    version_parser.add_argument("release_url")
    version_parser.add_argument("release_date")

    sed_parser = subparsers.add_parser(
        "sed", help="Cross-platform sed in-place editing"
    )
    sed_parser.add_argument(
        "pattern", type=str, help="Sed substitution pattern (e.g., 's|old|new|g')"
    )
    sed_parser.add_argument("file", type=Path, help="File to edit in-place")

    args = parser.parse_args()
    return args.command, args


def main() -> None:
    command, args = parse_args()
    if command == "version":
        update_version_line(
            args.readme, args.version, args.release_url, args.release_date
        )
    elif command == "sed":
        sed_inplace(args.pattern, args.file)
    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
