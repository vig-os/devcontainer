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
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Ensure scripts dir is on path for transforms import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from transforms import (
    RemoveBlock,
    RemoveLines,
    RemovePrecommitHooks,
    ReplaceBlock,
    Sed,
    StripTrailingBlankLines,
    Transform,
)

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
    # ── Cursor skills ───────────────────────────────────────────────────
    Entry(
        src=".cursor/skills/",
        transforms=[
            # code:verify: generalize devcontainer-specific test recipes
            Sed(
                pattern=r"just test-image",
                replace="just test",
                target="code:verify/SKILL.md",
            ),
            # design:plan: generalize devcontainer-specific test recipes
            Sed(
                pattern=r"just test-image",
                replace="just test",
                target="design:plan/SKILL.md",
            ),
        ],
    ),
    # ── Cursor worktree config ────────────────────────────────────────────
    Entry(src=".cursor/worktrees.json"),
    # ── Project config ───────────────────────────────────────────────────
    Entry(src=".gitmessage"),
    Entry(src=".yamllint"),
    Entry(src=".pymarkdown"),
    Entry(src=".pymarkdown.config.md"),
    Entry(src=".hadolint.yaml"),
    # ── GitHub templates & config ────────────────────────────────────────
    Entry(src=".github/label-taxonomy.toml"),
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
    # ── GitHub CLI recipes (managed, replaced on upgrade) ────────────────
    Entry(src="justfile.gh", dest=".devcontainer/justfile.gh"),
    Entry(src="scripts/gh_issues.py", dest=".devcontainer/scripts/gh_issues.py"),
    # ── Worktree recipes (managed, replaced on upgrade) ───────────────
    Entry(src="justfile.worktree", dest=".devcontainer/justfile.worktree"),
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
