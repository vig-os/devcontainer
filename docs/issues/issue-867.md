---
type: issue
state: closed
created: 2026-07-06T08:24:45Z
updated: 2026-07-06T10:47:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/867
comments: 0
labels: bug, priority:low, area:ci, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:34.038Z
---

# [Issue 867]: [fix(changelog): Renovate entries land under the #### Modules sub-heading](https://github.com/vig-os/devkit/issues/867)

Cosmetic follow-up split out of #863 (see the "Out of scope" note on PR #864).

## Problem

`insert_renovate_changelog_entry` in `packages/vig-utils/src/vig_utils/renovate_changelog_pr.py` appends new entries at the **bottom** of the `## Unreleased → ### Changed` block. Since #816 introduced the `#### Modules` sub-heading convention inside `### Changed`, a Renovate dependency bump now lands **under `#### Modules`**, misattributing a CI-action/dependency bump as a module change (observed on #862, where the codeql-action bump appeared beneath `#### Modules`).

## Desired behaviour

Renovate entries land as **plain `### Changed` bullets at the top of the section**, above any `####` sub-heading, with correct Keep-a-Changelog spacing.

## Fix

Insert at the top of `### Changed` (reuse the existing `min_insert` marker) instead of at `next_sec`/end, with a blank-line spacing guard when the section opens with a heading. The position-independent idempotency guard (`_pr_marked_in_changed`) is unaffected. TDD with a `#### Modules` fixture.

Targets `dev`. Goes live for Renovate PRs after the next image rebuild that bakes the updated `vig-utils` console script.
