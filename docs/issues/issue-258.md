---
type: issue
state: closed
created: 2026-03-11T09:02:36Z
updated: 2026-03-11T20:14:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/258
comments: 1
labels: feature, area:ci, effort:medium, area:testing, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-12T07:59:29.559Z
---

# [Issue 258]: [[FEATURE] Automated RC deploy-and-test via PR in smoke-test repo](https://github.com/vig-os/devcontainer/issues/258)

### Description

Refurbish `repository-dispatch.yml` in the smoke-test repo so that each RC publish triggers a full deploy-test-report cycle: the workflow fetches the RC image, re-deploys the workspace via `install.sh`, commits the changes via a PR, lets PR-triggered CI validate the deployment, and auto-merges on success. Drop CHANGELOG from the smoke-test repo entirely.

### Problem Statement

The current `repository-dispatch.yml` (#169) validates the dispatch payload and calls `ci.yml` / `ci-container.yml` via `workflow_call`, but:

1. **No deployment** -- it runs CI against whatever code is already in the repo. If the RC ships updated template files, they are never deployed or tested.
2. **No commit trail** -- nothing records which RC was tested or what changed.
3. **No tracking mechanism** -- CHANGELOG doesn't make sense for a bot-only repo that receives only automated RC deployments.
4. **Bug** -- line 82 references `needs.ci.container.result` (typo: should be `needs.ci-container.result`).

### Proposed Solution

**Workflow flow:**

```
repository_dispatch (rc_tag)
    │
    ├── validate: extract & validate rc_tag
    │
    ├── deploy:
    │   ├── close stale RC PRs
    │   ├── install.sh --version <rc_tag> --smoke-test --force .
    │   ├── write RC tag to .vig-os (from #257)
    │   ├── detect changes (git diff)
    │   ├── if changes: create branch rc/<rc_tag>, commit, push, create PR
    │   └── enable auto-merge
    │
    ├── ci-container: workflow_call with explicit rc_tag
    │   (PR-triggered ci.yml handles bare-runner validation)
    │
    └── summary: report results
```

**Design decisions:**

1. **PR-based deploy** -- each RC deployment creates a branch (`rc/<rc-tag>`) and PR to `main`. CI triggers naturally on the PR. Auto-merge on success. PR history = audit trail.
2. **No CHANGELOG** -- commit history is the log. Each merged PR shows which RC was deployed. GitHub Actions history shows test results. If queryable tags are wanted later, the workflow can tag successful merges.
3. **Inline `ci-container` kept** -- GitHub Actions `container:` directive evaluates at workflow parse time, so PR-triggered `ci-container.yml` can't read `.vig-os` dynamically. The inline `workflow_call` with explicit RC tag is the pragmatic solution.
4. **Stale PR cleanup** -- before creating a new RC PR, close any open `rc-deploy` labeled PRs.

**Files to change:**

- **Rewrite**: `assets/smoke-test/.github/workflows/repository-dispatch.yml` -- add deploy job, PR creation, auto-merge, fix typo
- **Update**: `assets/smoke-test/README.md` -- document new flow, no CHANGELOG, how to check status

### Alternatives Considered

- **Direct commit to main** -- simpler but less traceable. PR-based flow was chosen for audit trail and CI integration.
- **Inline CI via `workflow_call` only** -- `workflow_call` uses the caller's ref, not the newly deployed code. PR-triggered CI tests the actual deployed files.
- **CHANGELOG / deployment log file** -- adds maintenance burden for a bot-only repo. Commit + PR history provides the same information with zero overhead.

### Additional Context

- Depends on #257 (`.vig-os` config file) for the deploy step that writes the RC tag.
- Related to #169 (Phase 1 smoke-test setup). This issue covers the workflow refurbishment beyond basic dispatch wiring.
- `install.sh` supports `--version VER` to pull a specific image tag -- confirmed in the existing codebase.
- Ubuntu runners have Docker, which `install.sh` needs to pull and run the image.

### Impact

- **Who benefits**: Release operators. RC testing becomes fully automated with a clear pass/fail signal (merged PR = passed).
- **Compatibility**: Backward compatible. Only changes the smoke-test repo workflow and assets.

### Changelog Category

Added
---

# [Comment #1]() by [c-vigo]()

_Posted on March 11, 2026 at 09:03 AM_

## Implementation Plan

Depends on #257 (`.vig-os` config file).

### 1. Rewrite `repository-dispatch.yml`

Rewrite `assets/smoke-test/.github/workflows/repository-dispatch.yml` with the following job structure:

**`validate`** (keep existing, minor cleanup):
- Extract and validate `rc_tag` from `client_payload`
- Output `rc_tag`

**`deploy`** (new job):
```yaml
deploy:
  name: Deploy RC to workspace
  needs: validate
  runs-on: ubuntu-22.04
  outputs:
    has_changes: ${{ steps.check.outputs.has_changes }}
    pr_number: ${{ steps.pr.outputs.pr_number }}
  steps:
    - uses: actions/checkout@...

    - name: Close stale RC PRs
      run: |
        gh pr list --label rc-deploy --state open --json number -q '.[].number' | \
          xargs -I{} gh pr close {} --comment "Superseded by new RC"

    - name: Run installer with RC image
      env:
        RC_TAG: ${{ needs.validate.outputs.rc_tag }}
      run: |
        bash install.sh --version "$RC_TAG" --smoke-test --force .

    - name: Write RC tag to .vig-os
      env:
        RC_TAG: ${{ needs.validate.outputs.rc_tag }}
      run: |
        sed -i "s/^DEVCONTAINER_VERSION=.*/DEVCONTAINER_VERSION=${RC_TAG}/" .vig-os

    - name: Check for changes
      id: check
      run: |
        if git diff --quiet; then
          echo "has_changes=false" >> "$GITHUB_OUTPUT"
        else
          echo "has_changes=true" >> "$GITHUB_OUTPUT"
        fi

    - name: Create branch and PR
      if: steps.check.outputs.has_changes == 'true'
      id: pr
      env:
        RC_TAG: ${{ needs.validate.outputs.rc_tag }}
      run: |
        BRANCH="rc/${RC_TAG}"
        git checkout -b "$BRANCH"
        git add -A
        git commit -m "chore: deploy ${RC_TAG}"
        git push -u origin "$BRANCH"
        PR_URL=$(gh pr create --base main --head "$BRANCH" \
          --title "chore: deploy ${RC_TAG}" \
          --body "Automated RC deployment triggered by repository_dispatch." \
          --label rc-deploy)
        gh pr merge "$PR_URL" --auto --merge
        echo "pr_number=$(gh pr view "$PR_URL" --json number -q .number)" >> "$GITHUB_OUTPUT"
```

**`ci-container`** (kept, runs after deploy):
```yaml
ci-container:
  name: Run container CI (RC image)
  needs: [validate, deploy]
  uses: ./.github/workflows/ci-container.yml
  with:
    image-tag: ${{ needs.validate.outputs.rc_tag }}
```

Rationale: GitHub Actions `container:` directive evaluates at parse time, so PR-triggered `ci-container.yml` can't read `.vig-os` dynamically. The inline `workflow_call` with explicit RC tag validates the RC image. PR-triggered `ci.yml` (bare runner) validates the deployed template files.

**`summary`** (rewrite, fix typo):
- Aggregate results from `validate`, `deploy`, `ci-container`
- Fix `needs.ci.container.result` → `needs.ci-container.result` (bug)
- Post summary comment on PR if one was created

### 2. Drop `ci-bare` inline call

The bare-runner CI (`ci.yml`) triggers naturally on the PR via `pull_request` event. No need for an inline `workflow_call`.

### 3. Update `README.md`

Update `assets/smoke-test/README.md` to document:
- The automated deploy-via-PR flow
- That `.vig-os` contains the deployed RC tag
- No CHANGELOG -- commit + PR history is the log
- How to check RC test status:
  ```bash
  gh -R vig-os/devcontainer-smoke-test pr list --label rc-deploy
  gh -R vig-os/devcontainer-smoke-test run list --workflow repository-dispatch.yml
  ```

### 4. Permissions

The workflow needs:
- `contents: write` (create branches, push commits)
- `pull-requests: write` (create PRs, enable auto-merge)

If `main` is branch-protected, the RELEASE_APP (already installed on `devcontainer-smoke-test`) provides the required token. The deploy step would need a `actions/create-github-app-token` step similar to what `release.yml` already does for the dispatch.

### Design: No CHANGELOG in smoke-test repo

Tracking is via:
- **PR history**: each RC deployment = one PR. Merged = passed, open = failed.
- **Commit history on main**: `chore: deploy X.Y.Z-rcN` entries.
- **GitHub Actions runs**: detailed CI results per RC.

### Open questions

- **`install.sh` on bare runner**: needs Docker to pull the image. Ubuntu runners have Docker -- confirm in a test run.
- **`rc-deploy` label**: needs to be created in the smoke-test repo (or passed via `--label` which auto-creates if the user has permissions).
- **Branch protection**: determine if smoke-test `main` is protected and whether RELEASE_APP can bypass.

