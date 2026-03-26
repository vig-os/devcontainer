---
type: issue
state: closed
created: 2026-03-13T13:21:43Z
updated: 2026-03-13T13:42:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/296
comments: 0
labels: bug, priority:high, area:ci, area:image, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:54.872Z
---

# [Issue 296]: [[BUG] RC smoke-test deploy writes stable DEVCONTAINER_VERSION, breaking container CI](https://github.com/vig-os/devcontainer/issues/296)

### Description
Release-candidate smoke-test deploys can write `.vig-os` with a stable tag (`X.Y.Z`) instead of the dispatched RC tag (`X.Y.Z-rcN`), causing `ci-container.yml` to resolve a non-existent image tag and fail before lint/tests run.

### Steps to Reproduce
1. Trigger smoke-test dispatch with RC tag (example: `0.3.0-rc2`).
2. Open generated deploy PR in `vig-os/devcontainer-smoke-test`.
3. Observe `.vig-os` contains `DEVCONTAINER_VERSION=0.3.0` (stable), not `0.3.0-rc2`.
4. Let `CI (Container)` run on that PR.
5. `Resolve image tag` fails at `docker manifest inspect ghcr.io/vig-os/devcontainer:0.3.0`.

### Expected Behavior
For RC dispatches, generated workspace metadata and CI image resolution should use the exact dispatched tag (`X.Y.Z-rcN`), and container CI should validate that same published RC tag.

### Actual Behavior
Deploy PR metadata references the RC tag, but `.vig-os` is rendered with the stable base version, so container CI validates `ghcr.io/vig-os/devcontainer:X.Y.Z` and fails when only `X.Y.Z-rcN` exists.

### Environment
- **OS**: GitHub Actions Ubuntu runner
- **Container Runtime**: Docker (Actions runner)
- **Image Version/Tag**: expected `0.3.0-rc2`, resolved `0.3.0`
- **Architecture**: AMD64

### Additional Context
- Failing job: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23052471041?pr=30
- Related smoke-test PR: https://github.com/vig-os/devcontainer-smoke-test/pull/30
- Related parent scope: #169

- [ ] Permanent fix ensures RC publish version is propagated to rendered workspace `.vig-os` and downstream CI tag resolution.
- [ ] Add/adjust automated test coverage to prevent regression of RC tag propagation.
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

### Possible Solution
Propagate `publish_version` (not base `version`) into build-time/template replacement used for workspace assets during candidate releases, or otherwise ensure `.vig-os` receives the exact RC tag used for pushed manifests.
