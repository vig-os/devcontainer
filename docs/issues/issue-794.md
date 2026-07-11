---
type: issue
state: closed
created: 2026-07-01T08:24:20Z
updated: 2026-07-01T11:20:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/794
comments: 1
labels: docs, area:workflow, effort:medium
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:45.732Z
---

# [Issue 794]: [docs(rfc): record org nix dev-environment strategy (activation / shell-definition / local-services)](https://github.com/vig-os/devkit/issues/794)

**Source:** [exo-fleet#76](https://github.com/exo-pet/exo-fleet/issues/76) comment thread (devenv→mkShell port) + a request to record the org-wide strategy. **Deferred/sequenced** as a docs ADR, sibling to #775 (uv2nix) and #787 (secrets).

## Context

exo-fleet #76 ports its devShell off `cachix/devenv` to plain `pkgs.mkShell` to kill a ~165s cold-eval IFD tax. A comment there broadens the question to compare **devenv / devshell / mkshell / direnv**. That phrasing is a *category error* — it conflates three separable axes:

1. **Activation** — `nix-direnv` (auto on `cd`, GC-rooted) vs manual `nix develop`. Complementary, not exclusive.
2. **Shell definition** — `pkgs.mkShell` vs `numtide/devshell` vs `cachix/devenv`. Mutually exclusive per repo.
3. **Local services / processes** — `devenv up`-style MinIO/Postgres orchestration, which devenv *bundles into* axis 2 (the source of the confusion).

This repo has **already largely decided** axes 1–2: `install.sh --mode devcontainer|direnv|both` already ships the dual-mode delivery; `mkProjectShell` (`flake.nix:159-263`) is plain `pkgs.mkShell`; the image is built from the same `devTools` SSoT with a parity test (`devShellTools`, `flake.nix:400/450`) that `devshell`/`devenv` would interpose on. Issue #27 ("Adopt Nix/devenv") is already **Superseded** by the flake-SSoT epic (#625/#631/#637). The hooks axis is mid-convergence: this repo → `git-hooks.nix` + `prek` (#778/#791), exo-fleet #76 → `git-hooks.nix` too.

## Goal

Produce `docs/rfcs/ADR-nix-devenv-strategy.md` that (a) names the three axes and *why the four-way question is a category error*, (b) ratifies `pkgs.mkShell` (via `mkProjectShell`) + `nix-direnv` on axes 1–2 with the parity-SSoT + IFD reasoning, and (c) adopts `process-compose` + `services-flake` as the org default for axis 3 (local services), with a shared-helper implementation tracked as a follow-up.

## Scope & non-goals

- **Non-goal:** build the shared `mkProjectServices` helper here — separate follow-up feature issue.
- **Non-goal:** mandate anything on exo-pet/exoma repos. This ADR is *authoritative for vig-os* and a *recommendation* to siblings.
- **Non-goal:** re-run the exo-fleet timing as a spike — cite #76's measured numbers.

## Deliverables

- `docs/rfcs/ADR-nix-devenv-strategy.md` in the house style of `docs/rfcs/ADR-uv2nix-pyproject-nix.md`.
- A cross-link paragraph in `docs/NIX.md`.
- A follow-up feature issue for the `mkProjectServices` helper, linked from the ADR.

## Acceptance criteria

- [ ] ADR merged in house frontmatter/section style, with bold **Decision (TL;DR)** + **Reconsider if**.
- [ ] Three-axis framing explicit; names direnv as *activation*; states the definition axis is settled (de-facto + de-jure #27 + parity-SSoT).
- [ ] Both decision matrices present (shell-definition; local-services).
- [ ] Local-services axis adopts `process-compose` + `services-flake` with a concrete `nix run .#services` example + a follow-up issue link for `mkProjectServices`.
- [ ] exo-fleet #76 port timing (cold ~165s vs warm ~5s) cited.
- [ ] Blast radius stated (vig-os authoritative; exo-pet/exoma recommended).
- [ ] Hooks convergence recorded (#778/#791 prek/git-hooks.nix ↔ exo-fleet #76).

Refs #76

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

Resolved on `dev` by PR #796 (`docs: record org nix dev-environment strategy ADR`). The activation / shell-definition / local-services strategy is recorded as an ADR.

