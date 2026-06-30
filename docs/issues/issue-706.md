---
type: issue
state: open
created: 2026-06-25T12:12:30Z
updated: 2026-06-25T12:12:30Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/706
comments: 0
labels: bug, priority:high, area:workspace, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:53.528Z
---

# [Issue 706]: [[BUG] Downstream venv path Sed transform points at the dead Debian /opt/venv path](https://github.com/vig-os/devcontainer/issues/706)

## Problem
`scripts/manifest.toml:47` rewrites the workspace template's `${workspaceFolder}/.venv/bin/python3` → `/opt/venv/bin/python3` (the decommissioned Debian image path). That value lands in `assets/workspace/.vscode/settings.json:7`, but the Nix image uses `/root/assets/workspace/.venv` (see `assets/workspace/.devcontainer/devcontainer.json:21`). Downstream projects get a broken IDE Python interpreter.

## Recommendation
Update the `manifest.toml` transform target to the Nix venv path, regenerate, and confirm `settings.json`. Spot-check inside the built image that the interpreter resolves.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
