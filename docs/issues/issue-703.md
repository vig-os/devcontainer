---
type: issue
state: closed
created: 2026-06-25T10:09:15Z
updated: 2026-07-01T11:17:50Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/703
comments: 1
labels: bug, priority:high, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:02.846Z
---

# [Issue 703]: [Nix dev-shell leaks the Nix C++ runtime onto LD_LIBRARY_PATH, breaking `just` on non-NixOS hosts](https://github.com/vig-os/devkit/issues/703)

## Description

Inside the Nix dev-shell (`nix develop` / `direnv`), **every `just` recipe fails
immediately on a non-NixOS (FHS) host** with a glibc symbol-version error:

```
/usr/bin/env: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_ABI_DT_X86_64_PLT' not found
   (required by /nix/store/…-glibc-2.42-67/lib/libm.so.6)
```

Root cause: the dev-shell unconditionally exports
`LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib` (the Nix C++ runtime, linked against
**glibc 2.42**) — added in #698 so the `pymarkdown` pre-commit wheel can resolve
`libstdc++.so.6`. On an FHS host whose **system glibc is older** (Ubuntu 24.04 =
2.39), that Nix `libstdc++` gets pulled into host binaries and drags in the Nix
`libm.so.6` (2.42), which requires the `GLIBC_ABI_DT_X86_64_PLT` symbol version
the host's 2.39 `libc` does not export. The mix of host-`libc` + Nix-`libm`
aborts the load.

Every `just` recipe runs via a `#!/usr/bin/env bash` shebang, so the host
`/usr/bin/env` is the binary that dies — taking down `build`, `test-bats`, and
every other recipe before the body even starts.

The leak only reaches `/usr/bin/env` when something forces `libstdc++` into it;
on this host `/etc/ld.so.preload` (a corporate endpoint agent) does exactly that,
but the underlying defect — injecting a newer-glibc C++ runtime onto a global
`LD_LIBRARY_PATH` seen by host binaries — is host-agnostic.

## Steps to Reproduce

On an FHS host with system glibc older than the flake's Nix glibc (e.g. Ubuntu
24.04):

1. `nix develop`
2. `just build` (or `just test-bats`, or any recipe)

## Expected Behavior

`just` recipes run inside the dev-shell on FHS hosts exactly as they do on NixOS.

## Actual Behavior

Every recipe aborts with `version 'GLIBC_ABI_DT_X86_64_PLT' not found … required
by …/glibc-2.42-…/lib/libm.so.6`. Works on NixOS because there the system glibc
*is* the Nix glibc (no skew), so the same injection is ABI-compatible.

## Environment

- **OS**: Ubuntu 24.04.4 LTS (glibc 2.39); works on a NixOS host (glibc 2.42)
- **Container Runtime**: N/A — this is the `nix develop` dev-shell, not the image
- **Image Version/Tag**: branch `feature/625-nix-claude-migration`
- **Architecture**: x86_64

## Additional Context

Regression from #698 (Nix/Claude migration epic #625). The `LD_LIBRARY_PATH`
injection is only *needed* on NixOS (FHS hosts already have `libstdc++` on the
default loader path) and only *ABI-safe* on NixOS (system glibc == Nix glibc).

## Possible Solution

Gate the Nix C++ runtime injection to NixOS hosts (`[ -e /etc/NIXOS ]`): inject
only where it is both required and ABI-compatible. On every FHS host it becomes a
no-op, so the system `libstdc++` serves the wheel and nothing leaks into host
binaries. Update the #698 dev-shell tests accordingly (the injection becomes
NixOS-only) and add an FHS leak-guard.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:17 AM_

Resolved on `dev` by PR #704 (`fix(setup): gate dev-shell C++ runtime LD_LIBRARY_PATH injection to NixOS`). The dev-shell `LD_LIBRARY_PATH` export is now guarded behind `[ -e /etc/NIXOS ]`, so it is never injected on FHS/non-NixOS hosts, and uses the append-not-clobber form. An FHS-leak guard test was added alongside.

