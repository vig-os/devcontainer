---
type: issue
state: open
created: 2026-02-17T22:32:42Z
updated: 2026-02-17T22:32:42Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/63
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-17T22:32:55.922Z
---

# [Issue 63]: [Add Cursor commands and rules for agent-driven development workflows](https://github.com/vig-os/devcontainer/issues/63)

## Description

Add new Cursor commands (`.cursor/commands/`) and rules (`.cursor/rules/`) to improve coding agent effectiveness across the full development lifecycle — from issue creation through implementation, testing, review, and CI debugging.

Follows up on #61 which added issue templates and changelog guidance. This issue covers the remaining agent workflow gaps.

## Problem Statement

Currently, coding agents lack structured guidance for several common workflows:
- **Starting work on an issue** — the `branch-naming.mdc` rule provides passive guidance but there is no invokable command to run the full `gh issue develop` workflow
- **Creating issues** — no command to auto-detect template type, populate fields, and use correct labels
- **Test-driven development** — no enforcement of write-test-first discipline; agents default to code-first
- **Self-review before PR** — no structured review step between committing and submitting a PR
- **Verification before claiming done** — agents claim "done" without running tests or checking evidence
- **CI diagnosis** — no workflow for fetching failed CI logs and tracing root cause
- **Systematic debugging** — agents tend to guess-and-fix instead of following root cause analysis
- **Plan-based execution** — no structured way to break large features into tasks with checkpoints

## Proposed Commands and Rules

### Tier 1 — High impact, daily use

| Command/Rule | Type | Purpose |
|---|---|---|
| `start-issue.md` | Command | Start work on an issue: read issue, `gh issue develop`, checkout branch, restore context |
| `create-issue.md` | Command | Create a GitHub issue: detect template type, populate fields, use correct labels |
| `tdd.md` + `tdd.mdc` | Command + Rule | Test-driven development: RED-GREEN-REFACTOR cycle using existing `just test-*` recipes |
| `review.md` | Command | Self-review: diff against base, check acceptance criteria, changelog, commit messages; structured severity report |
| `verify.md` | Command | Verification before completion: run tests, check evidence, no "should pass" claims |

### Tier 2 — CI/GitHub integration

| Command | Type | Purpose |
|---|---|---|
| `check-ci.md` | Command | Check CI status: `gh pr checks` / `gh run list`, show pass/fail per workflow |
| `fix-ci.md` | Command | Diagnose failing CI: `gh run view --log-failed`, trace root cause, propose fix |

### Tier 3 — Planning and debugging

| Command | Type | Purpose |
|---|---|---|
| `plan.md` | Command | Write implementation plan: break issue into bite-sized tasks with file paths and verification steps |
| `execute-plan.md` | Command | Execute plan in batches with human checkpoints, sequential subagent dispatch |
| `debug.md` | Command | Systematic debugging: 4-phase root cause process (investigate, analyze, hypothesize, implement) |

### Future — Workflow redesign

| Item | Type | Purpose |
|---|---|---|
| Worktree-based development | Workflow change | `git worktree` support for parallel subagent execution; requires updating `start-issue`, `submit-pr`, `after-pr-merge` |

## Inspiration

- [obra/superpowers](https://github.com/obra/superpowers) — agentic skills framework with TDD, systematic debugging, verification-before-completion, subagent-driven development, and code review skills
- Existing repo commands (`commit-msg.md`, `submit-pr.md`, `after-pr-merge.md`) establish the pattern

## Acceptance Criteria

- [ ] Tier 1 commands and rules created and functional
- [ ] Tier 2 commands created and functional
- [ ] Tier 3 commands created and functional
- [ ] Existing commands (`submit-pr.md`) updated to reference `review.md` as prerequisite
- [ ] CHANGELOG.md updated under `## Unreleased / ### Added`

## Implementation Notes

- Each command should follow the style of existing commands (see `commit-msg.md`, `submit-pr.md`)
- Rules (`.mdc`) should use `alwaysApply: true` for behavioral rules like TDD
- Commands that invoke `gh` CLI should handle common error cases (auth, permissions, rate limits)
- The worktree workflow is intentionally deferred — it requires updating multiple existing commands and rules
- Consider splitting this into sub-issues per tier if the scope is too large for one branch
