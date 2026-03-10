---
type: issue
state: open
created: 2026-02-24T07:13:32Z
updated: 2026-03-09T21:06:05Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/169
comments: 0
labels: feature, area:ci, area:testing, effort:large, semver:minor
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-10T04:14:47.771Z
---

# [Issue 169]: [[FEATURE] Smoke-test repository to validate shipped CI/CD workflows](https://github.com/vig-os/devcontainer/issues/169)

### Description

Create a dedicated test repository (`vig-os/devcontainer-smoke-test`) where the workspace template is deployed and the shipped CI/CD workflows are executed against a real GitHub Actions environment. Integrate this with the release-candidate (RC) workflow so that every release is smoke-tested before reaching downstream users.

This issue covers **Phase 1** only: establishing the smoke-test repo, wiring RC publishing with cross-repo dispatch, and verifying the end-to-end flow with a real RC cycle. Phases 2 and 3 are documented below for context but are out of scope.

### Problem Statement

Two gaps exist in the current testing strategy:

1. **Shipped workflows are never executed in a real GitHub Actions environment.** The five workflows under `assets/workspace/.github/workflows/` are template files copied to downstream projects, but no test validates they actually run. If an action pin breaks, a `uv` version incompatibility appears, or a runner environment changes, no test catches it until a real user hits the failure.

2. **The devcontainer image is never validated as a CI environment.** The image ships all CI tools (Python, uv, pre-commit, ruff, pytest), but nothing proves a full CI workflow (lint, test, security) runs successfully inside it. `test-image` validates tool presence/versions; `test-integration` validates the devcontainer lifecycle. Neither tests the end-to-end CI use case. An in-repo test that re-runs tools inside the container adds little value over `test-image` -- what's needed is validation in a real GitHub Actions environment.

Both gaps are addressed by combining the smoke-test repo with a release-candidate workflow.

### Proposed Solution

#### Release-candidate flow

```
release/X.Y.Z branch
    │
    ▼
CI passes on PR ──► Publish X.Y.Z-rc1 to GHCR
                         │
                         ▼
               Smoke-test repo triggered (repository_dispatch)
                         │
                    ┌────┴────┐
                    │         │
                  pass       fail
                    │         │
                    ▼         ▼
             Promote to    Fix on release branch
             X.Y.Z +      Publish X.Y.Z-rc2
             latest        (re-trigger smoke)
```

#### Scope: Phase 1 -- Smoke-test repo + RC dispatch

**Smoke-test repo (`vig-os/devcontainer-smoke-test`):**
- Deploy a fresh workspace via `init-workspace.sh`
- Two CI variants:
  - **Bare-runner CI** (`ci.yml`): validates `setup-env`, action pins, runner compat
  - **Container CI** (`ci-container.yml`): uses `container: ghcr.io/vig-os/devcontainer:<tag>` to validate the image as a CI environment
- Trigger: `repository_dispatch` from the devcontainer repo on RC publish
- Orchestration: `repository-dispatch.yml` validates payload, runs both CI variants with the RC tag

**Devcontainer repo (release workflow changes):**
- RC publishing: release workflow publishes `X.Y.Z-rc1` to GHCR on candidate releases
- Cross-repo dispatch: triggers smoke-test repo via `repository_dispatch` with the RC tag (using GitHub App token)
- Manual smoke gate: release operator verifies smoke-test results before final publish (documented in `docs/RELEASE_CYCLE.md`)

**Verification:** run an end-to-end RC cycle (cut a release branch, publish an RC, confirm dispatch fires, confirm both smoke-test workflows pass).

---

<details>
<summary>Future phases (out of scope)</summary>

#### Phase 2 -- Extended validation

- Validate `codeql.yml` and `scorecard.yml` in the smoke-test repo
- Add `release.yml` dry-run validation (seed repo with dev/main branching model)
- Automate the gate: smoke-test repo posts a commit status or dispatches back to the devcontainer repo, allowing the release workflow to proceed automatically
- Periodic re-validation on a schedule (catch runner environment drift)

#### Phase 3 -- Full coverage

- Configure GitHub App for `sync-issues.yml` testing
- Full release cycle simulation in the smoke-test repo
- Status dashboard or badge reporting smoke-test health

</details>

### Alternatives Considered

- **In-repo CI workflow test (composite action + `podman exec`):** Runs CI commands inside the freshly built image using the tar artifact. While it tests the image pre-merge, it doesn't validate real GitHub Actions behavior (`container:` directive quirks, runner networking, `actions/checkout` inside containers). The smoke-test repo covers this more faithfully. `test-image` already validates tool installation, so the in-repo test adds marginal value.
- **`nektos/act` (local runner):** Cannot run CodeQL, Scorecard, dependency-review, or anything needing GitHub API context. Incomplete `GITHUB_TOKEN` simulation. Only partially validates `ci.yml`.
- **Reusable workflows:** Would require restructuring shipped templates as callable workflows -- changes the template architecture for all downstream users. Over-engineering.
- **In-repo workflow testing:** The devcontainer repo's own CI already uses different workflows; mixing template workflows would create confusion and require mocking the template project structure.

### Additional Context

RC image lifecycle:
- RC tags follow SemVer pre-release format: `X.Y.Z-rc1`, `X.Y.Z-rc2`, etc.
- RCs are published to the same GHCR registry (`ghcr.io/vig-os/devcontainer`)
- RC tags are retained after final release (audit trail; negligible storage cost)
- No circular dependency: the devcontainer repo's own CI does not depend on the smoke-test repo

### Impact

- **Who benefits:** All downstream users of the devcontainer template. Regressions in shipped workflows and the image's CI capability are caught before release.
- **Compatibility:** Backward compatible. No changes to shipped templates.
- **Cost:** Public repo = free GitHub Actions minutes. RC images add minor GHCR storage.

### Changelog Category

Added

### Acceptance Criteria

- [x] Smoke-test repo exists with a deployed workspace from the current template
- [x] Bare-runner CI (`ci.yml`) runs successfully against the deployed workspace
- [ ] RC publishing works: release workflow can publish `X.Y.Z-rc1` to GHCR
- [ ] Smoke-test repo is triggered via `repository_dispatch` on RC publish
- [ ] Container CI (`ci-container.yml`) runs successfully using the RC image via `container:` directive
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
