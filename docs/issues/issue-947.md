---
type: issue
state: closed
created: 2026-07-08T20:43:44Z
updated: 2026-07-09T05:40:32Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/947
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:18.740Z
---

# [Issue 947]: [fix: consumer release.yml reusable-calling jobs miss packages: read (startup_failure)](https://github.com/vig-os/devkit/issues/947)

## Problem
#920 added `packages: read` to the internal jobs of the reusable release workflows (`release-core.yml` x3, `release-publish.yml` x2) so they can pull the authenticated GHCR image. But the **reusable-workflow-calling jobs** in the scaffold `release.yml` (`core`, `publish`) were not updated to grant `packages: read`. A reusable workflow cannot request a permission its calling job did not grant, so the whole run fails with `startup_failure` ("workflow file issue").

- Worked in 0.4.1 (no `packages: read` anywhere; no mismatch).
- Never caught upstream: the devcontainer repo's own `release.yml` is monolithic (no reusable calls); the split lives only in the shipped scaffold, exercised only by the smoke-test.
- ci.yml is unaffected (not a reusable caller; its container jobs hold `packages: read` at job level).

Surfaced by the 0.5.0-rc1 smoke-test downstream release orchestration (devcontainer-smoke-test release run startup_failure). Refs vig-os/devcontainer#943.

## Fix
Grant `packages: read` on the `core` and `publish` calling jobs in `assets/workspace/.github/workflows/release.yml` (release-extension requests none). Audit `promote-release.yml` for the same #920 pattern.

Refs: #920
---

# [Comment #1]() by [c-vigo]()

_Posted on July 9, 2026 at 05:40 AM_

Fixed by #948 (merged to `release/0.5.0`). Granted `packages: read` on the `core` and `publish` reusable-calling jobs; verified each caller's grant is now a superset of its callee's requested scopes. Validated end-to-end: the 0.5.0-rc2 smoke-test's downstream release run went from `startup_failure` to **success** (https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28976856991). Closing.

