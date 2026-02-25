---
type: issue
state: open
created: 2026-02-24T17:23:00Z
updated: 2026-02-24T17:24:54Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/192
comments: 0
labels: refactor, area:workflow, effort:small
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:50.766Z
---

# [Issue 192]: [[REFACTOR] Add pull-latest-dev-and-merge step to PR-creating skills](https://github.com/vig-os/devcontainer/issues/192)

### Description

The PR-creating skills (`pr_create`, `pr_solve`, `worktree_pr`, `solve-and-pr`, `worktree_solve-and-pr`) do not ensure the branch is up to date with `origin/dev` (or the target base branch) before creating a pull request. This can lead to PRs with merge conflicts or stale code.

Each of these skills should pull the latest target branch from origin and resolve any merge conflicts **before** creating the PR.

### Files / Modules in Scope

- `.cursor/skills/pr_create/SKILL.md`
- `.cursor/skills/pr_solve/SKILL.md`
- `.cursor/skills/solve-and-pr/SKILL.md`
- `.cursor/skills/worktree_pr/SKILL.md`
- `.cursor/skills/worktree_solve-and-pr/SKILL.md`

### Out of Scope

- No changes to non-PR-creating skills
- No changes to the underlying git infrastructure or justfile recipes

### Invariants / Constraints

- All existing skill workflows must continue to function as before
- The merge/rebase step must happen before the PR is created, not after
- If merge conflicts cannot be resolved automatically, the skill must stop and report the conflict (interactive skills) or post a comment asking for help (autonomous skills)
- No behavior change to other workflow steps

### Acceptance Criteria

- [ ] `pr_create` step 1 ("Ensure Git is up to date") also merges `origin/<base_branch>` into the current branch and handles conflicts
- [ ] `pr_solve` step 5 ("Execute fixes") ensures the branch is rebased/merged with `origin/<base_branch>` before pushing
- [ ] `worktree_pr` step 1 ("Ensure clean state") pulls and merges `origin/<base_branch>` before pushing
- [ ] `worktree_solve-and-pr` pipeline includes the merge-with-base step in the PR phase (via `worktree_pr`)
- [ ] `solve-and-pr` launcher does not need changes itself (it delegates to `worktree_solve-and-pr`), but verify this
- [ ] Conflict handling is documented: interactive skills ask the user, autonomous skills post a question via `worktree_ask`
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

No changelog needed

### Additional Context

Currently `pr_create` fetches and pulls the current branch but does not merge the base branch. `worktree_pr` fetches and pushes but similarly skips merging the base. `pr_solve` handles merge conflicts as "manual action required" but doesn't proactively pull latest before fixing. This refactoring makes the "pull latest base, resolve conflicts" step a consistent pre-PR gate across all five skills.
