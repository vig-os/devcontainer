---
type: issue
state: closed
created: 2026-03-17T15:47:36Z
updated: 2026-07-02T11:41:45Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/349
comments: 1
labels: area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:21.483Z
---

# [Issue 349]: [[CI] Address Node.js 20 action deprecation warnings before June 2, 2026](https://github.com/vig-os/devkit/issues/349)

## Context
Release workflow run [#23201577188](https://github.com/vig-os/devcontainer/actions/runs/23201577188) shows Node.js 20 deprecation warnings:
- Build and Test (amd64): `actions/cache@0400d5f...` uses Node.js 20
- Build and Test (arm64): `actions/cache@0400d5f...` uses Node.js 20
- Publish Release: `anchore/sbom-action@57aae52...` uses Node.js 20

GitHub warning indicates JavaScript actions will default to Node.js 24 starting June 2, 2026.

## Goal
Remove or mitigate Node.js 20 runtime dependencies in release CI ahead of the deadline.

## Scope
- Investigate transitive `actions/cache@0400d5f...` source (likely via `docker/build-push-action`) and upgrade to a Node.js 24-compatible path.
- Investigate `anchore/sbom-action` Node.js 24 readiness.
- If upstream does not support Node.js 24 in time, define fallback implementation (e.g., SBOM generation via CLI) and migration path.

## Acceptance Criteria
- `release.yml` no longer emits Node.js 20 deprecation warnings for action runtimes, or
- An explicit documented temporary exception exists with owner + follow-up date if blocked by upstream.
- Validation run confirms current status and remaining risk.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 2, 2026 at 11:41 AM_

All CI actions migrated to node24 runtimes ahead of the 2026-06-02 deadline — including the originally-flagged `anchore/sbom-action` (v0.24.0) and `actions/cache` (v6). No Node 20 action runtimes remain in `.github/` (PRs #540/#541/#543/#544). Closing.

