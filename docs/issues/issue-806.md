---
type: issue
state: closed
created: 2026-07-03T11:46:55Z
updated: 2026-07-03T12:52:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/806
comments: 2
labels: chore, area:workspace
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:43.881Z
---

# [Issue 806]: [[CHORE] Audit scaffold justfile recipes for compose-era leftovers post-#799/#795](https://github.com/vig-os/devkit/issues/806)

## Context

While implementing #795 (which renamed the scaffolded devcontainer verbs to `devc-*`), a broader reevaluation of the scaffold justfiles was deferred here to keep #795's diff minimal.

## Scope

Audit `assets/workspace/justfile`, `.devcontainer/justfile.devc`, `.devcontainer/justfile.gh`, `.devcontainer/justfile.worktree`, and `justfile.project` for:

- Compose-era assumptions that #799 (sidecar/multi-container removal) may have stranded — e.g. whether the `docker-compose.project.yaml` (`services: {}`) / `docker-compose.local.yaml` layering in every `devc-*` recipe still earns its keep for a single devcontainer service
- `justfile.worktree` ships in `.devcontainer/` but is not imported by the scaffold root justfile — confirm intentional and document, or wire an `import?`
- Recipe naming consistency after the `devc-*` namespacing (#795): are `check`/`devcontainer-upgrade` in the right groups/names?
- Stale/duplicated doc references to renamed or removed recipes

## Non-goals

- No behavior changes to the services opt-in shipped in #795

Refs #799, #795
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 12:09 PM_

Deferred to the devkit rename cycle (post-0.4.0): the 0.4.0 release scope is frozen to the Nix cutover (#639), and this audit touches the same scaffold files the rename (#781) will sweep — doing both in one pass avoids two consumer-visible scaffold churns.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 3, 2026 at 12:52 PM_

Closed in #809 

