---
type: issue
state: closed
created: 2026-06-26T08:14:19Z
updated: 2026-07-02T12:47:43Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/719
comments: 1
labels: chore, priority:low, area:image
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:59.320Z
---

# [Issue 719]: [chore: remove unused hadolint from the flake devTools and decide the sidecar.Containerfile fixture's fate](https://github.com/vig-os/devkit/issues/719)

## Context

Follow-up from #625 / PR #670. The Debian `Containerfile` and the `hadolint` pre-commit hook were removed when the image went Nix-only (#642), but `hadolint` is still in the flake `devTools` (`flake.nix`). It is no longer used for linting; `tests/fixtures/sidecar.Containerfile` (its only remaining lint target) is now unlinted.

## Proposed work

- Decide whether `tests/fixtures/sidecar.Containerfile` is still needed.
- If not, drop the fixture and remove `hadolint` from `devTools`. If it is, document why and either re-wire a lint or keep `hadolint` deliberately.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 2, 2026 at 12:47 PM_

Subsumed by #799 — we're dropping the sidecar/multi-container capability entirely (which resolves the fixture's fate) and removing `hadolint` from `devTools` as part of that. Tracking there.

