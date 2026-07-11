---
type: issue
state: closed
created: 2026-07-08T12:28:38Z
updated: 2026-07-08T14:14:50Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/929
comments: 2
labels: feature, area:workspace, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:22.952Z
---

# [Issue 929]: [[FEATURE] Language-neutral scaffold: drop the shipped Python package starter](https://github.com/vig-os/devkit/issues/929)

## Description

Make the copied project scaffold (`assets/workspace/`) **language-neutral** by
removing the shipped Python **package** starter and guarding the Python task
recipes so they no-op on a repo with no `pyproject.toml`.

## Problem Statement

The scaffold has always shipped a Python package starter — `pyproject.toml`,
`src/template_project/`, `tests/test_example.py` — plus uv/ruff/pytest recipes,
and a CI contract (`just sync|precommit|test`) that assumes a Python project.

Many `vig-os`/EXOMA consumers are **not** Python packages (Rust `scitadel`, the
TypeScript actions, `nvd-mirror`). For them the starter is wrong: they must
delete files and edit recipes, and — worse — their CI **fails out of the box**
because `just test` runs `uv run pytest`, which exits `5` ("no tests collected")
with no project.

Delivery modes (`devcontainer|direnv|both|bare`) control *how* the scaffold is
delivered, not *what language* — all four rsync the same Python-laden template.
The Python starter predates the capability-modules design (#884) and the flake
`nix flake init -t` template mechanism, which are the intended language axis.

## Proposed Solution

1. **Delete** the Python package starter from `assets/workspace/`:
   `pyproject.toml`, `src/` (`src/template_project/`), `tests/`.
2. **Guard** the Python recipes in `assets/workspace/justfile.project` the same
   way `sync` already is (`@if [ -f pyproject.toml ]; then …; fi`): `lint`,
   `format`, `test`, `test-cov`. They then exit 0 with no `pyproject.toml`,
   keeping both CI contracts (`assets/workspace/.github/workflows/ci.yml` and
   `assets/workspace-bare/.github/workflows/ci.yml`) green on non-Python repos.
   `precommit` (prek) needs no guard (ruff hooks match nothing → pass).
3. **`assets/init-workspace.sh`**: drop the `src/template_project`→`src/${SHORT_NAME}`
   rename and the `tests/test_example.py` import-rewrite. Keep `pyproject.toml`
   in `PRESERVE_FILES` (the #738 "consumer owns its own pyproject" guarantee
   still holds), and keep `CI_CONTRACT_RECIPES` + the base-recipe re-append
   (recipes still exist, just self-guarded).
4. Update tests (`test_install_script.py`, `test_image.py`, `test_integration.py`,
   `tests/bats/init-workspace.bats`), `docs/MIGRATION.md`, the generated README
   template, and `CHANGELOG.md`.

Investigated and cleared: the image build does **not** break (the scaffold `.venv`
is prebaked with `python -m venv`, not `uv sync`; it never reads `pyproject.toml`),
and `just sync-workspace`/`sync_manifest.py` will **not** re-add the Python files
(it copies only files listed in `scripts/manifest.toml`, which lists none of them).

## Alternatives Considered

- **Multiple bootstrap templates** (`--template python|rust|ts`): rejected — it
  duplicates the standards layer N times and reintroduces exactly the drift the
  `nix/hooks.nix` SSoT work removed.
- **Keep status quo, document the deletion steps**: rejected — leaves broken CI
  on adoption for every non-Python repo.

## Impact

- **Who benefits:** every non-Python consumer (clean scaffold, green CI on
  adoption); Python consumers restore the starter via the opt-in `#python`
  flake template (companion issue).
- **Compatibility:** backward-compatible / `semver:minor`. Existing consumers
  keep their own preserved `pyproject.toml` (preservation is generic). Behavior
  change: a fresh scaffold no longer contains a Python package, and
  `just lint/format/test` no-op without a `pyproject.toml`.
- **Ships in the same release as the companion `#python` template** so Python
  users always have a restore path.

## Changelog Category

Changed (also a Removed entry for the dropped starter).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 12:28 PM_

Companion: #930 (opt-in Python starter flake template). Both should land in the same release so Python consumers always have a restore path.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 02:14 PM_

Done — merged into `dev` via #933 (merge `bcb08633`). The copied scaffold is now language-neutral: the Python package starter (`pyproject.toml`, `src/`, `tests/`) is gone and `just lint/format/test/test-cov` no-op (exit 0) without a `pyproject.toml`, so non-Python repos scaffold clean and their CI/release `just test` steps stay green. Python is opt-in via #930. Ships in 0.5.

