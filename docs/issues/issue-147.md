---
type: issue
state: closed
created: 2026-02-21T22:43:02Z
updated: 2026-02-21T23:30:48Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/147
comments: 3
labels: feature, area:workflow, effort:small
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-22T04:23:19.163Z
---

# [Issue 147]: [[FEATURE] Autonomous PR skill should use .github/pull_request_template.md](https://github.com/vig-os/devcontainer/issues/147)

### Description

The autonomous worktree PR creation skill (`worktree_pr` / `pr_create`) composes a freeform PR body and passes it via `gh pr create --body`, which bypasses the repo's `.github/pull_request_template.md` entirely.

### Problem Statement

PRs created by the autonomous agent have a different format (e.g. `## Summary` / `## Verification`) than the structured template the project uses. This makes reviews inconsistent and misses checklist items like Type of Change, Changelog Entry, and the standard Checklist.

Observed in PR #146 (created by `worktree_solve-and-pr` for issue #143).

### Proposed Solution

Update the PR creation skill(s) to:

1. Read `.github/pull_request_template.md` from the repo
2. Fill in each section using context already available to the agent (issue number, commit history, test results, changelog diff, file changes)
3. Pass the filled-in template as the `--body` argument to `gh pr create`

### Alternatives Considered

- Omitting `--body` so `gh` uses the template automatically — but then the agent can't pre-fill any content, leaving the PR body as raw placeholders.
- Post-processing: create the PR with `--body`, then edit it — adds unnecessary API calls.

### Impact

- Ensures all autonomous PRs follow the same structure as manual PRs
- Reviewers get consistent, complete information (type of change, changelog entry, checklist)
- No breaking change; improves existing behavior

### Acceptance Criteria

- [ ] Autonomous PRs use the repo's PR template structure
- [ ] All template sections are filled in from available context
- [ ] Checklist items are checked where applicable
- [ ] `Refs:` line is included

### Changelog Category

Changed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 10:53 PM_

## Design

### Approach: Explicit "read-then-fill" instructions in PR skills

Both `pr_create` and `worktree_pr` currently say "use the structure of `.github/pull_request_template.md`" — this is too vague and the agent composes a freeform body instead (observed in PR #146). The fix is to replace that vague instruction with an explicit read-then-fill procedure.

### Files to change

4 files (2 skills × 2 copies):

| File | Role |
|------|------|
| `.cursor/skills/pr_create/SKILL.md` | primary |
| `assets/workspace/.cursor/skills/pr_create/SKILL.md` | asset mirror |
| `.cursor/skills/worktree_pr/SKILL.md` | primary |
| `assets/workspace/.cursor/skills/worktree_pr/SKILL.md` | asset mirror |

### Changes to `pr_create` Step 4 and `worktree_pr` Step 5

Replace the current vague "use the structure" instruction with:

1. **Read the template**: `cat .github/pull_request_template.md`
2. **Use it as the literal skeleton** — keep every heading, every checkbox line, every sub-heading. Strip only the HTML comments (`<!-- ... -->`).
3. **Section-by-section mapping**:
   - **Description**: Summarize what the PR does from the issue body and commit messages.
   - **Type of Change**: Check the single box matching the branch type / commit types. Check `Breaking change` modifier only if commits contain `!`.
   - **Changes Made**: List changed files with bullet sub-details (from `git diff --stat` and `git log`).
   - **Changelog Entry**: Paste the exact `## Unreleased` diff from CHANGELOG.md. If no changelog update, write "No changelog needed" and explain.
   - **Testing**: Check `Tests pass locally` if tests were run. Check `Manual testing performed` only if actually done. Fill `Manual Testing Details` or write "N/A".
   - **Checklist**: Check only items that are genuinely true. Leave unchecked items unchecked — do not remove them.
   - **Additional Notes**: Add design links, context, or write "N/A".
   - **Refs**: `Refs: #<issue_number>`
4. **Explicit prohibitions**: Do not invent new sections. Do not rename headings. Do not omit sections. Do not remove unchecked boxes.

### What does NOT change

- The PR template itself (`.github/pull_request_template.md`)
- The rest of the skill workflows (git operations, CHANGELOG check, PR creation commands, delegation sections)
- No new files, no scripts, no config changes

### Testing strategy

Documentation/instruction-only change — no testable code. TDD skipped per project rules. Verification: next autonomous PR should match the template structure exactly.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 21, 2026 at 10:54 PM_

## Implementation Plan

Issue: #147
Branch: feature/147-pr-skill-use-template

### Tasks

- [x] Task 1: Replace pr_create Step 4 with explicit read-then-fill procedure — `.cursor/skills/pr_create/SKILL.md` — verify: `rg "Read the template" .cursor/skills/pr_create/SKILL.md`
- [x] Task 2: Sync pr_create asset mirror — `assets/workspace/.cursor/skills/pr_create/SKILL.md` — verify: `diff .cursor/skills/pr_create/SKILL.md assets/workspace/.cursor/skills/pr_create/SKILL.md` (no diff)
- [x] Task 3: Replace worktree_pr Step 5 with explicit read-then-fill procedure — `.cursor/skills/worktree_pr/SKILL.md` — verify: `rg "Read the template" .cursor/skills/worktree_pr/SKILL.md`
- [x] Task 4: Sync worktree_pr asset mirror — `assets/workspace/.cursor/skills/worktree_pr/SKILL.md` — verify: `diff .cursor/skills/worktree_pr/SKILL.md assets/workspace/.cursor/skills/worktree_pr/SKILL.md` (no diff)

---

# [Comment #3]() by [gerchowl]()

_Posted on February 21, 2026 at 11:04 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (4 tasks)
- Execute: all tasks done
- Verify: lint passed, precommit passed (hadolint skipped — Docker daemon not running locally)
- PR: https://github.com/vig-os/devcontainer/pull/148
- CI: all checks pass

