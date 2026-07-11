---
type: issue
state: closed
created: 2026-06-30T08:34:11Z
updated: 2026-06-30T11:21:57Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/761
comments: 1
labels: chore, priority:low, effort:small, area:testing
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:51.051Z
---

# [Issue 761]: [[CHORE] Offline skip-guard for network-dependent image tests](https://github.com/vig-os/devkit/issues/761)

## Chore Type

CI / Build change (test robustness)

## Description

PR #670 review (larger nit). Network-dependent image tests (`uv add`,
`npm i -g tsx`) fail in offline/air-gapped runs. Add an offline skip-guard so
they skip cleanly rather than fail when there is no network.

## Acceptance Criteria

- [ ] Network-dependent image tests skip (not fail) when offline
- [ ] Online runs still execute them
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Implementation Notes

Guard the `uv add` / `npm i -g tsx` image tests with an offline detection skip.

## Files

- `tests/test_image.py` (network-dependent cases)

## Related Issues

Parent: #625. From PR #670 review (Comment 2, larger nits).

**Priority:** Low · **Changelog Category:** Changed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:21 AM_

Landed on the migration branch via #768.

