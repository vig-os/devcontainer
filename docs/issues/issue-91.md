---
type: issue
state: open
created: 2026-02-19T14:42:07Z
updated: 2026-02-19T15:28:37Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/91
comments: 0
labels: chore
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-19T15:36:54.394Z
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

- [ ] Remove `issues` and `pull_request` triggers from `sync-issues.yml`
- [ ] Keep `schedule` and `workflow_dispatch` triggers
- [ ] Simplify target branch logic (remove PR-merged-into-main branch)
- [ ] Optionally adjust cron time if needed
- [ ] Verify `release.yml` and `post-release.yml` dispatch calls still work (no changes needed there)
