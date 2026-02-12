---
type: issue
state: open
created: 2026-02-12T20:16:22Z
updated: 2026-02-12T20:16:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/53
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-12T20:16:40.754Z
---

# [Issue 53]: [[FEATURE] Reduce file duplication and package Python scripts as installable module](https://github.com/vig-os/devcontainer/issues/53)

## Description

Several files in this repository are manually duplicated across `scripts/`, `assets/`, `docs/`, and `assets/workspace/`. Changes must be mirrored by hand, which is error-prone and increases maintenance burden. This issue proposes a consolidated approach.

## Problem Statement

Three categories of duplication exist today:

### 1. Python scripts (`scripts/` vs `assets/`)

`validate_commit_msg.py` (and potentially future utilities) exists in both:
- `scripts/validate_commit_msg.py` — used by the repo's own pre-commit hooks and CI
- `assets/validate_commit_msg.py` — copied into initialized workspaces by `init-workspace.sh`

Any bug fix or feature (e.g. the recent `chore` Refs exemption) must be applied to both files identically.

### 2. Documentation and Cursor rules (repo root vs workspace template)

These files are mirrored between the repo and the workspace template:
- `docs/COMMIT_MESSAGE_STANDARD.md` ↔ `assets/workspace/docs/COMMIT_MESSAGE_STANDARD.md`
- `.cursor/rules/commit-messages.mdc` ↔ `assets/workspace/.cursor/rules/commit-messages.mdc`

### 3. npm dependency not tracked by Dependabot

`@devcontainers/cli` is installed via a raw `npm install -g @devcontainers/cli@0.81.1` in `.github/actions/setup-env/action.yml`. Dependabot's npm ecosystem cannot detect version pins inside YAML files, so this dependency will not receive automated update PRs.

## Proposed Solution

### A. Package Python scripts as an installable module

Extract the shared Python scripts (`validate_commit_msg.py`, `check_action_pins.py`, `prepare-changelog.py`, `utils.py`) into a proper Python package (e.g. `vigos_devtools` or similar). This package would:

- Live in a single location (e.g. `src/vigos_devtools/`)
- Be installed in the container image via `pip install` / `uv pip install` during the build
- Provide CLI entry points (e.g. `vigos-validate-commit`, `vigos-check-pins`) via `pyproject.toml` `[project.scripts]`
- Be copied or installed into initialized workspaces (either as a pip dependency or by `init-workspace.sh`)
- Eliminate the need for `assets/validate_commit_msg.py` entirely

### B. Single-source documentation and rules

- Use `init-workspace.sh` to copy docs/rules from the canonical location at init time, rather than maintaining a second copy in `assets/workspace/`
- Alternatively, keep the template copies but add a CI check that verifies they match the source files (fail if they drift)

### C. Add `package.json` for npm dependency tracking

Add a minimal `package.json` (e.g. in `.github/` or project root) declaring `@devcontainers/cli` as a dependency. Then add an npm ecosystem entry to `.github/dependabot.yml`:

```yaml
  - package-ecosystem: "npm"
    directory: "/"  # or ".github/"
    schedule:
      interval: "weekly"
      day: "monday"
    target-branch: "dev"
    commit-message:
      prefix: "build"
      include: "scope"
```

The `setup-env` action would then read the version from `package.json` instead of hardcoding it.

## Alternatives Considered

- **Symlinks** — Git preserves symlinks, but they break on Windows and complicate container builds.
- **Git submodules** — Overkill for a handful of files within the same repo.
- **Renovate** — Supports regex-based version detection in arbitrary files (would track the npm pin without a `package.json`), but adds another dependency management tool alongside Dependabot.

## Impact

- Eliminates manual mirroring of ~5 files across 2-3 locations
- Reduces risk of silent drift between repo and workspace template
- Enables Dependabot to track the `@devcontainers/cli` version automatically
- Packaging Python scripts as a module enables proper testing, versioning, and reuse across the org
