---
type: issue
state: closed
created: 2026-07-06T16:24:32Z
updated: 2026-07-08T07:54:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/877
comments: 2
labels: bug, priority:high, area:workspace, effort:medium, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:32.561Z
---

# [Issue 877]: [fix(workspace): scaffold upgrade strands base recipes — justfile.project is preserved but now owns sync/precommit/test, breaking the shipped ci.yml](https://github.com/vig-os/devkit/issues/877)

### Description

Found during 0.4.0 consumer field-validation (EXOMA/hyrr `feature/519-devcontainer-rc4-validation`, EXOMA/talys `feature/552-devcontainer-rc4-validation`).

The 0.4.0 scaffold retired `.devcontainer/justfile.base` and relocated the base recipes (`lint`, `format`, `precommit`, `test`, `test-cov`, `sync`, `update`) into `justfile.project`. But `justfile.project` is **preserved on upgrade** by design — so any repo upgrading from the 0.3.x scaffold keeps its old `justfile.project` and never receives the relocated recipes, while the **shipped `ci.yml` template calls `just sync` / `just precommit` / `just test`**. Result: in-container CI fails with `error: justfile does not contain recipe 'sync'` (hyrr PR vig-os side: see EXOMA/hyrr#520 run 28743681271). Fresh scaffolds are unaffected (smoke-test passes) — only the upgrade path breaks.

Two aggravations observed:
- The stale `.devcontainer/justfile.base` file is left behind on upgraded repos (nothing imports it — dead weight and confusion).
- In talys the root `justfile` ended up with **no scaffold import block at all** (no `import? '.devcontainer/justfile.devc'` etc.), so even the fresh-template `justfile.project` recipes were unreachable. Worth checking whether the installer merges/preserves a customized root justfile correctly.

### Possible Solution

Options (pick per SSoT design): (a) move CI-required recipes into a *managed* justfile (`justfile.devc` or a new managed file) instead of the preserved `justfile.project`; (b) make the upgrade path append missing base recipes to an existing `justfile.project` (or fail loudly listing them); (c) at minimum, a MIGRATION.md step + upgrade-time warning.

Related observation (may deserve its own issue): the template `sync` recipe changed semantics from plain `uv sync` to `uv sync --all-extras --all-groups`, which breaks repos that quarantine platform-limited deps in optional extras (hyrr's `geometry` extra ships cp312/313-only wheels).

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 09:46 AM_

Fix up in #891. Design decision: **option (b) — upgrade-time repair**. `init-workspace --force` probes each CI-contract recipe (`lint format precommit test test-cov sync update`) with `just --show` and appends only the missing ones to the preserved `justfile.project`, sourced verbatim from the template (SSoT) under a marked review-me banner — customized recipes always win and re-runs are no-ops.

Option (a) (managed justfile) was rejected: `justfile.devc` doesn't exist in `direnv`-mode workspaces, and any managed root-level file would duplicate-recipe-clash with fresh 0.4.0 scaffolds and already-migrated consumers, reversing the deliberate 0.4.0 team-owns-these-recipes design. Option (c) alone leaves upgraded CI red until a human intervenes; its MIGRATION.md step and warning are included anyway.

Also in #891: the stale `.devcontainer/justfile.base` is removed on upgrade (only where the scaffold manages `.devcontainer/`, never in `direnv` mode per #738), and the installer now warns when the root `justfile` lacks the scaffold `import?` block (the talys case).

The `uv sync --all-extras --all-groups` semantics observation is untouched and likely deserves its own issue.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

