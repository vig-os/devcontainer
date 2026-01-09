#!/usr/bin/env python3
"""Utility functions for build scripts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_PATTERN = re.compile(r"^- \*\*Version\*\*:.*$", re.MULTILINE)


def sed_inplace(pattern: str, file_path: Path | str) -> None:
    """Cross-platform sed in-place editing.

    Supports sed substitution patterns like: s|old|new|g
    The delimiter can be any character (typically |, /, #, etc.)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

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
    # Pattern format: s<delim><pattern><delim><replacement><delim>[flags]
    # We need to find the last delimiter (before flags) and second-to-last (end of replacement)
    # Start searching from position 2 (after 's' and first delimiter)
    delim_positions = []
    pos = 1  # Start at the first delimiter (position 1)
    while True:
        pos = pattern.find(delimiter, pos + 1)
        if pos == -1:
            break
        delim_positions.append(pos)

    if len(delim_positions) < 2:
        raise ValueError(
            f"Invalid sed pattern: {pattern} (expected format: s<delim><pattern><delim><replacement>[<delim><flags>])"
        )

    # Extract components
    # Pattern is between first delimiter (pos 1) and second delimiter
    # Replacement is between second delimiter and third delimiter (or end if no flags)
    # Flags are after last delimiter
    search_pattern = pattern[
        2 : delim_positions[0]
    ]  # After 's' and first delim, up to second delim
    replacement = pattern[
        delim_positions[0] + 1 : delim_positions[1]
    ]  # Between second and third delim
    flags = (
        pattern[delim_positions[1] + 1 :]
        if delim_positions[1] + 1 < len(pattern)
        else ""
    )

    # Read file
    text = path.read_text()

    # Determine if global replacement (g flag)
    global_replace = "g" in flags

    # Perform substitution
    if global_replace:
        updated_text = text.replace(search_pattern, replacement)
    else:
        # Replace only first occurrence
        updated_text = text.replace(search_pattern, replacement, 1)

    # Write back
    path.write_text(updated_text)


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
