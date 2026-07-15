---
type: issue
state: closed
created: 2026-07-15T06:36:43Z
updated: 2026-07-15T08:29:50Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1093
comments: 1
labels: bug, priority:high
assignees: none
milestone: none
projects: none
parent: 1096
children: none
synced: 2026-07-15T11:04:54.094Z
---

# [Issue 1093]: [[BUG] Bumping DEVKIT_VERSION without the matching vigos flake pin ships the #1053 JSONC banner without its check-json exclude — every commit fails, no warning](https://github.com/vig-os/devkit/issues/1093)

## Summary

Bumping `DEVKIT_VERSION` (the **scaffold image**, via `install.sh --force`) without bumping the pinned **`vigos` flake input** in `flake.nix` silently breaks **every commit** for a direnv-mode consumer, and nothing warns that the two must move together.

Surfaced upgrading the `commit-action` pilot 1.1.0 → 1.2.0.

## Mechanism

The two halves of the #1053 JSONC-banner change ship from **different places**:

- The **provenance banner** on `.vscode/settings.json` / `.devcontainer/devcontainer.json` / `workspace.code-workspace.example` is written by the **scaffold** (`init-workspace.sh`, keyed to `DEVKIT_VERSION`).
- The compensating **`check-json` exclude** for exactly those JSONC files lives in **`nix/hooks.nix`**, delivered through the **`vigos` flake input**.

A consumer that pins the flake input (`vigos.url = "github:vig-os/devkit?ref=1.1.0"`) and bumps only the scaffold gets the **banner without the exclude**: the strict `check-json` hook then rejects `//`-commented JSONC and **every `pre-commit`/commit fails** (`.vscode/settings.json: Failed to json decode`).

## Impact

- Silent and total for direnv/flake consumers: not one file, *every* commit, until the flake input is bumped to match.
- No signal ties the failure to the version skew; the scaffold upgrade reports success and leaves the tree red.
- Affects any consumer that pins the flake input rather than floating it — which `flake.nix`'s own comments recommend once you depend on module-option stability.

## Suggested fix (one or more)

- In `install.sh --force`, **detect and warn** when the pinned `vigos` flake input in `flake.nix`/`flake.lock` does not match the target `DEVKIT_VERSION`, and print the `nix flake update vigos` follow-up (or offer to run it).
- Or have the upgrade **bump the pinned flake `ref`** to the target version as part of the scaffold (it is a managed concern that must stay in lockstep with the image).
- Document the lockstep invariant where the version pin is set.

## Interim workaround (applied in commit-action)

Bumped `vigos.url` to `?ref=1.2.0` and ran `nix flake update vigos`; regenerating the hooks then brought the `check-json` exclude in and the suite green.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 08:29 AM_

Fixed by #1101 (merged to `dev`, commit `04016b0e`; ships in the next release). Shipped: `install.sh --force` now **warns** when a consumer's pinned `vigos` flake `ref` lags the `DEVKIT_VERSION` being written (non-fatal; silent for a floating input or a matching pin), and `docs/MIGRATION.md` documents the scaffold↔flake lockstep invariant. Warn-only by design — the preserved `flake.nix` is never auto-edited. Part of #1096.

