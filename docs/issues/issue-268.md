---
type: issue
state: closed
created: 2026-03-12T11:26:59Z
updated: 2026-03-12T11:48:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/268
comments: 0
labels: chore, priority:blocking, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-12T12:05:20.530Z
---

# [Issue 268]: [[CHORE] Split prepare-release auth: COMMIT_APP for refs/commits, RELEASE_APP for PR operations](https://github.com/vig-os/devcontainer/issues/268)

### Chore Type
CI / Build change

### Description
`prepare-release.yml` currently uses a single `RELEASE_APP` token for both git/ref writes and PR operations in the `prepare` job.

This fails on protected `dev` branch rules when attempting to commit `CHANGELOG.md` directly:
- Repository rule violations found
- Changes must be made through a pull request
- Required status check \"Test Summary\" is expected

Workflow run reference: https://github.com/vig-os/devcontainer/actions/runs/22999412063

### Acceptance Criteria
- [ ] `prepare-release.yml` generates **two** app tokens in the `prepare` job:
  - `COMMIT_APP_*` token for git/ref operations (`commit-action`, ref create/update/delete)
  - `RELEASE_APP_*` token for PR/label/comment operations
- [ ] Steps that write to `refs/heads/dev` and release branch refs use `COMMIT_APP` token
- [ ] PR creation and PR metadata operations use `RELEASE_APP` token
- [ ] Workflow succeeds without branch-protection/repository-rule violation in release preparation path

### Implementation Notes
- Mirror the auth split already documented/used in `.github/workflows/sync-main-to-dev.yml`:
  - COMMIT app = least-privilege git/ref identity
  - RELEASE app = pull-request scoped operations
- Primary target: `.github/workflows/prepare-release.yml`

### Related Issues
None identified.

### Priority
Critical

### Changelog Category
No changelog needed

### Additional Context
Failure excerpt from run:
- \"Repository rule violations found\"
- \"Changes must be made through a pull request\"
- `Prepare Release Branch` failed while committing prepared `CHANGELOG.md` to `dev`.
