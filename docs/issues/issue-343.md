---
type: issue
state: closed
created: 2026-03-17T14:36:47Z
updated: 2026-03-17T14:59:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/343
comments: 0
labels: bug, priority:high, area:ci, area:workflow
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:22.527Z
---

# [Issue 343]: [fix(ci): sync workspace manifest during release finalization to prevent changelog drift](https://github.com/vig-os/devcontainer/issues/343)

## Problem

Release finalization updates root `CHANGELOG.md` but does not sync the workspace mirror `assets/workspace/.devcontainer/CHANGELOG.md` before committing.

As a result, CI fails in Project Checks when pre-commit runs `sync-manifest` and detects modified files.

Failing run example: https://github.com/vig-os/devcontainer/actions/runs/23198605456/job/67414012578?pr=342

## Proposed Solution

In `.github/workflows/release.yml` finalize job (final releases only), run:

`uv run python scripts/sync_manifest.py sync assets/workspace/`

After changelog/doc regeneration and before collecting finalization files for commit.

## Acceptance Criteria
- Finalize workflow includes synced workspace changelog when root changelog changes.
- Release PR CI no longer fails on `sync-manifest` drift for finalized changelog updates.
- Candidate release flow remains unchanged.
- No unrelated files are modified by the finalization commit.
