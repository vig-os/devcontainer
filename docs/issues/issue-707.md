---
type: issue
state: closed
created: 2026-06-25T12:12:31Z
updated: 2026-07-01T14:35:57Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/707
comments: 1
labels: bug, area:workflow, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:01.706Z
---

# [Issue 707]: [[BUG] Duplicate sync-manifest pre-commit hook definition](https://github.com/vig-os/devkit/issues/707)

## Problem
`.pre-commit-config.yaml` defines `id: sync-manifest` twice — line 125 (no file filter, runs every commit) and line 226 (filtered to `manifest.toml`). Causes redundant/confusing double execution.

## Recommendation
Keep one definition (prefer the `manifest.toml`-filtered one), delete the other. Verify with `pre-commit run sync-manifest --all-files`.

## Context
Found during the state-of-the-repo review of #670 (epic #625); flagged independently by two reviewers.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 02:35 PM_

Already resolved on `dev`. `.pre-commit-config.yaml` now defines `id: sync-manifest` exactly once (the duplicate was removed in `30f02ed4`, fix(setup): drop the duplicate sync-manifest pre-commit hook, #712). No double execution remains. Closing as done.

