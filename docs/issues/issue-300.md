---
type: issue
state: open
created: 2026-03-13T16:02:23Z
updated: 2026-03-13T16:21:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/300
comments: 0
labels: bug, priority:blocking, area:ci, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:54.274Z
---

# [Issue 300]: [[BUG] finalize-release leaves generated docs stale and breaks release-branch CI](https://github.com/vig-os/devcontainer/issues/300)

### Description

Running `just finalize-release 0.3.0` creates a release commit that updates changelog/release metadata, but does not include regenerated docs required by the `generate-docs` pre-commit hook. This causes CI to fail on the release branch/PR.

Additionally, the release PR text can become stale at finalize time because bugfixes may be added on the release branch and the release date is only set during finalization.

### Steps to Reproduce

1. Run `just finalize-release 0.3.0`.
2. Observe the created release commit (e.g. `3656e13`) only includes `CHANGELOG.md`.
3. Let CI run on `release/0.3.0` (PR #270).
4. In `Project Checks`, pre-commit runs `generate-docs` and modifies tracked docs, then exits non-zero.

### Expected Behavior

Release finalization should leave the repository in a CI-clean state; no pre-commit hook should modify files in CI.

Release PR content should be refreshed before merge so it reflects final changelog state (including finalized date and late bugfixes).

### Actual Behavior

`generate-docs` modifies:
- `README.md`
- `CONTRIBUTE.md`
- `TESTING.md`
- `docs/SKILL_PIPELINE.md`

and CI fails with:
`generate-docs (regenerate from templates) ... Failed`
`- files were modified by this hook`

Additionally, in `CHANGELOG.md`, the release date for `0.3.0` is set, but the release link/reference is not updated as expected.

### Environment

- GitHub Actions (`ubuntu-latest`)
- Release branch: `release/0.3.0`
- PR: #270
- Failing run: https://github.com/vig-os/devcontainer/actions/runs/23058119634/job/66977093968?pr=270

### Additional Context

- Related parent work: #242
- Related but distinct issue: #144 (hook trigger scope for skills)
- Non-blocking warnings about cache/tar appear in logs, but root failure is hook-generated file diffs.

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

### PR Text Requirements (clarification)

For the release PR body/content:

- The checklist/instructions currently shown under:
  - `### Testing Checklist`
  - `### When Ready to Release`
  can be posted as a PR comment instead of being part of the persistent PR body text.

- The `### Related` section with release automation issue links should not be included in the release PR body.

### Possible Solution

Update `just finalize-release` flow to regenerate and stage docs before creating the finalize commit, e.g. run docs generation (or `pre-commit run generate-docs --all-files`) and fail fast if the working tree is dirty after release metadata updates.

Also add a finalize-time step (before merge) that refreshes release PR content from the finalized `CHANGELOG.md` so the PR reflects the final release state.

### Changelog Category

Fixed

