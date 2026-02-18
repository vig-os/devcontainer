#!/usr/bin/env python3
"""Remove specific pre-commit hooks from .pre-commit-config.yaml."""

import sys
from pathlib import Path

import yaml


def remove_hooks(config_path: Path, hook_ids_to_remove: set[str]) -> None:
    """Remove specified hooks from pre-commit config."""
    with config_path.open() as f:
        config = yaml.safe_load(f)

    if not config or "repos" not in config:
        return

    # Filter out hooks and empty repo blocks
    filtered_repos = []
    for repo in config["repos"]:
        if "hooks" not in repo:
            filtered_repos.append(repo)
            continue

        # Filter hooks
        filtered_hooks = [
            hook for hook in repo["hooks"] if hook.get("id") not in hook_ids_to_remove
        ]

        # Only keep repo if it still has hooks
        if filtered_hooks:
            repo["hooks"] = filtered_hooks
            filtered_repos.append(repo)

    config["repos"] = filtered_repos

    # Write back with proper YAML formatting
    with config_path.open("w") as f:
        # Preserve the leading comment and structure
        f.write("---\n")
        f.write("# .pre-commit-config.yaml\n\n")
        f.write(r"exclude: ^\.github_data/" + "\n\n")
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=120)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: remove-precommit-hooks.py <config-file> <hook-id> [hook-id...]")
        sys.exit(1)

    config_file = Path(sys.argv[1])
    hooks_to_remove = set(sys.argv[2:])

    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    remove_hooks(config_file, hooks_to_remove)
