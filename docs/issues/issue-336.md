---
type: issue
state: closed
created: 2026-03-17T10:43:38Z
updated: 2026-03-17T12:37:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/336
comments: 0
labels: chore, priority:high, area:ci, area:workflow, effort:medium
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:23.371Z
---

# [Issue 336]: [[CHORE] Harden release orchestration semantics for 0.3.1](https://github.com/vig-os/devcontainer/issues/336)

### Chore Type
CI / Build change

### Description
Align the release workflow behavior with the intended cross-repo contract for 0.3.1: candidate dispatch is fire-and-forget, final checks downstream RC status deterministically, and final release publication is resilient to partial failures.

### Acceptance Criteria
- [ ] `publish-candidate` dispatches to smoke-test without waiting for downstream completion (no 30-min poll loop).
- [ ] Rollback is decoupled from smoke-test downstream completion status (dispatch failure handling only, no downstream timeout rollback).
- [ ] Final-gate downstream RC pre-release check includes bounded retries for transient GitHub API failures.
- [ ] Final GitHub Release creation happens at the end of `publish` (after GHCR push/signing/SBOM/attestation), so a release-create failure can be retried manually without rerunning artifact publishing.
- [ ] Smoke-test dispatch workflow uses explicit concurrency control to prevent branch/PR/release races for overlapping dispatches.

### Implementation Notes
- Target workflow: `.github/workflows/release.yml`
- Target workflow: `assets/smoke-test/.github/workflows/repository-dispatch.yml`
- Keep existing contract semantics:
  - candidate: dispatch only, user verifies downstream pre-release manually
  - final: validate latest RC downstream pre-release before publishing final
- After moving release creation to end, retain `--verify-tag` for final release creation.

### Related Issues
Related to #310, #331, #330

### Priority
High

### Changelog Category
Changed

### Additional Context
This issue consolidates the five release-audit points needed before publishing 0.3.1 and testing the improved deployment + downstream release path in the smoke-test repository.
