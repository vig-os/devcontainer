---
type: issue
state: closed
created: 2026-06-30T08:34:01Z
updated: 2026-06-30T11:11:42Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/757
comments: 1
labels: bug, priority:medium, area:ci, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:52.569Z
---

# [Issue 757]: [[BUG] M4 — install.sh --skip-pull under docker + bare safety in ci.yml](https://github.com/vig-os/devkit/issues/757)

## Description

PR #670 review (M4). Two script bugs.

**`install.sh:520`** uses podman-only `$RUNTIME image exists` (docker has no such
subcommand; `2>/dev/null` hides the error → `--skip-pull` always fails under
docker).

**`ci.yml:243`** runs bare `safety check … || true` (deprecated in 3.x; safety
is installed in the uv env but invoked without `uv run`, unlike the adjacent
`uv run bandit` at `:237`).

## Steps to Reproduce

1. Run `install.sh --skip-pull` under **docker** (not podman) → present image not detected.
2. Inspect `ci.yml:243` → `safety` invoked bare, outside the uv env, with `|| true`.

## Expected Behavior

`--skip-pull` detects a present image under both docker and podman; `safety`
runs inside the uv env.

## Actual Behavior

`--skip-pull` always fails under docker; `safety` runs bare and deprecated.

## Fix

- `install.sh:520` → `$RUNTIME image inspect "$IMAGE" >/dev/null 2>&1` (works on docker + podman).
- `ci.yml:243` → `uv run safety …`; reconsider the `|| true`.

## Acceptance Criteria

- [ ] `install.sh --skip-pull` detects a present image under **docker**
- [ ] `safety` runs via `uv run`; `|| true` reconsidered
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Files

- `install.sh`
- `.github/workflows/ci.yml`

## Related Issues

Parent: #625. From PR #670 review (Comment 2, M4).

**Changelog Category:** Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:11 AM_

Landed on the migration branch via #764 (merge `b43883b`).

