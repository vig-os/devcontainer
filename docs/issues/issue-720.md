---
type: issue
state: open
created: 2026-06-26T08:14:20Z
updated: 2026-06-26T08:14:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/720
comments: 0
labels: priority:low, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-27T05:58:59.204Z
---

# [Issue 720]: [ci: automate the uv version sync between flake.nix and setup-env](https://github.com/vig-os/devcontainer/issues/720)

## Context

Follow-up from #625 / PR #670. The `uv` version is hardcoded in two places that must move in lockstep with the nixpkgs `uv`:

- `flake.nix` — the Python-downloads metadata URL pins `astral-sh/uv/<version>` (currently `0.11.23`).
- `.github/actions/setup-env/action.yml` — pins the same version string.

If the nixpkgs `uv` advances and these are not bumped together, the download-metadata URL goes stale.

## Proposed work

- Derive the version from a single source (e.g. read it from the nixpkgs `uv` at build time), or add a Renovate rule / CI check that keeps the two pins in sync.

Refs: #625
