---
type: issue
state: closed
created: 2026-03-19T13:02:01Z
updated: 2026-03-19T16:02:53Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/373
comments: 0
labels: feature, area:workspace, area:workflow, effort:small, semver:minor
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:25.335Z
---

# [Issue 373]: [[FEATURE] Expose release recipes in downstream workspace justfile](https://github.com/vig-os/devcontainer/issues/373)

## Description

Make the release recipes currently defined in the root `justfile` available in downstream projects via the workspace/devcontainer `justfile` templates.

Target recipes:
- `prepare-release`
- `publish-candidate`
- `finalize-release`
- `reset-changelog`
- `pull`

## Problem Statement

Downstream projects do not currently get the same release automation entry points that exist in this repository’s root `justfile`. This creates inconsistent release workflows and forces teams to manually reproduce commands or trigger GitHub workflows ad hoc.

## Proposed Solution

Add release recipe support to downstream-facing justfile templates so downstream repositories can run the same release operations with a consistent interface.

Implementation should:
- preserve current behavior in this repository
- provide sane defaults for `ref` handling (matching current recipe behavior)
- keep GitHub workflow dispatch flags passthrough support

## Acceptance Criteria

- [ ] Downstream-generated justfile includes `prepare-release`, `publish-candidate`, `finalize-release`, `reset-changelog`, and `pull`
- [ ] Each recipe dispatches the correct workflow/command with expected default refs
- [ ] Existing downstream projects can adopt the recipes without breaking current workflows
- [ ] Documentation references the downstream release recipe availability and usage
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Alternatives Considered

- Keep release recipes only in the root repository and require downstream projects to duplicate them manually.
- Provide only partial release helpers downstream (rejected because it keeps workflows inconsistent).

## Additional Context

Related:
- #71 (broader downstream justfile recipe expansion)
- #330 (downstream release extensibility contract)

Source context:
- `justfile` release group recipes around `prepare-release`, `finalize-release`, `publish-candidate`, `reset-changelog`, `pull`

## Impact

This is a backward-compatible enhancement that standardizes release operations across downstream projects and reduces manual release process drift.

## Changelog Category

Added
