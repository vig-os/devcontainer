---
type: issue
state: open
created: 2026-02-24T10:13:58Z
updated: 2026-03-09T17:43:05Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/173
comments: 2
labels: feature, area:ci, effort:medium, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-10T04:14:47.464Z
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
- [x] Smoke-test repo runs both CI variants against the RC image tag
- [ ] Manual release gate process is documented (where and how to check smoke results)
- [ ] Cross-repo dispatch secret is created and documented
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [c-vigo]()

_Posted on March 9, 2026 at 03:50 PM_

## Smoke-Test Listener Side — Complete

The **smoke-test repo (dispatch listener)** scope of this issue is fully implemented and validated. This covers acceptance criterion 2.

### What was delivered

- **[vig-os/devcontainer-smoke-test#14](https://github.com/vig-os/devcontainer-smoke-test/pull/14)** — Upgraded `repository-dispatch.yml` from stub to validate → orchestrate → summary flow; parameterized `ci-container.yml` image tag via `workflow_call` input; added `workflow_call` trigger to `ci.yml`.
- **[vig-os/devcontainer-smoke-test#23](https://github.com/vig-os/devcontainer-smoke-test/pull/23)** — Fixed `pull-requests: write` permission required by the dispatch caller ceiling.

### Post-merge dispatch validation (3/3 passed)

| # | Scenario | Expected | Result | Run |
|---|---|---|---|---|
| 1 | Success path (`rc_tag=latest`) | All stages pass | **PASS** | [smoke-test-trigger #2](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/22861303250) |
| 2 | Missing `rc_tag` | `validate` + `summary` fail | **PASS** | [smoke-test-trigger #3](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/22861406455) |
| 3 | Invalid image tag (`does-not-exist-tag`) | `validate` passes, `ci-container` fails pull, `summary` fails | **PASS** | [smoke-test-trigger #4](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/22861464558) |

### Remaining work (devcontainer repo side)

The following acceptance criteria are still open and require changes in **this** repo:

- [ ] **RC publish automatically triggers the smoke-test repo via `repository_dispatch`** — the release workflow needs to send the dispatch after RC image push (requires cross-repo token)
- [ ] **Cross-repo dispatch secret is created and documented** — fine-grained PAT or GitHub App token with dispatch permission to `vig-os/devcontainer-smoke-test`
- [ ] **Manual release gate process is documented** — operator workflow for checking smoke results before final release
- [ ] **TDD compliance**

---

# [Comment #2]() by [c-vigo]()

_Posted on March 9, 2026 at 05:42 PM_

Manual ops note for #173 completion:

- Install `RELEASE_APP` on `vig-os/devcontainer-smoke-test`
- Required repository permission: **Contents: Read**
- Purpose: allow `release.yml` in `vig-os/devcontainer` to send cross-repo `repository_dispatch` events for RC smoke-test triggering

This is a one-time GitHub App installation/configuration step.

