---
type: issue
state: closed
created: 2026-06-25T12:12:30Z
updated: 2026-07-01T11:17:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/706
comments: 1
labels: bug, priority:high, area:workspace, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:02.062Z
---

# [Issue 706]: [[BUG] Downstream venv path Sed transform points at the dead Debian /opt/venv path](https://github.com/vig-os/devkit/issues/706)

## Problem
`scripts/manifest.toml:47` rewrites the workspace template's `${workspaceFolder}/.venv/bin/python3` → `/opt/venv/bin/python3` (the decommissioned Debian image path). That value lands in `assets/workspace/.vscode/settings.json:7`, but the Nix image uses `/root/assets/workspace/.venv` (see `assets/workspace/.devcontainer/devcontainer.json:21`). Downstream projects get a broken IDE Python interpreter.

## Recommendation
Update the `manifest.toml` transform target to the Nix venv path, regenerate, and confirm `settings.json`. Spot-check inside the built image that the interpreter resolves.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:17 AM_

Resolved on `dev` by PR #716 (`fix(setup): point the workspace python interpreter at the workspace venv`). The dead `/opt/venv` sed transform is gone — the scaffolded `.vscode/settings.json` now points at `${workspaceFolder}/.venv/bin/python3`, with a regression guard in `tests/test_transforms.py` asserting the interpreter never resolves to `/opt/venv`.

