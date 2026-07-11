---
type: issue
state: closed
created: 2026-07-04T15:52:24Z
updated: 2026-07-04T20:01:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/818
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:41.633Z
---

# [Issue 818]: [A1 — vigos.* option namespace, module skeleton, renamed option, umbrella default](https://github.com/vig-os/devkit/issues/818)

Create nix/home/{default,packages,shell,multiplexer,cli,direnv,git}.nix. packages.nix = the #777 package-only module re-keyed as `vigos.packages.enable` + `mkRenamedOptionModule` from `programs.vigos-devtools.enable` (declared exactly once). Other modules = enable-option skeletons. default.nix = imports-only umbrella (all disabled by default). Export as path modules under homeManagerModules.* + homeModules.* aliases; modules resolve packages from devkit's locked nixpkgs + overlay (self-pkgs). Extend deadnix/statix check scope to nix/.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:13 PM_

Landed via PR #835 into `feature/814-home-environment-modules` (commits: red schema tests → module skeleton → input+matrix, TDD).

Local evidence: `nix run .#nix-fast-build -- --flake .#checks.x86_64-linux` fully green including the new hm-minimal/hm-full legs (warm build 7s — the Tier-0 10-min budget is safe); `pytest tests/test_flake_checks.py` 9/9; darwin full-profile activationPackage drvPath evaluates. Notes: devTools relocated to `nix/devtools.nix` (verbatim) and `batsWithLibs` extracted to `nix/bats.nix` so flake + modules share one SSoT; deadnix/statix scope extended to `nix/`.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

