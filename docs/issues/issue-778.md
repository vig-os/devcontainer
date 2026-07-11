---
type: issue
state: closed
created: 2026-06-30T12:52:08Z
updated: 2026-07-03T11:22:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/778
comments: 1
labels: chore, priority:medium, area:workflow, effort:medium
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:48.481Z
---

# [Issue 778]: [[CHORE] Adopt git-hooks.nix with package = pkgs.prek (supersedes #40)](https://github.com/vig-os/devkit/issues/778)

**Source:** PR #670 roadmap, thread B — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). **Supersedes #40.** Deferred (own PR + CI shakeout).

Adopt **git-hooks.nix with `package = pkgs.prek`**: generate `.pre-commit-config.yaml` from Nix (no drift from `devTools`), drop the Python `pre-commit` from `imageTools` (one fewer manylinux/FHS consumer), and expose `checks.pre-commit` so hooks run under `nix flake check`. ⚠️ prek's YAML parser is stricter than pre-commit's and may reject tolerated hooks — needs a CI shakeout. Closes the discussion in #40. Refs #40, #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 11:22 AM_

Closed in #791 

