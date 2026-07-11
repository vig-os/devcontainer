---
type: issue
state: closed
created: 2026-07-07T15:26:14Z
updated: 2026-07-09T13:28:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/912
comments: 0
labels: bug
assignees: none
milestone: 0.5.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:26.121Z
---

# [Issue 912]: [fix(skills): correct broken links, duplicate sections, name/title mismatches, drop commands/](https://github.com/vig-os/devkit/issues/912)

## Problem

A batch of correctness bugs has accumulated in `.claude/skills/`:

1. **Broken relative links** — Many `SKILL.md` files link to `../../rules/*.mdc` (e.g. `branch-naming.mdc`, `subagent-delegation.mdc`, `tdd.mdc`, `commit-messages.mdc`, `coding-principles.mdc`) and `../docs/RELEASE_CYCLE.md`. `.claude/rules/` does not exist (rules were converted to skills in #626); `.claude/skills/../docs/` does not exist either. These links are all dead.

2. **Duplicate `## Delegation` sections** — `ci_check/SKILL.md`, `worktree_ci-fix/SKILL.md`, and `worktree_verify/SKILL.md` each have the entire `## Delegation` section copy-pasted twice.

3. **Skill name mismatch** — `solve-and-pr/SKILL.md` launches `just worktree-start <n> "/worktree-solve-and-pr"` but the actual skill directory is `worktree_solve-and-pr` (underscore). The slash command `/worktree-solve-and-pr` won't resolve.

4. **PR-title contradiction** — `pr_create/SKILL.md` says do NOT put the issue number in the PR title (GitHub appends `(#PR)`). `worktree_pr/SKILL.md` mandates `<type>: <description> (#<issue_number>)` in the title. These contradict each other.

5. **Obsolete `commands/` wrappers** — Every file in `.claude/commands/*.md` is a stub that just delegates to the corresponding `SKILL.md`. In current Claude Code, a skill named `X` already provides `/X`, making these wrappers dead weight. Some have extra context lines that need folding into the SKILL.md before deletion.

## Proposed Fix

1. Rewrite broken `../../rules/*.mdc` links to correct targets:
   - `branch-naming.mdc` → `../branch-naming/SKILL.md`
   - `subagent-delegation.mdc` → `../subagent-delegation/SKILL.md`
   - `tdd.mdc` → `../tdd/SKILL.md`
   - `commit-messages.mdc` / `coding-principles.mdc` → `../../../CLAUDE.md` (CLAUDE.md principles, no skill equivalent)
   - `../docs/RELEASE_CYCLE.md` → `../../../docs/RELEASE_CYCLE.md`

2. Remove the duplicate second `## Delegation` block in the three affected files.

3. Fix the slash command reference in `solve-and-pr/SKILL.md` to `/worktree_solve-and-pr`.

4. Update `worktree_pr/SKILL.md` to match `pr_create`'s rule: no issue number in PR title.

5. For commands with extra content, verify it's already in the SKILL.md (or fold it in), then delete the entire `.claude/commands/` directory.

## Acceptance Criteria

- [ ] TDD compliance (see `.claude/skills/tdd/SKILL.md`)
- [ ] `grep -rn 'rules/.*\.mdc' .claude/skills/` returns no results
- [ ] No duplicate `## Delegation` sections in any SKILL.md
- [ ] `solve-and-pr/SKILL.md` references `/worktree_solve-and-pr`
- [ ] `worktree_pr/SKILL.md` and `pr_create/SKILL.md` agree on PR title format
- [ ] `.claude/commands/` directory deleted
- [ ] `assets/workspace/.claude/` stays in sync (sync-manifest hook passes)
- [ ] Pre-commit passes cleanly

Refs: #626
