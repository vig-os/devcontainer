---
type: issue
state: closed
created: 2026-06-30T08:33:54Z
updated: 2026-06-30T11:11:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/754
comments: 1
labels: chore, priority:medium, area:image, area:testing, effort:large
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:53.764Z
---

# [Issue 754]: [[CHORE] M1 — Image-side .#devShellTools parity test](https://github.com/vig-os/devkit/issues/754)

## Chore Type

CI / Build change (test gate)

## Description

PR #670 review (M1). The `.#devShellTools` SSoT is only exercised on the
dev-shell side, not against the running image. `tests/test_flake_devshell.py`
evals `.#devShellTools` and runs each binary only in `nix develop`
(`:301-318`, `:434-453`). `tests/test_image.py` is hand-curated and covers
**10 of 27** `devTools` — missing `lazygit, delta, bats, jq, shellcheck,
nixfmt, typos, rg, fd, bat, eza, zoxide, starship, freeze, expect, nvim,
claude`. No in-container `nix eval .#devShellTools` test exists
(`test_image.py:951` only does `nix eval --expr "1 + 1"`).

## Acceptance Criteria

- [ ] Parametrized presence-on-PATH test in `tests/test_image.py` that evals `nix eval --json .#devShellTools.<system>` **inside the running container** and asserts each tool resolves on PATH
- [ ] Test fails when a `devTools` entry is absent from the image, passes otherwise
- [ ] Mirrors the dev-shell fixture at `test_flake_devshell.py:301-318`
- [ ] (Optional) dev-shell per-tool loop made two-way as well
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Implementation Notes

Turning the `.#devShellTools` SSoT into an actual image-side gate. This is the
heaviest Comment-2 item.

## Files

- `tests/test_image.py`
- optional: `tests/test_flake_devshell.py`

## Related Issues

Parent: #625. From PR #670 review (Comment 2, M1).

**Priority:** Medium · **Changelog Category:** Added

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:11 AM_

Landed on the migration branch via #766 (merge `685c7b8`).

