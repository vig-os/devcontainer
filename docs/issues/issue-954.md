---
type: issue
state: closed
created: 2026-07-09T11:16:12Z
updated: 2026-07-09T13:23:08Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/954
comments: 1
labels: bug, priority:low, area:workspace, semver:patch
assignees: none
milestone: 0.5.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:17.077Z
---

# [Issue 954]: [fix(workspace): imageless init-workspace --no-prompts defaults DEVKIT_ORG to literal 'vigOS/devc'](https://github.com/vig-os/devkit/issues/954)

## Summary

On the **imageless** `podman run … init-workspace.sh --no-prompts` upgrade path (no `install.sh`), `DEVKIT_ORG` is persisted as the literal **`vigOS/devc`** instead of the real org. Reproduced on the #921 imageless probe across `0.5.0-rc3` and `0.5.0-rc4`. The `install.sh` path resolves the org correctly (`vigOS`).

## Root cause

`assets/init-workspace.sh` line ~320–321:

```sh
if [[ "$NO_PROMPTS" == "true" ]]; then
    ORG_NAME="${ORG_NAME:-vigOS/devc}"
```

A **hardcoded literal default** (a leftover tuned to this repo's own self-scaffold) is used when `--no-prompts` is set with no `ORG_NAME` env and no `DEVKIT_ORG` in the manifest — exactly the raw imageless path. `install.sh`/interactive runs pass or prompt for `ORG_NAME`, so they never hit it.

Two problems: (1) an org value should never contain `/`; (2) `GITHUB_REPOSITORY` (`owner/repo`) **is** available on this path — `DEVKIT_REPO` resolves from it correctly — but `ORG_NAME` ignores it. The bad value is then sed-substituted into `{{ORG_NAME}}` across generated files (lines ~883/895), leaking a malformed org into Renovate config/docs, not just the manifest field.

## Fix

Default the org from the repo owner already in hand:

```sh
ORG_NAME="${ORG_NAME:-${GITHUB_REPOSITORY%%/*}}"   # e.g. vig-os/probe3 -> vig-os
```

falling back to a sane literal (`vigOS`) only if `GITHUB_REPOSITORY` is also unset. At minimum, drop the `/`-containing default.

## Acceptance criteria (TDD)

- Bats coverage: `init-workspace.sh --no-prompts` with `GITHUB_REPOSITORY=some-org/repo` and no `ORG_NAME` persists `DEVKIT_ORG=some-org` (not `vigOS/devc`), and no generated file contains a `/`-bearing `{{ORG_NAME}}` substitution.

Found during 0.5.0 validation (imageless #921 probe).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 9, 2026 at 01:23 PM_

Fixed in #956 (merged to `dev`). Imageless `init-workspace.sh --no-prompts` now derives `DEVKIT_ORG` from the `GITHUB_REPOSITORY` owner segment (fallback literal `vigOS`), dropping the bogus `vigOS/devc` default that also leaked a `/` into `{{ORG_NAME}}` substitutions. Covered by a new bats test. Ships in **0.5.1**.

