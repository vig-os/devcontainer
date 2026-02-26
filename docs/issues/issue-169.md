---
type: issue
state: open
created: 2026-02-24T07:13:32Z
updated: 2026-02-25T11:01:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/169
comments: 0
labels: feature, area:ci, area:testing, effort:large, semver:minor
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-26T04:22:25.432Z
---

# [Issue 169]: [[FEATURE] Smoke-test repository to validate shipped CI/CD workflows](https://github.com/vig-os/devcontainer/issues/169)

### Description

Create a dedicated test repository (e.g., `vig-os/devcontainer-smoke-test`) where the workspace template is deployed and the shipped CI/CD workflows are executed against a real GitHub Actions environment. Integrate this with a release-candidate (RC) workflow so that every release is smoke-tested before reaching downstream users.

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
                    │
                    ▼
             Delete X.Y.Z-rc* from GHCR
```

#### Phase 1 -- Smoke-test repo + RC publishing (high value)

**Smoke-test repo (`vig-os/devcontainer-smoke-test`):**
- Deploy a fresh workspace via `init-workspace.sh`
- Include two CI variants:
  - **Bare-runner CI**: the shipped `ci.yml` as-is (validates `setup-env`, action pins, runner compat)
  - **Container CI**: a `ci-container.yml` that uses `container: ghcr.io/vig-os/devcontainer:<tag>` (validates the image as a CI environment)
- Trigger: `repository_dispatch` from the devcontainer repo on RC publish
- Validate `ci.yml` and `ci-container.yml` run successfully
- Report results back (commit status or dispatch)

**Devcontainer repo (release workflow changes):**
- Add RC publishing capability: after CI passes on a release branch PR, publish `X.Y.Z-rc1` to GHCR
- Trigger smoke-test repo via `repository_dispatch` with the RC tag
- Gate final release on smoke-test results (manual initially, automated later)
- Clean up `X.Y.Z-rc*` tags from GHCR after final `X.Y.Z` is published

#### Phase 2 -- Extended validation

- Validate `codeql.yml` and `scorecard.yml` in the smoke-test repo
- Add `release.yml` dry-run validation (seed repo with dev/main branching model)
- Automate the gate: smoke-test repo posts a commit status or dispatches back to the devcontainer repo, allowing the release workflow to proceed automatically
- Periodic re-validation on a schedule (catch runner environment drift)

#### Phase 3 -- Full coverage

- Configure GitHub App for `sync-issues.yml` testing
- Full release cycle simulation in the smoke-test repo
- Status dashboard or badge reporting smoke-test health

### Alternatives Considered

- **In-repo CI workflow test (composite action + `podman exec`):** Runs CI commands inside the freshly built image using the tar artifact. While it tests the image pre-merge, it doesn't validate real GitHub Actions behavior (`container:` directive quirks, runner networking, `actions/checkout` inside containers). The smoke-test repo covers this more faithfully. `test-image` already validates tool installation, so the in-repo test adds marginal value.
- **`nektos/act` (local runner):** Cannot run CodeQL, Scorecard, dependency-review, or anything needing GitHub API context. Incomplete `GITHUB_TOKEN` simulation. Only partially validates `ci.yml`.
- **Reusable workflows:** Would require restructuring shipped templates as callable workflows -- changes the template architecture for all downstream users. Over-engineering.
- **In-repo workflow testing:** The devcontainer repo's own CI already uses different workflows; mixing template workflows would create confusion and require mocking the template project structure.

### Additional Context

Per-workflow feasibility assessment:
- `ci.yml` -- **HIGH**: Self-contained, triggers on PR, validates `setup-env`, uv, pre-commit, pytest, Bandit, Safety
- `ci-container.yml` (new) -- **HIGH**: Same as `ci.yml` but using `container:` directive with the devcontainer image
- `codeql.yml` -- **HIGH**: Triggers on PRs touching `.py` files, no special secrets needed
- `scorecard.yml` -- **HIGH**: Triggers on push to main, needs public repo for `id-token:write`
- `release.yml` -- **MEDIUM**: Requires orchestrating a full release cycle (branch, CHANGELOG, approved PR)
- `sync-issues.yml` -- **MEDIUM**: Requires GitHub App credentials and seed issues

RC image lifecycle:
- RC tags follow SemVer pre-release format: `X.Y.Z-rc1`, `X.Y.Z-rc2`, etc.
- RCs are published to the same GHCR registry (`ghcr.io/vig-os/devcontainer`)
- After final release, RC tags are deleted via `gh api` to keep the registry clean
- No circular dependency: the devcontainer repo's own CI does not depend on the smoke-test repo

Future direction: once `ci-container.yml` is proven in the smoke-test repo, the template `ci.yml` itself can migrate to use `container:` with the devcontainer image, eventually retiring `setup-env` for most jobs.

### Impact

- **Who benefits:** All downstream users of the devcontainer template. Regressions in shipped workflows and the image's CI capability are caught before release.
- **Compatibility:** Backward compatible. No changes to shipped templates in Phase 1. The `container:` migration is a future opt-in change.
- **Cost:** Public repo = free GitHub Actions minutes. RC images add minor GHCR storage (cleaned up after release).

### Changelog Category

Added

### Acceptance Criteria

- [x] Smoke-test repo exists with a deployed workspace from the current template
- [x] Bare-runner CI (`ci.yml`) runs successfully against the deployed workspace
- [ ] Container CI (`ci-container.yml`) runs successfully using the RC image via `container:` directive
- [ ] RC publishing works: release workflow can publish `X.Y.Z-rc1` to GHCR
- [ ] Smoke-test repo is triggered via `repository_dispatch` on RC publish
- [ ] RC tags are cleaned up from GHCR after final release
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
