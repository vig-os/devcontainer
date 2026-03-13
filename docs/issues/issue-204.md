---
type: issue
state: closed
created: 2026-02-25T12:31:39Z
updated: 2026-02-25T14:17:15Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/204
comments: 0
labels: bug, area:workspace, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-26T04:22:23.726Z
---

# [Issue 204]: [[BUG] postAttachCommand fails in mock-up workspace with crun getcwd error](https://github.com/vig-os/devcontainer/issues/204)

### Description

When testing remote devcontainer orchestration in a mock-up folder, the devcontainer initializes successfully but fails at `postAttachCommand` with a runtime error from `crun`.

Part of PR #166 review and should be tracked under parent issue #70.

### Steps to Reproduce

1. Open a generated/mock-up workspace (e.g. `/home/carlosvigo/Documents/vigOS/tmp`) in devcontainer.
2. Let `initializeCommand` complete successfully.
3. Wait for `postAttachCommand` execution.

### Expected Behavior

`postAttachCommand` runs successfully and completes post-attach setup.

### Actual Behavior

The attach phase fails with:

`Error: crun: getcwd: No such file or directory: OCI runtime attempted to invoke a command that was not found`

Terminal exits immediately after the failed post-attach step.

### Environment

- **OS**: Ubuntu 24.04
- **Container Runtime**: Podman rootless (Linux)
- **Image Version/Tag**: dev
- **Architecture**: AMD64

### Additional Context

Observed during validation of PR #166 (`feature/70-remote-devc-orchestration`) while testing in a mock-up folder where workspace path resolution appears inconsistent during attach.

### Possible Solution

- Make `postAttachCommand` robust to workspace cwd/path mismatch in generated/mock-up workspaces.
- Prefer invoking script through a shell command that does not depend on runtime cwd state.
- Add regression coverage for attach flow in mock-up folders.

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] Reproduced in automated or scripted test
- [ ] `postAttachCommand` succeeds in mock-up workspace
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
