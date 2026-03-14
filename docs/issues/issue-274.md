---
type: issue
state: closed
created: 2026-03-12T12:54:01Z
updated: 2026-03-12T14:03:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/274
comments: 0
labels: none
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:57.785Z
---

# [Issue 274]: [fix: PR fingerprint check blocks plain-text mentions of Cursor/Copilot](https://github.com/vig-os/devcontainer/issues/274)

## Problem
The PR title/body fingerprint check is producing false positives when normal prose mentions AI tooling names (for example, \"Cursor\" or \"Copilot\").

Observed run:
- Workflow run: https://github.com/vig-os/devcontainer/actions/runs/23002702709
- Job: https://github.com/vig-os/devcontainer/actions/runs/23002702709/job/66791079620?pr=270

Note: that specific job failed first on PR title format, but the same workflow includes `check-pr-agent-fingerprints`, and local repro confirms the false-positive behavior.

## Reproduction
Run locally:

```bash
PR_TITLE='docs: mention copilot integration' \\
PR_BODY='This PR updates Cursor docs with plain text mention of Copilot as comparison.' \\
uv run check-pr-agent-fingerprints
```

Current result:
- exits non-zero
- prints: `PR title or body contains blocked AI agent fingerprint: 'cursor'`

## Expected behavior
Plain-text references to tools/vendors in documentation or explanatory text should not fail the check by default. The check should block agent identity fingerprints (trailers, bot identities, explicit attribution patterns), not generic mentions.

## Likely root cause
`.github/agent-blocklist.toml` includes broad name substrings under `[patterns].names`, including:
- `cursor`
- `copilot`

Because matching is case-insensitive substring-based, any ordinary text mentioning those words is rejected.

## Suggested direction
Narrow matching scope so it targets identity attribution patterns instead of broad substrings. For example:
- keep strict trailer checks (`Co-authored-by`, etc.)
- restrict name matching to attribution contexts (author lines/signatures), or
- add explicit allow patterns/contexts for normal prose references.
