---
type: issue
state: closed
created: 2026-06-23T06:54:05Z
updated: 2026-07-01T11:19:07Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/633
comments: 1
labels: feature, area:image, area:workspace
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:13.820Z
---

# [Issue 633]: [T1.3 — direnv onboarding (nix-direnv)](https://github.com/vig-os/devkit/issues/633)

Tracking: #625



## Context

`.envrc` uses bare `use flake`, which re-evaluates on every entry and risks the dev-shell
closure being garbage-collected. `nix-direnv` adds a GC-rooted, cached evaluation so
re-entry is instant — the non-container onboarding fast path.

## Scope

**In:**
- Switch `.envrc` to **nix-direnv** (GC-rooted, cached).
- Document the clone → `direnv allow` flow + the Cachix substituter in `CONTRIBUTE.md`.

**Out:**
- The downstream template stub (#640).

## Tasks

- [ ] Update `.envrc` to use nix-direnv
- [ ] Document onboarding + Cachix substituter in `CONTRIBUTE.md`

## Acceptance criteria

- A clean clone + `direnv allow` yields a working shell in seconds on a warm cache.

## Dependencies

- **Depends-on:** #631.
- **Blocks:** none.

## Files

- `.envrc`
- `CONTRIBUTE.md`

## Test notes

- Manual onboarding check; ensure the documented Cachix substituter avoids a from-source
  build on first `direnv allow`.

## Related issues

- **#255** (Document Nix flake as alternative dev setup) — **superseded by this issue.** Fold
  in its specifics: target `docs/templates/CONTRIBUTE.md.j2` (the source template, not the
  generated `CONTRIBUTE.md`), document enabling the `nix-command` + `flakes` experimental
  features, and regenerate with `just docs`. Close #255 when this lands.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30) (dev-shell/direnv onboarding, commit 4c30fa8b). `.envrc` self-bootstraps a pinned nix-direnv with a `use flake` fallback; onboarding documented in `CONTRIBUTE.md`/`docs/NIX.md`. Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

