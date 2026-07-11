---
type: issue
state: closed
created: 2026-07-08T13:41:47Z
updated: 2026-07-08T14:14:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/934
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:21.807Z
---

# [Issue 934]: [Renovate pins requires-python, reverting the Nix range migration](https://github.com/vig-os/devkit/issues/934)

## Problem

The shared `renovate-default` preset (`assets/workspace/.github/renovate-default.json`) applies `rangeStrategy: pin` to the `pep621` manager ("Python (PEP 621) — always pin ranges"). This pins **every** range, including `requires-python`.

Since the Nix migration (c7839602, Refs #666) deliberately set `requires-python = ">=3.14,<3.15"` as a **range** — because the Nix toolchain pins the exact interpreter via `flake.lock`, making an `==` pin redundant and *unsatisfiable against nixpkgs* — Renovate keeps regenerating a PR to pin it back (e.g. #861, now closed).

## Fix

Scope the `pep621` pin so it no longer manages the `python` interpreter constraint, while still pinning real package dependencies. Land in the shared preset so all consumers inherit it.

## Notes
- #861 closed as the symptom.
- Preset resolves from the repo default branch (`main`), so the fix is only fully effective for Renovate once promoted to main.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 02:14 PM_

Resolved by #935 (merged to `dev`, commit 7710e00c). The shared `renovate-default` preset now exempts `requires-python` from the pep621 pin rule, so Renovate no longer regenerates the python-pin PR (#861). Full effect once promoted to `main`, where Renovate resolves the preset.

