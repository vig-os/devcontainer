---
type: issue
state: closed
created: 2026-07-06T07:15:48Z
updated: 2026-07-06T14:02:44Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/863
comments: 0
labels: bug, priority:blocking, area:ci, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:34.508Z
---

# [Issue 863]: [fix(ci): Renovate changelog automation self-triggers an empty-commit loop and skips the workspace mirror](https://github.com/vig-os/devkit/issues/863)

## Summary

The Renovate changelog automation (`renovate-changelog-build.yml` → `renovate-changelog-commit.yml`) has two independent defects, surfaced on #862.

## Defect 1 — self-triggering empty-commit loop

`renovate-changelog-commit.yml` pushes the changelog commit with a **GitHub App token** (which re-triggers workflows). The build's `if` gates only on the PR **author** (`renovate[bot]`, permanent) and never the **pusher**, and `vig-os/commit-action` has no empty-diff guard, so it creates same-tree no-op commits. Result: the bot's own push fires a fresh `synchronize` → build → commit → … On #862 this produced **150+ identical empty commits** before it was stopped by manually disabling the build workflow.

The Python idempotency guard in `renovate_changelog_pr.py` works correctly ("already contains entry"), but overlapping stale-checkout builds still emit `modified=true` and commit.

## Defect 2 — workspace mirror left out of sync (red CI)

The bot commits only root `CHANGELOG.md`, but `scripts/manifest.toml` mandates a verbatim mirror at `assets/workspace/.devcontainer/CHANGELOG.md`. The automation never regenerates it, so the `sync-manifest` pre-commit gate fails and the PR can never go green — independent of the loop.

## Fix (targeting `release/0.4.0`)

1. **Break the loop:** add a pusher guard `github.event.sender.login != 'commit-action-bot[bot]'` to both jobs' `if` in `renovate-changelog-build.yml`.
2. **Keep the mirror in sync:** the build copies root `CHANGELOG.md` → the verbatim mirror and includes both in the artifact; `renovate-changelog-commit.yml` commits `FILE_PATHS: CHANGELOG.md,assets/workspace/.devcontainer/CHANGELOG.md` (precedent: `prepare-release.yml`).

## Operational note

`renovate-changelog-build.yml` is currently **disabled manually** to stop the loop. Re-enable after the fix reaches `dev` (via `sync-main-to-dev`), then use #862 to validate end-to-end.

## Out of scope (follow-up)

Cosmetic: entries append at the bottom of `### Changed`, landing under `#### Modules` sub-headings. Separate output-formatting fix in `renovate_changelog_pr.py`.
