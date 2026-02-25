---
type: issue
state: open
created: 2026-02-24T10:13:58Z
updated: 2026-02-24T10:13:58Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/173
comments: 0
labels: feature, area:ci, effort:medium, semver:minor
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-25T04:25:54.739Z
---

# [Issue 173]: [[FEATURE] Wire cross-repo dispatch and release gate for smoke testing](https://github.com/vig-os/devcontainer/issues/173)

### Description

Connect the RC publishing workflow to the smoke-test repo via `repository_dispatch`, so that publishing an RC image automatically triggers smoke testing. Document the manual release gate process where the operator checks smoke results before triggering the final release.

### Problem Statement

After #170 (smoke-test repo), #171 (container CI), and #172 (RC publishing) are complete, the pieces exist but are not wired together. RC images get published but don't automatically trigger smoke tests, and there is no documented process for gating the final release on smoke results.

### Proposed Solution

**Devcontainer repo (dispatch trigger):**
- After RC is published to GHCR, send `repository_dispatch` to `vig-os/devcontainer-smoke-test` with the RC tag as payload
- Requires a GitHub token with cross-repo dispatch permission (fine-grained PAT or GitHub App token stored as a repo secret)

**Smoke-test repo (dispatch listener):**
- The stub `repository_dispatch` listener (created in #170) is updated to:
  - Receive the RC tag from the dispatch payload
  - Update the `container:` image tag in `ci-container.yml` (or pass it as an input)
  - Run both `ci.yml` (bare-runner) and `ci-container.yml` (container) against the RC

**Release gate (manual initially):**
- Document the process: after RC publish, operator waits for smoke-test repo CI to pass, then triggers the final release workflow
- Future automation (Phase 2): smoke-test repo dispatches back to devcontainer repo on completion, enabling an automated gate

### Alternatives Considered

See parent issue #169 for full alternatives analysis.

### Additional Context

This is sub-issue 4 of 4 for #169 (Phase 1). This is the integration point that depends on all three prior sub-issues.

Dependencies:
- #170 (smoke-test repo exists)
- #171 (container CI variant exists)
- #172 (RC publishing exists)

Cross-repo dispatch requires a secret with `repo` scope or a GitHub App token. This should be documented and the secret created as part of this issue.

### Impact

- Backward compatible. The final release workflow gains a new pre-step (RC + smoke) but the existing flow remains functional.
- Requires a new repo secret for cross-repo dispatch.

### Changelog Category

Added

### Acceptance Criteria

- [ ] RC publish automatically triggers the smoke-test repo via `repository_dispatch`
- [ ] Smoke-test repo runs both CI variants against the RC image tag
- [ ] Manual release gate process is documented (where and how to check smoke results)
- [ ] Cross-repo dispatch secret is created and documented
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
