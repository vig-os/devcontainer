---
type: issue
state: closed
created: 2026-06-26T08:14:20Z
updated: 2026-07-03T07:46:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/720
comments: 1
labels: priority:low, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:58.953Z
---

# [Issue 720]: [ci: automate the uv version sync between flake.nix and setup-env](https://github.com/vig-os/devkit/issues/720)

## Context

Follow-up from #625 / PR #670. The `uv` version is hardcoded in two places that must move in lockstep with the nixpkgs `uv`:

- `flake.nix` — the Python-downloads metadata URL pins `astral-sh/uv/<version>` (currently `0.11.23`).
- `.github/actions/setup-env/action.yml` — pins the same version string.

If the nixpkgs `uv` advances and these are not bumped together, the download-metadata URL goes stale.

## Proposed work

- Derive the version from a single source (e.g. read it from the nixpkgs `uv` at build time), or add a Renovate rule / CI check that keeps the two pins in sync.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 07:46 AM_

Resolved by #801 (merged to `dev`). Reframed from 'automate the uv version sync' to eliminating the drift at its root: CI now provisions every job from the flake and the second, hardcoded `uv` pin in `setup-env` was deleted, so the version flows from a single source (`flake.lock` via `pkgs.uv.version`).

