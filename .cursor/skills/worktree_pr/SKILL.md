---
name: worktree_pr
description: Autonomous PR creation from a worktree branch.
disable-model-invocation: true
---

# Autonomous PR

Create a pull request **without user interaction**. This is the worktree variant of [pr:create](../pr_create/SKILL.md).

**Rule: no blocking for feedback. Auto-generate PR text from commits and issue.**

## Precondition: Issue Branch Required

1. Run: `git branch --show-current`
2. The branch name **must** match `<type>/<issue_number>-<summary>` (e.g. `feature/79-declarative-sync-manifest`). See [branch-naming.mdc](../../rules/branch-naming.mdc) for the full convention.
3. Extract the `<issue_number>` from the branch name.

## Workflow Steps

### 1. Ensure clean state

```bash
git status
git fetch origin
```

- If there are uncommitted changes, commit them first.
- Push the branch: `git push -u origin HEAD`

### 2. Determine base branch

Detect whether this issue is a sub-issue and resolve the correct merge target:

1. Determine the repo: `gh repo view --json nameWithOwner --jq '.nameWithOwner'`
2. Check for a parent issue:

   ```bash
   gh api repos/{owner}/{repo}/issues/{issue_number}/parent --jq '.number'
   ```

3. If a parent exists, resolve its linked branch:

   ```bash
   gh issue develop --list <parent_number>
   ```

   - Use the parent's branch as `<base_branch>`.
   - If the parent has no linked branch, fall back to `dev`.

4. If no parent exists, use `dev` as `<base_branch>`.

### 3. Gather context

```bash
git log <base_branch>..HEAD --oneline
git diff <base_branch>...HEAD --stat
gh issue view <issue_number> --json title,body
```

- Read the issue title and acceptance criteria.
- Summarize what the commits accomplish.

### 4. Ensure CHANGELOG is updated

- Check `CHANGELOG.md` for an entry under `## Unreleased` that covers the changes.
- If missing, add the appropriate entry and commit.

### 5. Generate PR text

- Use the structure from [.github/pull_request_template.md](../../.github/pull_request_template.md).
- Populate: Description, Related Issue(s) (`Closes #<issue_number>`), Type of Change, Changes Made, Testing, Checklist.
- Write the body to `.github/pr-draft-<issue_number>.md`.

### 6. Create PR

```bash
# Append reviewer if PR_REVIEWER is set in environment
REVIEWER_ARG=""
if [ -n "${PR_REVIEWER:-}" ]; then
  REVIEWER_ARG="--reviewer $PR_REVIEWER"
fi

gh pr create --base <base_branch> --title "<type>: <description> (#<issue_number>)" \
  --body-file .github/pr-draft-<issue_number>.md \
  --assignee @me $REVIEWER_ARG
```

If the `WORKTREE_REVIEWER` environment variable is set (populated by `just worktree-start`), add the reviewer:

```bash
gh pr create --base <base_branch> --title "<type>: <description> (#<issue_number>)" \
  --body-file .github/pr-draft-<issue_number>.md \
  --assignee @me \
  --reviewer "$WORKTREE_REVIEWER"
```

The reviewer is the person who launched the worktree (their gh user login), not the agent.

### 7. Clean up

- Delete the draft file: `rm .github/pr-draft-<issue_number>.md`
- Report the PR URL.

## Delegation

The following steps SHOULD be delegated to reduce token consumption:

- **Steps 1-2** (precondition check, ensure clean state, determine base branch): Spawn a Task subagent with `model: "fast"` that validates the branch name, runs `git status`/`git fetch`, pushes the branch, checks for a parent issue via `gh api`, resolves the base branch. Returns: issue number, base branch name, clean state confirmation.
- **Step 3** (gather context): Spawn a Task subagent with `model: "fast"` that executes `git log`, `git diff`, `gh issue view` and returns the raw outputs. Returns: commit log, diff stat, issue title/body.
- **Steps 6-7** (create PR, clean up): Spawn a Task subagent with `model: "fast"` that takes the PR title and body file path, executes `gh pr create`, deletes the draft file, and returns the PR URL.

Steps 4-5 (ensure CHANGELOG updated, generate PR text) should remain in the main agent as they require understanding changes and writing structured content.

Reference: [subagent-delegation rule](../../rules/subagent-delegation.mdc)

## Important Notes

- Never block for user review of the PR text. Generate the best text from available context.
- Base branch is auto-detected: parent issue's branch for sub-issues, `dev` otherwise.
- The PR title should follow commit message conventions: `type(scope): description (#issue)`.
- **NEVER add 'Co-authored-by: Cursor <cursoragent@cursor.com>'** to commit messages.
