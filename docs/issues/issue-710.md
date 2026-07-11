---
type: issue
state: closed
created: 2026-06-25T12:12:36Z
updated: 2026-07-03T07:46:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/710
comments: 1
labels: chore, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:00.540Z
---

# [Issue 710]: [[CHORE] Cosmetic cleanup: justfile typo + stale Debian comments](https://github.com/vig-os/devkit/issues/710)

## Problem
- `justfile:251` duplicated word: 'Cleaning Cleaning up lingering test containers…'.
- Several comments in `tests/test_image.py`, `flake.nix`, and `assets/workspace/.devcontainer/scripts/post-create.sh` still narrate 'the Debian image…' as historical context — harmless but searchable noise.

## Recommendation
Single small cleanup commit; trim or link the Debian comments to #642. Do not over-engineer.

## Context
Found during the state-of-the-repo review of #670 (epic #625). Low priority; can attach to #642.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 07:46 AM_

Closing as done. The justfile duplicated-word typo was already fixed and merged in #714. The remaining item this issue tracked — the stale 'the Debian image…' comments in `tests/test_image.py`, `flake.nix`, and `post-create.sh` — is folded into the Debian-path decommission (#642), so there's nothing left uniquely tracked here.

