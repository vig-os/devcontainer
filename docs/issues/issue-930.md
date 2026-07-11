---
type: issue
state: closed
created: 2026-07-08T12:28:41Z
updated: 2026-07-08T14:14:53Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/930
comments: 2
labels: feature, area:workspace, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:22.494Z
---

# [Issue 930]: [[FEATURE] Opt-in Python starter as a flake template (nix flake init -t ...#python)](https://github.com/vig-os/devkit/issues/930)

## Description

Ship an **opt-in Python project starter** as a flake template, so a consumer who
*does* want a Python package can restore one with
`nix flake init -t github:vig-os/devcontainer#python`.

## Problem Statement

Companion to the language-neutral scaffold change (the copied scaffold no longer
ships `pyproject.toml`/`src/`/`tests/`). Python consumers — still the majority —
need a first-class, single-sourced way to get the Python package layout back
without hand-writing `pyproject.toml`/`src/`/`tests/` or running bare `uv init`.

## Proposed Solution

Add `templates/python/` mirroring the existing `templates/personal/`
(`flake.nix`-registered `nix flake init -t` template):

- `templates/python/pyproject.toml` — minimal: hatchling build,
  `requires-python = ">=3.14,<3.15"`, `dev = [pytest, pytest-cov]` pinned to the
  image versions. Drops the heavy `science`/`jupyter` extras of the old scaffold.
- `templates/python/src/example_pkg/__init__.py`, `tests/__init__.py`,
  `tests/test_example.py`.
- `templates/python/README.md` — usage + the rename step.

Uses a **concrete** package name (`example_pkg`) the user renames, because
`nix flake init -t` performs **no** token substitution (unlike the
`init-workspace.sh` scaffold path). Register in `flake.nix` next to
`templates.personal`:

```nix
templates.python = {
  path = ./templates/python;
  description = "Opt-in Python project starter (pyproject + src/ + pytest)";
};
```

Add `test_python_template_is_exposed` (mirroring `test_personal_template_is_exposed`)
and a one-line pointer in the generated README / `docs/MIGRATION.md`.

## Alternatives Considered

- Fold into a `--template` selector in `install.sh`: rejected — see the
  companion issue; duplicates the standards layer and fights SSoT.
- Leave users to `uv init` by hand: workable but loses the vig-os-consistent
  pin set and the single-sourced starter.

## Impact

- **Who benefits:** Python consumers (one-command restore of the package layout).
- **Compatibility:** purely additive / `semver:minor`. No change to existing
  scaffolded repos.
- **Ships in the same release as the language-neutral scaffold change** so there
  is never a window without a restore path.

## Changelog Category

Added.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 12:28 PM_

Companion: #929 (language-neutral scaffold — removes the shipped Python starter). Both should land in the same release.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 02:14 PM_

Done — merged into `dev` via #933 (merge `bcb08633`). `nix flake init -t github:vig-os/devcontainer#python` restores an opt-in Python package layout (pyproject + src/ + pytest) onto the now language-neutral scaffold (#929). Ships in 0.5.

