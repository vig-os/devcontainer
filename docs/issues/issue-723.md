---
type: issue
state: closed
created: 2026-06-29T07:16:28Z
updated: 2026-06-30T07:42:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/723
comments: 1
labels: bug, area:workspace
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:58.615Z
---

# [Issue 723]: [[BUG] dev-shell neovim inherits host ~/.config/nvim and crashes on startup (nixvim plugins missing)](https://github.com/vig-os/devkit/issues/723)

## Problem

The dev-shell ships plain upstream `neovim` on `PATH` (`flake.nix:116`, `neovim # nvim`, absorbed from #545). When a user who manages their editor with **nixvim** (home-manager) enters the shell via direnv, that bare `neovim` shadows their nixvim-wrapped `nvim`.

nixvim does **not** bake plugins into `init.lua`. It produces two things:

1. The config at the standard `~/.config/nvim/init.lua` — auto-sourced by *any* neovim, because it's the standard XDG path.
2. A wrapper binary whose sole extra job is `--cmd "set packpath^=…vim-pack-dir"` — the dir where all plugins (catppuccin, etc.) actually live.

The dev-shell's bare neovim auto-sources the host `init.lua` but never sets that `packpath`, so `require("catppuccin")` aborts on startup:

```
E5113: Lua chunk: ~/.config/nvim/init.lua:49: module 'catppuccin' not found
```

So `nvim` is broken inside the dev-shell for anyone with a nixvim/home-manager config, while it works fine in any window outside the shell. The same class of breakage hits any user whose `~/.config/nvim` assumes a specific launcher (LazyVim with a pinned lockfile, etc.).

## Recommendation

A dev-shell editor should never inherit the host user's personal `~/.config/nvim`. Isolate it by setting `NVIM_APPNAME` in the dev-shell, so nvim looks under `~/.config/$NVIM_APPNAME` (which doesn't exist) and starts vanilla:

Add a dedicated hook in `mkProjectShell` (composed like `ldLibraryPathHook`, so it applies regardless of any consumer-supplied `shellHook`):

```nix
nvimIsolationHook = ''
  export NVIM_APPNAME="vigos-dev"
'';
# ...
shellHook = ldLibraryPathHook + "\n" + nvimIsolationHook + "\n" + shellHook;
```

This keeps `neovim` available in the shell as a vanilla editor without colliding with the user's config or state dirs.

## Context

Diagnosed live: the failing nvim's luajit (`pmj0a9…`) differs from the user's nixvim-wrapper luajit (`bjcrj67…`) — confirming a *different* neovim binary sourcing the *same* `init.lua`. Trigger is `cd` into a project where this flake's dev-shell is direnv-activated.

Refs: #625

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #724 (f566fff) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

