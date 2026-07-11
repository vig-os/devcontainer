---
type: issue
state: closed
created: 2026-07-04T15:52:28Z
updated: 2026-07-04T20:01:39Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/821
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:40.558Z
---

# [Issue 821]: [A4 — Wave-1 modules: vigos.{shell,multiplexer,cli,direnv,git}](https://github.com/vig-os/devkit/issues/821)

vigos.shell: bash+zsh, starship, atuin, opt-in secretsEnv export hook per ADR spec. vigos.multiplexer: tmux. vigos.cli: modern-unix configuration only (packages ship solely via homeManagerModules.packages). vigos.direnv: direnv + nix-direnv. vigos.git: identity options, signingKeyPath default-null (signing activates only when set), gh, lazygit, delta. Every scalar mkDefault; extraConfig passthroughs; platform guards.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:20 PM_

Landed via PR #837 (4 commits, TDD: red behavior test → vigos.shell → vigos.{multiplexer,cli,direnv} → vigos.git) into `feature/814-home-environment-modules`.

Evidence: `nix-fast-build .#checks.x86_64-linux` fully green including hm-minimal/hm-full; `pytest tests/test_flake_checks.py` 10/10 (wave-1 behavior test asserts all programs enabled in the full profile, signing inactive by default, secretsEnv defaulting off); `ci-full-aarch64-darwin` activationPackage evaluates. statix forced the single-`programs`-set style in shell.nix (caught locally, fixed pre-push).

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

