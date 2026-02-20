---
type: issue
state: open
created: 2026-02-20T09:30:54Z
updated: 2026-02-20T09:30:54Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/101
comments: 0
labels: chore
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T13:17:18.431Z
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
