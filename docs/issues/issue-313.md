---
type: issue
state: open
created: 2026-03-13T22:05:11Z
updated: 2026-03-13T22:05:11Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/313
comments: 0
labels: chore, priority:medium, area:ci
assignees: none
milestone: 0.3.1
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:53.749Z
---

# [Issue 313]: [[CHORE] Trigger smoke-test repository_dispatch from finalize-release for existing final tag](https://github.com/vig-os/devcontainer/issues/313)

### Chore Type
CI / Build change

### Description
Add a release workflow path to trigger `repository_dispatch` to `vig-os/devcontainer-smoke-test` using an existing final release tag (for example `v0.3.0`) without re-running full candidate/finalize release automation.

### Acceptance Criteria
- [ ] A documented and supported release command/workflow step triggers `repository_dispatch` to `vig-os/devcontainer-smoke-test`.
- [ ] Dispatch payload includes the selected release tag (e.g. `v0.3.0`).
- [ ] The path is usable when release `0.3.0` already exists (no re-finalize required).
- [ ] The workflow fails clearly if token/app permissions for cross-repo dispatch are missing.

### Implementation Notes
- Reuse existing dispatch contract already consumed by smoke repo (`event_type=smoke-test-trigger`, `client_payload[tag]=...`).
- Keep behavior consistent with current release automation and permission model (`RELEASE_APP` / GitHub App token where applicable).
- Reference current release workflow dispatch logic and extract/reuse where possible to avoid duplicated logic.

### Related Issues
Related to #300, #310

### Priority
Medium

### Changelog Category
No changelog needed

### Additional Context
Operator need: trigger smoke test deployment for an already-published release (e.g. `0.3.0`) without creating a new candidate release run.
