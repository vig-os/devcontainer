---
type: issue
state: closed
created: 2026-02-20T09:30:54Z
updated: 2026-02-20T14:08:56Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/101
comments: 1
labels: chore
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:36.750Z
---

# [Issue 101]: [[CHORE] Remove manual sync-issues workflow triggers from skills](https://github.com/vig-os/devcontainer/issues/101)

### Chore Type

CI / Build change

### Description

Four skills currently trigger the `sync-issues` workflow via `gh workflow run sync-issues.yml` after posting comments to issues. Since the sync workflow has moved to a 24h schedule (`cron: '0 2 * * *'`), these fire-and-forget triggers are unnecessary and should be removed.

Affected skills:
- `.cursor/skills/worktree:plan/SKILL.md` (line 69-73)
- `.cursor/skills/worktree:brainstorm/SKILL.md` (line 61-65)
- `.cursor/skills/design:brainstorm/SKILL.md` (line 65-69)
- `.cursor/skills/design:plan/SKILL.md` (line 77-81)

### Acceptance Criteria

- [ ] Remove the `gh workflow run sync-issues.yml` trigger step from `worktree:plan/SKILL.md`
- [ ] Remove the `gh workflow run sync-issues.yml` trigger step from `worktree:brainstorm/SKILL.md`
- [ ] Remove the `gh workflow run sync-issues.yml` trigger step from `design:brainstorm/SKILL.md`
- [ ] Remove the `gh workflow run sync-issues.yml` trigger step from `design:plan/SKILL.md`
- [ ] Step numbering in each skill remains correct after removal

### Implementation Notes

Each skill has a numbered step that triggers the workflow. Remove the entire step (description + code block) and renumber subsequent steps if necessary. The `design:brainstorm/SKILL.md` also mentions the sync-issues workflow in a comment about H2 headers (line 64) — that reference to header-level bumping is still valid context and can stay, but consider rewording since the sync is now on a schedule rather than triggered inline.

### Priority

Low

### Changelog Category

No changelog needed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 02:02 PM_

## Implementation Plan

Issue: #101
Branch: chore/101-remove-manual-sync-issues-triggers

### Tasks

- [x] Task 1: Remove the sync-issues trigger step (step 5, lines 69-73) from `worktree:plan/SKILL.md` and renumber step 4 — `.cursor/skills/worktree:plan/SKILL.md` — verify: `grep -c 'sync-issues' .cursor/skills/worktree:plan/SKILL.md` returns 0
- [x] Task 2: Remove the sync-issues trigger step (step 4 substep, lines 61-65) from `worktree:brainstorm/SKILL.md` and renumber step 6 — `.cursor/skills/worktree:brainstorm/SKILL.md` — verify: `grep -c 'sync-issues' .cursor/skills/worktree:brainstorm/SKILL.md` returns 0
- [x] Task 3: Remove the sync-issues trigger step (step 4 substep, lines 65-69) from `design:brainstorm/SKILL.md` and reword the H2 header comment on line 64; renumber step 6 — `.cursor/skills/design:brainstorm/SKILL.md` — verify: `grep -c 'sync-issues' .cursor/skills/design:brainstorm/SKILL.md` returns 0
- [x] Task 4: Remove the sync-issues trigger step (step 5, lines 77-81) from `design:plan/SKILL.md` — `.cursor/skills/design:plan/SKILL.md` — verify: `grep -c 'sync-issues' .cursor/skills/design:plan/SKILL.md` returns 0
- [x] Task 5: Verify step numbering is correct in all four files and all changes pass linting — all four files — verify: visual inspection of step numbers

