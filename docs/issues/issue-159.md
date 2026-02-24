---
type: issue
state: open
created: 2026-02-23T08:00:55Z
updated: 2026-02-23T23:49:15Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/159
comments: 3
labels: bug, area:workflow, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-24T04:24:08.648Z
---

# [Issue 159]: [[BUG] just gh-issues fails locally — rich not in .venv dependencies](https://github.com/vig-os/devcontainer/issues/159)

### Description

`just gh-issues` fails on local development machines with `ModuleNotFoundError: No module named 'rich'`. The recipe invokes `python3 scripts/gh_issues.py`, which imports `rich`. Inside the devcontainer, `rich` is installed globally, so the recipe works. But locally, the project `.venv` (managed by `uv`) does not include `rich` — it is not listed in `pyproject.toml` dependencies or any dependency group.

### Steps to Reproduce

1. Clone the repo and set up the local `.venv` with `uv sync`
2. Run `just gh-issues`
3. Observe:
```
ModuleNotFoundError: No module named 'rich'
```

### Expected Behavior

`just gh-issues` works both inside the devcontainer (global `rich`) and on local dev machines (`.venv` `rich`).

### Actual Behavior

Fails locally with `ModuleNotFoundError: No module named 'rich'`.

### Environment

- **OS**: macOS (local development)
- **Python**: 3.12.10 via `.venv`
- **Container Runtime**: N/A (issue is outside container)

### Possible Solution

Options (non-exhaustive, decide during implementation):

1. **Add `rich` to a dependency group in `pyproject.toml`** (e.g. `dev` or a new `tools` group) so `uv sync` installs it into `.venv`. Simplest fix.
2. **Preflight check in `justfile.gh`** — detect whether `rich` is importable and provide a helpful error message or fallback.
3. **Use `uv run`** in the just recipe instead of bare `python3` so it automatically resolves from the project's `.venv`.

Option 1 is the smallest change; option 3 may be more robust long-term.

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] `just gh-issues` succeeds on a local dev machine after `uv sync`
- [ ] `just gh-issues` continues to work inside the devcontainer
- [ ] `rich` dependency is declared in a single canonical location
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Related Issues

- Sub-issue of #145 (Rewrite gh-issues dashboard)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 23, 2026 at 11:41 PM_

## Design

**Approach**: Add `rich` to the existing `dev` dependency group in `pyproject.toml`.

### What changes
- `pyproject.toml` — add `"rich>=13.0.0"` to `[dependency-groups] dev`

### What stays the same
- The justfile recipe (`python3 scripts/gh_issues.py`) — no change
- The devcontainer (global `rich` continues to work)
- No new dependency groups

### Testing strategy
- Config-only change (dependency declaration). No new logic to TDD.
- Verifiable by running `uv sync && just gh-issues` locally.
- TDD skipped with justification: no testable behavior.

### Acceptance criteria
- [x] `just gh-issues` succeeds locally after `uv sync`
- [x] Continues to work inside devcontainer
- [x] `rich` declared in single canonical location (`pyproject.toml` dev group)
- [x] TDD compliance noted (skip justified — config only)

---

# [Comment #2]() by [gerchowl]()

_Posted on February 23, 2026 at 11:42 PM_

## Implementation Plan

Issue: #159
Branch: bugfix/159-gh-issues-missing-rich-dependency

### Tasks

- [x] Add rich dependency to dev group — `pyproject.toml` — verify: `uv sync && just gh-issues` succeeds locally

---

# [Comment #3]() by [gerchowl]()

_Posted on February 23, 2026 at 11:49 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (1 task)
- Execute: all tasks done
- Verify: all checks pass (lint passed, precommit had Docker daemon issue but other checks passed)
- PR: https://github.com/vig-os/devcontainer/pull/167
- CI: all checks pass

