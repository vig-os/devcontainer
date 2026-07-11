---
type: issue
state: closed
created: 2026-06-24T16:18:52Z
updated: 2026-06-30T07:42:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/698
comments: 2
labels: bug, priority:medium, area:workflow, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:03.620Z
---

# [Issue 698]: [[BUG] pre-commit: make the pymarkdown hook (pyjson5 C-extension / libstdc++) run on NixOS](https://github.com/vig-os/devkit/issues/698)

## Description

Follow-up to #697. The `pymarkdown` pre-commit hook also fails on a NixOS host,
but it is a different failure class than the standalone Rust binaries: it is a
pure-Python tool whose dependency `pyjson5` ships a **C extension** that needs
`libstdc++.so.6` on the loader path, which a NixOS host does not provide outside
an FHS/`nix develop` environment.

This is split from #697 because the standalone binaries (`ruff`, `typos`) have
drop-in `nixpkgs` packages, whereas `pymarkdown` does not — so it needs its own
investigation and decision.

## Evidence

```
$ uv run pre-commit run pymarkdown --all-files
  File ".../pyjson5/__init__.py", line 1, in <module>
    from .pyjson5 import *
ImportError: libstdc++.so.6: cannot open shared object file: No such file or directory
```

`pymarkdown` is **not** packaged in `nixpkgs` (`pymarkdown` /
`python3Packages.pymarkdownlnt` both absent), so the simple "add to `devTools` +
`language: system`" recipe from #697 does not apply directly.

## Options to investigate

1. **Provide `libstdc++` to the loader in the dev-shell** — add
   `pkgs.stdenv.cc.cc.lib` and set `LD_LIBRARY_PATH` (or `NIX_LD_LIBRARY_PATH`)
   in `mkProjectShell` so the existing manylinux `pyjson5` wheel resolves its
   C library. Smallest change; keeps the upstream `rev:` pin; mildly impure.
2. **Package `pymarkdown` in the flake** — `buildPythonApplication` from the
   PyPI sdist with `pyjson5` taken from `nixpkgs` (`python3Packages.pyjson5`,
   built against the Nix `libstdc++`), exposed as a `pymarkdown` binary, then a
   `language: system` hook. Most hermetic / SSoT-aligned; most work; adds a
   version to maintain.
3. **`nix-ld` (host-level)** — `programs.nix-ld.enable` with
   `libraries = [ pkgs.stdenv.cc.cc ]` makes the wheel work unchanged. Not
   repo-enforceable (per-contributor system config); document as fallback. See
   the alternative discussion in #697.
4. **Drop/replace `pymarkdown`** — only if markdown linting can move to a
   Nix-friendly tool without losing the `.pymarkdown` config behaviour
   (likely undesirable; listed for completeness).

**Leaning:** Option 1 as the pragmatic unblock (and it generalises to any future
C-extension Python hook), with Option 2 as the hermetic end-state if we want
`pymarkdown` fully off upstream wheels. Confirm during execution.

## Acceptance criteria

- [ ] `pre-commit run pymarkdown --all-files` passes in the dev-shell on a NixOS
      host (no `--no-verify`)
- [ ] Chosen mechanism documented in `docs/NIX.md`
- [ ] CI project-checks job stays green
- [ ] If the dev-shell gains `libstdc++`/`LD_LIBRARY_PATH`, a dev-shell parity
      test asserts it (mirrors the existing `UV_PYTHON`/`BATS_LIB_PATH` tests)

## Relationship

- Completes "pre-commit fully NixOS-compatible" together with #697.
- Independent of the `prek` runner migration (#40).

Refs: #625

---

# [Comment #1]() by [c-vigo]()

_Posted on June 24, 2026 at 05:01 PM_

Fixed and merged into the epic branch `feature/625-nix-claude-migration` via #700 (merge `77a8f4a`). Verified in the dev-shell: `pre-commit run pymarkdown` passes (the `pyjson5` C extension resolves `libstdc++` via the dev-shell `LD_LIBRARY_PATH`). Left open to match the epic's sub-issue convention (cf. #695).

---

# [Comment #2]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #700 (c59f932) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

