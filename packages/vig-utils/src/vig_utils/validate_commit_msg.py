#!/usr/bin/env python3
"""Validate commit messages against the project's commit message standard.

Reads the commit message from a file path (as provided by Git's commit-msg hook)
and exits 0 if the message complies, non-zero with an error on stderr otherwise.

See docs/COMMIT_MESSAGE_STANDARD.md for the full standard.

Usage:
    validate-commit-msg <path-to-commit-message-file> [--types TYPE,TYPE,...] [--scopes SCOPE,SCOPE,...] [--refs-optional-types TYPE,TYPE,...] [--require-scope] [--subject-only]

Examples:
    validate-commit-msg .git/COMMIT_EDITMSG
    validate-commit-msg .git/COMMIT_EDITMSG --types feat,fix,docs
    validate-commit-msg .git/COMMIT_EDITMSG --scopes api,cli,utils
    validate-commit-msg .git/COMMIT_EDITMSG --refs-optional-types chore,build
    validate-commit-msg .git/COMMIT_EDITMSG --types feat,fix --scopes api,cli --refs-optional-types chore
    validate-commit-msg .git/COMMIT_EDITMSG --scopes api,cli,utils --require-scope
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Default approved commit types (single source of truth; keep in sync with COMMIT_MESSAGE_STANDARD.md)
DEFAULT_APPROVED_TYPES = frozenset[str](
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

# Default types where the Refs line is optional (maintenance commits that may not relate to an issue)
DEFAULT_REFS_OPTIONAL_TYPES = frozenset[str]({"chore"})

# Agent identity fingerprints (case-insensitive). Commit messages containing these are rejected.
# Refs: #163
_AGENT_FINGERPRINT_PATTERNS: list[tuple[str, int]] = [
    (r"Co-authored-by", re.IGNORECASE),
    (r"cursoragent", re.IGNORECASE),
    (r"\bclaude\b", re.IGNORECASE),
    (r"\bcodex\b", re.IGNORECASE),
    (r"\bchatgpt\b", re.IGNORECASE),
    (r"\bcopilot\b", re.IGNORECASE),
]
_AGENT_FINGERPRINT_PATTERNS_COMPILED = [
    re.compile(pattern, flags) for pattern, flags in _AGENT_FINGERPRINT_PATTERNS
]


def _contains_agent_fingerprint(content: str) -> bool:
    """Check if content contains AI agent identity fingerprints."""
    for pattern_re in _AGENT_FINGERPRINT_PATTERNS_COMPILED:
        if pattern_re.search(content):
            return True
    return False


# Build regex patterns dynamically based on approved types and optional refs types
def _build_patterns(
    approved_types: frozenset[str],
) -> tuple[re.Pattern[str], re.Pattern[str], re.Pattern[str]]:
    """Build regex patterns based on approved types.

    Returns:
        (subject_pattern, ref_pattern, issue_ref_pattern)
    """
    # First line: type(scope)!: short description
    # - type: one of approved_types
    # - scope: optional, alphanumeric and hyphens in parentheses; multiple scopes comma-separated
    # - !: optional, breaking change
    # - short description: rest of line
    subject_pattern = re.compile(
        r"^([a-z]+)(\([a-zA-Z0-9-]+(?:\s*,\s*[a-zA-Z0-9-]+)*\))?!?: .+$"
    )

    # Refs line: Refs: followed by at least one reference (must include at least one issue)
    # Issue refs: #36 or [#36](URL) (GitHub auto-linked format after push).
    # Other refs: REQ-..., RISK-..., SOP-...
    _issue = r"(?:#\d+|\[#\d+\]\([^)]+\))"
    _other = r"(?:REQ-[a-zA-Z0-9-]+|RISK-[a-zA-Z0-9-]+|SOP-[a-zA-Z0-9-]+)"
    _token = rf"(?:{_issue}|{_other})"
    ref_pattern = re.compile(rf"^Refs:\s+{_token}(?:\s*,\s*{_token})*\s*$")
    # At least one GitHub issue ref (plain #N or linked [#N](URL)) must be present
    issue_ref_pattern = re.compile(r"#\d+")

    return subject_pattern, ref_pattern, issue_ref_pattern


def validate_commit_message(
    content: str,
    approved_types: frozenset[str] | None = None,
    approved_scopes: frozenset[str] | None = None,
    refs_optional_types: frozenset[str] | None = None,
    require_scope: bool = False,
    subject_only: bool = False,
) -> tuple[bool, str | None]:
    """Validate a commit message string.

    Args:
        content: The commit message content to validate.
        approved_types: Set of allowed commit types. Defaults to DEFAULT_APPROVED_TYPES.
        approved_scopes: Set of allowed scopes. If None or empty, scopes are not enforced.
        refs_optional_types: Set of commit types where Refs line is optional. Defaults to DEFAULT_REFS_OPTIONAL_TYPES.
        require_scope: If True, at least one scope is mandatory. Defaults to False.
        subject_only: If True, validate only the subject line (type, scope, description).
            Skips blank-line, body, and Refs validation. Useful for PR title checks.

    Returns:
        (True, None) if valid.
        (False, error_message) if invalid.
    """
    if approved_types is None:
        approved_types = DEFAULT_APPROVED_TYPES
    if refs_optional_types is None:
        refs_optional_types = DEFAULT_REFS_OPTIONAL_TYPES
    # Scopes are optional - if not provided or empty, don't enforce them
    if approved_scopes is None:
        approved_scopes = frozenset[str]()

    # require_scope requires approved_scopes to be configured
    if require_scope and not approved_scopes:
        return (
            False,
            "require_scope=True requires approved_scopes to be configured.",
        )

    # Reject agent identity fingerprints (Refs: #163)
    if _contains_agent_fingerprint(content):
        return (
            False,
            "Commit message contains AI agent fingerprint (e.g. Co-authored-by, "
            "cursoragent, claude). Remove agent identity from commit.",
        )

    subject_pattern, ref_pattern, issue_ref_pattern = _build_patterns(approved_types)

    if not content:
        return False, "Commit message is empty."

    lines = content.rstrip().splitlines()
    if not lines:
        return False, "Commit message is empty."

    # First line: type(scope): short description
    first = lines[0]
    match = subject_pattern.match(first)
    if not match:
        return (
            False,
            "First line must match 'type(scope): short description'. "
            "Example: feat: add new feature",
        )
    type_part = match.group(1)
    if type_part not in approved_types:
        return (
            False,
            f"Unknown commit type '{type_part}'. "
            f"Allowed types: {', '.join(sorted(approved_types))}",
        )

    # Validate scope if provided and scopes are configured
    scope_part = match.group(2)  # Will be like "(scope)" or "(scope1, scope2)" or None
    if require_scope and scope_part is None:
        return (
            False,
            f"A scope is required for this commit type, valid scopes are: {', '.join(sorted(approved_scopes))}",
        )
    if scope_part is not None and approved_scopes:
        # Scope is provided and scopes are configured; validate each scope is in the approved list
        # Remove the parentheses to get the scope content
        scope_content = scope_part[1:-1]
        # Split by comma and strip whitespace
        scope_names = [s.strip() for s in scope_content.split(",")]
        # Validate each scope is in the approved list
        invalid_scopes = [s for s in scope_names if s not in approved_scopes]
        if invalid_scopes:
            return (
                False,
                f"Unknown scope(s): {', '.join(invalid_scopes)}. "
                f"Allowed scopes: {', '.join(sorted(approved_scopes))}",
            )

    if subject_only:
        return True, None

    # Require at least one blank line between subject and body/Refs
    # For types with optional Refs, a subject-only message is valid
    if len(lines) < 2:
        if type_part in refs_optional_types:
            return True, None
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
        if type_part in refs_optional_types:
            return True, None
        return False, "Missing mandatory 'Refs: <IDs>' line (e.g. Refs: #36)."

    if not ref_pattern.match(refs_line.strip()):
        return (
            False,
            "Refs line must contain at least one reference. "
            "Accepted: issue numbers (#36), REQ-..., RISK-..., SOP-...",
        )

    # At least one GitHub issue reference is required
    if not issue_ref_pattern.search(refs_line):
        return (
            False,
            "Refs line must include at least one GitHub issue (e.g. #36).",
        )

    return True, None


def main() -> int:
    """Entry point for Git commit-msg hook and CLI.

    Supports both traditional positional arguments and optional configuration arguments
    that can be provided via CLI or pre-commit hook configuration.
    """
    parser = argparse.ArgumentParser(
        prog="validate-commit-msg",
        description="Validate commit messages against the project's commit message standard.",
    )
    parser.add_argument(
        "message_file",
        help="Path to commit message file (typically .git/COMMIT_EDITMSG from Git hook)",
    )
    parser.add_argument(
        "--types",
        type=str,
        default=None,
        help="Comma-separated list of allowed commit types (default: feat,fix,docs,chore,refactor,test,ci,build,revert,style)",
    )
    parser.add_argument(
        "--scopes",
        type=str,
        default=None,
        help="Comma-separated list of allowed scopes. If not provided, scopes are not enforced (default: none)",
    )
    parser.add_argument(
        "--refs-optional-types",
        type=str,
        default=None,
        help="Comma-separated list of commit types where Refs line is optional (default: chore)",
    )
    parser.add_argument(
        "--require-scope",
        action="store_true",
        help="Require at least one scope in the commit message (default: false)",
    )
    parser.add_argument(
        "--subject-only",
        action="store_true",
        help="Validate only the subject line (skip body and Refs). Useful for PR title validation.",
    )

    args = parser.parse_args()

    # Parse custom types if provided
    approved_types = DEFAULT_APPROVED_TYPES
    if args.types:
        approved_types = frozenset(
            t.strip() for t in args.types.split(",") if t.strip()
        )

    # Parse custom scopes if provided
    approved_scopes = frozenset()  # Empty by default (no scope enforcement)
    if args.scopes:
        approved_scopes = frozenset(
            s.strip() for s in args.scopes.split(",") if s.strip()
        )

    # Parse custom refs-optional types if provided
    refs_optional_types = DEFAULT_REFS_OPTIONAL_TYPES
    if args.refs_optional_types:
        refs_optional_types = frozenset(
            t.strip() for t in args.refs_optional_types.split(",") if t.strip()
        )

    path = Path(args.message_file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8", errors="replace")
    valid, error = validate_commit_message(
        content,
        approved_types=approved_types,
        approved_scopes=approved_scopes,
        refs_optional_types=refs_optional_types,
        require_scope=args.require_scope,
        subject_only=args.subject_only,
    )
    if valid:
        return 0
    print(error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
