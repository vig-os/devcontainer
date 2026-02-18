---
name: worktree:pr
description: Autonomous PR creation from a worktree branch.
disable-model-invocation: true
---

# Autonomous PR

Create a pull request **without user interaction**. This is the worktree variant of [pr:create](../pr:create/SKILL.md).

**Rule: no blocking for feedback. Auto-generate PR text from commits and issue.**

## Precondition: Issue Branch Required

1. Run: `git branch --show-current`
2. The branch name **must** match `<type>/<issue_number>-*` or `worktree/<issue_number>*`.
3. Extract the `<issue_number>` from the branch name.

## Workflow Steps

### 1. Ensure clean state

```bash
git status
git fetch origin
```

- If there are uncommitted changes, commit them first.
- Push the branch: `git push -u origin HEAD`

### 2. Gather context

```bash
git log dev..HEAD --oneline
git diff dev...HEAD --stat
gh issue view <issue_number> --json title,body
```

- Read the issue title and acceptance criteria.
- Summarize what the commits accomplish.

### 3. Ensure CHANGELOG is updated

- Check `CHANGELOG.md` for an entry under `## Unreleased` that covers the changes.
- If missing, add the appropriate entry and commit.

### 4. Generate PR text

- Use the structure from [.github/pull_request_template.md](../../.github/pull_request_template.md).
- Populate: Description, Related Issue(s) (`Closes #<issue_number>`), Type of Change, Changes Made, Testing, Checklist.
- Write the body to `.github/pr-draft-<issue_number>.md`.

### 5. Create PR

```bash
gh pr create --base dev --title "<type>: <description> (#<issue_number>)" \
  --body-file .github/pr-draft-<issue_number>.md \
  --assignee @me
```

### 6. Clean up

- Delete the draft file: `rm .github/pr-draft-<issue_number>.md`
- Report the PR URL.

## Important Notes

- Never block for user review of the PR text. Generate the best text from available context.
- Always target `dev` unless the issue specifies otherwise.
- The PR title should follow commit message conventions: `type(scope): description (#issue)`.
