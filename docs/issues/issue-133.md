---
type: issue
state: open
created: 2026-02-20T23:28:42Z
updated: 2026-02-20T23:28:42Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/133
comments: 0
labels: feature, area:workflow, effort:medium, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:16.837Z
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
