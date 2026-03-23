---
type: issue
state: closed
created: 2026-03-22T12:27:55Z
updated: 2026-03-22T12:59:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/410
comments: 1
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-23T04:34:21.393Z
---

# [Issue 410]: [[BUG] sync-main-to-dev conflict detection always reports false positives](https://github.com/vig-os/devcontainer/issues/410)

### Description

The "Detect merge conflicts" step in `sync-main-to-dev.yml` always reports `conflict=true`, even when dev is a strict ancestor of main and conflicts are mathematically impossible. This causes every sync PR to be mislabeled as `merge-conflict` and auto-merge is never enabled.

### Steps to Reproduce

1. Push to `main` (triggers sync-main-to-dev workflow)
2. Workflow runs "Detect merge conflicts" step
3. `git merge --no-commit --no-ff origin/main 2>/dev/null` returns non-zero
4. PR is created with `(conflicts)` title and `merge-conflict` label
5. "Enable auto-merge" step is skipped

### Expected Behavior

When dev is behind main with no divergent commits, the conflict check should report `conflict=false`, the PR should have a clean title, no `merge-conflict` label, and auto-merge should be enabled.

### Actual Behavior

Every run reports false conflicts. Verified across 5 consecutive runs in downstream (vig-os/devcontainer-smoke-test) and 1 run in upstream (vig-os/devcontainer). Evidence from [PR #59](https://github.com/vig-os/devcontainer-smoke-test/pull/59): GitHub API confirms `mergeStateStatus: CLEAN` and `mergeable: MERGEABLE`, branch compare shows dev is 0 ahead / 3 behind main.

### Environment

- **Upstream:** `ubuntu-22.04` runner, git 2.53.0
- **Downstream:** `ghcr.io/vig-os/devcontainer` container on `ubuntu-22.04`, git 2.39.5
- Bug reproduces in both environments

### Additional Context

The exact cause of the `git merge` non-zero exit is unknown because `2>/dev/null` suppresses all error output. The step does not distinguish between actual conflicts (exit 1) and other failures (exit 128+).

Affected workflow runs (downstream): `23402800270`, `23382600708`, `23382437352`, `23381148959`, `23339310830`. Upstream: `23060324149`.

Both `.github/workflows/sync-main-to-dev.yml` (upstream) and the downstream copy are affected.

### Possible Solution

1. Remove or replace `2>/dev/null` — capture stderr for logging
2. Distinguish exit codes: 1 = conflict, other = unexpected error
3. Add a fast-path: `git merge-base --is-ancestor origin/dev origin/main` → skip conflict check (conflicts impossible when dev is an ancestor)
4. Consider `git merge-tree --write-tree` (git 2.38+) for in-memory merge without working-tree side effects

### Changelog Category

Fixed

---

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [c-vigo]()

_Posted on March 22, 2026 at 12:31 PM_

## Implementation Plan

### Analysis

The `Detect merge conflicts` step (L172-183) uses `git merge --no-commit --no-ff origin/main 2>/dev/null` to trial-merge main into the local dev checkout. Two problems:

1. **`2>/dev/null` swallows ALL errors** — any non-zero exit (permissions, ownership, config) is misinterpreted as a merge conflict.
2. **Working-tree merge is fragile** — it depends on clean index state, correct directory ownership, and git config, all of which vary between runner and container environments.

The false positive cascades into three downstream effects in the same job:
- **"Create PR" step** (L205-255): picks the `(conflicts)` title/body path and adds the `merge-conflict` label.
- **"Enable auto-merge" step** (L257-268): condition `steps.merge-check.outputs.conflict != 'true'` evaluates false → step is skipped.

### Approach: replace trial merge with `git merge-tree`

`git merge-tree --write-tree <branch1> <branch2>` (git ≥ 2.38) performs a **purely in-memory** three-way merge — no working tree, no index, no config dependencies. Exit 0 = clean, exit 1 = conflicts.

Both environments meet the prerequisite: container has git 2.39.5, runner has git 2.53.0.

### Changes

**File 1 — `.github/workflows/sync-main-to-dev.yml`**

Replace the `Detect merge conflicts` step body (L175-183):

```bash
set -euo pipefail
retry --retries 3 --backoff 3 --max-backoff 20 -- git fetch origin main dev
if git merge-tree --write-tree origin/dev origin/main >/dev/null 2>&1; then
  echo "conflict=false" >> "$GITHUB_OUTPUT"
  echo "Trial merge clean — no conflicts detected."
else
  echo "conflict=true" >> "$GITHUB_OUTPUT"
  echo "::warning::Trial merge detected conflicts between origin/dev and origin/main."
  git merge-tree --write-tree origin/dev origin/main 2>&1 || true
fi
```

Key differences from current code:
- `git merge-tree` operates in-memory — no `git merge --abort` cleanup needed.
- Fetches both `main` and `dev` to ensure refs are fresh (current code only fetches `main`).
- On conflict, re-runs merge-tree **without** suppression to log conflicting paths.
- Uses `::warning::` annotation for visibility in the Actions UI.

No changes to the "Create PR" or "Enable auto-merge" steps — they already key off `steps.merge-check.outputs.conflict` correctly.

**File 2 — downstream smoke-test copy** (out of scope)

The downstream `vig-os/devcontainer-smoke-test` maintains its own copy of this workflow (per its header comment: "intentionally decoupled"). The same fix should be applied there separately after verifying it works upstream.

### Test strategy

This is a CI workflow change — no unit-testable code. Verification:

1. Push fix to a feature branch, trigger `workflow_dispatch` on that branch.
2. Confirm the `Detect merge conflicts` step logs "Trial merge clean" and sets `conflict=false`.
3. Confirm "Enable auto-merge" step runs (not skipped).
4. Manually verify with a branch that has real CHANGELOG conflicts to confirm true positives still work.

### Scope

- 1 file changed: `.github/workflows/sync-main-to-dev.yml`
- ~10 lines replaced in the `Detect merge conflicts` step
- No changes to step conditions, PR creation logic, or auto-merge logic

