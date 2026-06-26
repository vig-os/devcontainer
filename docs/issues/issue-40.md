---
type: issue
state: open
created: 2026-02-02T08:56:09Z
updated: 2026-06-24T16:19:13Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/40
comments: 4
labels: feature, priority:backlog, area:workflow
assignees: none
milestone: Backlog
projects: none
parent: none
children: none
synced: 2026-06-26T06:18:00.511Z
---

# [Issue 40]: [[DISCUSSION] Migration to prek](https://github.com/vig-os/devcontainer/issues/40)

Should we migrate from `pre-commit` to [`prek`](https://github.com/j178/prek)?
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 03:18 PM_

@c-vigo Should we target this for the 0.4 milestone, or keep it on the backlog for now?

---

# [Comment #2]() by [c-vigo]()

_Posted on February 20, 2026 at 03:49 PM_

@gerchowl backlog

---

# [Comment #3]() by [c-vigo]()

_Posted on June 23, 2026 at 06:56 AM_

Decision point surfaced by #634 (part of #625): the pre-commit cache layer is rebuilt on the Nix image, so `pre-commit` vs `prek` (both packaged in nixpkgs) is the natural choice to make there. Light reference — not superseded.

---

# [Comment #4]() by [c-vigo]()

_Posted on June 24, 2026 at 04:19 PM_

## Context from the NixOS migration (#625)

While fixing the BATS suite on the Nix toolchain (#695) we hit the broader
problem that several pre-commit hooks cannot run on a NixOS host because their
tools ship as generic-linux (manylinux) binaries: `ruff`, `ruff-format`, `typos`
(Rust wheels) and `pymarkdown` (its `pyjson5` C-extension needs `libstdc++`).
That work is now tracked as #697 (binary hooks → flake) and #698 (pymarkdown).

### How `prek` relates

`prek` is a **runner** replacement (a faster, single-binary, Python-bootstrap-free
reimplementation of `pre-commit`, compatible with `.pre-commit-config.yaml`). It
runs the *same* hook repos, so on its own it does **not** fix the NixOS binary
incompatibility — a `ruff`/`typos` manylinux wheel still won't execute under
`prek` on NixOS. The compatibility fix (sourcing hook tools from the flake, #697)
is needed regardless of the runner.

The two tracks are complementary, and there's a natural ordering:

1. **First** make hooks flake-sourced / NixOS-compatible (#697, #698). This turns
   the binary hooks into `language: system` hooks resolved from the dev-shell.
2. **Then** `prek` becomes a clean swap: `prek` is itself a single binary
   (packaged in `nixpkgs`), so it drops the Python bootstrap the current runner
   needs, and it runs `language: system` hooks natively. Adopting `prek` after
   #697/#698 is lower-risk and a bigger win (speed + one fewer Python dependency).

### Suggested next step for this issue

Re-scope from open-ended discussion to: "Evaluate/adopt `prek` as the pre-commit
runner **after** #697/#698 land," with a concrete spike (package `prek` from the
flake, run the suite, compare wall-clock and behaviour). Could be pulled under
#625 if we want it in the migration epic.


