---
type: issue
state: open
created: 2026-06-16T07:21:54Z
updated: 2026-06-16T07:21:54Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/590
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-16T07:35:08.317Z
---

# [Issue 590]: [[BUG] sync-main-to-dev merge can drop the fresh `## Unreleased` scaffold](https://github.com/vig-os/devcontainer/issues/590)

## Description

The `sync-main-to-dev` release-cycle pattern relies on the `main → dev` merge **preserving** the empty `## Unreleased` scaffold that `prepare-release` leaves on `dev`. The workflow encodes this assumption explicitly:

> ```
> # With the new CHANGELOG flow, dev already has ## Unreleased (created during
> # prepare-release), so no CHANGELOG reset is needed here.
> ```
> — [`.github/workflows/sync-main-to-dev.yml`](https://github.com/vig-os/devcontainer/blob/main/.github/workflows/sync-main-to-dev.yml)

That assumption is fragile. After a release, `main`'s CHANGELOG has the dated `## [X.Y.Z]` section and **no** `## Unreleased`, while `dev` has both `## Unreleased` (empty) and `## [X.Y.Z] - TBD`. Both sides inserted overlapping text immediately under the changelog header, so the 3-way merge can resolve **cleanly** by taking `main`'s region — silently dropping `## Unreleased` from `dev`. No conflict is raised, so the auto-merge goes green and the loss is invisible until someone opens the next structure PR with nowhere to add an entry.

This is not hypothetical: the **part-registry** repo, which adopts this same release-cycle/sync pattern, loses `## Unreleased` on `dev` **every release** and has needed a manual restore chore PR each time:
- 0.2.3 → `vig-os/part-registry#30` (`chore(repo): restore Unreleased section after 0.2.3 sync`)
- 0.2.4 → `vig-os/part-registry#35` (same)

Filing here because the release-cycle + changelog tooling (`prepare-changelog`, the shared workflow shape) is the SSoT in this repo and part-registry's is a documented adaptation of it — the fix belongs in the canonical pattern so adopters inherit it.

## Steps to Reproduce

1. On `dev`, run `prepare-release` for `X.Y.Z` (freezes `## Unreleased` → `## [X.Y.Z] - TBD`, leaves a fresh empty `## Unreleased`).
2. Finalize the release; merge `release/X.Y.Z → main` (main now has dated `## [X.Y.Z]`, no `## Unreleased`).
3. Let `sync-main-to-dev` open and merge the `main → dev` PR.
4. Inspect `dev`'s `CHANGELOG.md`.

## Expected Behavior

After the sync, `dev`'s `CHANGELOG.md` retains a fresh empty `## Unreleased` section above the dated `## [X.Y.Z]`, ready for ongoing work — with no manual intervention.

## Actual Behavior

In part-registry the merge resolves cleanly but drops `## Unreleased`; `dev`'s changelog jumps straight from the header to `## [X.Y.Z]`. A manual chore PR is required each release to re-add the scaffold. devcontainer's own `dev` happens to still carry `## Unreleased` today (post-release entries were added since), so the latent fragility is masked here but lives in the shared pattern.

## Proposed Fix

Make the canonical `sync-main-to-dev` defensively **guarantee** the scaffold rather than assume the merge preserves it — e.g. after creating the sync branch / before opening the PR, ensure a `## Unreleased` block exists immediately under the header (idempotent: insert only if absent), or have `prepare-release`/the sync step own the invariant explicitly. Reuse the shared `prepare-changelog` tooling so the behavior is single-sourced.

## Environment / Context

- Repos: `vig-os/devcontainer` (canonical pattern), `vig-os/part-registry` (adopter, where the bug is observed)
- Workflow: `.github/workflows/sync-main-to-dev.yml`
- Changelog tool: `prepare-changelog` (run from `ghcr.io/vig-os/devcontainer`)
