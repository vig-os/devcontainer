---
type: issue
state: closed
created: 2026-07-17T20:27:10Z
updated: 2026-07-20T10:47:14Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1208
comments: 1
labels: feature, priority:medium, area:ci, area:workspace, effort:medium
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:05.233Z
---

# [Issue 1208]: [workflow-model: scaffold render core (render_workflow_model + sync-main-to-dev exclude + preview mirror)](https://github.com/vig-os/devkit/issues/1208)

Part of #1205. Depends on #1205 sub-1 (manifest key).

- **Copy-exclude** `sync-main-to-dev.yml` in trunk (`EXCLUDE_ARGS` after mode excludes ~:1148-1153) + post-copy prune for gitflow→trunk upgrade (~:1259, modeled on the container-docs prune).
- **`render_workflow_model()`** (sibling to `render_codeql_matrix()` ~:857), run in trunk, anchored `dev→main` edits: `prepare-release.yml` (`ref: dev`, `heads/dev`, step names — anchored so `development`/`devkit`/`devcontainer` untouched); `ci.yml` (drop `- dev` from `on:` filter, `TRUNK="dev"`→`main`); `codeql.yml` (drop `- dev`); `sync-issues.yml` (default + fallbacks dev→main); scaffolded `branch-naming/SKILL.md` (base default); scaffolded `.pre-commit-config.yaml` (drop `(?!dev$)`).
- **`--force` preview mirror** (:917-990): skip `sync-main-to-dev.yml` in copy report, list under DELETIONS on gitflow→trunk, note the rendered files — keep `--preview` truthful.

Compose as separate sequential if/case blocks (mode × model orthogonal, never combined case).

Refs: #1205
---

# [Comment #1]() by [c-vigo]()

_Posted on July 20, 2026 at 10:47 AM_

Implemented via PR #1212, shipped in 1.4.0 via unfreeze PR #1215.

