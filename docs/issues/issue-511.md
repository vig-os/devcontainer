---
type: issue
state: closed
created: 2026-04-10T06:32:05Z
updated: 2026-04-10T13:19:49Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/511
comments: 0
labels: feature, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-10T13:54:27.274Z
---

# [Issue 511]: [[FEATURE] Smoke-test dispatch: trigger promote-release for final; wait on CI for RC](https://github.com/vig-os/devcontainer/issues/511)

## Description

Update the smoke-test `repository-dispatch` workflow so **final** releases dispatch downstream `promote-release.yml` (publish release, merge PR, cleanup RC tags) instead of only merging the release PR; and so **RC** triggers verify release-PR CI but **do not** merge to `main`.

## Problem statement

- Issue #507 / PR #510 fixed draft-release handling in `promote-release.yml`.
- Today `assets/smoke-test/.github/workflows/repository-dispatch.yml` runs `merge-release-pr` for **both** RC and final: it enables auto-merge and polls.
- Downstream `release.yml` creates a **draft** final release; nobody publishes it, so the release stays draft.
- Upstream `.github/workflows/promote-release.yml` requires a **published** (non-draft, non-prerelease) downstream final release before it proceeds — so automation fails unless someone publishes manually.
- For RC, merging the release PR to `main` on every candidate is unnecessary; the branch is recreated on the next dispatch.

## Proposed solution

Behavior split by `release_kind`:

**Common path (RC + final):** existing steps through `trigger-release` unchanged in intent; then replace terminal merge behavior as below.

1. **Remove** the `merge-release-pr` job.
2. **Add** `wait-release-pr-ci` (RC + final): after `trigger-release`, poll required checks on the release PR (`gh pr checks`); succeed when green; fail on failure or timeout (e.g. 30 min). For RC this is terminal — PR stays open.
3. **Add** `trigger-promote-release` (**final only**): `if: needs.validate.outputs.release_kind == 'final'`; repository-dispatch `promote-release.yml` on `dev` with `version=$BASE_VERSION`; same dispatch-and-poll pattern as `trigger-release` / `trigger-prepare-release`. Downstream `promote-release` validates draft + PR, publishes release, merges PR, cleans RC tags.
4. **Update** `summary` and `notify-failure`: depend on `wait-release-pr-ci` and `trigger-promote-release`; treat skipped `trigger-promote-release` on RC as success, not failure.

**Docs:** Update `docs/CROSS_REPO_RELEASE_GATE.md` — receiver triggers `promote-release` for final; RC path no longer merges.

**Scope:** `assets/smoke-test/.github/workflows/repository-dispatch.yml` + `docs/CROSS_REPO_RELEASE_GATE.md`. Do **not** change upstream or workspace-template `promote-release.yml` in this issue.

## Alternatives considered

- Duplicate publish/merge/cleanup logic in `repository-dispatch.yml` — rejected (DRY; dogfood `promote-release` template).

## Additional context

- Workspace template already ships `assets/workspace/.github/workflows/promote-release.yml` via `init-workspace.sh`.
- **Prerequisite:** PR #510 merged and deployed to the smoke-test repo before exercising this change end-to-end.
- Related: #507 (draft release API), #510 (fix).

## Impact

- Unblocks upstream `promote-release` by publishing the downstream final release automatically.
- RC flow stops merging prematurely; aligns with cross-repo gate contract for pre-releases.

**Changelog category:** Changed

- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

