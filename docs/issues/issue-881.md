---
type: issue
state: closed
created: 2026-07-07T08:22:49Z
updated: 2026-07-08T07:54:23Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/881
comments: 1
labels: bug, priority:medium, area:image, effort:small, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:31.005Z
---

# [Issue 881]: [fix(image): pre-commit binary dropped without a compat path — preserved consumer recipes and .githooks calling it break](https://github.com/vig-os/devkit/issues/881)

### Description

Found during 0.4.0 consumer field-validation (EXOPET/vault, pin 0.3.5 → 0.4.0).

The 0.4.0 image ships `prek` only; the `pre-commit` binary was retired with the prek migration (#778). Consumer files that are *preserved on upgrade* still call `pre-commit`:

- vault `justfile.project` → `precommit:` recipe ran `pre-commit run --all-files` → exit 127 in-image;
- vault `.githooks/{pre-commit,commit-msg,prepare-commit-msg}` (repo-managed `core.hooksPath` hooks from the old scaffold) → same failure at commit time, additionally with `#!/bin/bash` shebangs that break on NixOS hosts.

Same failure class as #877 (preserved config referencing retired pieces), but image-side: even a *repaired* justfile can't save a consumer whose own hook scripts call the removed tool.

### Possible Solution

One or more of: (a) ship a `pre-commit -> prek` compat shim in the image for one release cycle (prek is drop-in for `run`-style invocations); (b) MIGRATION.md entry + upgrade-time scan warning for `pre-commit` references in preserved files (`justfile.project`, `.githooks/`, docs); (c) fold into the #877 upgrade-path hardening.

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

