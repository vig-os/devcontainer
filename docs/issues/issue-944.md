---
type: issue
state: closed
created: 2026-07-08T17:18:44Z
updated: 2026-07-09T05:40:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/944
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:19.503Z
---

# [Issue 944]: [fix: #python template declares pytest as an extra, not a dependency-group (breaks just test)](https://github.com/vig-os/devkit/issues/944)

## Problem
`templates/python/pyproject.toml` (the opt-in Python starter, #930) declares dev tooling as an **extra**:
```toml
[project.optional-dependencies]
dev = ["pytest==9.1.1", "pytest-cov==7.1.0"]
```
But the scaffold's managed `sync` recipe is groups-only by design (`sync *args="--all-groups"`; extras opt-in). So a project scaffolded from `nix flake init -t ...#python` that follows the template README ("Then `just sync` and `just test`") gets `just sync` → `uv sync --all-groups`, which does **not** install the pytest extra → `just test` → `uv run pytest` fails with `Failed to spawn: pytest`.

Not currently caught by CI: no test inits the template and runs its `just sync && just test` (`test_just_test_recipe` covers only the language-neutral base). Surfaced downstream via the smoke-test (vig-os/devcontainer#943, devcontainer-smoke-test#205).

## Fix
Move `pytest`/`pytest-cov` to `[dependency-groups].dev` (PEP 735) so the default groups-only `just sync` installs them and `uv run pytest` works. Aligns the template with the scaffold's 'extras are opt-in' contract.

Refs: #943
---

# [Comment #1]() by [c-vigo]()

_Posted on July 9, 2026 at 05:40 AM_

Fixed by #945 (merged to `release/0.5.0`). Moved `pytest`/`pytest-cov` to `[dependency-groups].dev` in `templates/python/pyproject.toml`; verified a scaffolded copy runs `uv sync --all-groups` + `uv run pytest` green. Closing.

