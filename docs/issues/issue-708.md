---
type: issue
state: closed
created: 2026-06-25T12:12:33Z
updated: 2026-07-01T14:35:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/708
comments: 1
labels: chore, area:ci, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:01.331Z
---

# [Issue 708]: [[CHORE] ruff target-version lags runtime (py312 vs requires-python >=3.14)](https://github.com/vig-os/devkit/issues/708)

## Problem
`pyproject.toml:8` sets `requires-python = ">=3.14,<3.15"` but `:58` sets `target-version = "py312"`. Ruff lints against the wrong Python version.

## Recommendation
Set `target-version = "py314"`; confirm `ruff check` / `just lint` clean.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 02:35 PM_

Already resolved on `dev`. `pyproject.toml:58` sets `target-version = "py314"` (matching `requires-python = ">=3.14,<3.15"`), landed in `8975ecaa` (chore(ci): set ruff target-version to py314, #711). `ruff` now lints against the correct Python version. Closing as done.

