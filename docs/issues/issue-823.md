---
type: issue
state: closed
created: 2026-07-04T15:52:52Z
updated: 2026-07-04T20:01:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/823
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:39.815Z
---

# [Issue 823]: [B2 — Wave 2: vigos.claude + canonical secrets dir into the devcontainer](https://github.com/vig-os/devkit/issues/823)

vigos.claude per ADR Axis 5: settings.json seeded copy-if-absent; hooks + org CLAUDE.md fragment (~/.claude/vigos.md) copied via home.activation with checksum-overwrite + .bak; no symlinks anywhere in .claude/; top-level CLAUDE.md user-owned, seeded with one @vigos.md import line; DISABLE_AUTOUPDATER via home.sessionVariables; agent runtime deps. Devcontainer consumes ~/.config/vigos/secrets/ via env-file/mount (compose scaffolding only, image untouched) — absorbs #546. Optional off-by-default workspace-CLAUDE.md management option.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 06:30 PM_

Landed via PR #844 into `feature/814-home-environment-modules` (TDD: policy tests → module). Axis-5 policy implemented exactly as the ADR records it: seeded settings.json (seed = `includeCoAuthoredBy=false` only), managed `vigos.md` fragment with checksum-overwrite + `.bak`, `@vigos.md` import seeding into the user-owned CLAUDE.md, no symlinks under `~/.claude/`, `DISABLE_AUTOUPDATER` via sessionVariables, workspace-file option default-empty. Container path: scaffold compose mounts `~/.config/vigos/secrets:ro` + post-create bashrc export hook (same semantics as `vigos.shell.secretsEnv`). Wave-2/3 draft PR: #846.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

