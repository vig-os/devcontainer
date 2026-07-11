---
type: issue
state: closed
created: 2026-07-07T15:32:14Z
updated: 2026-07-08T07:54:32Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/915
comments: 1
labels: bug, priority:high, area:workspace, effort:small, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:24.976Z
---

# [Issue 915]: [fix(workspace): scaffold justfile.gh log/branch recipes collide with consumer justfile.project](https://github.com/vig-os/devkit/issues/915)

Found during 0.4.1-rc1 consumer-upgrade testing.

## Problem

The scaffold-managed `.devcontainer/justfile.gh` (SSoT: repo-root `justfile.gh`, synced via manifest) defines `log` and `branch` recipes. Any consumer whose preserved `justfile.project` also defines `log`/`branch` (mat does) gets a hard `just` parse error after upgrade:

```
error: recipe `log` first defined on line 23 is redefined on line 84
```

`just` refuses to load **any** recipe until the duplicate is resolved, which also silently disables the #877 base-recipe repair (it skips with a false "no 'sync' recipe found" warning). Reproduced on mat both from a clean 0.3.3 base and from the 0.4.0 branch. Out of the box, `just` is unusable until the consumer hand-deletes the duplicates.

Note: `log`/`branch` were added to `justfile.gh` during the 0.4.0 cycle, so this is a latent 0.4.0 collision surfaced by rc1 testing, not strictly rc1-introduced — but it breaks the upgrade path this release targets and should be fixed in 0.4.1.

## Proposed fix

Namespace the scaffold recipes so they cannot collide with arbitrary consumer recipes: `log`→`gh-log`, `branch`→`gh-branch` (matching the existing `gh-issues`). Update the SSoT `justfile.gh`, re-sync, and update any internal callers (skills/docs).

Refs: #877
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

