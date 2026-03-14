---
type: issue
state: closed
created: 2026-03-13T07:53:26Z
updated: 2026-03-13T10:23:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/285
comments: 0
labels: refactor, area:workspace, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:56.314Z
---

# [Issue 285]: [[REFACTOR] Replace source with value parsing for .vig-os config loading](https://github.com/vig-os/devcontainer/issues/285)

## Description

`initialize.sh` and `version-check.sh` both load `.vig-os` using `source "$config_file"`, which executes the file as shell code. Since `.vig-os` is a simple key-value config (`DEVCONTAINER_VERSION=X.Y.Z`), it should be parsed as data rather than executed.

This reduces the attack surface if `.vig-os` is ever modified by an untrusted source (e.g. a compromised installer or user-edited workspace).

Flagged by Copilot review: https://github.com/vig-os/devcontainer-smoke-test/pull/25

## Files / Modules in Scope

- `assets/workspace/.devcontainer/scripts/initialize.sh` (function `load_vig_os_config`)
- `assets/workspace/.devcontainer/scripts/version-check.sh` (function `get_current_version`)

## Out of Scope

- `.vig-os` file format (keep as-is: `KEY=VALUE`)
- CI workflows
- Smoke-test assets

## Invariants / Constraints

- All existing tests must pass without modification
- Behavior must remain identical: `DEVCONTAINER_VERSION` is read from `.vig-os` and used the same way
- Both macOS and Linux `sed` paths in `initialize.sh` must still work

## Acceptance Criteria

- [ ] Both scripts parse `.vig-os` with grep/cut (or equivalent) instead of `source`
- [ ] Invalid or unexpected content in `.vig-os` does not execute
- [ ] All existing tests pass
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

## Changelog Category

No changelog needed

## Additional Context

Pattern appears in two files with identical structure. Both were flagged independently by Copilot on vig-os/devcontainer-smoke-test#25.
