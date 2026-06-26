---
type: issue
state: open
created: 2026-06-25T12:12:36Z
updated: 2026-06-25T12:12:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/710
comments: 0
labels: chore, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:52.400Z
---

# [Issue 710]: [[CHORE] Cosmetic cleanup: justfile typo + stale Debian comments](https://github.com/vig-os/devcontainer/issues/710)

## Problem
- `justfile:251` duplicated word: 'Cleaning Cleaning up lingering test containers…'.
- Several comments in `tests/test_image.py`, `flake.nix`, and `assets/workspace/.devcontainer/scripts/post-create.sh` still narrate 'the Debian image…' as historical context — harmless but searchable noise.

## Recommendation
Single small cleanup commit; trim or link the Debian comments to #642. Do not over-engineer.

## Context
Found during the state-of-the-repo review of #670 (epic #625). Low priority; can attach to #642.

Refs: #625
