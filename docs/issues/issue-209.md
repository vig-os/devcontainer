---
type: issue
state: open
created: 2026-02-26T12:01:01Z
updated: 2026-02-26T12:01:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/209
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-27T04:19:04.769Z
---

# [Issue 209]: [[FEATURE] Graceful degradation when no internet connection is available](https://github.com/vig-os/devcontainer/issues/209)

## Description

Some tools shipped with the devcontainer require internet access (e.g. GitHub API via `just gh-issues`, `just sync`). When the container is started without internet connectivity, these commands currently fail in an unhandled way with no actionable feedback to the user.

The container should still start and function normally in offline environments. Network-dependent commands should detect the lack of connectivity and fail gracefully with a clear warning instead of crashing.

## Problem Statement

Users working in air-gapped environments, on a plane, or on a restricted network can't use the container meaningfully today because offline failures are silent, confusing, or produce unhelpful error messages. The container should be usable for all local-only workflows even without internet access.

## Proposed Solution

- Add a connectivity probe (e.g. a short `curl` or `ping` to a known host) that runs before any network-dependent `just` recipe.
- If the probe fails, print a clear, human-readable warning (e.g. `⚠  No internet connection — skipping gh-issues`) and exit with a non-zero code.
- Affected recipes at minimum: `just sync`, `just gh-issues`.
- The probe should be fast (low timeout) to not delay normal usage.
- Container startup (`post-start.sh`, `initialize.sh`) must not block or error on offline detection.

## Alternatives Considered

- Wrap individual tool calls in try/catch — noisier and harder to maintain than a single reusable probe.
- Skip the check entirely and rely on tool-native error messages — poor UX, messages are not actionable.

## Impact

- Benefits all users who work in connectivity-restricted environments.
- Backward compatible: no change in behavior when internet is available.

## Changelog Category

Added

## Acceptance Criteria

- [ ] `just gh-issues` prints a warning and exits cleanly when offline
- [ ] `just sync` prints a warning and exits cleanly when offline
- [ ] Container starts without errors in an offline environment
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
