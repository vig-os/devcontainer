---
type: issue
state: closed
created: 2026-07-07T15:32:06Z
updated: 2026-07-08T07:54:30Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/914
comments: 1
labels: bug, priority:high, area:ci, effort:small, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:25.385Z
---

# [Issue 914]: [fix(ci): consumer template ships devcontainer-only renovate-changelog mirror step](https://github.com/vig-os/devkit/issues/914)

Found during 0.4.1-rc1 consumer-upgrade testing (regression from the #874/#863 self-mirror work).

## Problem

The manifest (`scripts/manifest.toml`) syncs `.github/workflows/renovate-changelog-build.yml` and `renovate-changelog-commit.yml` from repo root into the consumer template `assets/workspace/…` **verbatim** (no transform). The devcontainer repo's own copy legitimately keeps its `assets/workspace/.devcontainer/CHANGELOG.md` mirror in lockstep:

- `renovate-changelog-build.yml`: `cp CHANGELOG.md assets/workspace/.devcontainer/CHANGELOG.md` (+ the `changelog-artifact/assets/workspace/...` copy).
- `renovate-changelog-commit.yml`: `FILE_PATHS: CHANGELOG.md,assets/workspace/.devcontainer/CHANGELOG.md`.

No consumer has an `assets/workspace/` tree, so under `set -euo pipefail` these steps hard-fail on every consumer Renovate changelog run. Confirmed leaked into hyrr and talys during upgrade testing, and by direct inspection of the rc1 image template.

## Proposed fix

Add a manifest transform (e.g. `RemoveBlock` / `RemoveLines`) on both renovate-changelog entries that strips the `assets/workspace` mirror step and the extra `FILE_PATHS` path when generating the consumer template, then re-run `just sync`. The devcontainer repo's own root workflows keep the mirror; only the downstream template drops it.

Refs: #874
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

