---
type: issue
state: open
created: 2026-03-06T19:02:51Z
updated: 2026-03-06T19:02:51Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/224
comments: 0
labels: chore, area:workflow, effort:small
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:38.677Z
---

# [Issue 224]: [[CHORE] Add Claude Code integration (CLAUDE.md, .claude/ skills)](https://github.com/vig-os/devcontainer/issues/224)

### Chore Type

Configuration change

### Description

The project currently has Cursor-specific agent configuration (`.cursor/rules/`, `.cursor/skills/`) and a `CLAUDE.md` that mirrors the Cursor rules. Claude Code uses its own conventions (`.claude/` directory, slash-command skills, `CLAUDE.md`).

Add proper Claude Code integration so Claude Code sessions pick up project conventions, skills, and workflows natively — without relying solely on CLAUDE.md duplication.

### Acceptance Criteria

- [ ] `.claude/` directory with project-level settings
- [ ] `CLAUDE.md` references `.cursor/skills/` and `.cursor/rules/` as SSoT (no duplication)
- [ ] Claude Code slash commands mapped from existing `.cursor/skills/`
- [ ] Verify Claude Code picks up conventions in a fresh session

### Implementation Notes

- Claude Code reads `CLAUDE.md` at project root automatically
- Claude Code supports custom slash commands via `.claude/commands/` directory
- Skills in `.cursor/skills/` use `SKILL.md` format — adapt to Claude Code's command format
- Keep `.cursor/` as SSoT; `.claude/` should reference, not duplicate

### Related Issues

New — no existing issue covers this.

### Priority

Low

### Changelog Category

No changelog needed
