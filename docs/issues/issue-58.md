---
type: issue
state: open
created: 2026-02-17T18:44:24Z
updated: 2026-02-17T18:44:24Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/58
comments: 0
labels: question
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:33.251Z
---

# [Issue 58]: [validate-commit-msg: enforce types/scopes/refs by default](https://github.com/vig-os/devcontainer/issues/58)

cc @c-vigo

**Suggestion:** `validate-commit-msg` should ship with types, scopes, and refs **enforced by default** (strict-by-default) instead of being opt-in via commented-out CLI args.

**Why:** Users won't discover commented-out config. If enforcement is on by default, they experience the value immediately. The pre-commit error message can link to `.pre-commit-config.yaml` with a "customize or disable" hint — easy opt-out beats invisible opt-in.

**TL;DR:** Default strict → show config path in error → users discover greatness, can relax if needed.

Ref: `.pre-commit-config.yaml` lines 120–126.
