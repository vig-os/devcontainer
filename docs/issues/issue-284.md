---
type: issue
state: closed
created: 2026-03-12T18:24:38Z
updated: 2026-03-13T11:19:04Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/284
comments: 1
labels: bug, priority:blocking, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:56.588Z
---

# [Issue 284]: [[BUG] Smoke-test receiver should accept dispatch tag payload](https://github.com/vig-os/devcontainer/issues/284)

## Description

Two issues in `assets/smoke-test/.github/workflows/repository-dispatch.yml`:

1. **Payload key mismatch**: Candidate release dispatch sends `client_payload.tag`, but the deployed smoke-test receiver workflow validates `client_payload.rc_tag`, causing dispatch-triggered runs to fail at validation.

2. **Cross-repo reference**: The deploy commit message uses `Refs: #258`, but this runs in the smoke-test repo context where issue #258 does not exist. It should use a fully-qualified reference (`Refs: vig-os/devcontainer#258`).

## Steps to Reproduce

1. Trigger candidate release in `vig-os/devcontainer`.
2. Observe successful dispatch from `release.yml`.
3. Open triggered run in `vig-os/devcontainer-smoke-test`.
4. See validation failure in `Validate dispatch payload`.

## Expected Behavior

Receiver accepts `client_payload.tag` and continues to deploy/CI jobs. Deploy commits reference the correct cross-repo issue.

## Actual Behavior

Receiver run fails early in payload validation and downstream jobs are skipped. Deploy commits (when they succeed) link to a non-existent local issue.

## Environment

- **OS**: GitHub Actions Ubuntu runner
- **Container Runtime**: N/A
- **Image Version/Tag**: `0.3.0-rc1`
- **Architecture**: N/A

## Additional Context

- Triggering release run: https://github.com/vig-os/devcontainer/actions/runs/23016037898
- Failed smoke-test run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23016596595
- Failed job: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23016596595/job/66841363171
- Related incident: https://github.com/vig-os/devcontainer/issues/283
- Cross-repo reference flagged by Copilot: https://github.com/vig-os/devcontainer-smoke-test/pull/25

## Possible Solution

1. Update receiver to accept `client_payload.tag` (already correct in source-of-truth `assets/smoke-test/.github/workflows/repository-dispatch.yml`; needs manual re-deploy to smoke-test repo).
2. Change `Refs: #258` to `Refs: vig-os/devcontainer#258` in the deploy commit message template.

After the fix, the user must manually re-deploy the smoke-test workflow before triggering the release workflow again.

## Changelog Category

Fixed

## Acceptance Criteria

- [ ] Receiver workflow accepts `client_payload.tag`
- [ ] Deploy commit references correct cross-repo issue
- [ ] Validation step succeeds when dispatch contains `tag`
- [ ] Manual re-deploy is documented and completed before re-triggering
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [c-vigo]()

_Posted on March 13, 2026 at 10:39 AM_

> 1. **Payload key mismatch**: Candidate release dispatch sends `client_payload.tag`, but the deployed smoke-test receiver workflow validates `client_payload.rc_tag`, causing dispatch-triggered runs to fail at validation.

Fixed in [devcontainer-smoke-test/#24](https://github.com/vig-os/devcontainer-smoke-test/pull/24)

