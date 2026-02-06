#!/usr/bin/env python3
"""
Prepare CHANGELOG.md for release.

This script:
1. Moves Unreleased section content to a new version section (with TBD date)
2. Creates a fresh Unreleased section at the top
3. Cleans up empty subsections (only keeps those with actual content)

Usage:
    python3 scripts/prepare-changelog.py VERSION [CHANGELOG_FILE]

Example:
    python3 scripts/prepare-changelog.py 1.0.0 CHANGELOG.md
"""

import re
import sys
from pathlib import Path

# Standard CHANGELOG subsections in order
STANDARD_SECTIONS = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]


def extract_unreleased_content(content):
    """
    Extract content from Unreleased section.

    Returns dict: {section_name: content_lines}
    """
    # Find Unreleased section
    unreleased_match = re.search(
        r"## Unreleased\s*\n(.*?)(?=\n## \[|\Z)", content, re.DOTALL
    )

    if not unreleased_match:
        raise ValueError("No '## Unreleased' section found in CHANGELOG")

    unreleased_text = unreleased_match.group(1)

    # Extract each subsection
    sections = {}
    for section in STANDARD_SECTIONS:
        # Match section header, then capture content until next section/heading
        # Use negative lookahead to stop before next ### or ##
        pattern = rf"### {section}\s*\n((?:(?!###|##).)*)"
        match = re.search(pattern, unreleased_text, re.DOTALL)
        if match:
            section_content = match.group(1).strip()
            # Only keep if it has actual bullet points (lines starting with -)
            if section_content:
                lines_with_content = [
                    line
                    for line in section_content.split("\n")
                    if line.strip() and line.strip().startswith("-")
                ]
                if lines_with_content:
                    sections[section] = section_content

    return sections


def create_new_changelog(version, old_sections, rest_of_changelog):
    """
    Create new CHANGELOG structure.

    Args:
        version: Version string (e.g., "1.0.0")
        old_sections: Dict of sections with content from old Unreleased
        rest_of_changelog: Everything after the old Unreleased section
    """
    lines = []

    # Header (keep existing if present, or add minimal)
    lines.append("# Changelog\n")
    lines.append("\n")
    lines.append(
        "All notable changes to this project will be documented in this file.\n"
    )
    lines.append("\n")
    lines.append(
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
    )
    lines.append(
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n"
    )
    lines.append("\n")

    # New empty Unreleased section (always include all standard sections for consistency)
    lines.append("## Unreleased\n")
    lines.append("\n")
    for section in STANDARD_SECTIONS:
        lines.append(f"### {section}\n")
        lines.append("\n")

    # Version section with TBD date
    lines.append(f"## [{version}] - TBD\n")
    lines.append("\n")

    # Add sections that have content
    if old_sections:
        for section in STANDARD_SECTIONS:
            if section in old_sections:
                lines.append(f"### {section}\n")
                lines.append("\n")
                lines.append(old_sections[section])
                lines.append("\n")
                lines.append("\n")

    # Add rest of changelog
    lines.append(rest_of_changelog)

    return "".join(lines)


def prepare_changelog(version, filepath="CHANGELOG.md"):
    """
    Main function to prepare CHANGELOG for release.

    Args:
        version: Semantic version (e.g., "1.0.0")
        filepath: Path to CHANGELOG.md
    """
    # Validate version format
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError(f"Invalid semantic version: {version}")

    # Read current CHANGELOG
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CHANGELOG not found: {filepath}")

    content = path.read_text()

    # Extract Unreleased content
    old_sections = extract_unreleased_content(content)

    # Get everything after Unreleased section
    rest_match = re.search(r"## Unreleased\s*\n.*?(?=\n## \[)", content, re.DOTALL)

    if rest_match:
        # Find start of next version section
        next_version_start = content.find("\n## [", rest_match.end())
        if next_version_start != -1:
            rest_of_changelog = content[next_version_start + 1 :]
        else:
            rest_of_changelog = ""
    else:
        rest_of_changelog = ""

    # Create new CHANGELOG
    new_content = create_new_changelog(version, old_sections, rest_of_changelog)

    # Write back
    path.write_text(new_content)

    return old_sections


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/prepare-changelog.py VERSION [CHANGELOG_FILE]")
        print("\nExample:")
        print("  python3 scripts/prepare-changelog.py 1.0.0")
        print("  python3 scripts/prepare-changelog.py 1.0.0 CHANGELOG.md")
        sys.exit(1)

    version = sys.argv[1]
    filepath = sys.argv[2] if len(sys.argv) > 2 else "CHANGELOG.md"

    try:
        sections = prepare_changelog(version, filepath)

        print(f"✓ Prepared CHANGELOG for version {version}")
        if sections:
            print(
                f"✓ Moved {len(sections)} section(s) with content to [{version}] - TBD"
            )
            for section in sections:
                print(f"  - {section}")
        else:
            print("⚠ Warning: No content found in Unreleased section")
        print("✓ Created fresh Unreleased section")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
