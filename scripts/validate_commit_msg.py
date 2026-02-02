#!/usr/bin/env python3
"""Validate commit messages against the project's commit message standard.

Reads the commit message from a file path (as provided by Git's commit-msg hook)
and exits 0 if the message complies, non-zero with an error on stderr otherwise.

See docs/COMMIT_MESSAGE_STANDARD.md for the full standard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Approved commit types (single source of truth; keep in sync with COMMIT_MESSAGE_STANDARD.md)
APPROVED_TYPES = frozenset[str](
    {
        "feat",
        "fix",
        "docs",
        "chore",
        "refactor",
        "test",
        "ci",
        "build",
        "revert",
        "style",
    }
)

# First line: type(scope)!: short description
# - type: one of APPROVED_TYPES
# - scope: optional, alphanumeric and hyphens in parentheses
# - !: optional, breaking change
# - short description: rest of line
SUBJECT_PATTERN = re.compile(r"^([a-z]+)(\([a-zA-Z0-9-]+\))?!?: .+$")

# Refs line: Refs: followed by at least one reference (must include at least one issue)
# Reference: #?\d+ (issue) or REQ-..., RISK-..., SOP-... (alphanumeric/hyphens)
REF_PATTERN = re.compile(
    r"^Refs:\s+"
    r"(?:(?:#?\d+)|(?:REQ-[a-zA-Z0-9-]+)|(?:RISK-[a-zA-Z0-9-]+)|(?:SOP-[a-zA-Z0-9-]+))"
    r"(?:\s*,\s*"
    r"(?:(?:#?\d+)|(?:REQ-[a-zA-Z0-9-]+)|(?:RISK-[a-zA-Z0-9-]+)|(?:SOP-[a-zA-Z0-9-]+))"
    r")*\s*$"
)
# At least one GitHub issue (#36 or 36 as standalone ref) must be present in Refs
# Match #36 or "Refs: 36" or ", 36" so we don't match 123 in REQ-123
ISSUE_REF_PATTERN = re.compile(r"#\d+|(?:Refs:\s+|,\s+)\d+")


def validate_commit_message(content: str) -> tuple[bool, str | None]:
    """Validate a commit message string.

    Returns:
        (True, None) if valid.
        (False, error_message) if invalid.
    """
    if not content:
        return False, "Commit message is empty."

    # Enforce exactly one trailing newline
    if not content.endswith("\n"):
        return False, "Commit message must end with exactly one trailing newline."
    if len(content) >= 2 and content[-2] == "\n":
        return (
            False,
            "Commit message must end with exactly one trailing newline (no multiple newlines at end).",
        )

    lines = content.rstrip().splitlines()
    if not lines:
        return False, "Commit message is empty."

    # First line: type(scope): short description
    first = lines[0]
    match = SUBJECT_PATTERN.match(first)
    if not match:
        return (
            False,
            "First line must match 'type(scope): short description'. "
            "Example: feat: add new feature",
        )
    type_part = match.group(1)
    if type_part not in APPROVED_TYPES:
        return (
            False,
            f"Unknown commit type '{type_part}'. "
            f"Allowed types: {', '.join(sorted(APPROVED_TYPES))}",
        )

    # Require at least one blank line between subject and body/Refs
    if len(lines) < 2:
        return False, "Missing blank line and 'Refs: <IDs>' after the subject line."
    if lines[1].strip():
        return (
            False,
            "A blank line is required between the subject and body/Refs.",
        )

    # Find Refs line (after the blank line; optional body lines allowed before it)
    refs_line = None
    for line in lines[2:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Refs:"):
            if refs_line is not None:
                return False, "Only one Refs line is allowed."
            refs_line = line
        elif refs_line is not None:
            # Body or other content after Refs line is not allowed
            return (
                False,
                "Only one Refs line is allowed; it must be the last non-empty line.",
            )

    if refs_line is None:
        return False, "Missing mandatory 'Refs: <IDs>' line (e.g. Refs: #36)."

    if not REF_PATTERN.match(refs_line.strip()):
        return (
            False,
            "Refs line must contain at least one reference. "
            "Accepted: issue numbers (#36), REQ-..., RISK-..., SOP-...",
        )

    # At least one GitHub issue reference is required
    if not ISSUE_REF_PATTERN.search(refs_line):
        return (
            False,
            "Refs line must include at least one GitHub issue (e.g. #36).",
        )

    return True, None


def main() -> int:
    """Entry point for Git commit-msg hook and CLI."""
    if len(sys.argv) != 2:
        print(
            "Usage: validate_commit_msg.py <path-to-commit-message-file>",
            file=sys.stderr,
        )
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8", errors="replace")
    valid, error = validate_commit_message(content)
    if valid:
        return 0
    print(error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
