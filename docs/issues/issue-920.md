---
type: issue
state: closed
created: 2026-07-07T15:52:17Z
updated: 2026-07-08T11:28:13Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/920
comments: 1
labels: feature, priority:low, area:ci, area:workspace, effort:medium
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:24.202Z
---

# [Issue 920]: [[FEATURE] Private-image CI support: authenticated resolve-image probe + templated container credentials](https://github.com/vig-os/devkit/issues/920)

## Context

Split out from #854 (Part B, audit item 8). The shipped container-based CI
workflows assume `ghcr.io/vig-os/devcontainer` is **public and
unauthenticated**. #854 documented the limitation loudly in
`assets/workspace/docs/container-ci-quirks.md` ("Public-image assumption") and
delivered the direnv nix-direct lane + the cheap skew fixes; the first-class
private-image fix was deferred here to keep that PR reviewable.

## Problem

- `assets/workspace/.github/actions/resolve-image/action.yml` validates the tag
  with an **unauthenticated** `docker manifest inspect "$IMAGE" > /dev/null 2>&1`
  — stderr is swallowed, so an auth/rate-limit failure surfaces only as the
  generic "Cannot access image manifest".
- The in-container jobs (`ci.yml`, `prepare-release.yml`, `promote-release.yml`,
  `release*.yml`, `sync-*`) declare `container: { image: … }` with **no
  `credentials:` block`**, so a private image (or an anonymous pull throttled by
  GHCR) fails opaquely at the job's container-pull step.

## Scope

- Authenticated probe in `resolve-image` (login to GHCR with a registry token
  when one is available; keep the anonymous path for public images) with a
  clear "authentication required / denied" message.
- A templated `credentials:` block on the shipped container jobs, wired to a
  documented secret (e.g. `GHCR_PULL_TOKEN`), opt-in so public consumers are
  unaffected.
- Rides the devkit rename cycle (#781), which already rewrites the whole
  `assets/workspace/` scaffold — the blast radii overlap.

Refs: #854, #781
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 11:28 AM_

Closed by #925

