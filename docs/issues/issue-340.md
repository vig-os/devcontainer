---
type: issue
state: closed
created: 2026-03-17T13:28:43Z
updated: 2026-03-17T14:07:02Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/340
comments: 0
labels: chore, priority:medium, area:ci, effort:small, semver:patch, security
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:22.804Z
---

# [Issue 340]: [[CHORE] Harden repository-dispatch permissions and align CI trigger docs](https://github.com/vig-os/devcontainer/issues/340)

## Chore Type
CI / Build change

## Description
Address two Copilot review findings from the smoke-test dispatch workflow update:

1) Scope token permissions to least privilege in `.github/workflows/repository-dispatch.yml`.
2) Align header comments with actual CI workflows triggered on deploy PRs.

Source:
- PR: https://github.com/vig-os/devcontainer-smoke-test/pull/34
- Copilot comment (permissions): https://github.com/vig-os/devcontainer-smoke-test/pull/34#discussion_r2946713598
- Copilot comment (CI comment drift): https://github.com/vig-os/devcontainer-smoke-test/pull/34#discussion_r2946713569

## Acceptance Criteria
- [ ] Workflow-level `permissions` are reduced to least privilege (`contents: read` or `{}`).
- [ ] Job-level `contents: write` is granted only where required (`publish-release`).
- [ ] `repository_dispatch` triggering remains unchanged after permission scoping.
- [ ] Header comment accurately reflects current CI workflows that run on deploy PRs.
- [ ] Changes remain minimal and limited to the workflow file.

## Implementation Notes
- Target file: `.github/workflows/repository-dispatch.yml`
- Keep runtime behavior unchanged except permission scoping.
- Prefer wording in comments that minimizes future drift.

## Related Issues
- Related PR: https://github.com/vig-os/devcontainer-smoke-test/pull/34
- Copilot comments:
  - https://github.com/vig-os/devcontainer-smoke-test/pull/34#discussion_r2946713598
  - https://github.com/vig-os/devcontainer-smoke-test/pull/34#discussion_r2946713569

## Priority
Medium

## Changelog Category
Security

## Additional Context
This combines both Copilot findings into one focused hardening/consistency task to keep tracking overhead low.
