---
type: issue
state: open
created: 2026-06-25T12:12:31Z
updated: 2026-06-25T12:12:31Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/707
comments: 0
labels: bug, area:workflow, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:53.276Z
---

# [Issue 707]: [[BUG] Duplicate sync-manifest pre-commit hook definition](https://github.com/vig-os/devcontainer/issues/707)

## Problem
`.pre-commit-config.yaml` defines `id: sync-manifest` twice — line 125 (no file filter, runs every commit) and line 226 (filtered to `manifest.toml`). Causes redundant/confusing double execution.

## Recommendation
Keep one definition (prefer the `manifest.toml`-filtered one), delete the other. Verify with `pre-commit run sync-manifest --all-files`.

## Context
Found during the state-of-the-repo review of #670 (epic #625); flagged independently by two reviewers.

Refs: #625
