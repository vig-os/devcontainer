#!/usr/bin/env python3
"""Declarative workspace sync manifest.

Single source of truth for which files are copied from the repo root into
assets/workspace/ and what transformations are applied to generalize them
for downstream projects.

Usage:
    uv run python scripts/sync_manifest.py sync <dest_dir> [--project-root <root>]
    uv run python scripts/sync_manifest.py list
    uv run python scripts/sync_manifest.py list --transformed

Called by:
    - scripts/prepare-build.sh  (build-time: sync into build/assets/workspace/)
    - just sync-workspace       (dev-time: sync into assets/workspace/)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

# ── Transform types ──────────────────────────────────────────────────────────


class Transform(Protocol):
    """A post-copy transformation applied to a synced file."""

    def apply(self, file_path: Path) -> None: ...


def _resolve(file_path: Path, target: str) -> Path | None:
    """Resolve a transform target path, returning None if it doesn't exist."""
    path = file_path / target if target else file_path
    if not path.exists():
        return None
    return path


@dataclass
class Sed:
    """Regex substitution on a file (or a specific file within a directory entry)."""

    pattern: str
    replace: str
    target: str = ""

    def apply(self, file_path: Path) -> None:
        path = _resolve(file_path, self.target)
        if path is None:
            return
        content = path.read_text()
        content = re.sub(self.pattern, self.replace, content)
        path.write_text(content)


@dataclass
class RemoveLines:
    """Remove lines matching a regex pattern."""

    pattern: str
    target: str = ""

    def apply(self, file_path: Path) -> None:
        path = _resolve(file_path, self.target)
        if path is None:
            return
        content = path.read_text()
        lines = content.splitlines(keepends=True)
        filtered = [line for line in lines if not re.search(self.pattern, line)]
        path.write_text("".join(filtered))


@dataclass
class StripTrailingBlankLines:
    """Remove trailing blank lines from a file, keeping a single final newline."""

    target: str = ""

    def apply(self, file_path: Path) -> None:
        path = _resolve(file_path, self.target)
        if path is None:
            return
        content = path.read_text()
        path.write_text(content.rstrip() + "\n")


@dataclass
class RemoveBlock:
    """Remove a block of lines from start_pattern through end_pattern (inclusive)."""

    start_pattern: str
    end_pattern: str
    target: str = ""

    def apply(self, file_path: Path) -> None:
        path = _resolve(file_path, self.target)
        if path is None:
            return
        content = path.read_text()
        lines = content.splitlines(keepends=True)
        result = []
        skipping = False
        for line in lines:
            if not skipping and re.search(self.start_pattern, line):
                skipping = True
                continue
            if skipping:
                if re.search(self.end_pattern, line):
                    skipping = False
                continue
            result.append(line)
        path.write_text("".join(result))


@dataclass
class RemovePrecommitHooks:
    """Remove pre-commit hooks by id and clean up empty repo blocks."""

    hook_ids: list[str]

    def apply(self, file_path: Path) -> None:
        content = file_path.read_text()
        lines = content.splitlines(keepends=True)
        result: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this line starts a hook we want to remove
            if any(f"id: {hid}" in line for hid in self.hook_ids):
                # Skip until next hook (- id:) or next repo (- repo:) or blank line after block
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # Stop before next hook or repo definition
                    if re.match(r"^      - id:", next_line) or re.match(
                        r"^  - repo:", next_line
                    ):
                        break
                    i += 1
                    # If we hit a blank line, consume it and stop
                    if next_line.strip() == "":
                        break
                continue
            result.append(line)
            i += 1

        # Second pass: remove empty repo blocks (repo: local with hooks: but no actual hooks)
        final: list[str] = []
        i = 0
        result_lines = result
        while i < len(result_lines):
            line = result_lines[i]
            if re.match(r"^  - repo: local", line):
                # Buffer this repo block header
                buf = [line]
                i += 1
                while i < len(result_lines) and not re.match(
                    r"^  - repo:", result_lines[i]
                ):
                    buf.append(result_lines[i])
                    i += 1
                # Check if buffer has any actual hooks
                has_hooks = any(re.match(r"^      - id:", b) for b in buf)
                if has_hooks:
                    final.extend(buf)
                # If no hooks, discard the entire block (including comment above)
                # Check if last line in final is a comment for this section
                elif final and final[-1].strip().startswith("#"):
                    final.pop()  # Remove the section comment too
                continue
            final.append(line)
            i += 1

        file_path.write_text("".join(final))


