---
type: issue
state: open
created: 2026-02-23T08:07:17Z
updated: 2026-02-23T08:07:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/161
comments: 0
labels: bug, area:ci, area:workspace, effort:medium, semver:patch
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-24T04:24:08.252Z
---

# [Issue 161]: [[BUG] vig-utils pre-commit hooks fail in deployed workspace CI](https://github.com/vig-os/devcontainer/issues/161)

## Problem

The workspace template `.pre-commit-config.yaml` contains local hooks whose `entry` calls `uv run <command>` where the command is a CLI entry point from `vig-utils`:

- **`check-action-pins`** (L104-109) — `uv run check-action-pins`
- **`validate-commit-msg`** (L131-146) — `uv run validate-commit-msg`

`vig-utils` is a local path dependency (`packages/vig-utils`, editable) that only exists in the devcontainer repo. When the `.pre-commit-config.yaml` is deployed to downstream projects via `sync_manifest.py`, these commands don't exist — there is no `check-action-pins` or `validate-commit-msg` package on PyPI for `uv run` to resolve.

**Result:** The CI lint job (`uv run pre-commit run --all-files`) in any deployed workspace will fail on these two hooks.

## Other hooks with similar issues

Auditing all `repo: local` hooks in the workspace template for CI portability:

| Hook | Entry | Issue |
|---|---|---|
| `check-action-pins` | `uv run check-action-pins` | **vig-utils CLI** — not installable in downstream |
| `validate-commit-msg` | `uv run validate-commit-msg` | **vig-utils CLI** — not installable in downstream |
| `pip-licenses` | `uv run pip-licenses` | PyPI package — `uv run` may auto-resolve, but fragile |
| `bandit` | `uv run bandit` | PyPI package — `uv run` may auto-resolve, but fragile |
| `just-fmt` | `just --fmt --unstable` | OK — `setup-env` action installs `just` by default |
| `check-skill-names` | `scripts/check-skill-names.sh` | Script not synced to downstream; but only triggers on `.cursor/skills/` which may not exist |

The `pip-licenses` and `bandit` hooks may work if `uv run` falls back to tool-resolution mode, but this depends on uv version and configuration. They are not in the workspace template's `pyproject.toml` dependencies either.

## Options

### 1. Skip affected hooks in CI

Add `SKIP=check-action-pins,validate-commit-msg` to the CI workflow.

- **Pros:** Zero effort, immediate fix
- **Cons:** Loses CI enforcement entirely; hooks only protect local commits; easy to bypass

### 2. Publish vig-utils as a standalone PyPI package

Make vig-utils installable from PyPI (or a private index) so `uv run check-action-pins` resolves.

- **Pros:** Clean dependency model; version-pinnable; `uv run` just works
- **Cons:** Publishing overhead; needs PyPI account or private index; versioning and release process for a small internal package; overkill for ~450 LOC of stdlib-only code

### 3. Move CI-necessary scripts into `.github/`

Ship `check_action_pins.py` and `validate_commit_msg.py` as standalone scripts under `.github/scripts/` in the workspace template. Change pre-commit entries to `python .github/scripts/check_action_pins.py`.

- **Pros:** Self-contained in every project; works in CI and locally; no external deps
- **Cons:** Two copies of the logic (vig-utils for devcontainer repo, standalone scripts for downstream); SSoT risk unless sync_manifest generates/copies from vig-utils source

### 4. Ship as standalone scripts via sync manifest

Add the vig-utils modules to the sync manifest as standalone scripts (e.g., `scripts/check_action_pins.py`). Change pre-commit entry from `uv run check-action-pins` to `python scripts/check_action_pins.py`. Since both tools are pure stdlib Python (~152 and ~307 LOC), no dependencies are needed.

- **Pros:** Works everywhere; SSoT maintained via sync; no publishing overhead; no external deps
- **Cons:** Need to restructure modules to be importable as both package entry points and standalone scripts (add `if __name__ == "__main__"` guards); sync manifest grows; entry point style differs between devcontainer repo and downstream

### 5. Convert to a pre-commit hook repository

Add a `.pre-commit-hooks.yaml` to a dedicated repo (or vig-utils itself). Downstream projects reference it as `repo: https://github.com/...`. Pre-commit installs hooks in isolated environments automatically.

- **Pros:** Idiomatic pre-commit pattern; automatic environment management; version-pinned via git SHA
- **Cons:** Requires vig-utils to be a standalone installable repo (not a subdirectory); repo must be accessible from CI; more complex setup; effectively a variant of option 2

### 6. Use `language: python` hooks with `additional_dependencies`

Change the hooks from `language: system` to `language: python` and specify `additional_dependencies: [vig-utils @ git+https://...]` (if the repo is accessible).

- **Pros:** Pre-commit manages the virtualenv; clean
- **Cons:** Requires repo access from CI; git URL dependency pinning is fragile; sub-package path not supported by pre-commit

## Recommendation

**Short-term:** Option 1 (skip in CI) to unblock deployments immediately.

**Medium-term:** Option 4 (standalone scripts via sync) — restructure the two vig-utils tools to work both as package entry points and as standalone scripts. The sync manifest copies them to `scripts/` in downstream projects.

**Long-term:** Option 5 (pre-commit hook repo) if/when vig-utils is extracted to its own repository, which would also cleanly solve option 2.

## Acceptance criteria

- [ ] Deployed workspace CI lint job passes without manual `SKIP` workarounds
- [ ] `check-action-pins` and `validate-commit-msg` run in both devcontainer repo and downstream projects
- [ ] No SSoT violation — logic lives in one place
