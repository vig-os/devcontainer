---
type: issue
state: closed
created: 2026-06-26T08:14:05Z
updated: 2026-07-02T11:41:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/717
comments: 1
labels: docs, priority:low, area:docs
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:00.109Z
---

# [Issue 717]: [docs: document the local Nix image build/iterate loop and downstream agent-models.toml customization](https://github.com/vig-os/devkit/issues/717)

## Context

Follow-up from the Nix migration (#625, PR #670). The docs cover the dev-shell fast path (`nix develop`/direnv) well, but two local-dev workflows are undocumented:

1. **Building/iterating the local Nix image** — `CONTRIBUTE.md`/`TESTING.md` mention `just test-image` but not when/how a developer builds the image locally vs. pulling from the registry, or how to iterate on the image itself (`just build` → `just test-image`).
2. **Downstream `agent-models.toml` customization** — `assets/workspace/.claude/agent-models.toml` ships `[models]`/`[skill-tiers]`, but there is no doc on how a downstream project overrides tiers or model assignments.

## Proposed work

- Add a short "building the image locally" section to `CONTRIBUTE.md` (and/or `docs/NIX.md`).
- Add an `agent-models.toml` customization note to `docs/SKILL_PIPELINE.md` or the workspace README.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 2, 2026 at 11:41 AM_

Done via PR #798 (merged to `dev`). `docs/NIX.md` documents the local build/iterate loop (`just build` → `just test-image`, when to build vs pull) and `docs/SKILL_PIPELINE.md` covers downstream `agent-models.toml` tier/model overrides.

