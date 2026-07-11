---
type: issue
state: closed
created: 2026-06-23T06:53:53Z
updated: 2026-07-01T11:19:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/626
comments: 1
labels: chore, docs, area:workflow
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:16.522Z
---

# [Issue 626]: [C1 — Make `.claude/` the SSoT for rules & skills](https://github.com/vig-os/devkit/issues/626)

Tracking: #625



## Context

`.cursor/` (7 `rules/*.mdc`, 30 `skills/*/SKILL.md`) is today's single source of truth for
agent rules and skills; `.claude/commands/*.md` (29 files) are thin wrappers that point into
`.cursor/skills/`. Moving to a Claude-native setup means making `.claude/` the SSoT and
removing the `.cursor/` indirection.

**Mapping decision:** Cursor `rules/*.mdc` have no 1:1 Claude equivalent, so they split by
kind — **static principles → `CLAUDE.md`** (always-on context), **actionable workflows →
`.claude/skills/`** (loaded on demand). This matches how Claude actually loads context and
avoids bloating always-on context with procedural content.

## Scope

**In:**
- Move static-principle rules → `CLAUDE.md`; workflow-style rules → `.claude/skills/`.
- Move skills → `.claude/skills/`.
- Rewrite the 29 command wrappers to the new paths (or native Claude skills).
- Port `agent-models.toml` / `worktrees.json` equivalents.
- Delete root `.cursor/`.

**Out:**
- Worktree CLI swap (#627).
- Template `.cursor/` under `assets/workspace/` (#629).

## Tasks

- [ ] Migrate `.cursor/rules/*.mdc` (principles → `CLAUDE.md`, workflows → `.claude/skills/`)
- [ ] Migrate `.cursor/skills/*/SKILL.md` to `.claude/skills/`
- [ ] Rewrite / replace the `.claude/commands/*.md` wrappers
- [ ] Port `agent-models.toml` and `worktrees.json` equivalents
- [ ] Delete root `.cursor/`
- [ ] Update the command table in `CLAUDE.md`

## Acceptance criteria

- Every former `/project:*` command resolves with no `.cursor/` path.
- No broken references to `.cursor/` anywhere in tracked files.

## Dependencies

- **Depends-on:** none (start immediately).
- **Blocks:** #629.

## Files

- `.cursor/**` (delete)
- `.claude/commands/*.md`
- `.claude/skills/**`
- `CLAUDE.md`

## Test notes

- Add a check (bats or pytest) asserting no tracked file references `.cursor/skills/`.

## Related issues

- **#144** (generate-docs hook misses skill dirs) — `docs/generate.py` scans
  `.cursor/skills/*/SKILL.md` and the pre-commit hook's `files` filter matches it. Moving
  skills to `.claude/skills/` **changes both**; update the scanner + hook filter here, which
  makes #144's narrow fix moot. Close/redirect #144 when this lands.
- **#162 / #178 / #157** (worktree-skill features) reference `.cursor/skills/<skill>/SKILL.md`
  paths that move under this issue — coordinate so those issues point at the new paths.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30). Root `.cursor/` deleted; `.claude/skills/**` + `CLAUDE.md` are the rules/skills SSoT. Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

