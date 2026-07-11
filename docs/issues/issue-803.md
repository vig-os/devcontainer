---
type: issue
state: closed
created: 2026-07-03T07:11:41Z
updated: 2026-07-03T07:46:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/803
comments: 1
labels: chore
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:44.591Z
---

# [Issue 803]: [[CHORE] Pin pre-commit python to 3.14 so PEP 758 bare-except syntax stops false-flagging](https://github.com/vig-os/devkit/issues/803)

## Context

Ratified decision (2026-07-03, revised): **keep** the PEP 758 unparenthesized `except X, Y:` form — it is the forward Python standard (valid 3.14, 3.15, onward) and is exactly what `ruff format` produces at `target-version = py314` (it *strips* added parentheses). Parenthesizing to `except (X, Y):` fights the formatter and pins formatting to the past, so we do **not** do that.

The only thing that breaks on the current syntax is a tool running a **pre-3.14 Python parser**. Locally, the flake-provided `pre-commit` is itself a Python-3.13 app, so it builds its `debug-statements` hook env with 3.13, which rejects PEP 758 with `SyntaxError: multiple exception types must be parenthesized`. CI is unaffected when pre-commit runs under the project's 3.14.

## Fix

Pin pre-commit to the project interpreter so every python-language hook matches the code:

```yaml
default_language_version:
  python: python3.14
```

This makes the bare flake `pre-commit` (3.13) build hook envs with 3.14, so the false SyntaxError disappears regardless of how pre-commit is invoked. Future-proof and aligned with `requires-python >=3.14`.

## Out of scope

- Propagating the "embrace PEP 758, don't parenthesize" convention to the org standards SSoT (`vig-os/meta/docs`) — track separately.

## Notes

Superseded the initial framing of this issue (which proposed parenthesizing) after finding ruff enforces the unparenthesized form. Surfaced while fixing CI on #718 (PR #802).
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 07:46 AM_

Resolved by #804 (merged to `dev`). Decision: keep the PEP 758 unparenthesized `except X, Y:` form (the forward standard, valid 3.14+, and what ruff-format emits at target py314) and fix the tooling instead — pinned `default_language_version: python: python3.14` so pre-commit hook envs match the project interpreter. Follow-up: record the convention in the org standards SSoT (`vig-os/meta/docs`).

