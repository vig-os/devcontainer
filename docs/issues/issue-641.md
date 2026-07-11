---
type: issue
state: closed
created: 2026-06-23T06:54:18Z
updated: 2026-07-02T11:41:35Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/641
comments: 1
labels: feature, area:workspace
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:10.827Z
---

# [Issue 641]: [T4.3 — Install/init UX: choose devcontainer / direnv / both](https://github.com/vig-os/devkit/issues/641)

Tracking: #625



## Context

Users `curl`-install/init a repo from this template. They should be able to choose how the
development environment is delivered: a devcontainer, a direnv (flake) setup, or both. Simple
repos want just direnv; orchestrated repos want the container; some want both.

## Scope

**In:**
- Add an interactive (and `--mode=devcontainer|direnv|both` non-interactive) selection to the
  install/init script:
  - **devcontainer** → scaffold `.devcontainer/` (existing template), no flake stub required;
  - **direnv** → scaffold `flake.nix` + `.envrc` (the #640 minimal stub), no `.devcontainer/`;
  - **both** → scaffold all of the above.
- Document the default + prompt copy in `README.md` / `CONTRIBUTE.md`.

**Out:**
- The stub contents themselves (#640).

## Tasks

- [ ] Add interactive mode selection to the install/init script
- [ ] Add a `--mode=devcontainer|direnv|both` non-interactive flag
- [ ] Wire each mode to scaffold exactly the right file set
- [ ] Document default + prompt copy

## Acceptance criteria

- Each mode scaffolds exactly the right files and nothing else.
- The non-interactive flag works in CI.

## Dependencies

- **Depends-on:** #640.
- **Blocks:** none.

## Files

- `assets/init-workspace.sh`
- `scripts/init.sh`
- the `curl` entrypoint
- docs

## Test notes

- Extend `init-workspace.bats` with one case per mode (devcontainer / direnv / both).

## Related issues

- **#66** (improve workspace init: global `just` command, better non-empty error output) —
  same install/init entrypoint; land the mode picker and its UX improvements together.
- **#71** (expand `justfile.base` recipes) — the scaffolded modes should expose a consistent
  recipe set; coordinate so direnv-only repos still get the relevant recipes.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 2, 2026 at 11:41 AM_

Done via PR #663 (landed on `dev` through the #625 epic PR #670). Both `install.sh` and `assets/init-workspace.sh` support `--mode devcontainer|direnv|both` (interactive prompt when unset, default `both`), and each mode prunes to exactly the right file set after scaffold.

