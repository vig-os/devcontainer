---
type: issue
state: closed
created: 2026-03-09T15:16:51Z
updated: 2026-03-09T15:36:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/247
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:45.006Z
---

# [Issue 247]: [[BUG] CodeQL paths filter causes merge protection to block PRs with no Python changes](https://github.com/vig-os/devcontainer/issues/247)

## Description

The `codeql.yml` workflow template uses a `paths: ['**.py']` filter on the `pull_request` trigger. When a PR targeting `main` (or `dev`/`release/**`) contains no Python file changes, the CodeQL workflow is correctly skipped by GitHub Actions. However, if the repository has **code scanning merge protection** enabled (Settings > Code security > Code scanning > Protection rules), the merge gate expects CodeQL SARIF results for every PR commit. Since CodeQL never ran, there are no results to evaluate, and the check is stuck permanently in a "waiting" state — blocking the merge.

## Steps to Reproduce

1. Enable code scanning merge protection on a downstream repo that uses the `codeql.yml` template
2. Open a PR targeting `main` that modifies only non-Python files (e.g. workflow YAML, lock files, markdown)
3. Observe that all CI checks pass, but the code scanning gate shows: _"Code scanning is waiting for results from CodeQL for the commits \<sha\>."_
4. The PR cannot be merged

## Expected Behavior

PRs with no Python changes should not be blocked by the CodeQL merge protection gate. The workflow should either run and produce an empty/clean result, or the check should be satisfied without results when the paths filter excluded the run.

## Actual Behavior

The code scanning merge protection waits indefinitely for CodeQL results that will never arrive because the workflow was skipped by the `paths` filter.

## Environment

- **Workflow**: `.github/workflows/codeql.yml` (template)
- **Downstream repo**: `vig-os/devcontainer-smoke-test`
- **Blocked PR**: https://github.com/vig-os/devcontainer-smoke-test/pull/23
- **Trigger**: `pull_request` to `main` with `paths: ['**.py']`

## Additional Context

Discovered while merging a CI permissions bugfix (vig-os/devcontainer-smoke-test#22) that only touched workflow YAML, `uv.lock`, and `CHANGELOG.md`.

## Possible Solution

Remove the `paths` filter from the `pull_request` trigger so CodeQL always runs on PRs targeting protected branches. CodeQL on a small Python toolchain is fast (~15s analysis) so the overhead is negligible, and it guarantees SARIF results are always uploaded for the merge protection gate.

Alternatively, add a lightweight "skip" job that uploads an empty SARIF file when no `.py` files are in the diff, so the code scanning check is always satisfied.
