---
type: issue
state: closed
created: 2026-06-25T12:12:34Z
updated: 2026-07-01T14:35:58Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/709
comments: 1
labels: docs, effort:small, area:docs
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:00.967Z
---

# [Issue 709]: [[DOCS] Regenerate TESTING.md — stale 'Python 3.12' (image is 3.14)](https://github.com/vig-os/devkit/issues/709)

## Problem
`docs/templates/TESTING.md.j2:33` and generated `TESTING.md:33` say 'Python 3.12, uv'; the Nix image ships CPython 3.14 (README already correct). Template not regenerated after the version bump.

## Recommendation
Fix the `.j2` template and run `just docs`.

## Context
Found during the state-of-the-repo review of #670 (epic #625).

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 02:35 PM_

Already resolved on `dev`. `docs/templates/TESTING.md.j2:33` and generated `TESTING.md:33` now read 'Python 3.14, uv' (fixed in `fdd1a0cf`, docs: correct the Python version to 3.14 in the TESTING template). Closing as done.

