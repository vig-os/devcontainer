---
type: issue
state: closed
created: 2026-06-23T06:54:00Z
updated: 2026-07-01T11:19:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/630
comments: 1
labels: area:workflow, area:testing, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:14.982Z
---

# [Issue 630]: [C5 — Adapt Cursor-coupled tests & keep the AI blocklist](https://github.com/vig-os/devkit/issues/630)

Tracking: #625



## Context

`test_image.py::test_cursor_agent_installed` (~line 179) and `tests/bats/worktree.bats`
(skip-on `command -v agent`, assert `"Cursor Agent"`) assume `cursor-agent`. Separately,
`validate_commit_msg.py` + `.github/agent-blocklist.toml` block AI identities in commit
history — **this control must keep blocking `cursor` AND `claude`** (it is the org "never
name an AI in history" rule, not a Cursor dependency).

## Scope

**In:**
- Remove the `cursor-agent` image test.
- Rewrite `worktree.bats` to the `claude` CLI.
- Add a test asserting both `cursor` and `claude` identities are blocked in commit messages
  (covers `validate_commit_msg.py` + `.github/agent-blocklist.toml`, exercised via
  `packages/vig-utils/tests/test_check_pr_agent_fingerprints.py`).

**Out:**
- Other test refactors (#635).

## Tasks

- [ ] Remove `test_cursor_agent_installed`
- [ ] Rewrite `tests/bats/worktree.bats` for the `claude` CLI
- [ ] Add/extend a blocklist test proving cursor + claude are both rejected
      (in `packages/vig-utils/tests/test_check_pr_agent_fingerprints.py`)

## Acceptance criteria

- Suite green after #627 / #628.
- Blocklist test proves both `cursor` and `claude` identities are rejected.

## Dependencies

- **Depends-on:** #627, #628.
- **Blocks:** none.

## Files

- `tests/test_image.py`
- `tests/bats/worktree.bats`
- `packages/vig-utils/tests/test_check_pr_agent_fingerprints.py`

## Test notes

- TDD — write the blocklist test first (it should pass; it guards against a regression that
  drops the cursor entries while removing Cursor).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30). `test_cursor_agent_installed` removed; worktree tests run on `claude`; the AI blocklist still asserts both `cursor` and `claude` are blocked (`agent-blocklist.toml` retains both). Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

