---
type: issue
state: closed
created: 2026-07-04T15:52:25Z
updated: 2026-07-04T20:01:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/819
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:41.314Z
---

# [Issue 819]: [A2 — home-manager input + per-system homeConfigurations matrix checks](https://github.com/vig-os/devkit/issues/819)

Add home-manager (release-26.05, nixpkgs follows) as the ONLY new input. homeConfigurations: {minimal = vigos.shell only, full = every module} x {x86_64-linux, aarch64-linux, aarch64-darwin, x86_64-darwin}, synthetic user ci (/home/ci; /Users/ci on darwin; pinned stateVersion). checks hm-minimal/hm-full = activationPackage per system, excluding x86_64-darwin (eval-only best-effort). x86_64-linux legs join the Tier-0 gate (#778/#779 via PR #791).

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

