---
type: issue
state: open
created: 2026-02-20T23:44:19Z
updated: 2026-02-20T23:44:19Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/134
comments: 0
labels: chore, area:ci
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:16.419Z
---

# [Issue 134]: [[CHORE] Granular CODEOWNERS for scripts/ — per-file ownership by concern](https://github.com/vig-os/devcontainer/issues/134)

## Problem

`scripts/` has a single blanket CODEOWNERS rule (`@c-vigo`), but the directory contains scripts serving different concerns:

- **Build/release** (security-sensitive): `build.sh`, `prepare-build.sh`, `clean.sh`, `sync_manifest.py`, `utils.py`
- **Developer tooling**: `gh_issues.py`, `setup-labels.sh`, `resolve-branch.sh`
- **Dev environment setup**: `init.sh`, `requirements.yaml`

Touching any script — even a developer convenience tool like `gh_issues.py` — triggers a review from the build/release owner, adding unnecessary friction.

## Solution

Replace the `scripts/` wildcard CODEOWNERS rule with per-file rules that assign ownership by concern:

| Pattern | Owner | Reason |
|---|---|---|
| `scripts/build.sh` | `@c-vigo` | Build/release |
| `scripts/prepare-build.sh` | `@c-vigo` | Build/release |
| `scripts/clean.sh` | `@c-vigo` | Build/release |
| `scripts/sync_manifest.py` | `@c-vigo` | Build/release |
| `scripts/utils.py` | `@c-vigo` | Build/release |
| `scripts/gh_issues.py` | `@gerchowl` | Developer tooling |
| `scripts/setup-labels.sh` | `@gerchowl` | Developer tooling |
| `scripts/resolve-branch.sh` | `@gerchowl` | Developer tooling |
| `scripts/init.sh` | `@c-vigo` | Dev environment |
| `scripts/requirements.yaml` | `@c-vigo` | Dev environment |

## Acceptance criteria

- [ ] `scripts/` wildcard removed from CODEOWNERS
- [ ] Per-file rules added per table above
- [ ] CODEOWNERS passes validation (no syntax errors)
