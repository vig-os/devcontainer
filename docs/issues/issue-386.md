---
type: issue
state: open
created: 2026-03-19T22:19:40Z
updated: 2026-03-19T22:23:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/386
comments: 0
labels: bug, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:22.293Z
---

# [Issue 386]: [[BUG] Trigger prepare-release step fails with "not a git repository" in smoke-test dispatch](https://github.com/vig-os/devcontainer/issues/386)

## Description

The downstream smoke-test orchestration fails in the `trigger-prepare-release` phase because the step that runs `gh workflow run prepare-release.yml` is executed outside a Git worktree context.

Error from the failed job:
`failed to run git: fatal: not a git repository (or any of the parent directories): .git`

## Steps to Reproduce

1. Sync workspace workflow templates to downstream repo (as done in local test), including:
   - `ci.yml`
   - `release-core.yml`
   - `release-publish.yml`
   - `sync-issues.yml`
   - `sync-main-to-dev.yml`
2. Run the smoke-test dispatch flow for `0.3.1-rc5`.
3. Open downstream run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304352254
4. Inspect job `Trigger and wait for prepare-release workflow` -> step `Trigger prepare-release`.

## Expected Behavior

`trigger-prepare-release` should successfully trigger `prepare-release.yml`, and release orchestration should continue to release PR readiness/release steps.

## Actual Behavior

`trigger-prepare-release` fails immediately with:
`fatal: not a git repository (or any of the parent directories): .git`

As a result:
- prepare: failure
- release PR readiness: skipped
- release workflow: skipped
- summary: failure

## Environment

- **Source repo**: `vig-os/devcontainer`
- **Downstream repo**: `vig-os/devcontainer-smoke-test`
- **Downstream run**: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304352254
- **Failed job**: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304352254/job/67826845826
- **Deploy PR context**: https://github.com/vig-os/devcontainer-smoke-test/pull/40

## Additional Context

Related issues:
- Root-cause predecessor: #380
- Generic dispatch failure tracker: #384
- Similar duplicate tracker: #382

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

## Possible Solution

Ensure the `trigger-prepare-release` job runs in a checked-out repository context before invoking `gh workflow run` (or invoke `gh` in a way that does not require local git context, if supported by current command usage).

## Changelog Category

Fixed

