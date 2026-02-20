---
name: ci_check
description: Checks the CI pipeline status for the current branch or PR.
disable-model-invocation: true
---

# Check CI Status

Check the CI pipeline status for the current branch or PR.

## Workflow Steps

### 1. Identify context

- If on a branch with an open PR: `gh pr checks`
- If no PR exists: `gh run list --branch $(git branch --show-current) --limit 5`

### 2. Show status per workflow

Report each workflow's status:

```
CI Status for <branch/PR>:
- CI: ✓ pass / ✗ fail / ○ pending
- CodeQL: ✓ pass / ✗ fail / ○ pending
- Scorecard: ✓ pass / ✗ fail / ○ pending
- Security Scan: ✓ pass / ✗ fail / ○ pending
```

### 3. On failure

- Show the failing job name and step.
- Run `gh run view <run-id> --log-failed` to fetch the failure log.
- Summarize the error (first relevant error line, not the full log).
- Suggest next steps: fix locally, or use [ci_fix](../ci_fix/SKILL.md) for deeper diagnosis.

## Important Notes

- If CI is still running, report "pending" and suggest waiting or checking back.
- Do not guess the cause of a failure. Fetch the actual log.
