---
type: issue
state: open
created: 2026-06-24T16:18:19Z
updated: 2026-06-24T17:01:19Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/697
comments: 1
labels: bug, priority:high, area:workflow, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:55.166Z
---

# [Issue 697]: [[BUG] pre-commit: source binary hooks (ruff, ruff-format, typos) from the flake for NixOS compatibility](https://github.com/vig-os/devcontainer/issues/697)

## Description

On a NixOS host, `pre-commit run` / `git commit` cannot run several hooks because
their tools are distributed as generic-linux (manylinux) binaries that NixOS
cannot execute out of the box (no FHS `ld-linux`, no `libstdc++.so.6` on the
loader path). This forces `--no-verify` for every local commit on NixOS — the
exact friction hit while landing #695.

This issue covers the **standalone-binary** hooks, which have clean Nix-native
replacements. The Python C-extension case (`pymarkdown`) is split into a
follow-up because it needs a different mechanism (see Refs).

## Affected hooks (empirically confirmed on a NixOS host)

`pre-commit run <hook> --all-files`, outside an FHS environment:

| Hook | Source | Result | Cause |
|------|--------|--------|-------|
| `ruff`, `ruff-format` | `astral-sh/ruff-pre-commit` | **BROKEN** | Rust manylinux wheel; `Could not start dynamically linked executable` |
| `typos` | `crate-ci/typos` | **BROKEN** | Rust manylinux wheel; same |
| `shellcheck` | `shellcheck-py` | OK | statically linked binary — no change needed |
| `check-*`, `trailing-whitespace`, `yamllint` | pure-Python repos | OK | no native deps |
| all `repo: local` (`taplo`, `just`, `nixfmt`, `uv run …`) | `language: system` | OK | resolved from the flake dev-shell |

So the broken-and-fixable-here set is **`ruff`, `ruff-format`, `typos`**.

## Root cause

These hooks pull a compiled binary from a `rev:`-pinned upstream repo as a
manylinux wheel. The binary is dynamically linked against the generic Linux
loader, which does not exist on NixOS. The local `language: system` hooks already
work because they resolve their tool from the Nix dev-shell (the #625 toolchain
SSoT) — that is the pattern to extend.

## Proposed solution (recommended: flake-sourced `language: system`)

Make these hooks resolve their tool from the flake instead of an upstream wheel,
consistent with the #625 "toolchain is the flake SSoT" direction:

1. Add `ruff` and `typos` to `devTools` in `flake.nix` (both are in `nixpkgs`:
   `ruff` 0.15.x, `typos` 1.46.x; `ruff` is already in `imageTools`). The
   per-tool parity test (`tests/test_flake_devshell.py`) covers them automatically.
2. Convert the three hooks to `repo: local` / `language: system`:
   - `ruff` → `entry: ruff check --fix`, `types: [python]`
   - `ruff-format` → `entry: ruff format`, `types: [python]`
   - `typos` → `entry: typos`
   Preserve existing args/filters.
3. Remove the `astral-sh/ruff-pre-commit` and `crate-ci/typos` repo blocks.
4. Confirm CI stays green: `test-project` runs `uv run pre-commit run --all-files`
   under `provision-via-flake`, so `ruff`/`typos` are already on PATH from the flake.
5. Re-sync the scaffolded `.pre-commit-config.yaml` (it is mirrored into
   `assets/workspace/` via `scripts/sync_manifest.py`), so downstream workspaces
   inherit the fix.
6. Update `docs/NIX.md` / `CONTRIBUTE.md`: pre-commit runs inside the dev-shell
   (direnv) and needs no host setup.

**Tradeoff:** hook versions move from upstream `rev:` pins (Renovate
`pre-commit` manager) to `nixpkgs`/`flake.lock` (Renovate `nix` manager). This is
the same SSoT consolidation #625 already applies to the rest of the toolchain.

## Alternative considered — `nix-ld`

Enabling `programs.nix-ld` on the NixOS host (optionally with
`stdenv.cc.cc.lib`) would let the upstream wheels run unchanged, preserving
`rev:` pinning. Rejected as the *primary* fix because it is per-contributor
**system** configuration the repo cannot enforce, and it is impure (relies on
host setup) — counter to the #625 hermetic/SSoT goal. It remains a fine
**documented interim/fallback** and is the likely mechanism for the `pymarkdown`
follow-up.

## Acceptance criteria

- [ ] `ruff`, `ruff-format`, `typos` run via the flake (`language: system`)
- [ ] `ruff` and `typos` added to `devTools`; parity test green
- [ ] `pre-commit run --all-files` passes in the dev-shell on a NixOS host for
      these hooks (no `--no-verify` needed for them)
- [ ] CI project-checks job stays green
- [ ] Scaffolded `assets/workspace/.pre-commit-config.yaml` re-synced
- [ ] Docs note pre-commit runs inside the dev-shell

## Out of scope

- `pymarkdown` (Python C-extension / `libstdc++`) — separate follow-up
- Migrating the pre-commit **runner** to `prek` — tracked in #40
- Nixifying the already-working pure-Python hooks (no compat need)

Refs: #625

---

# [Comment #1]() by [c-vigo]()

_Posted on June 24, 2026 at 05:01 PM_

Fixed and merged into the epic branch `feature/625-nix-claude-migration` via #699 (merge `f30f4f9`). Verified in the dev-shell: `ruff`/`ruff-format`/`typos` hooks pass resolving the flake tools; `ruff` removed from the venv so it is no longer shadowed under `uv run`; `just lint`/`format` repointed to the flake `ruff`. Left open to match the epic's sub-issue convention (cf. #695).

