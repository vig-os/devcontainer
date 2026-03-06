---
type: issue
state: open
created: 2026-02-24T16:29:46Z
updated: 2026-02-24T16:45:50Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/186
comments: 3
labels: bug, area:image, area:workspace, effort:small, semver:patch
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-25T04:25:51.927Z
---

# [Issue 186]: [[BUG] Container image missing bandit and check-skill-names.sh for workspace pre-commit hooks](https://github.com/vig-os/devcontainer/issues/186)

## Description

The workspace `.pre-commit-config.yaml` (deployed from `assets/workspace/`) contains two `local` hooks that fail inside the devcontainer because their dependencies are not available:

1. **`bandit`** — `entry: uv run bandit -r src/ -ll` fails because `bandit` is not installed system-wide in the Containerfile. The system pip install (Containerfile L176-180) installs `pre-commit`, `rich`, `ruff`, and `pip-licenses` but omits `bandit`.
2. **`check-skill-names`** — `entry: scripts/check-skill-names.sh .cursor/skills` fails because the script only exists in the devcontainer repo (`scripts/check-skill-names.sh`), not in the deployed workspace. There is no `assets/workspace/scripts/` directory.

## Steps to Reproduce

1. Bootstrap a fresh project using the standard setup:
   ```bash
   mkdir test-project && cd test-project
   curl -fsSL https://raw.githubusercontent.com/vig-os/devcontainer/dev/scripts/bootstrap.sh | bash
   ```
2. Open the devcontainer
3. Make any change to a Python file or `.cursor/skills/` and attempt to commit

## Expected Behavior

All pre-commit hooks pass (or are skipped if no matching files exist).

## Actual Behavior

```
bandit (Python security linting).........................................Failed
- hook id: bandit
- exit code: 2
error: Failed to spawn: `bandit`
  Caused by: No such file or directory (os error 2)

check-skill-names (enforce naming convention)............................Failed
- hook id: check-skill-names
- exit code: 1
Executable `/workspace/<project>/scripts/check-skill-names.sh` not found
```

## Environment

- **OS**: Any (reproducible on macOS host + Debian Bookworm container)
- **Container Runtime**: Podman or Docker
- **Image Version/Tag**: `:dev` built from current `dev` branch

## Possible Solution

1. Add `bandit` to the system-wide pip install in the Containerfile (alongside `pip-licenses`)
2. Copy `scripts/check-skill-names.sh` into `assets/workspace/scripts/` so `init-workspace.sh` deploys it

## Additional Context

Related to #161 which covers the `vig-utils` CLI hooks (`check-action-pins`, `validate-commit-msg`). This issue is narrower — the tools here are either standard PyPI packages or repo scripts that simply need to be included in the image/workspace.

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] `bandit` is available in the container image
- [ ] `scripts/check-skill-names.sh` is deployed to the workspace
- [ ] All pre-commit hooks pass in a freshly deployed workspace
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 24, 2026 at 04:32 PM_

## Design

**Problem**: Two pre-commit hooks fail in freshly deployed workspaces because their dependencies are missing from the container image and workspace template.

**Root causes**:
1. **bandit** — The hook uses `uv run bandit -r src/ -ll`. The workspace template has no bandit in pyproject.toml, and the container image does not install bandit system-wide. Unlike pip-licenses (which is installed in the Containerfile), bandit is omitted.
2. **check-skill-names** — The hook invokes `scripts/check-skill-names.sh .cursor/skills`. The script exists only in the devcontainer repo root (`scripts/check-skill-names.sh`), not in `assets/workspace/`. The sync manifest (`scripts/manifest.toml`) does not copy it, so deployed workspaces lack the script.

**Solution** (aligned with issue proposed solution):

1. **Add bandit to Containerfile** — Extend the existing `uv pip install --system` block (L176–180) to include `bandit`, alongside pre-commit, rich, ruff, and pip-licenses. Use the same pattern as pip-licenses. Add a version test in `tests/test_image.py` (similar to `test_pip_licenses_installed`).

2. **Add check-skill-names.sh to workspace manifest** — Add a manifest entry in `scripts/manifest.toml` to copy `scripts/check-skill-names.sh` to `assets/workspace/scripts/check-skill-names.sh`. Run `just sync-workspace` so the file appears in the workspace template. The pre-commit hook already references `scripts/check-skill-names.sh` relative to the workspace root, so no hook change is needed.

**Data flow**:
- Containerfile change → bandit available on PATH in container
- Manifest + sync → `assets/workspace/scripts/check-skill-names.sh` exists → bootstrap/init deploys it to project root `scripts/`

**Testing strategy**:
- **bandit**: Add `test_bandit_installed` in `tests/test_image.py` (RED first, then GREEN per TDD).
- **check-skill-names**: The script is already covered by `tests/bats/skill-naming.bats`. Verification: run `just sync-workspace` and confirm `assets/workspace/scripts/check-skill-names.sh` exists; pre-commit in a fresh workspace will pass.

**Constraints**:
- Minimal diff; no refactors.
- TDD: test before implementation for bandit.
- Traceability: Refs #186 in all commits.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 24, 2026 at 04:32 PM_

## Implementation Plan

Issue: #186
Branch: bugfix/186-missing-bandit-and-check-skill-names

### Tasks

- [x] Task 1: Add test_bandit_installed to tests/test_image.py (RED) — `tests/test_image.py` — verify: `just test tests/test_image.py -k bandit` fails
- [x] Task 2: Add bandit to Containerfile uv pip install — `Containerfile` — verify: `just test-image` passes (bandit test green)
- [x] Task 3: Add check-skill-names.sh to manifest.toml — `scripts/manifest.toml` — verify: `just sync-workspace` and `test -f assets/workspace/scripts/check-skill-names.sh`
- [x] Task 4: Update CHANGELOG.md under Unreleased — `CHANGELOG.md` — verify: grep -A2 "## Unreleased" CHANGELOG.md shows Fixed entry for #186

---

# [Comment #3]() by [gerchowl]()

_Posted on February 24, 2026 at 04:45 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (4 tasks)
- Execute: all tasks done
- Verify: all checks pass (just test, just lint; precommit passes with hadolint skipped locally due to Docker not running)
- PR: https://github.com/vig-os/devcontainer/pull/188
- CI: pending — no checks reported yet on branch; workflows may have delayed trigger. Please verify CI status on the PR.

