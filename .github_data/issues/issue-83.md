---
type: issue
state: open
created: 2026-02-18T16:28:59Z
updated: 2026-02-18T16:50:07Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/83
comments: 0
labels: feature
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-18T16:59:39.794Z
---

# [Issue 83]: [[FEATURE] Integrate GitHub Projects into triage skill for board-level tracking](https://github.com/vig-os/devcontainer/issues/83)

### Description

Extend the issue triage skill (`.cursor/skills/issue-triage/`) to interact with GitHub Projects (v2) via `gh` CLI / GraphQL API. After triaging issues into clusters with milestones and labels, the skill would also manage project board placement — adding issues to the correct project, setting custom fields (status, priority, sprint), and reflecting the triage decisions on the board.

### Problem Statement

The triage skill currently operates only on issues (labels, milestones, sub-issues). GitHub Projects provide a board/table view with custom fields (Status, Priority, Effort, etc.) that are separate from issue labels. After triage, someone must manually drag issues into the project board and set fields — duplicating what the skill already decided.

### Proposed Solution

Use `gh project` and `gh api graphql` to:

1. **List org/repo projects** — `gh project list --owner vig-os`
2. **Add issues to a project** — `gh project item-add <project_number> --owner vig-os --url <issue_url>`
3. **Set custom fields** — via GraphQL mutations (`updateProjectV2ItemFieldValue`) to set Status, Priority, Effort, etc. from the triage matrix values
4. **Read existing project items** — to avoid duplicates and detect issues already on the board

Add a new optional Phase 5.5 (after labels/milestones, before summary) that:
- Asks the user which project to target (or auto-detects if there's only one)
- Maps triage dimensions to project fields (Priority label → Priority field, Readiness → Status field)
- Adds issues to the project and sets fields in a single batch (with approval)

### Alternatives Considered

- **Manual board management** — current state; works but duplicates triage effort
- **GitHub Actions automation** — trigger on label changes to auto-add to project; decouples from triage flow
- **Only use labels, skip projects** — simpler but loses the board/table visualization

### Additional Context

- `gh project` CLI commands are available since `gh` v2.21+
- Custom field mutations require the GraphQL API (REST API doesn't support project v2 fields)
- Related to #81 (triage skill) and #82 (triage discussion)

### Impact

- Benefits project maintainers who use GitHub Projects for sprint planning
- Backward compatible — purely additive, opt-in during triage
- No impact if no project exists in the org/repo

### Changelog Category

Added
