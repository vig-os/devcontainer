---
type: issue
state: closed
created: 2026-06-23T20:46:21Z
updated: 2026-07-01T11:19:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/666
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:09.574Z
---

# [Issue 666]: [T2.4 — Nix image toolchain parity: pass the full testinfra suite](https://github.com/vig-os/devkit/issues/666)

## Context

Tracking: #625. The Nix-built image (T2.1 #634) builds and is multi-arch (#636), and the testinfra
suite was made portable (#635), but the image still **fails 32 of 63 `tests/test_image.py` tests**
(the discovery phase left `nix-image.yml` `continue-on-error`). Completing the switch (Nix-only,
#642) requires the full image suite to pass on the Nix image first.

## Root causes

- **Python toolchain absent + version conflict (~26):** `requires-python = "==3.14.6"` is
  unsatisfiable on nixpkgs-26.05 (3.14.4), so `uv sync` fails; and `vig-utils` + `ruff`/`bandit`/
  `pre-commit`/`pip-licenses` aren't in the image (the Debian image baked them via `uv pip install`
  at build, which a hermetic Nix build can't do).
- **Missing tools (3):** `cargo-binstall`, `just-lsp`, `typstyle`.
- **Version-assertion tests:** pin Debian-era versions of nixpkgs-sourced tools.

## Plan (Nix-native)

- Relax `requires-python` to `>=3.14,<3.15` (root, `packages/vig-utils`, `assets/workspace`); the
  `flake.lock` is the reproducibility anchor now. Regenerate `uv.lock`. Drop the
  `UV_PYTHON_DOWNLOADS_JSON_URL` managed-CPython workaround.
- `flake.nix`: package `vig-utils` as a `buildPythonPackage` into a `python314.withPackages` env so
  `import vig_utils` + its console scripts work; add `ruff`/`bandit`/`pip-licenses` +
  `cargo-binstall`/`just-lsp`/`typstyle` from nixpkgs.
- Adapt `tests/test_image.py` to the #635 presence-not-version pattern for nixpkgs-sourced tools; the
  pre-commit cache test asserts the dir exists (hermetic builds can't pre-fetch hook repos).

## Acceptance criteria

- `tests/test_image.py` passes 63/63 on the Nix image; `nix-image.yml` testinfra is a real gate.
- No regression to the dev-shell (`nix develop`) or the multi-arch build.

Refs: #625, #634, #635
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30) + PR #667 (commit 142e405f). The Nix image passes the full `test_image.py` suite (63/63) and `nix-image.yml` is a real gate (not `continue-on-error`). Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

