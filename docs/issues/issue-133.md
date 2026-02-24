---
type: issue
state: closed
created: 2026-02-20T23:28:42Z
updated: 2026-02-21T23:29:51Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/133
comments: 1
labels: feature, area:workflow, effort:medium, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-22T04:23:21.200Z
---

# [Issue 133]: [[FEATURE] Add pr_solve skill — diagnose PR failures, plan fixes, execute](https://github.com/vig-os/devcontainer/issues/133)

### Description

Add a new `pr_solve` skill that takes a PR number, diagnoses all failures (CI failures, review feedback, merge conflicts), creates a structured fix plan via `design_plan`, then executes the fixes.

This fills the gap between the existing atomic skills (`ci_check`, `ci_fix`, `code_review`) and the fully autonomous `worktree_solve-and-pr`. Today, fixing a failing PR requires the user to manually orchestrate: check CI, read review comments, diagnose each failure, then fix. `pr_solve` composes existing skills into a single interactive workflow with a planning checkpoint before any code changes.

### Problem Statement

When a PR has failures (CI red, reviewer requested changes, merge conflicts), the user must manually invoke multiple skills in sequence (`ci_check` → `ci_fix`, read review comments, etc.) and decide the order of fixes. There is no single entry point that gathers all PR problems, produces a consolidated fix plan, and executes it.

### Proposed Solution

A `pr_solve` skill with this workflow:

1. **Gather all PR problems** — Compose `ci_check` (CI status), `gh pr view` (review comments, requested changes), and merge state into a single diagnostic report.
2. **Present diagnosis** — Show the user a structured summary of all issues found.
3. **Plan fixes** — Use `design_plan` conventions to break the diagnosis into ordered fix tasks, presented for user approval.
4. **Execute fixes** — Apply fixes following TDD discipline (`code_tdd`), commit after each task.
5. **Verify** — Run `ci_check` after pushing to confirm fixes landed.

The skill reuses existing skills by reference (SSoT) rather than duplicating their logic.

### Alternatives Considered

- **Keep using individual skills manually** — Works but requires the user to orchestrate the sequence. Error-prone when multiple failures interact.
- **Extend `ci_fix` to also handle review feedback** — Violates single responsibility; CI failures and review feedback are different concerns that happen to co-occur on PRs.

### Impact

- Benefits any developer working with PRs that have multiple failure types.
- Backward compatible — new skill, no changes to existing skills.

### Acceptance Criteria

- [ ] `pr_solve` skill file at `.cursor/skills/pr_solve/SKILL.md`
- [ ] Skill composes `ci_check`, review comment fetching, and merge state detection into a single diagnostic step
- [ ] Diagnosis is presented to the user before any fixes are attempted
- [ ] Fix plan follows `design_plan` conventions (ordered tasks, files, verification)
- [ ] User must approve the plan before execution begins
- [ ] Skill is registered in `CLAUDE.md` command table
- [ ] Workspace copy via `scripts/sync_manifest.py` (not manual)
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 08:58 PM_

## Implementation Plan

Issue: #133
Branch: `feature/133-pr-solve-skill`

### Tasks

- [x] Task 1: Create `pr:solve` skill file with full workflow (identify PR, gather problems, present diagnosis, plan fixes, execute, verify) — `.cursor/skills/pr:solve/SKILL.md` — verify: `test -f .cursor/skills/pr:solve/SKILL.md && head -5 .cursor/skills/pr:solve/SKILL.md`
- [x] Task 2: Register `/pr:solve` in `CLAUDE.md` command table in alphabetical order — `CLAUDE.md` — verify: `grep 'pr:solve' CLAUDE.md`
- [x] Task 3: Run workspace sync to propagate the new skill to `assets/workspace/` — `just sync-workspace` — verify: `test -f assets/workspace/.cursor/skills/pr:solve/SKILL.md`
- [x] Task 4: Add changelog entry under `## Unreleased` / `### Added` — `CHANGELOG.md` — verify: `grep 'pr.solve' CHANGELOG.md`

### Skill Design (Task 1 detail)

**Frontmatter:** `name: pr:solve`, `description`, `disable-model-invocation: true`

**Workflow (6 steps):**

1. **Identify the PR** — user provides PR number; `gh pr view` for metadata; derive issue number from PR body (`Closes #N` / `Refs: #N`).
2. **Gather all problems** — three parallel data sources, each separated:
   - CI failures: `gh pr checks` + `gh run view --log-failed` (composes ci:check pattern)
   - Review feedback: `gh api` for reviews and inline comments — only unresolved threads
   - Merge state: `gh pr view --json mergeable,mergeStateStatus` — report but never auto-rebase
3. **Present diagnosis** — structured summary, each finding cites source. Explicit "clean PR" exit if no problems.
4. **Plan fixes** — design:plan conventions (ordered tasks, files, verification). User must approve. Merge conflicts flagged as manual action.
5. **Execute fixes** — code:tdd discipline, git:commit after each task, push after each fix.
6. **Verify** — ci:check after push. Max 2 loops then escalate to user.

**Key guardrails:** no fixes without diagnosis first; no guessing; no auto-rebase; no stacking fixes; max loop count; delegation section for data-gathering.

