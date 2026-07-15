---
type: issue
state: open
created: 2026-07-15T10:04:20Z
updated: 2026-07-15T10:04:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1112
comments: 0
labels: bug, priority:low, area:workspace, effort:medium, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-15T11:04:48.208Z
---

# [Issue 1112]: [[BUG] direnv mode never sets core.hooksPath — commit-time hooks silently inactive until set manually](https://github.com/vig-os/devkit/issues/1112)

## Summary

Follow-up from **1.2.1-rc1 verification** (not fixed in the 1.2.1 train).

## Problem

In direnv mode the scaffold never sets `core.hooksPath`, so commit-time (pre-commit / prek) hooks are **silently inactive** until the consumer sets it manually. A developer can commit hook-violating content locally with no local gate.

This is currently documented in `docs/COMMIT_MESSAGE_STANDARD.md`, and CI compensates (the full hook suite runs in CI), so violations are caught before merge rather than never — but the local pre-commit gate the devcontainer mode provides is missing for direnv consumers.

## Suggested fix

Activate the hooks path automatically for direnv consumers — e.g. set `core.hooksPath` (or install the prek/pre-commit hook) via the `.envrc` / direnv hook so entering the dev shell wires up commit-time hooks, matching the devcontainer-mode experience.

## SemVer

Patch — closes a local-gate gap; CI behavior unchanged.
