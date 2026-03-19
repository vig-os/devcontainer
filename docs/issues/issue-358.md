---
type: issue
state: open
created: 2026-03-18T13:49:55Z
updated: 2026-03-18T21:59:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/358
comments: 0
labels: feature, area:ci, effort:large, semver:minor
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-19T04:27:46.207Z
---

# [Issue 358]: [[FEATURE] Redesign smoke-test dispatch to exercise the full downstream release cycle](https://github.com/vig-os/devcontainer/issues/358)

### Description

Redesign `assets/smoke-test/.github/workflows/repository-dispatch.yml` so that each upstream dispatch exercises the downstream repo's complete release cycle: deploy to dev, prepare-release, and release -- with automated PR approval, CI gating, and upstream failure reporting.

The current implementation creates a deploy PR to dev (with auto-merge) and then immediately creates a GitHub Release before the deploy PR is even merged, bypassing the downstream's `prepare-release.yml` and `release.yml` workflows entirely. The release artifact is premature and structurally unsound as a gate for the upstream final release.

### Problem Statement

1. **Premature release:** The `publish-release` job creates a GitHub Release before the deploy PR merges. CI on the deploy PR has not yet validated the new devcontainer version.
2. **Downstream release cycle not exercised:** The smoke-test repo has fully-featured `prepare-release.yml` and `release.yml` workflows, but the dispatch bypasses both. The downstream release pipeline is never validated.
3. **Hollow upstream gate:** The upstream `release.yml` checks for a downstream pre-release for the latest RC tag. The current `publish-release` satisfies this gate, but the release it checks against was created before the deploy was validated by CI.
4. **No failure reporting to upstream:** When the dispatch fails, there is no notification to the upstream repo. Failures go unnoticed unless someone manually checks the downstream.
5. **No wait-for-merge:** The workflow enables auto-merge on the deploy PR and immediately proceeds, without confirming the PR actually merged.

### Proposed Solution

Redesign the workflow into three phases:

**Phase 1 -- Deploy (modified)**
- `validate`: add `base_version` output (strip `-rcN` suffix from tag).
- `deploy`: after the installer runs, generate a fresh `CHANGELOG.md` with a single Unreleased entry (avoids double-freeze problems on re-dispatches). Keep branch creation, signed commit, PR, and auto-merge.
- `wait-deploy-merge` (new): poll the deploy PR until it merges (30 min timeout).

**Phase 2 -- Release orchestration (replaces `publish-release`)**
- `cleanup-release` (new): if `release/<base_version>` branch exists from a previous dispatch, close its PR and delete the branch. Ensures `prepare-release` can always run cleanly.
- `trigger-prepare-release` (new): `gh workflow run prepare-release.yml -f version=<base_version>`, poll until completion (20 min timeout).
- `ready-release-pr` (new): find the draft PR created by prepare-release, mark it ready, auto-approve with the Release App token, wait for CI (30 min timeout).
- `trigger-release` (new): `gh workflow run release.yml -f version=<base_version> -f release-kind=<kind>`, poll until completion (30 min timeout).

**Phase 3 -- Failure reporting (new)**
- `notify-failure`: on any job failure, create an issue on the upstream repo (`vig-os/devcontainer`) with dispatch metadata, which phase failed, artifacts created (PRs, branches, tags), and manual cleanup instructions. No automated rollback -- artifacts stay in place for debugging. Subsequent dispatches use a new RC version and start fresh.

**Removed:** the `publish-release` job is deleted entirely.

### Alternatives Considered

- **Keep `publish-release` and just add wait-for-merge:** Would fix the premature-release issue but still bypass the downstream release cycle. The smoke-test pipeline would remain untested.
- **Split into multiple event-driven workflows:** Would avoid long-running polling jobs but requires more complex inter-workflow state management and event routing. A single workflow with polling is simpler and keeps full observability in one run.
- **Automated rollback on failure:** Rejected in favor of leaving artifacts for debugging. The next dispatch uses a new RC version anyway, so leftover artifacts don't block progress.

### Additional Context

- Related: #354 (intermittent deploy failure -- separate bug, but may interact with the retry/polling logic)
- The pipeline is exercised on every upstream RC and final release dispatch
- Phase 2 jobs run on bare `ubuntu-22.04` (no devcontainer needed -- they only make API calls and poll); the triggered workflows resolve their own image from `.vig-os`

### Impact

- **Who benefits:** Release reliability -- every RC validates the full downstream cycle before the upstream gates on it.
- **Breaking change:** No. This changes an internal CI workflow template; no user-facing API or contract changes.

### Acceptance Criteria

- [ ] Deploy PR is confirmed merged before any release orchestration begins
- [ ] `prepare-release.yml` and `release.yml` are triggered and polled to completion
- [ ] Release PR is auto-approved and CI-gated before release
- [ ] On any failure, an issue is created on the upstream repo with full context
- [ ] The `publish-release` job is removed
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Changed
