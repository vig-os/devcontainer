---
type: issue
state: open
created: 2026-02-24T07:13:32Z
updated: 2026-03-12T11:44:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/169
comments: 1
labels: feature, area:ci, area:testing, effort:large, semver:minor
assignees: none
milestone: 0.3
projects: none
parent: none
children: 170, 171, 172, 173, 197, 161, 122, 264
synced: 2026-03-12T12:05:21.429Z
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
---

# [Comment #1]() by [c-vigo]()

_Posted on March 12, 2026 at 10:27 AM_

## RC Cycle Test Plan

Full end-to-end release-candidate cycle to validate the remaining acceptance criteria.

---

### Pre-flight Checks

- [x] **`dev` branch CI is green** -- check [Actions > CI](https://github.com/vig-os/devcontainer/actions/workflows/ci.yml)
- [x] **CHANGELOG `## Unreleased` has content** -- browse [CHANGELOG.md on dev](https://github.com/vig-os/devcontainer/blob/dev/CHANGELOG.md)
- [x] **No `release/0.3.0` branch or `0.3.0*` tags exist** -- check [branches](https://github.com/vig-os/devcontainer/branches) and [tags](https://github.com/vig-os/devcontainer/tags)
- [x] **Smoke-test repo accessible** -- visit [vig-os/devcontainer-smoke-test](https://github.com/vig-os/devcontainer-smoke-test)
- [x] **Latest development version manually deployed to smoke-test**: [here](https://github.com/vig-os/devcontainer-smoke-test/commit/5c691fe6c3a1dd3063f569c0c190340297f37086)
- [x] **Local tests pass** (optional)
  ```bash
  git checkout dev && git pull origin dev
  just test
  ```

---

### Phase 1: Prepare Release

- [ ] **Trigger the prepare-release workflow**
  ```bash
  just prepare-release 0.3.0
  ```

- [ ] **Workflow completes successfully** -- monitor in [Actions](https://github.com/vig-os/devcontainer/actions/workflows/prepare-release.yml)

#### Verification checklist

- [ ] `release/0.3.0` branch appears in [branches](https://github.com/vig-os/devcontainer/branches)
- [ ] Draft PR from `release/0.3.0` to `main` appears in [Pull Requests](https://github.com/vig-os/devcontainer/pulls)
- [ ] Release branch CHANGELOG has `## [0.3.0] - TBD` (no `## Unreleased`)
- [ ] `dev` CHANGELOG has empty `## Unreleased` above `## [0.3.0] - TBD`

---

### Phase 2: Review & Test Release Branch

- [ ] **CI passes on release PR** -- check PR's "Checks" tab
  ```bash
  gh run list --branch release/0.3.0 --workflow ci.yml --limit 1
  ```
- [ ] **Review CHANGELOG** -- verify all 0.3 changes are documented with correct issue refs
- [ ] **Mark PR as ready for review** -- click "Ready for review" in the PR UI, or:
  ```bash
  gh pr ready <PR_NUMBER>
  ```
- [ ] **Get PR approval** -- add a reviewer in the PR sidebar

> **Fixing issues:** All fixes go through bugfix PRs targeting `release/0.3.0` (branch is write-protected).

---

### Phase 3: Publish Release Candidate :star: Core #169 validation

#### 3a. Dry run (recommended)

- [ ] **Run candidate publish in dry-run mode**
  ```bash
  just publish-candidate 0.3.0 -f "dry-run=true"
  ```
- [ ] **Validate job passes** -- confirms all prerequisites without making changes

#### 3b. Publish the RC

- [ ] **Trigger the actual candidate publish**
  ```bash
  just publish-candidate 0.3.0
  ```
- [ ] **Monitor in [Actions > Release](https://github.com/vig-os/devcontainer/actions/workflows/release.yml)** -- all 5 jobs should complete:

  | Job | Expected outcome |
  |-----|-----------------|
  | validate | `0.3.0`, kind `candidate`, computed tag `0.3.0-rc1`, PR verified |
  | finalize | No CHANGELOG changes (candidate mode), outputs current SHA |
  | build-and-test (amd64) | Build + image tests + integration tests + Trivy scan pass |
  | build-and-test (arm64) | Same as amd64 |
  | publish | Tag pushed, images on GHCR, manifest created, cosign signed, SBOM + provenance attested |

#### 3c. Verify RC image on GHCR :white_check_mark: Acceptance criterion 1

- [ ] **Tag `0.3.0-rc1` exists** -- check [tags](https://github.com/vig-os/devcontainer/tags)
- [ ] **Image is pullable**
  ```bash
  docker pull ghcr.io/vig-os/devcontainer:0.3.0-rc1
  ```
- [ ] **Multi-arch manifest** -- inspect on [GHCR package page](https://github.com/vig-os/devcontainer/pkgs/container/devcontainer) or:
  ```bash
  docker buildx imagetools inspect ghcr.io/vig-os/devcontainer:0.3.0-rc1
  ```
  Expect both `linux/amd64` and `linux/arm64` platforms.
- [ ] **No `latest` tag updated** (candidate mode should not touch `latest`)
- [ ] **Cosign signature verifies** (optional)
  ```bash
  cosign verify \
    --certificate-identity-regexp='https://github.com/vig-os/devcontainer/' \
    --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
    ghcr.io/vig-os/devcontainer:0.3.0-rc1
  ```

---

### Phase 4: Smoke-Test Gate :star: Core #169 validation

#### 4a. Dispatch fired :white_check_mark: Acceptance criterion 2

- [ ] **New dispatch run appears** in [smoke-test Actions > Repository Dispatch](https://github.com/vig-os/devcontainer-smoke-test/actions/workflows/repository-dispatch.yml)
  ```bash
  gh run list --repo vig-os/devcontainer-smoke-test --workflow repository-dispatch.yml --limit 3
  ```
  > If no run appears, check the devcontainer release workflow's publish job logs for the "Trigger smoke-test repository dispatch" step. Look for token generation warnings.

- [ ] **Dispatch `validate` job passes** -- tag `0.3.0-rc1` matches `^[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+)?$`
- [ ] **Dispatch `deploy` job passes** -- runs installer with `--version 0.3.0-rc1`, creates branch `chore/deploy-0.3.0-rc1`, opens PR to `dev`

#### 4b. Bare-runner CI passes

- [ ] **CI triggered on deploy PR** -- check [smoke-test PRs](https://github.com/vig-os/devcontainer-smoke-test/pulls), then the PR's Checks tab
  ```bash
  gh pr checks <PR_NUMBER> --repo vig-os/devcontainer-smoke-test
  ```
- [ ] Lint & Format: pre-commit hooks pass
- [ ] Tests: pytest passes with coverage
- [ ] Security Scan: bandit + safety pass
- [ ] CI Summary: green

#### 4c. Container CI passes with RC image :white_check_mark: Acceptance criterion 3

This is the **critical test** -- the one that previously failed with `does-not-exist-tag`.

- [ ] **`ci-container.yml` triggered** on the deploy PR
- [ ] **"Initialize containers" succeeds** -- runner pulls `ghcr.io/vig-os/devcontainer:0.3.0-rc1` and starts the container
- [ ] Lint & Format (container): pre-commit hooks pass inside the devcontainer image
- [ ] Tests (container): pytest passes inside the devcontainer image
- [ ] CI Summary (container): green

```bash
gh run list --repo vig-os/devcontainer-smoke-test --workflow ci-container.yml --limit 1
gh run view <RUN_ID> --repo vig-os/devcontainer-smoke-test
```

---

### Phase 5: Fix & Retry (if smoke tests fail)

<details>
<summary>Expand if any smoke-test workflow fails</summary>

1. **Diagnose:**
   ```bash
   gh run view <FAILED_RUN_ID> --repo vig-os/devcontainer-smoke-test --log-failed
   ```

2. **Fix on the release branch** via a bugfix PR:
   ```bash
   git checkout -b bugfix/N-fix-description release/0.3.0
   # ... fix ...
   git push origin bugfix/N-fix-description
   gh pr create --base release/0.3.0 --head bugfix/N-fix-description
   ```

3. **Re-publish candidate** (auto-increments to `0.3.0-rc2`):
   ```bash
   just publish-candidate 0.3.0
   ```

4. Repeat Phase 4 for the new RC.

</details>

---

### Phase 6: Finalize Release

> Only proceed when **both** smoke-test workflows (bare-runner + container) are green.

- [ ] **Trigger final release**
  ```bash
  just finalize-release 0.3.0
  ```
- [ ] **Workflow completes** -- monitor in [Actions > Release](https://github.com/vig-os/devcontainer/actions/workflows/release.yml)

#### Verification checklist

- [ ] CHANGELOG date set (`[0.3.0] - TBD` replaced with `[0.3.0] - YYYY-MM-DD`)
- [ ] sync-issues triggered and completed
- [ ] Both architectures build and test successfully
- [ ] Tag `0.3.0` created -- check [tags](https://github.com/vig-os/devcontainer/tags)
- [ ] Image published as `ghcr.io/vig-os/devcontainer:0.3.0`
- [ ] `latest` tag updated to `0.3.0`
- [ ] Cosign signature + SBOM + provenance attached
- [ ] Verify images:
  ```bash
  docker pull ghcr.io/vig-os/devcontainer:0.3.0
  docker pull ghcr.io/vig-os/devcontainer:latest
  docker buildx imagetools inspect ghcr.io/vig-os/devcontainer:0.3.0
  ```

---

### Phase 7: Post-Release

- [ ] **Merge release PR to main** -- click "Merge pull request" in the PR UI, or:
  ```bash
  gh pr merge <PR_NUMBER> --merge
  ```
- [ ] **sync-main-to-dev fires** -- check [Actions > sync-main-to-dev](https://github.com/vig-os/devcontainer/actions/workflows/sync-main-to-dev.yml)
- [ ] **Dev is updated** -- sync PR auto-merges if conflict-free
- [ ] **Final state** -- both tags exist:
  ```bash
  git fetch --all --tags
  git tag | grep 0.3.0
  # Expected: 0.3.0  and  0.3.0-rc1 (or rc2, etc.)
  ```

---

### Summary: Acceptance Criteria vs. Verification Steps

| # | Criterion | Verified at | Evidence |
|---|-----------|------------|----------|
| 1 | RC publishing works (`X.Y.Z-rc1` to GHCR) | Phase 3c | Tag exists, image pullable, multi-arch manifest present |
| 2 | Smoke-test triggered via `repository_dispatch` | Phase 4a | Dispatch run visible in smoke-test repo Actions |
| 3 | Container CI passes using RC image | Phase 4c | `ci-container.yml` all-green, containers initialize with real RC tag |
| 4 | TDD compliance | Ongoing | Commit history shows test-first commits per TDD rules |

---

### Known Risks

| Risk | Mitigation |
|------|-----------|
| Container CI can't pull RC image | Ensure GHCR package visibility is public, or smoke-test repo has `packages:read` |
| Cross-repo dispatch doesn't fire | `RELEASE_APP` must be installed on `vig-os/devcontainer-smoke-test` with `contents:write`; check publish job logs for token warnings |
| Release workflow fails mid-run | Automatic rollback resets branch + deletes tag + creates issue |
| RC tag collision from concurrent run | Tag push step detects collision; re-run to infer next RC number |


