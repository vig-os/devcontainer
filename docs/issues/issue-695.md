---
type: issue
state: open
created: 2026-06-24T15:52:47Z
updated: 2026-06-24T15:55:19Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/695
comments: 0
labels: bug, area:testing, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:55.512Z
---

# [Issue 695]: [[BUG] BATS suite fails locally on Nix branch: bats helper libs unresolved (node_modules not installed)](https://github.com/vig-os/devcontainer/issues/695)

## Description

All 246 BATS tests fail at `load test_helper` in the local Nix dev shell, with:

```
Could not find library 'bats-support' relative to test file or in BATS_LIB_PATH
```

The failure is environmental, not a problem with the tests themselves — every `.bats` file errors during `setup()` before any assertion runs.

## Root cause

`tests/bats/test_helper.bash` resolves the BATS helper libraries (`bats-support`, `bats-assert`, `bats-file`) in three steps:

1. `node_modules/bats-support` (local dev)
2. `/usr/lib/bats-support` (CI via `bats-core/bats-action`)
3. `bats_load_library` fallback (needs `BATS_LIB_PATH`)

On the Nix-migration branch none of these resolve locally:

- **`node_modules/` is never populated.** The helper libs are declared as npm deps in `package.json`, but the Nix-first `just init` / dev-shell flow no longer runs `npm install`/`npm ci`. `just test-bats` invokes `npx bats`, which auto-fetches only `bats-core` into the npx cache — not the three helper libraries.
- **`/usr/lib/bats-*` is gone** — that path was the Debian build path, decommissioned in this migration (1d4e9db).
- **`BATS_LIB_PATH` is unset** in the dev shell, so the `bats_load_library` fallback also fails.

CI is unaffected: `.github/actions/setup-env` installs the libs to `/usr/lib` via `bats-core/bats-action` and exports `BATS_LIB_PATH`, and `test-project` runs the `bats` binary directly. The gap is local-only.

## Steps to Reproduce

1. Enter the Nix dev shell on `feature/625-nix-claude-migration` with no `node_modules/` present.
2. Run `just test-bats` (or `npx bats tests/bats/`).
3. Every test errors with the `bats-support` not-found message.

## Expected Behavior

`just test-bats` runs the suite locally in the Nix dev shell without manual setup.

## Actual Behavior

246 tests, 246 failures — all fail in `setup()` at `load test_helper` because the helper libraries cannot be found.

## Environment

- **OS**: NixOS (Nix dev shell)
- **Branch**: `feature/625-nix-claude-migration`
- **bats**: via `npx bats` (1.13.0 from `package.json`); `bats` not on `PATH`, not in the flake
- `node_modules/` absent; `BATS_LIB_PATH` empty

## Verification

Running `npm ci` populates `node_modules/{bats,bats-support,bats-assert,bats-file}`; afterwards the first resolution branch in `test_helper.bash` succeeds and the suite passes (e.g. `worktree-claude-cli.bats` → 5/5 ok). This confirms the diagnosis.

## Possible Solution

Pick one (the migration intent should decide):

1. **Add bats + helper libs to the flake** (consistent with "Nix-first" for the rest of the toolchain) and have `test_helper.bash` resolve them via `BATS_LIB_PATH`/Nix store. Removes the npm dependency for local testing.
2. **Make `just test-bats` (or `just init`) ensure `node_modules` is installed** (`npm ci`) before running, keeping the existing npm-based resolution. Lowest-effort; matches the current `package.json` comment that BATS "keeps its npm config".

Option 1 aligns better with the #625 migration goal; option 2 is a quick unblock.

## Changelog Category

Fixed

Refs: #625