@dataclass
class ReplaceBlock:
    """Replace a block of lines (start through end, inclusive) with new content.

    If keep_start is True, the start line is preserved and replacement is
    inserted after it.  Otherwise the start line is also replaced.
    """

    start_pattern: str
    end_pattern: str
    replacement: str
    target: str = ""
    keep_start: bool = False

    def apply(self, file_path: Path) -> None:
        path = _resolve(file_path, self.target)
        if path is None:
            return
        content = path.read_text()
        lines = content.splitlines(keepends=True)
        result = []
        skipping = False
        replaced = False
        for line in lines:
            if not skipping and re.search(self.start_pattern, line):
                skipping = True
                if self.keep_start:
                    result.append(line)
                if not replaced:
                    result.append(self.replacement)
                    replaced = True
                continue
            if skipping:
                if re.search(self.end_pattern, line):
                    skipping = False
                continue
            result.append(line)
        path.write_text("".join(result))


# ── Manifest entry ───────────────────────────────────────────────────────────


@dataclass
class Entry:
    """A file or directory to sync from repo root to workspace template.

    Attributes:
        src: Source path relative to project root.
        dest: Destination path relative to workspace root (defaults to src).
        transforms: List of post-copy transformations to apply.
    """

    src: str
    dest: str = ""
    transforms: list[Transform] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.dest:
            self.dest = self.src

    @property
    def is_transformed(self) -> bool:
        return len(self.transforms) > 0


# ── The manifest ─────────────────────────────────────────────────────────────

VALIDATE_COMMIT_MSG_ARGS_REPLACEMENT = (
    "        # Optional: customize commit types, scopes, or refs-optional types via CLI arguments.\n"
    "        # By default, scopes are not enforced. Set --scopes to require specific scopes.\n"
    "        # Examples (choose one args line):\n"
    '        #   args: ["--types", "feat,fix,docs,chore"]\n'
    '        #   args: ["--scopes", "api,cli,utils"]\n'
    '        #   args: ["--refs-optional-types", "chore"]\n'
    '        #   args: ["--types", "feat,fix,docs", "--scopes", "api,cli,utils",'
    ' "--refs-optional-types", "chore"]\n'
)

MANIFEST: list[Entry] = [
    # ── Docs ─────────────────────────────────────────────────────────────
    Entry(src="docs/COMMIT_MESSAGE_STANDARD.md"),
    # ── Cursor rules ─────────────────────────────────────────────────────
    Entry(
        src=".cursor/rules/",
        transforms=[
            RemoveLines(
                pattern=r"Full reference: \[docs/COMMIT_MESSAGE_STANDARD\.md\]",
                target="commit-messages.mdc",
            ),
        ],
    ),
    # ── Cursor commands ──────────────────────────────────────────────────
    Entry(
        src=".cursor/commands/",
        transforms=[
            # tdd.md: generalize devcontainer-specific test recipes
            Sed(
                pattern=r"just test-image",
                replace="just test",
                target="tdd.md",
            ),
            Sed(
                pattern=r"just test-integration",
                replace="just test-cov",
                target="tdd.md",
            ),
            Sed(
                pattern=r"just test-utils",
                replace="just test-pytest",
                target="tdd.md",
            ),
            # verify.md: generalize devcontainer-specific test recipes
            Sed(
                pattern=r"just test-image",
                replace="just test",
                target="verify.md",
            ),
        ],
    ),
    # ── Project config ───────────────────────────────────────────────────
    Entry(src=".gitmessage"),
    Entry(src=".yamllint"),
    Entry(src=".pymarkdown"),
    Entry(src=".pymarkdown.config.md"),
    Entry(src=".hadolint.yaml"),
    # ── GitHub templates & config ────────────────────────────────────────
    Entry(src=".github/pull_request_template.md"),
    Entry(src=".github/ISSUE_TEMPLATE/"),
    Entry(src=".github/actions/setup-env/"),
    Entry(
        src=".github/dependabot.yml",
        transforms=[
            # Remove Docker ecosystem section (devcontainer-specific)
            RemoveBlock(
                start_pattern=r"^\s+# Docker",
                end_pattern=r"^$",
            ),
            StripTrailingBlankLines(),
        ],
    ),
    Entry(src=".github/workflows/scorecard.yml"),
    Entry(src=".github/workflows/sync-issues.yml"),
    Entry(src=".github/workflows/codeql.yml"),
    # ── Pre-commit config ────────────────────────────────────────────────
    Entry(
        src=".pre-commit-config.yaml",
        transforms=[
            # Remove devcontainer-repo-specific hooks
            RemovePrecommitHooks(hook_ids=["generate-docs"]),
            # Generalize Bandit paths for downstream projects
            Sed(
                pattern=r"bandit -r packages/vig-utils/src/ scripts/ assets/workspace/",
                replace="bandit -r src/",
            ),
            # Replace validate-commit-msg args with commented examples
            ReplaceBlock(
                start_pattern=r"^\s+args: \[$",
                end_pattern=r"^\s+\]$",
                replacement=VALIDATE_COMMIT_MSG_ARGS_REPLACEMENT,
            ),
        ],
    ),
]


