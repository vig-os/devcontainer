---
name: code:review
description: Performs a structured self-review of changes before submitting a PR.
disable-model-invocation: true
---

# Self-Review

Structured self-review of changes before submitting a PR.

## Workflow Steps

### 1. Gather context

Determine the base branch (the branch this PR will merge into):

```bash
# If a PR exists for the current branch, use its base
BASE=$(gh pr view --json baseRefName --jq '.baseRefName' 2>/dev/null)
# Otherwise fall back to the default branch
: "${BASE:=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')}"
```

Then review the diff:

```bash
git diff "$BASE"...HEAD --stat
git log "$BASE"..HEAD --oneline
```

- Read the linked issue's acceptance criteria.

### 2. Review diff against requirements

- For each acceptance criterion, verify it is addressed in the diff.
- Flag any criterion that is not covered.
- Flag any change that is not traceable to a requirement (scope creep).

### 3. Check project standards

- **Changelog**: is `CHANGELOG.md` updated under `## Unreleased`? Does the entry match the changes?
- **Commit messages**: do all commits follow [commit-messages.mdc](../../rules/commit-messages.mdc)?
- **Tests**: are there tests for new/changed behavior?
- **Docs**: are documentation changes needed? Were templates in `docs/templates/` edited (not generated files)?

### 4. Produce review report

Report findings in this structure:

```
## Review: <branch> → <base>

### Acceptance Criteria
- [x] Criterion 1 — covered by <file/commit>
- [ ] Criterion 2 — NOT addressed

### Issues
- **Critical**: <blocks merge> (if any)
- **Important**: <should fix before merge> (if any)
- **Minor**: <nice to have> (if any)

### Assessment
Ready to submit / Needs fixes before PR
```

### 5. Fix or proceed

- If Critical or Important issues found, fix them before proceeding.
- If only Minor issues, note them and proceed to [pr:create](../pr:create/SKILL.md).

## Important Notes

- Run this before every PR submission. The [pr:create](../pr:create/SKILL.md) workflow should reference this as a prerequisite.
- Do not skip the acceptance criteria check — it catches the most common agent failure (incomplete work).
