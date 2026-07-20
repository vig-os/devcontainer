---
type: issue
state: closed
created: 2026-07-17T20:27:19Z
updated: 2026-07-20T10:47:16Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1209
comments: 1
labels: feature, priority:medium, area:workspace, effort:medium
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:04.599Z
---

# [Issue 1209]: [workflow-model: install.sh --workflow flag + dev-branch creation gating](https://github.com/vig-os/devkit/issues/1209)

Part of #1205. Depends on #1205 sub-1 (manifest key).

- `install.sh`: `--workflow gitflow|trunk` flag parse (~:436-442) + enum validate (~:485-489); thread to init-workspace (~:713-714); adopt-persisted fallback (~:562-564).
- `init-workspace.sh`: matching `--workflow` flag parse (~:163-170) + validate (~:180-186).
- **Gate dev creation** in `setup_git_repo` (:848-875): `git branch dev` (:851-855) + missing-dev warning (:862-866) run only in gitflow; push hint (:875) drops `dev` in trunk. `git init -b main` (:825) unchanged.

Single canonical `--workflow` flag; no `--no-dev` alias.

Refs: #1205
---

# [Comment #1]() by [c-vigo]()

_Posted on July 20, 2026 at 10:47 AM_

Implemented via PR #1212, shipped in 1.4.0 via unfreeze PR #1215.

