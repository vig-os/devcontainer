#!/usr/bin/env python3
"""Check that all external GitHub Actions are pinned to commit SHAs.

Scans workflow files (.github/workflows/*.yml) and composite action files
(.github/actions/*/action.yml) for `uses:` directives referencing external
actions, and verifies each is pinned to a full 40-character commit SHA.

Local actions (starting with ./) are excluded from checks.

Exit codes:
    0 — All external actions are properly SHA-pinned
    1 — One or more actions use mutable references (tags or branches)

Usage:
    check-action-pins
    check-action-pins --verbose

Refs: #50
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Pattern: captures the full action reference after `uses:`
# Matches lines like: `uses: actions/checkout@v4` or `uses: owner/repo/path@ref`
USES_PATTERN = re.compile(r"^\s*uses:\s+([^\s#]+)")

# A valid SHA pin is exactly 40 hex characters
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def find_workflow_files(repo_root: Path) -> list[Path]:
    """Find all GitHub Actions workflow and composite action files."""
    files: list[Path] = []

    # Workflow files
    workflows_dir = repo_root / ".github" / "workflows"
    if workflows_dir.is_dir():
        files.extend(sorted(workflows_dir.glob("*.yml")))
        files.extend(sorted(workflows_dir.glob("*.yaml")))

    # Composite action files
    actions_dir = repo_root / ".github" / "actions"
    if actions_dir.is_dir():
        for action_dir in sorted(actions_dir.iterdir()):
            for name in ("action.yml", "action.yaml"):
                action_file = action_dir / name
                if action_file.is_file():
                    files.append(action_file)

    return files


def check_file(filepath: Path, verbose: bool = False) -> list[str]:
    """Check a single file for unpinned action references.

    Returns a list of error messages for unpinned actions.
    """
    errors: list[str] = []

    with filepath.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            match = USES_PATTERN.match(line)
            if not match:
                continue

            action_ref = match.group(1)

            # Skip local actions (e.g., ./.github/actions/build-image)
            if action_ref.startswith("./"):
                if verbose:
                    print(f"  {filepath}:{line_num}: SKIP (local) {action_ref}")
                continue

            # Split action reference into name and ref
            if "@" not in action_ref:
                errors.append(
                    f"{filepath}:{line_num}: missing version reference: {action_ref}"
                )
                continue

            action_name, ref = action_ref.rsplit("@", 1)

            # Check if ref is a full SHA
            if SHA_PATTERN.match(ref):
                if verbose:
                    print(f"  {filepath}:{line_num}: OK {action_name}@{ref[:12]}...")
            else:
                errors.append(
                    f"{filepath}:{line_num}: unpinned action: "
                    f"{action_name}@{ref} (expected 40-char SHA)"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that all external GitHub Actions are pinned to commit SHAs."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show all checked references"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: auto-detect)",
    )
    args = parser.parse_args()

    # Auto-detect repo root
    repo_root = args.repo_root or Path.cwd()

    files = find_workflow_files(repo_root)
    if not files:
        print(f"No workflow files found under {repo_root}")
        return 1

    all_errors: list[str] = []

    for filepath in files:
        rel_path = filepath.relative_to(repo_root)
        if args.verbose:
            print(f"Checking {rel_path}...")
        errors = check_file(filepath, verbose=args.verbose)
        # Rewrite errors with relative paths
        for error in errors:
            all_errors.append(error.replace(str(filepath), str(rel_path)))

    if all_errors:
        print(f"\nFound {len(all_errors)} unpinned action(s):\n")
        for error in all_errors:
            print(f"  {error}")
        print(
            "\nAll external GitHub Actions must be pinned to commit SHAs."
            "\nFormat: uses: owner/action@<40-char-sha> # vX.Y.Z"
        )
        return 1

    file_count = len(files)
    print(f"All external actions are SHA-pinned ({file_count} files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
