---
type: issue
state: open
created: 2026-03-21T14:01:52Z
updated: 2026-03-21T22:43:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/405
comments: 1
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-22T04:25:22.149Z
---

# [Issue 405]: [[BUG] sync-main-to-dev PRs do not trigger CI in downstream repos](https://github.com/vig-os/devcontainer/issues/405)

### Description

PRs created by `assets/workspace/.github/workflows/sync-main-to-dev.yml` in downstream repos (e.g. `devcontainer-smoke-test`) do not trigger CI workflows. Because branch protection on `dev` requires CI to pass, these PRs can never be merged—even when auto-merge is enabled.

The root cause is a GitHub Actions limitation: events (`push`, `pull_request`) triggered by a GitHub App installation token do not start new workflow runs, to prevent recursive loops. The `sync-main-to-dev` workflow uses:

- `commit-app-token` (GitHub App) to push the sync branch—no `push` event fires
- `release-app-token` (GitHub App) to create the PR—no `pull_request` event fires

Latest deployment: https://github.com/vig-os/devcontainer-smoke-test/pull/51  
Blocked sync PR: https://github.com/vig-os/devcontainer-smoke-test/pull/52

The upstream workflow (`.github/workflows/sync-main-to-dev.yml`) in this repo has the same pattern and may be affected too.

### Steps to Reproduce

1. Merge a PR to `main` in a downstream repo (e.g. `devcontainer-smoke-test`)
2. `sync-main-to-dev` fires, creates a sync branch and opens a PR targeting `dev`
3. Observe: no CI workflows run on the PR
4. PR remains unmergeable due to required status checks

### Expected Behavior

CI workflows should run on the sync PR so it can pass required status checks and be merged (or auto-merged).

### Actual Behavior

No CI workflows are triggered. The PR is stuck with pending/missing status checks and cannot be merged.

### Environment

- **GitHub Actions** runner: `ubuntu-22.04`
- **Workflow:** `assets/workspace/.github/workflows/sync-main-to-dev.yml`
- **Downstream repo:** `vig-os/devcontainer-smoke-test`

### Additional Context

This is a known GitHub limitation: when workflows use certain tokens to perform tasks, events from those actions may not create new workflow runs (same class of behavior as `GITHUB_TOKEN` not re-triggering workflows).

### Possible Solution

Options to consider:

1. After creating the PR, explicitly trigger CI via `workflow_dispatch` or `repository_dispatch`
2. Use a PAT for the branch push or PR creation step (trades security for simplicity)
3. Close and reopen the PR with `GITHUB_TOKEN` to generate a new `pull_request` event from a different actor

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on March 21, 2026 at 10:43 PM_

## Root cause analysis

Investigation of the smoke-test deployment (PR #55 → sync run #12 → PR #56) reveals three distinct findings that reframe this issue.

### 1. `workflow_dispatch` checks don't associate with PRs

The current workaround dispatches CI via `gh workflow run ci.yml --ref "${SYNC_BRANCH}"`. CI runs and passes, but **GitHub does not include `workflow_dispatch`-triggered check runs in the PR's status check rollup**.

Evidence from PR https://github.com/vig-os/devcontainer-smoke-test/pull/56 (head SHA `0d7cfa8`):

- **REST API** (`/commits/{sha}/check-runs`): shows 8 check runs including `CI Summary` ✅ from the `workflow_dispatch` CI run
- **GraphQL** (`statusCheckRollup`): shows only 4 check runs, all from `push`-triggered workflows (Sync main to dev, Scorecard). **`CI Summary` is absent.**
- **Ruleset** on `dev`: requires `CI Summary` from integration 15368 (GitHub Actions)

The `workflow_dispatch` approach was always destined to fail — the checks exist on the commit but are invisible to GitHub's merge evaluation.

### 2. Conflict PRs never get `pull_request`-triggered CI

From [GitHub docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/events-that-trigger-workflows#pull_request):

> "Workflows do not run on `pull_request` activity if the pull request has a merge conflict. The merge conflict must be resolved first."

PR #56 is a conflict PR (`mergeable_state: dirty`). **Even if `pull_request` events fire correctly, GitHub skips `pull_request` workflows on PRs with merge conflicts** because it can't create the merge ref (`refs/pull/N/merge`). This is the actual root cause for the conflict PR case — no token type can overcome this limitation.

### 3. GitHub App tokens should trigger workflows (per docs)

The original diagnosis stated: "events triggered by a GitHub App installation token do not start new workflow runs."

This contradicts the [official documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow):

> "If you do want to trigger a workflow from within a workflow run, you can use a **GitHub App installation access token** or a personal access token instead of `GITHUB_TOKEN` to trigger events that require a token."

Both Apps have correct permissions (verified via API):
- **vig-os-release-app**: `pull_requests: write`, `contents: write`, `actions: write`
- **commit-action-bot**: `contents: write`, `workflows: write`

For **clean merges** (no conflicts), App-created PRs should trigger `pull_request` workflows naturally. This needs verification but is expected to work per the docs.

### Summary

| Scenario | Root cause | `pull_request` CI possible? |
|----------|-----------|---------------------------|
| Clean merge | Untested — App tokens should work per docs | Yes, if App triggers the event |
| Conflict merge | GitHub skips `pull_request` workflows on conflicting PRs | **No** — platform limitation |

### Next steps

1. **Clean merges**: Verify that the Release App token PR creation triggers `pull_request` CI. If it does, the `workflow_dispatch` step is unnecessary for this case.
2. **Conflict PRs**: Need an alternative mechanism since `pull_request` workflows can never run. Options: Commit Status API bridge (commit statuses DO appear in `statusCheckRollup`), or accept that conflict PRs require manual CI triggering after conflict resolution.

