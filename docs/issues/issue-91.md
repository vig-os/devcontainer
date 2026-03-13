---
type: issue
state: closed
created: 2026-02-19T14:42:07Z
updated: 2026-02-20T10:37:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/91
comments: 3
labels: chore, priority:blocking
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-20T13:17:20.320Z
---

# [Issue 91]: [Reduce sync-issues workflow frequency to daily schedule only](https://github.com/vig-os/devcontainer/issues/91)

## Description

The `sync-issues.yml` workflow currently triggers on multiple events:
- **Schedule:** daily at midnight UTC (`0 0 * * *`)
- **Issues:** `opened`, `reopened`, `closed`
- **Pull requests:** `opened`, `closed`
- **Manual:** `workflow_dispatch`

The event-driven triggers (issues and pull_request) cause the workflow to run on every issue or PR state change, which clutters the Actions tab and generates unnecessary commits and workflow runs.

## Proposed Change

Remove the `issues` and `pull_request` event triggers, keeping only:
- **Schedule:** daily at night (e.g. `0 2 * * *` — 2:00 AM UTC)
- **Manual:** `workflow_dispatch` (for on-demand syncs when needed)

This also allows simplifying the target branch decision logic. Currently the workflow handles a `pull_request` merged-into-main case that becomes dead code once the PR trigger is removed. The simplified logic would be:
- `workflow_dispatch` with `target-branch` input → use that value (validated against allowed branches)
- Everything else (schedule, dispatch without input) → `dev`

**Note:** The `workflow_dispatch` trigger with `target-branch` input must be preserved — it is used by `release.yml` (targets `release/$VERSION`) and `post-release.yml` (targets `dev`) to trigger on-demand syncs during the release cycle.

## Acceptance Criteria

- [x] Remove `issues` and `pull_request` triggers from `sync-issues.yml`
- [x] Keep `schedule` and `workflow_dispatch` triggers
- [x] Simplify target branch logic (remove PR-merged-into-main branch)
- [x] Optionally adjust cron time if needed
- [x] Verify `release.yml` and `post-release.yml` dispatch calls still work (no changes needed there)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 08:38 AM_

Closed by merged PR #95 (chore/91-reduce-sync-issues-frequency, merged 2026-02-19). Workflow frequency reduced to daily schedule only.

---

# [Comment #2]() by [c-vigo]()

_Posted on February 20, 2026 at 08:57 AM_

@gerchowl the [2am sync](https://github.com/vig-os/devcontainer/actions/runs/22211151138/job/64245460160) failed, leave open until I fix it

---

# [Comment #3]() by [c-vigo]()

_Posted on February 20, 2026 at 09:19 AM_

## Implementation plan: fix sync-issues schedule trigger and align main/dev

### Root Cause

PR #95 partially implemented issue #91 on `main` (removed `issues`/`pull_request` triggers, adjusted cron) but left a gap in the target branch logic. On schedule events, `github.event.inputs` does not exist, so:

- Line 53: `ref: ${{ github.event.inputs.target-branch }}` resolves to empty — checkout defaults to `main` (harmless but wrong: issue #91 says schedule should target `dev`)
- Line 106: `TARGET_BRANCH: refs/heads/${{ github.event.inputs.target-branch }}` resolves to `refs/heads/` — commit-action gets a 404 "Not Found"

The fix: add `|| 'dev'` fallbacks everywhere `github.event.inputs.*` is referenced, so schedule triggers default to `dev`.

### State Differences (main vs dev)

`dev` already has several improvements over `main` for this file:

- Pinned SHA action references (e.g. `actions/checkout@34e11...  # v4`)
- `output-dir: 'docs'` instead of `.github_data`
- `runs-on: ubuntu-22.04` instead of `ubuntu-latest`
- `timeout-minutes: 10`
- Top-level `permissions: {}`
- Removed stale cache restore-key prefix `sync-issues-state-`

The plan is to use dev's version as the base and add the fix + new inputs on top, so both branches converge.

### File Inventory

- `.github_data/` on `main`: 31 files (stale, will never be written to again since output-dir changed to `docs`)
- `.github_data/` on `dev`: 95 files (also stale, same reason)
- `docs/` on `dev`: 104 files (active sync target)

### Phase 1: Bugfix PR to main

#### 1. Create and link branch

Branch name `bugfix/91-fix-sync-issues-schedule` from `main`, linked to issue #91 via `gh issue develop`.

#### 2. Replace workflow file with dev version + fix + enhancements

Take `.github/workflows/sync-issues.yml` from `dev` as the base (it already has all the improvements above). Then apply these changes:

**a) Add `output-dir` and `commit-msg` workflow_dispatch inputs** (with defaults `docs` and `chore: sync issues and PRs`):

```yaml
workflow_dispatch:
  inputs:
    force-update:
      description: 'Force update all issues and PRs (ignores last sync timestamp)'
      required: false
      default: false
      type: boolean
    target-branch:
      description: 'Target branch to commit changes to (e.g., dev, release/x.y.z).'
      required: false
      default: 'dev'
      type: string
    output-dir:
      description: 'Directory to write synced issue/PR files to.'
      required: false
      default: 'docs'
      type: string
    commit-msg:
      description: 'Commit message for the sync commit.'
      required: false
      default: 'chore: sync issues and PRs'
      type: string
```

**b) Add `|| 'default'` fallback for all input references** (schedule events have no inputs):

- Checkout ref: `ref: ${{ github.event.inputs.target-branch || 'dev' }}`
- Sync action output-dir: `output-dir: ${{ github.event.inputs.output-dir || 'docs' }}`
- Commit TARGET_BRANCH: `TARGET_BRANCH: refs/heads/${{ github.event.inputs.target-branch || 'dev' }}`
- Commit COMMIT_MESSAGE: `COMMIT_MESSAGE: ${{ github.event.inputs.commit-msg || 'chore: sync issues and PRs' }}`
- Force-update: `updated-since: ${{ (github.event.inputs.force-update == 'true' && '1970-01-01T00:00:00Z') || '' }}`

**c) Callers are unaffected**: `release.yml` dispatches with `-f "target-branch=release/$VERSION"` and `post-release.yml` with `-f "target-branch=dev"` — neither passes `output-dir` or `commit-msg`, so they get defaults automatically.

#### 3. Delete `.github_data/` on this branch

Remove the 31 stale files in `.github_data/` (issues + pull-requests subdirectories). These were the old sync target and will never be updated again.

#### 4. Commit, push, and create PR to main

Can be multiple commits (e.g., one for the workflow fix, one for the `.github_data` deletion). PR references issue #91.

### Phase 2: Sync to dev (after main PR merges)

1. Create a branch from `dev` (e.g. `chore/sync-main-to-dev`)
2. Merge `main` into it — this brings the workflow fix and `.github_data` deletion
3. Additionally delete the 95 stale `.github_data/` files on dev (they were added independently on dev and won't be removed by the merge)
4. Update CHANGELOG under `## Unreleased` if warranted (likely a one-liner noting the schedule fix)
5. PR to `dev` for review

### Risks / Notes

- The `force-update` input reference already uses `&&`/`||` but still depends on `github.event.inputs.force-update` which is empty on schedule. Current behavior: empty evaluates to falsy, so `||` returns `''` — the sync action treats empty `updated-since` as "use last-sync state". This is correct; no change needed to the logic, but the parenthesization should be verified.
- After merge, the next scheduled run (2:00 AM UTC) will checkout `dev`, sync to `docs/`, and commit to `dev` — the desired behavior per issue #91.

