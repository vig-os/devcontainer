---
type: issue
state: closed
created: 2026-03-27T08:01:54Z
updated: 2026-03-27T12:57:35Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/459
comments: 1
labels: chore, priority:blocking, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:13.975Z
---

# [Issue 459]: [[CHORE] sync-main-to-dev failed after push to main (release 0.3.1)](https://github.com/vig-os/devcontainer/issues/459)

## Chore Type

CI / Build change

## Description

The `sync-main-to-dev.yml` workflow failed when `main` was updated by merge of release 0.3.1 ([PR #342](https://github.com/vig-os/devcontainer/pull/342)).

## Acceptance criteria

- [ ] `sync-main-to-dev` completes successfully for the same class of trigger (push to `main` that should open/update the sync PR), or any intentional behaviour change is tracked separately.

## Implementation notes

_(None.)_

## Related issues

_(None found for this run id.)_

## Priority

Critical (selected: blocking — `dev` may not receive `main` until this is resolved).

## Changelog category

Fixed (once the workflow is green again).

## Additional context

- **Failing run:** https://github.com/vig-os/devcontainer/actions/runs/23611588823  
  - Workflow: `sync-main-to-dev.yml`  
  - Job **Merge main into dev via PR**: `Process completed with exit code 127`  
  - Annotations also report: `Unexpected input(s) 'install-python'`, with valid inputs listed as `sync-dependencies`, `install-podman`, `install-node`, `node-version`, `install-devcontainer-cli`, `install-hadolint`, `install-just`, `install-taplo`, `install-bats` (steps referencing `setup-env`).

- **Last known successful run (comparison):** https://github.com/vig-os/devcontainer/actions/runs/23060324149 (release 0.3.0 / [PR #270](https://github.com/vig-os/devcontainer/pull/270)).

---

# [Comment #1]() by [c-vigo]()

_Posted on March 27, 2026 at 12:02 PM_

## RCA: sync-main-to-dev failed after push to main (release 0.3.1)

### Summary

The `sync-main-to-dev` workflow failed at the **"Re-check if dev is still behind main"** step (sync job, step 5) with `retry: command not found` (exit 127). Root cause is a **version skew** between `main` and `dev` in the `setup-env` composite action.

### Evidence

#### Failing run (23611588823)

- **Trigger:** push to `main` (release 0.3.1 merge, commit `c639954`)
- **check job:** succeeded (used `setup-env` from `main`)
- **sync job:** failed at step 5 with:
  - Warning: `Unexpected input(s) 'install-python', valid inputs are ['sync-dependencies', 'install-podman', 'install-node', 'node-version', 'install-devcontainer-cli', 'install-hadolint', 'install-just', 'install-taplo', 'install-bats']`
  - Error: `retry: command not found` (exit 127)

#### Key commit

`3aa4f4c` **fix(ci): centralize release retry helper via setup-env** (Refs: #365):

- Added `install-python` input to `.github/actions/setup-env/action.yml`
- Added the `retry()` shell helper function (exported via `BASH_ENV`)
- This commit reached `main` via the release 0.3.1 PR (#342)
- **Was NOT on `dev` before the sync** (confirmed: `git merge-base --is-ancestor 3aa4f4c 6b611c1` returns NO, where `6b611c1` is the dev-side parent of the manual sync merge `458d01b`)

#### Version skew mechanism

The `sync-main-to-dev.yml` workflow file on `main` references features that only exist in `main`'s `setup-env`:

- **check job:** default checkout → `main` code → `setup-env` from `main` → has `install-python` and `retry` → works
- **sync job:** explicit `ref: dev` checkout → `setup-env` from `dev` → `dev`'s `setup-env` lacks `install-python` and `retry` → `retry: command not found` → exit 127

This is a **chicken-and-egg problem**: the workflow that syncs `main` to `dev` depends on features that only exist on `main` and have not been synced to `dev` yet.

#### Why 0.3.0 succeeded (run 23060324149)

At that time, the sync workflow did not use `retry` or `install-python`. Those were added during the 0.3.1 cycle on a bugfix branch that went directly to `main`, never passing through `dev`.

### Fix direction

The `sync` job should not depend on `setup-env` features that might not exist on `dev`. Options:

1. **Remove `setup-env` from the `sync` job** — it only needs `git` and `gh` (both pre-installed on `ubuntu-22.04`). Inline a minimal retry function or remove retry wrappers for simple git/gh commands.
2. **Inline the `retry` helper** directly in `sync-main-to-dev.yml` so it does not depend on the checked-out `setup-env`.
3. **Run `setup-env` from `main` before checking out `dev`** (add a second checkout step).

Option 1 is the cleanest since the sync job genuinely does not need Python, uv, just, or other tools from `setup-env`.

