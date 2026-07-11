---
type: issue
state: closed
created: 2026-07-06T16:24:33Z
updated: 2026-07-08T07:54:19Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/878
comments: 1
labels: bug, priority:high, area:workspace, effort:small, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:32.145Z
---

# [Issue 878]: [fix(workspace): scaffold upgrade replaces .pre-commit-config.yaml, silently clobbering repo-specific hook config](https://github.com/vig-os/devkit/issues/878)

### Description

Found during 0.4.0 consumer field-validation (EXOMA/hyrr `feature/519-devcontainer-rc4-validation`, adoption commit 1812b74).

The scaffold upgrade replaced the consumer's `.pre-commit-config.yaml` wholesale (166 lines changed), silently dropping repo-specific configuration:

- the global `exclude:` block (physics data tables `data/stopping/`, `*.dat`, generated Tauri schemas, logo SVGs, jupytext notebook pairs, scratch docs) — after the upgrade, `prek run --all-files` in the 0.4.0 image "fixed" ~45 files it must never touch, including binary-adjacent `.dat` data tables;
- per-hook excludes, e.g. `detect-private-key` exclusion for `worker/src/index.ts` (PEM marker literals used as pattern strings) — post-upgrade the suite reports a false-positive private key.

A config replaced on upgrade must either be **managed** (and then repos can't customize it) or **preserved/merged** — replacing a customized file without warning is the worst of both. Same class as the justfile.project recipe-stranding issue (filed separately); together they made the consumer's hook suite unusable after the upgrade until hand-repaired.

### Possible Solution

Preserve-on-upgrade with a diff hint, or a merge step that retains `exclude:` blocks and per-hook `exclude:` keys, or at minimum a loud upgrade-time warning + MIGRATION.md entry listing what will be replaced.

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

