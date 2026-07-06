---
type: issue
state: open
created: 2026-06-25T12:12:33Z
updated: 2026-06-25T12:12:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/708
comments: 0
labels: chore, area:ci, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:52.989Z
---

# [Issue 708]: [[CHORE] ruff target-version lags runtime (py312 vs requires-python >=3.14)](https://github.com/vig-os/devcontainer/issues/708)

## Problem
`pyproject.toml:8` sets `requires-python = ">=3.14,<3.15"` but `:58` sets `target-version = "py312"`. Ruff lints against the wrong Python version.

## Recommendation
Set `target-version = "py314"`; confirm `ruff check` / `just lint` clean.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