# ── Sync logic ───────────────────────────────────────────────────────────────


def sync(project_root: Path, dest_base: Path) -> None:
    """Copy manifest entries from project_root into dest_base, applying transforms."""
    failed = False

    for entry in MANIFEST:
        src_path = project_root / entry.src
        dest_path = dest_base / entry.dest

        if not src_path.exists():
            print(f"  [MISSING] Source not found: {entry.src}", file=sys.stderr)
            failed = True
            continue

        if src_path.is_dir():
            # Directory: rsync-like copy (delete destination first for clean sync)
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            label = "SYNCED" if not entry.is_transformed else "TRANSFORMED"
            print(f"  [{label}]  {entry.src} -> {entry.dest}")
        elif src_path.is_file():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            label = "SYNCED" if not entry.is_transformed else "TRANSFORMED"
            print(f"  [{label}]  {entry.src} -> {entry.dest}")
        else:
            print(
                f"  [UNKNOWN] Source is neither file nor directory: {entry.src}",
                file=sys.stderr,
            )
            failed = True
            continue

        # Apply transforms
        for transform in entry.transforms:
            transform.apply(dest_path)

    if failed:
        print("Error: Some files could not be synced", file=sys.stderr)
        sys.exit(1)

    print("All manifest entries synced successfully.")


def list_entries(transformed_only: bool = False) -> None:
    """Print manifest entries, optionally only transformed ones."""
    for entry in MANIFEST:
        if transformed_only and not entry.is_transformed:
            continue
        marker = " [T]" if entry.is_transformed else ""
        dest = f" -> {entry.dest}" if entry.dest != entry.src else ""
        print(f"  {entry.src}{dest}{marker}")


# ── CLI ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Declarative workspace sync manifest")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # sync command
    sync_parser = subparsers.add_parser(
        "sync", help="Sync manifest entries to destination"
    )
    sync_parser.add_argument("dest", help="Destination directory")
    sync_parser.add_argument(
        "--project-root",
        default=None,
        help="Project root (default: auto-detect from script location)",
    )

    # list command
    list_parser = subparsers.add_parser("list", help="List manifest entries")
    list_parser.add_argument(
        "--transformed",
        action="store_true",
        help="Only show entries with transforms",
    )

    args = parser.parse_args()

    if args.command == "sync":
        project_root = (
            Path(args.project_root)
            if args.project_root
            else Path(__file__).resolve().parent.parent
        )
        dest = Path(args.dest)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"Syncing manifest entries to {dest}...")
        sync(project_root, dest)

    elif args.command == "list":
        list_entries(transformed_only=args.transformed)


if __name__ == "__main__":
    main()
