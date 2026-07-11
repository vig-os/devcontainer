---
type: issue
state: closed
created: 2026-03-11T07:37:14Z
updated: 2026-06-30T07:42:06Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/255
comments: 2
labels: docs, priority:low, effort:small, area:docs
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:22.189Z
---

# [Issue 255]: [[DOCS] Consolidated docs/NIX.md (flake architecture + onboarding)](https://github.com/vig-os/devkit/issues/255)

### Description

> **Re-scoped (2026-06-24).** The original ask — document the Nix flake / direnv
> in `CONTRIBUTE.md` — was largely delivered by #633 (the nix-direnv onboarding
> section). What remains is the *consolidated reference*: today the flake design
> rationale lives only as inline comments in `flake.nix` plus `docs/NIX2CONTAINER.md`,
> with no single onboarding/architecture doc. This issue now tracks adding
> `docs/NIX.md`.

Add `docs/NIX.md` as the single reference for the repo's Nix setup, covering:

- The flake as toolchain SSoT (`devTools`) and how dev-shell ↔ image parity is
  guarded (`tests/test_flake_devshell.py`).
- The stable/unstable channel split and the fast-mover overlay (`uv`, `gh`,
  `claude-code`).
- The Nix-built image (`dockerTools.buildLayeredImage`), bit-reproducibility, and
  multi-arch.
- The evaluator decision (CppNix vs Lix) and `pre-commit` vs `prek`.
- Cachix (`vig-os`) substituter usage and `direnv allow` onboarding.
- Where the publish-cutover lives (#639) and how `nixpkgs` bumps flow (Renovate
  `nix` manager).

### Documentation Type

Add new documentation

### Target Files

- `docs/NIX.md` (new — authored directly; not a generated file)
- Optional: a one-line pointer from `README` / `CONTRIBUTE` templates in
  `docs/templates/` if appropriate (regenerate with `just docs`)

### Acceptance Criteria

- [ ] `docs/NIX.md` exists and covers the topics above
- [ ] Any pointer added from a generated doc goes through `docs/templates/` and
      `just docs` is diff-clean
- [ ] Content is accurate against the current `flake.nix`

### Changelog Category

Added

### Additional Context

Part of the Nix migration epic #625. Supersedes the original CONTRIBUTE.md-only
scope (done in #633).

---

# [Comment #1]() by [c-vigo]()

_Posted on June 23, 2026 at 06:56 AM_

Superseded by #633 (part of #625), which switches `.envrc` to nix-direnv and documents the clone → `direnv allow` flow + the Cachix substituter in `docs/templates/CONTRIBUTE.md.j2`, plus enabling the `nix-command`/`flakes` experimental features. Will close when #633 lands.

---

# [Comment #2]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #681 (40f78e6) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

