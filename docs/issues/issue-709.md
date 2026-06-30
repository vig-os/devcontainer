---
type: issue
state: open
created: 2026-06-25T12:12:34Z
updated: 2026-06-25T12:12:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/709
comments: 0
labels: docs, effort:small, area:docs
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:52.698Z
---

# [Issue 709]: [[DOCS] Regenerate TESTING.md — stale 'Python 3.12' (image is 3.14)](https://github.com/vig-os/devcontainer/issues/709)

## Problem
`docs/templates/TESTING.md.j2:33` and generated `TESTING.md:33` say 'Python 3.12, uv'; the Nix image ships CPython 3.14 (README already correct). Template not regenerated after the version bump.

## Recommendation
Fix the `.j2` template and run `just docs`.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
