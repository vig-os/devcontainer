---
type: issue
state: closed
created: 2026-07-04T15:52:51Z
updated: 2026-07-08T12:58:44Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/822
comments: 3
labels: chore
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:40.181Z
---

# [Issue 822]: [B1 — Dogfood wave 1 in the maintainer's personal configuration](https://github.com/vig-os/devkit/issues/822)

Consume the wave-1 vigos.* modules from a branch of the maintainer's personal configuration (pre-release canary per the E2 policy exception). Acceptance = generation-diff bar: nvd diff shows no package changes AND a recursive home-files tree diff limited to this issue's expected-diff allowlist. May close per-module; wave complete when all private copies are deleted. Evidence (drvPaths, diff report, allowlist proposal) posted here.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:29 PM_

## Wave-1 dogfood evidence (canary branch, no switch)

Branch: `c-vigo/vigo-nixos@feature/devkit-wave1-dogfood` (commit 7bb4d36), consuming `devkit` = this repo's epic branch via flake input (`nixpkgs` follows the personal pin). Built in a worktree; the working checkout was untouched.

**Method:** vigos.{shell,multiplexer,cli,direnv,git} imported ON TOP of the personal config (plain assignments beat the modules' `mkDefault`); `starship.nix` and `direnv.nix` replaced outright as the removal preview. Baseline vs branch HM activationPackage built (`/tmp/hm-before` → `/tmp/hm-after`); system `toplevel` drvPath evaluates.

**Closure diff (`nix store diff-closures`)** — all expected:
- `zsh 5.9.1` + `nix-zsh-completions` + `.zshrc`/`.zshenv` — vigos.shell enables zsh alongside bash (new on this bash-only host; org policy for macOS colleagues).
- `gh 2.93.0` in home path + `gh-config.yml` — vigos.git's `programs.gh` (was system-level before).
- `home-manager` support delta ~79 KiB.

**home-files diff** — 5 files, all expected:
- `.bashrc`: `eza --git` alias + lazygit `lg` wrapper (vigos.cli / vigos.git integrations).
- `.config/git/config`: gh credential-helper stanzas (from `programs.gh.gitCredentialHelper`).
- `.zshrc`/`.zshenv`, `.config/gh/*`: new, as above.
- `fontconfig/10-hm-fonts.conf`: HM-internal ordering noise.

**Proposed expected-diff allowlist for wave-1 acceptance:** `{.zshrc, .zshenv, .config/gh/**, .bashrc (integration lines), .config/git/config (credential helper), fontconfig noise}` + packages `{zsh, nix-zsh-completions, gh(home)}`.

**Gaps found (keep private for now, no devkit scope growth):** none blocking — starship/direnv removal preview is diff-clean; atuin/bash/tmux/gh private modules remain co-enabled and merge cleanly over mkDefault.

**Left for acceptance (morning):** `nixos-rebuild switch` on the canary branch, allowlist sign-off, then per-module deletion of the private copies (atuin.nix, bash.nix, tmux.nix, gh.nix, modern-unix config parts) with per-deletion diff checks.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

## Waves 2+3 dogfood extension (canary branch updated, still no switch)

Branch now at `a04f355`, devkit input repointed to `dev` (the epic branch was deleted on merge; canary policy). New on the branch:

- `sesh.nix` / `gh-dash.nix` / `claude-config.nix` retired in favor of `vigos.{sesh,ghdash,claude}` — the 19 project seeds and the 6-window layout (files/edit/git/prs/shell/claude incl. yazi + gh-dash) ported as option values; gh-dash scoped as before via `repoFilters`.
- **Migration note surfaced by the closure diff:** the old symlink-managed `~/.claude` files and workspace CLAUDE.mds left the closure — the workspace hierarchy is carried over via `vigos.claude.claudeMd.workspaceFiles` so nothing disappears at switch; the old `global.md` deliberately does NOT go back under `~/.claude` (no symlinks there per the ADR) — merge its content into the user-owned `~/.claude/CLAUDE.md` at acceptance.
- `vigos.editor` stays off: the personal nixvim setup is richer, and the ADR keeps editors personal.

Build evidence: HM activationPackage builds green with all of wave 1+2+3 enabled against devkit@dev (`333db5da`); system toplevel evaluates.

Acceptance now covers the whole surface in one switch: `git switch feature/devkit-wave1-dogfood`, `nixos-rebuild switch`, verify sesh/gh-dash/claude behavior, sign off the allowlist, then delete the retired private modules.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 8, 2026 at 12:58 PM_

## B1 — wave-1 dogfood: evidence + expected-diff allowlist

Wave-1 `vigos.*` modules consumed from a branch of the maintainer's personal
config (`vigo-nixos`), pinned to `vig-os/devcontainer` `dev` @ `115eeeb2`
(E2 canary policy). One eval-green commit per module; **no `nixos-rebuild
switch` yet** — this is the pre-switch generation diff.

### drvPaths (system toplevel, `vigo-x1-gen13`)

| | store path | drv |
|---|---|---|
| baseline (`main`) | `wb0rsr7ln1n671di2qa3xjkhfrpsgg2s` | `mwdndi9…` |
| candidate (branch) | `v2v2r8x626pak1shj1jv07qw65121l61` | `xdg10w9…` |

Input-only commit (add `vigos`) left the drvPath **identical** to baseline
(`mwdndi9…`), and the `vigos.multiplexer` and `vigos.direnv` swaps were
byte-identical no-ops — proving those three change nothing built.

### `nvd diff` — package delta

```
Added packages:
[A.]  #1  gh-config.yml        <none>
[A.]  #2  gh-extensions        <none>
[A.]  #3  hm_..zshenv          <none>
[A.]  #4  hm_..zshrc           <none>
[A.]  #5  nix-zsh-completions  0.5.1-unstable-2025-12-12
[A.]  #6  zsh                  5.9.1, 5.9.1-man
Closure size: 2461 -> 2468 (18 paths added, 11 paths removed, delta +7, +7.8 MiB).
```

- **No packages removed, no versions changed** (the 11 removed paths are
  regenerated config derivations — bashrc etc.). Every tool that existed still
  exists at the same version.
- Two intended additions, both expected:
  1. **zsh** (+`nix-zsh-completions`, `.zshenv`/`.zshrc`) — the ADR org default
     (bash **and** zsh). Accepted for wave 1.
  2. **gh** config/extensions — `vigos.git` enables `programs.gh`, which the old
     `gh.nix` never did (it set `git_protocol` with `enable=false`, so it was
     **inert**). gh itself was already in the closure via `systemPackages`, so no
     new binary — only its now-managed config.

### home-files tree diff — allowlist

Seven paths differ; each is intended or a benign provenance update:

| Path | Change | Verdict |
|---|---|---|
| `.zshenv`, `.zshrc` | new (zsh init) | ✅ zsh org default |
| `.config/gh/config.yml` | new — `git_protocol: ssh` | ✅ activates the previously-inert intent |
| `.local/share/gh/` | new — gh extensions dir | ✅ from `programs.gh` |
| `.config/git/config` | **+** gh credential helpers (github.com, gist) | ✅ pure addition; identity, SSH signing, all 6 gitdir includes **unchanged** |
| `.bashrc` | **+** `eza='eza --git'` alias & lazygit `lg()` fn (module defaults); moved initExtra block | ✅ retained bits (claudh, Page-Up/Down binds, BASH_COMPLETION, atuin) all present; reorder is a semantic no-op |
| `.config/fontconfig/conf.d/10-hm-fonts.conf` | `home-manager-path` store hash only | ✅ auto — profile closure shifted (zsh); zero semantic change |

### New behaviours inherited from org defaults (flag for veto)

Adopting the modules pulls in org-curated defaults the hand-rolled config
lacked. All benign; listed so they can be suppressed if unwanted:

- `eza` bare invocation now shows git status (`eza.git = true`).
- `git` uses `gh` as a credential helper for github.com/gist.
- `lg` lazygit shell wrapper (cd-on-exit).
- zsh is installed and configured (not the login shell; bash stays default).

### Module → personal-override map

| devkit module | replaced | retained personal override |
|---|---|---|
| `vigos.shell` | `atuin/bash/starship.nix` (deleted) | atuin local-only settings; bash Page-Up/Down + ssh-completion knob |
| `vigos.multiplexer` | `tmux.nix` (slimmed) | 256color term, sesh/keybindings, yank/resurrect/continuum plugins |
| `vigos.cli` | `modern-unix.nix` (slimmed) | bat Just-syntax, eza aliases, btop, tealdeer, extra pkgs, delta options |
| `vigos.direnv` | `direnv.nix` (deleted) | — (fully covered) |
| `vigos.git` | `gh.nix` (deleted) + lazygit pkg line | full `programs.git` identity/signing/includes block; delta options |

### Status vs acceptance bar

- ✅ **no unexpected package changes** — only the two enumerated intended additions.
- ✅ **home-files diff limited to the allowlist** — 7 paths, all accounted for.
- ✅ private copies deleted: `atuin`, `bash`, `starship`, `direnv`, `gh`; `tmux`,
  `modern-unix` slimmed to personal-extras only.

### Switched & verified on the live host

`nixos-rebuild switch --flake .#vigo-x1-gen13` applied on `vigo-x1-gen13`.
Post-switch checks all green:

- `nvd diff /run/current-system <candidate>` → 0 paths — the running generation
  is exactly the candidate.
- All 16 tools resolve (zsh, eza, bat, fzf, rg, fd, delta, lazygit, gh, atuin,
  zoxide, starship, tmux, direnv, btop, tldr).
- Git signing intact: `user.signingkey`, `commit.gpgsign`, `format=ssh`,
  `allowed_signers` all present; a commit verifies **Good "git" signature** under
  the correct per-directory identity; 6 gitdir includes preserved.
- `gh`: `git_protocol: ssh` + credential helper active.

Wave 1 complete; the branch is merged to `vigo-nixos` `main`.


