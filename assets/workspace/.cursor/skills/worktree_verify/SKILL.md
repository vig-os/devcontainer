---
name: worktree_verify
description: Autonomous verification — full test suite + lint + precommit, evidence only, loops on failure.
disable-model-invocation: true
---

# Autonomous Verify

Run full verification and provide evidence **without user interaction**. This is the worktree variant of [code:verify](../code_verify/SKILL.md). On failure, loop back to fix.

**Rule: no "should work" or "looks correct". Evidence only. No blocking for feedback.**

## Precondition: Issue Branch Required

1. Run: `git branch --show-current`
2. The branch name **must** match `<type>/<issue_number>-<summary>` (e.g. `feature/79-declarative-sync-manifest`). See [branch-naming.mdc](../../rules/branch-naming.mdc) for the full convention.
3. Extract the `<issue_number>` from the branch name.

## Workflow Steps

### 1. Run full verification

Execute all relevant checks:

```bash
just test              # full test suite
just lint              # linters
just precommit         # pre-commit hooks on all files
```

Run each command fully. Do not rely on partial output or previous runs.

### 2. Analyze results

- Check exit codes.
- Count failures and warnings.
- For each check, record:

  ```
  Verification: <what was checked>
  Command: <what was run>
  Result: <pass/fail with key output>
  ```

### 3. Handle failures

If any check fails:

1. Diagnose the root cause from the output.
2. Fix the issue.
3. Commit the fix.
4. Re-run verification from step 1.
5. Repeat until all checks pass.

If stuck after 3 attempts on the same failure, use [worktree:ask](../worktree_ask/SKILL.md) to post a question on the issue.

### 4. Proceed to PR

Once all checks pass, invoke [worktree:pr](../worktree_pr/SKILL.md) to create the pull request.

## Important Notes

- Never claim "done" without running the commands in this session.
- Never skip a check because it "probably passes".
- Evidence-based reporting only — include actual command output.
