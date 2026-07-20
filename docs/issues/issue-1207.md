---
type: issue
state: closed
created: 2026-07-17T20:27:08Z
updated: 2026-07-20T10:47:13Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1207
comments: 1
labels: feature, priority:medium, area:workspace, effort:small, semver:minor
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:05.800Z
---

# [Issue 1207]: [workflow-model: DEVKIT_WORKFLOW manifest key + read/writeback + guards](https://github.com/vig-os/devkit/issues/1207)

Part of #1205.

Add the `DEVKIT_WORKFLOW` (`gitflow`|`trunk`, empty ⇒ gitflow) manifest key:
- `assets/workspace/.vig-os` template key + comment after the `DEVKIT_MODE` block (mirror `DEVKIT_MODE`'s comment).
- `assets/init-workspace.sh`: read pre-overwrite (~:290-297) + **conditional writeback only when trunk** (mirror `DEVKIT_TAG_PREFIX` ~:1440-1451, keeps existing `.vig-os` byte-identical); flag resolve order flag > manifest > default gitflow; loud enum guard; contradiction guard (mirror mode :313-329) refusing an explicit `--workflow` that differs from persisted, outside `--preview`/`--smoke-test`.
- `install.sh` persisted-read + corrupt/contradiction guards (~:532-560).

Refs: #1205
---

# [Comment #1]() by [c-vigo]()

_Posted on July 20, 2026 at 10:47 AM_

Implemented via PR #1212, shipped in 1.4.0 via unfreeze PR #1215.

