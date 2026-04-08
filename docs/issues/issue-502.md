---
type: issue
state: closed
created: 2026-04-07T21:58:08Z
updated: 2026-04-07T22:25:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/502
comments: 0
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-08T04:42:42.044Z
---

# [Issue 502]: [[BUG] Rollback after finalize-release failure does not restore TBD in release PR body](https://github.com/vig-os/devcontainer/issues/502)

### Description

When the `release.yml` workflow fails after the `finalize` job has already run the "Refresh release PR body from finalized changelog" step, the `rollback` job resets the release branch to its pre-finalization state but does **not** revert the PR body. This leaves the release PR in an inconsistent state: the branch's `CHANGELOG.md` contains `## [X.Y.Z] - TBD` while the PR body shows the finalized heading with a date and release link.

Observed on PR #486 (`release/0.3.2`):
- Branch `CHANGELOG.md`: `## [0.3.2] - TBD` (correctly rolled back)
- PR body: `# [Release 0.3.2](https://github.com/vig-os/devcontainer/releases/tag/0.3.2) - 2026-04-07` (not rolled back)

### Steps to Reproduce

1. Trigger `just finalize-release X.Y.Z` on a release branch with a draft PR
2. The `finalize` job succeeds far enough that the "Refresh release PR body from finalized changelog" step runs (`gh pr edit --body-file`)
3. A later job (`build-and-test` or `publish`) fails, triggering the `rollback` job
4. Rollback resets the branch to pre-finalization SHA but does not touch the PR body

### Expected Behavior

After rollback, the release PR body should be restored to its pre-finalize state — matching the TBD heading in the branch's `CHANGELOG.md` — so the PR accurately reflects the branch content.

### Actual Behavior

The PR body retains the finalized content (dated heading, release link) while the branch has been rolled back to TBD. This is misleading for anyone reviewing the PR or performing manual follow-up after the failure.

### Environment

- **OS**: GitHub Actions (ubuntu-22.04)
- **Workflow**: `.github/workflows/release.yml` — `rollback` job (line ~1357)
- **PR**: #486 (release/0.3.2)
- **Failed runs**: 24088109667, 24088003035

### Additional Context

The `rollback` job (lines 1357-1493 of `release.yml`) currently performs two actions:
1. Reset the release branch to the pre-finalization SHA via Git Data API revert commit
2. Create a failure issue

It does not call `gh pr edit` to restore the PR body.

The "Refresh release PR body from finalized changelog" step (line 595 of `release.yml`) runs inside the `finalize` job. If finalize completes this step successfully but a subsequent job fails, the PR body has already been mutated.

**Immediate manual remediation required:** PR #486 body must be manually updated to reflect the rolled-back TBD state (replace the finalized heading with the TBD changelog content from the branch).

### Possible Solution

Add a step to the `rollback` job (after branch rollback, before issue creation) that restores the PR body from the rolled-back branch's `CHANGELOG.md`:

1. Fetch `CHANGELOG.md` content from the pre-finalization SHA (or the newly rolled-back branch tip)
2. Extract the release section (which will contain `## [X.Y.Z] - TBD`)
3. Reconstruct the PR body in the original prepare-release format
4. Run `gh pr edit "$PR_NUMBER" --body-file <restored-body>`

The downstream workspace `release.yml` (`assets/workspace/.github/workflows/release.yml`) should be checked for the same gap.

### Changelog Category

Fixed

- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
- [ ] Manually fix PR #486 body to restore TBD state
