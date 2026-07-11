---
type: issue
state: closed
created: 2026-07-09T11:16:11Z
updated: 2026-07-09T13:23:06Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/953
comments: 1
labels: bug, priority:medium, area:workspace, semver:patch
assignees: none
milestone: 0.5.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:17.577Z
---

# [Issue 953]: [fix(workspace): scaffold copy drops nested README.md/CHANGELOG.md (unanchored preserve excludes)](https://github.com/vig-os/devkit/issues/953)

## Summary

The scaffold **copy step drops devkit-authored nested `README.md`/`CHANGELOG.md` files**, and the `--preview` report disagrees with what the copy actually writes. Found during `0.5.0-rc4` consumer validation (mat: 3 phantom ADDED docs; talys: 2), consistent rc3→rc4.

## Root cause

`assets/init-workspace.sh` `PRESERVE_FILES` (line ~55) lists bare names `README.md` and `CHANGELOG.md` to protect a consumer's **root** docs. Two paths consume it inconsistently:

- **Copy** builds rsync excludes as `--exclude=$preserved` (line ~695) → `--exclude=README.md`. With no leading slash, rsync matches by **basename at every depth**, so it silently drops *all* README/CHANGELOG in the template — including nested devkit docs (`.devcontainer/README.md`, `.devcontainer/CHANGELOG.md`, `.claude/skills/*/README.md`).
- **Preview** classifies via `is_preserved_file` (line ~526), which matches the **exact rel-path**, so a nested `.devcontainer/README.md` isn't "preserved" and — being absent from the consumer — is listed under **ADDED**.

Net: preview promises those files; the copy never writes them (non-idempotent preview + a real content-delivery gap: nested scaffold docs never ship to any consumer).

## Fix

Root-anchor the excludes at line ~695: `--exclude=/$preserved` (leading slash = anchored to the rsync transfer root), so the copy skips only the **exact** preserved paths — matching `is_preserved_file`'s exact-path semantics. Nested docs then ship *and* the preview matches reality. Full-path entries (`justfile.project`, `.github/CODEOWNERS`, …) are unaffected by anchoring.

## Acceptance criteria (TDD)

- Bats coverage in `tests/bats/init-workspace.bats`: a template with a nested `.devcontainer/README.md` **is copied** to the workspace on upgrade, while a consumer's pre-existing **root** `README.md`/`CHANGELOG.md` is still **preserved** (not clobbered).
- `--preview` ADDED set equals what the real `--force` upgrade writes for those docs (no phantom ADDED).

Found during 0.5.0 validation (relates to the #949/#951 preview-report work).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 9, 2026 at 01:23 PM_

Fixed in #956 (merged to `dev`). The scaffold copy now root-anchors the preserve excludes (`--exclude=/$preserved`) so devkit-authored **nested** `README.md`/`CHANGELOG.md` ship, and the `--preview` ADDED report matches what the apply writes. Covered by a new bats test (`tests/bats/init-workspace.bats`). Ships in **0.5.1**. (Auto-close didn't fire because #956 merged into `dev`, not the default branch `main`.)

