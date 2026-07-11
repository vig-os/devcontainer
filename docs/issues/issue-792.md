---
type: issue
state: closed
created: 2026-07-01T07:50:27Z
updated: 2026-07-01T11:20:25Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/792
comments: 1
labels: chore
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:46.077Z
---

# [Issue 792]: [test(flake): statix parity check fails — statix has no top-level --version](https://github.com/vig-os/devkit/issues/792)

## Problem

#777 (PR #790) added `statix` to the `devTools` SSoT. The dev-shell parity test
`tests/test_flake_devshell.py::test_each_tool_runs_in_devshell` invokes every
`devTools` binary with a version flag (default `--version`), but `statix` has no
top-level `--version` (nor `-V`): `statix --version` exits **2** with
`error: unexpected argument '--version' found`. So the parity test fails on
`statix` on every host.

Not currently caught by CI: `project-checks` runs this file only with
`-k "exposes_python3_and_precommit or hook_runner_is_prek or no_nix_cxx_runtime_leak"`,
so `test_each_tool_runs_in_devshell` is not gated — the regression is latent and
bites only a full local parity run.

## Fix

Add a `VERSION_FLAG_OVERRIDES` entry for `statix` (as already done for `expect`
and `tmux`), using `--help` (exits 0, proves the binary is runnable in the
dev-shell — statix exposes no version flag).

Refs: #777
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

Resolved on `dev` by PR #793 (`test: fix statix dev-shell parity check (--help, no top-level --version)`). The statix parity check now uses `--help` (statix has no top-level `--version`).

