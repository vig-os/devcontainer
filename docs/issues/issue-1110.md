---
type: issue
state: closed
created: 2026-07-15T10:03:58Z
updated: 2026-07-15T10:58:58Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1110
comments: 1
labels: bug, priority:medium, area:workspace, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-15T11:04:49.120Z
---

# [Issue 1110]: [[BUG] #1093 skew warning extracts the pin from the flake.nix doc-comment — always reports <tag>, false-fires on aligned consumers](https://github.com/vig-os/devkit/issues/1110)

## Summary

The #1093 flake-pin / `DEVKIT_VERSION` skew warning (new in 1.2.1, shipped in `assets/init-workspace.sh`) reads the pinned `vigos` ref from the **wrong line** of the consumer `flake.nix`. It matches the doc-comment *example* line before the real input line, and `head -n1` picks the comment.

Found during **1.2.1-rc1 verification** on the `commit-action` consumer.

## Root cause

`assets/init-workspace.sh` (~line 1120–1122):

```sh
pinned_ref="$(grep -oE 'vigos\.url[[:space:]]*=[[:space:]]*"github:vig-os/devkit\?ref=[^"]+"' \
    "$WORKSPACE_DIR/flake.nix" 2>/dev/null \
    | sed -E 's/.*\?ref=([^"]+)".*/\1/' | head -n1 || true)"
```

The standard-layout consumer `flake.nix` (`assets/workspace/flake.nix`, ~line 13) ships this doc-comment in the `inputs` block:

```
#   vigos.url = "github:vig-os/devkit?ref=<tag>";
```

The un-anchored grep matches that comment line, which sorts **before** the real pin line (~line 16), so `head -n1` returns `<tag>`.

## Consequences

(a) The warning always reports the current pin as the literal `<tag>` instead of the consumer's real pinned ref (e.g. `1.1.0`).

(b) Because `<tag>` never equals a real `DEVKIT_VERSION`, the warning **false-fires even when the consumer's pin already matches the target** — violating the changelog contract "a floating (unpinned) input or a matching pin stays silent". It never wrongly stays silent, so severity is quality/noise, but it defeats the feature's contract.

## Fix sketch

Extract the pin only from the **real, non-comment** input line — e.g. anchor with `^[[:space:]]*vigos\.url` (the doc-comment starts with `#`, so an anchored match skips it), or strip comment lines before grepping.

The existing #1093 bats tests (commit `3bfae419`, `tests/bats/init-workspace.bats`) use a minimal fixture flake.nix *without* the doc-comment line, so they don't catch this. New tests must use a fixture carrying BOTH the doc-comment example line and a real pin.

## SemVer

Patch — bug fix in the 1.2.1 release train, no behavior change for correctly-pinned consumers beyond removing the false warning.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 10:58 AM_

Verified live against the **real 1.2.1-rc2 artifacts** (image `ghcr.io/vig-os/devcontainer:1.2.1-rc2`, installer from tag `1.2.1-rc2`, baked `/root/assets/init-workspace.sh`). Fix shipped in 1.2.1-rc2 via #1113 (`fix(init-workspace): read flake pin from the real input line, not the doc comment`, 42d362184e9e1b83ae03c875f12fe3f55a6b109d).

A scratch direnv-mode consumer (`.vig-os` at `DEVKIT_VERSION=1.2.0`, `DEVKIT_MODE=direnv`) carried a `flake.nix` with **both** the doc-comment example line (`#   vigos.url = "github:vig-os/devkit?ref=<tag>";`) and a real pin line. `install.sh --version 1.2.1-rc2 --mode direnv --force` was run twice.

**ASSERT A — real pin `?ref=1.1.0` (skewed):** the warning fires and reports the REAL pin, not `<tag>`:

```
WARNING: scaffold upgraded to 1.2.1-rc2, but the pinned vigos flake input is still 1.1.0.
```

**ASSERT B — real pin `?ref=1.2.1-rc2` (aligned), doc-comment `<tag>` still present:** upgrade runs to completion (`Workspace initialized successfully!`) with **no skew warning** in the output. The buggy grep would have matched the doc-comment and false-fired `still <tag>`; it stays silent.

The doc-comment is no longer a source of the reported pin. Closing as fixed and verified.

