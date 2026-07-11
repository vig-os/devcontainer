---
type: issue
state: closed
created: 2026-07-04T15:52:54Z
updated: 2026-07-04T20:01:43Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/824
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:39.399Z
---

# [Issue 824]: [B3 — Wave 3: vigos.{sesh,ghdash,editor}](https://github.com/vig-os/devkit/issues/824)

vigos.sesh: standard tmux session layout with a projects option API (no hardcoded paths). vigos.ghdash: parameterized filters/repo paths. vigos.editor: programs.neovim + nixpkgs vimPlugins.claudecode-nvim (no nixvim input, per ADR Axis 3).

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 06:30 PM_

Landed via PR #845 into `feature/814-home-environment-modules` (TDD). `vigos.sesh` (sessions + layout.windows options, idempotent layout script, picker on prefix+o), `vigos.ghdash` (repoFilters → lean sections), `vigos.editor` (programs.neovim + vimPlugins.claudecode-nvim; bare devTools neovim lowPrio'd to avoid the buildEnv collision). 13/13 schema tests; hm-full green with all nine modules. Wave-2/3 draft PR: #846.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

