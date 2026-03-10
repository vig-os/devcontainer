---
type: issue
state: closed
created: 2026-03-09T06:50:13Z
updated: 2026-03-09T08:14:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/238
comments: 1
labels: bug, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:46.479Z
---

# [Issue 238]: [[BUG] Agent-blocklist scripts use wrong project_root and missing vig_utils dependency](https://github.com/vig-os/devcontainer/issues/238)

### Description

Three agent-blocklist scripts in `.devcontainer/scripts/` have two implementation defects from #163:

**A. Wrong `project_root` resolution**

All three scripts use `Path(__file__).resolve().parent.parent`, which resolves to `.devcontainer/` — not the repo root. The blocklist at `.github/agent-blocklist.toml` is never found, so every check silently no-ops.

Files:
- `scripts/check-agent-identity.py` (line 53)
- `scripts/check-pr-agent-fingerprints.py` (line 20)
- `scripts/prepare-commit-msg-strip-trailers.py` (line 54)

**B. Missing `vig_utils` dependency**

`check-agent-identity.py` and `check-pr-agent-fingerprints.py` import from `vig_utils.agent_blocklist`, which doesn't exist in downstream repos (and isn't declared as a dependency). The import would fail even if the path were correct.

**C. Inverted `IN_CONTAINER` guard in `.githooks/prepare-commit-msg`**

The hook checks `IN_CONTAINER = "false"`, but outside the devcontainer the variable is typically **unset** (not the literal string `"false"`). The guard never triggers. Should check `!= "true"` to fail closed.

### Steps to Reproduce

1. Clone any downstream repo using this devcontainer template (e.g. `devcontainer-smoke-test`)
2. Run `python .devcontainer/scripts/check-agent-identity.py` — exits 0 without checking anything
3. Commit from the host — `prepare-commit-msg` hook does not block it

### Expected Behavior

- Scripts resolve the repo root correctly and enforce the blocklist
- `IN_CONTAINER` guard blocks commits when the variable is unset

### Actual Behavior

- All three scripts silently no-op (blocklist path never found)
- Host commits are not blocked by the prepare-commit-msg hook

### Environment

- Discovered in [`devcontainer-smoke-test` PR #15](https://github.com/vig-os/devcontainer-smoke-test/pull/15) Copilot review
- Affects any repo using the devcontainer template

### Possible Solution

- **A:** Change `Path(__file__).resolve().parent.parent` → `.parents[2]` in all three scripts
- **B:** Inline the blocklist loading logic using `tomllib` (stdlib) instead of importing from `vig_utils`
- **C:** Change `if [ "${IN_CONTAINER:-}" = "false" ]` → `if [ "${IN_CONTAINER:-}" != "true" ]`

### Changelog Category

Fixed

Refs: #163, [vig-os/devcontainer-smoke-test#15](https://github.com/vig-os/devcontainer-smoke-test/pull/15)
---

# [Comment #1]() by [c-vigo]()

_Posted on March 9, 2026 at 08:02 AM_

## Implementation Plan

### Triage

Issue #238 describes three defects (A, B, C) from #163. After analysing the current codebase, **two of the three were already resolved** by the `vig-utils` migration (#218):

| Defect | Status | Explanation |
|--------|--------|-------------|
| **A. Wrong `project_root`** | ✅ Already fixed | The old standalone scripts used `Path(__file__).resolve().parent.parent` which resolved to `.devcontainer/` instead of the repo root. The migration to `vig-utils` replaced this with `find_repo_root(start=Path(__file__))` (`packages/vig-utils/src/vig_utils/utils.py` L122-147), which traverses up from `cwd` looking for `.github/`. Pre-commit hooks run with `cwd` = repo root, so this resolves correctly now. |
| **B. Missing `vig_utils` dependency** | ✅ Already fixed | The old scripts imported from `vig_utils.agent_blocklist` which didn't exist in downstream repos. The scripts now live *inside* `vig-utils` and import from `vig_utils.utils`. They're invoked as entry points (`uv run check-agent-identity`), so the dependency is always available. |
| **C. Inverted `IN_CONTAINER` guard** | ❌ Still present | All three workspace githooks (`assets/workspace/.githooks/{pre-commit,prepare-commit-msg,commit-msg}`) use `= "false"` but `IN_CONTAINER` is typically **unset** (not the literal `"false"`) outside the devcontainer. The guard never triggers on the host. |

### Tasks

- [x] Task 1: Write failing BATS tests for the `IN_CONTAINER` guard — `tests/bats/githooks.bats` — verify: 6 tests fail (unset, empty, "false" × 3 hooks)
- [x] Task 2: Fix `IN_CONTAINER` guard from `= "false"` to `!= "true"` in all three hooks — `assets/workspace/.githooks/{pre-commit,prepare-commit-msg,commit-msg}` — verify: all 12 BATS tests pass
- [x] Task 3: Update `CHANGELOG.md` under `### Fixed` — verify: entry references #238

