---
type: issue
state: closed
created: 2026-03-12T08:50:44Z
updated: 2026-03-12T10:26:51Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/266
comments: 0
labels: bug, priority:high, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-12T12:05:20.808Z
---

# [Issue 266]: [[BUG] just prepare-release runs default-branch workflow instead of dev ref and leaves partial release side effects](https://github.com/vig-os/devcontainer/issues/266)

## Description

https://github.com/vig-os/devcontainer/actions/runs/22993802679

✓ Release preparation workflow triggered for version 0.3.0
Monitor progress: gh run list --workflow prepare-release.yml dispatches the workflow file as resolved on the default branch () instead of the intended  branch context.  
This can run stale workflow logic and create inconsistent release artifacts.

Scope also includes cleanup/revert of artifacts produced by the failed run.

## Steps to Reproduce

1. On , run https://github.com/vig-os/devcontainer/actions/runs/22993804072

✓ Release preparation workflow triggered for version 0.3.0
Monitor progress: gh run list --workflow prepare-release.yml.
2. Observe workflow run: https://github.com/vig-os/devcontainer/actions/runs/22993432818/job/66759661102
3. Check the job behavior and failure in .

## Expected Behavior

- Release preparation runs workflow logic intended for  branch state.
- If a run fails mid-flight, automation either rolls back partial side effects or provides an explicit cleanup path.

## Actual Behavior

- Dispatch resolves workflow from .
- Run fails during PR creation ().
- Side effects remain from earlier steps (release branch and/or changelog freeze commit), requiring manual cleanup.

## Environment

- **OS**: Linux 6.17.0-14-generic
- **Shell**: bash
- **Repo**: 
- **Command**: https://github.com/vig-os/devcontainer/actions/runs/22993805350

✓ Release preparation workflow triggered for version 0.3.0
Monitor progress: gh run list --workflow prepare-release.yml

## Additional Context

- Related release automation work: #172
- Failure indicates partial execution model needs explicit rollback/compensation handling.

## Possible Solution

- Update  invocation path so workflow dispatch uses  (or equivalent explicit ref wiring).
- Add guardrails to verify runtime ref before mutating repository state.
- Add failure compensation for prepare-release:
  - delete created  branch on failure
  - revert/cherry-pick rollback for changelog freeze commit on  when PR creation fails
- Add tests/verification for dispatch-ref correctness and rollback behavior.
- [ ] TDD compliance (see )

## Changelog Category

Fixed
