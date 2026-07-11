---
type: issue
state: closed
created: 2026-06-30T08:34:06Z
updated: 2026-06-30T12:22:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/759
comments: 1
labels: chore, priority:low, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:51.760Z
---

# [Issue 759]: [[CHORE] Nits batch — PR #670 review trivial fixes](https://github.com/vig-os/devkit/issues/759)

## Chore Type

General task

## Description

PR #670 review — batch of trivial nits. Fold into a single `chore`/`docs`/`test`
pass.

## Acceptance Criteria

- [ ] `version-check.sh` help typo `"And (days)"` → `"Nd (days)"`
- [ ] `scripts/init.sh` "Pre-commit hooks installed" message reflects that `install-hooks` only fetches envs
- [ ] Unparenthesized `except A, B:` tuples fixed — `test_claude_ssot.py:53,74`, `conftest.py`
- [ ] `release.yml` summary: treat a `cancelled` required job as **not** green
- [ ] `install.sh` dry-run: derive from the real `CMD=(...)` via `printf '%q'`
- [ ] `install.sh`: guard the `git add -A && commit "initial scaffold"` against sweeping a populated dir

## Implementation Notes

These are independent one-liners; keep the diff minimal and grouped.

## Files

- `version-check.sh`, `scripts/init.sh`, `tests/test_claude_ssot.py`, `conftest.py`, `.github/workflows/release.yml`, `install.sh`

## Related Issues

Parent: #625. From PR #670 review (Comment 2, nits batch).

**Priority:** Low · **Changelog Category:** Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 12:22 PM_

Landed on the migration branch via #772.

