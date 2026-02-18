---
name: issue-triage
description: Triage open GitHub issues by analyzing them across priority, area, effort, SemVer impact, dependencies, and release readiness. Groups related issues into parent/sub-issue clusters, suggests milestone assignments, and applies approved changes via gh CLI. Use when the user asks to triage issues, groom the backlog, plan a milestone, or organize open issues.
---

# Issue Triage

Perform a full triage of all open issues in the current GitHub repo. Analyze
each issue across 7 dimensions, group related issues into parent/sub-issue
clusters, and suggest milestone assignments. All mutations require explicit
user approval.

## Phase 1: Collect

Gather all data needed for analysis. Run these commands and hold the results
in memory:

```bash
# Open issues (all fields needed for analysis)
gh issue list --state open --limit 200 \
  --json number,title,labels,milestone,assignees,body,createdAt,updatedAt

# Open PRs (for readiness context -- which issues have active work)
gh pr list --state open --json number,title,headRefName,labels,milestone

# Milestones
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | {number,title,state,open_issues,closed_issues}'

# Labels
gh label list --json name,description,color

# Existing sub-issue relationships (for each issue, skip 404s)
# List sub-issues of an issue:
gh api repos/{owner}/{repo}/issues/{n}/sub_issues 2>/dev/null
# Get parent of an issue:
gh api repos/{owner}/{repo}/issues/{n}/parent 2>/dev/null
```

Also read `.github_data/issues/` for local issue markdown files if available.

Determine `{owner}/{repo}` with:

```bash
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

## Phase 2: Check label taxonomy

Read [label-taxonomy.md](label-taxonomy.md) for the expected labels.

1. Compare the repo labels from Phase 1 against the taxonomy.
2. If any labels are missing, present them grouped by category (see example below).
3. Create approved labels with `gh label create`.

Example prompt for missing labels:

```
Missing labels:
  Priority: priority:blocking, priority:high, priority:medium, ...
  Area: area:ci, area:image, ...
Approve all / pick individually / skip?
```

Example label creation:

```bash
gh label create "priority:high" --color "d93f0b" \
  --description "Should be done in the current milestone"
```

## Phase 3: Analyze and build decision matrix

For each open issue, analyze the title, body, and existing labels to suggest
values across all 7 dimensions:

| Dimension | Values | How to determine |
|-----------|--------|-----------------|
| **Type** | existing labels: `feature`, `bug`, `question`, `task`, etc. | Already on the issue |
| **Area** | `ci`, `image`, `workspace`, `workflow`, `docs`, `testing` | Keywords in title/body, files referenced |
| **Priority** | `blocking`, `high`, `medium`, `low`, `backlog` | Impact described in body, dependency chains, age |
| **Effort** | `small`, `medium`, `large` | Scope of change described, number of files/components |
| **SemVer** | `major`, `minor`, `patch` | Breaking vs additive vs fix |
| **Readiness** | `needs design`, `ready`, `in progress`, `done` | Linked PRs/branches, design docs in body |
| **Dependencies** | Issue numbers | Cross-references in bodies (#N, "depends on", "blocks") |

### Grouping into clusters

Identify clusters of related issues:

1. **Shared area** -- multiple issues with the same inferred area
2. **Cross-references** -- issues that reference each other (`#N`, "depends on", "blocks", "related to")
3. **Thematic similarity** -- issues about the same component or initiative

For each cluster, determine a parent:
- If an existing open issue has **epic-level scope** (broad title, multiple sub-tasks implied), suggest it as parent
- Otherwise, suggest **creating a new parent issue** with a title summarizing the cluster

Issues that don't belong to any cluster go in an **Ungrouped** section.

### Matrix format

Present as grouped tables, one per cluster:

```
## Triage Decision Matrix

### Cluster: "<theme>" (suggested parent: #N or NEW)
| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| P #N | Parent issue title... | ... | ... | ... | ... | ... | ... | ... | ... |
| └ #M | Sub-issue title... | ... | ... | ... | ... | ... | ... | ... | #X |

### Ungrouped
| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #K | Standalone issue... | ... | ... | ... | ... | ... | ... | ... | ... |
```

Column key:
- **#**: `P` = parent, `P #N` = existing issue as parent, `└ #N` = sub-issue
- **Milestone**: suggest a SemVer milestone (`0.3`, `0.4`, etc.) or `backlog`
- **Deps**: issue numbers this issue depends on

## Phase 4: Present and get approval

1. Show the full decision matrix.
2. Ask the user to review. They can:
   - **Override any cell** (change priority, milestone, effort, etc.)
   - **Reassign rows** to different clusters or ungrouped
   - **Reject clusters** or individual suggestions
3. Iterate until the user says the matrix is approved.

## Phase 5: Apply changes (batched)

Present each batch for approval before executing. Wait for confirmation
between batches.

### Batch 1: New parent issues

For each cluster where the parent is NEW:

```bash
gh issue create --title "<cluster theme>" --label "<labels>" \
  --body "<description referencing sub-issues>"
```

Report the created issue number.

### Batch 2: Sub-issue links

Link sub-issues to their parents using the GitHub sub-issues REST API:

```bash
# Get the node_id of the child issue
CHILD_NODE_ID=$(gh issue view {child_number} --json nodeId --jq '.nodeId')

# Add as sub-issue to parent
gh api repos/{owner}/{repo}/issues/{parent_number}/sub_issues \
  -f sub_issue_id="$CHILD_NODE_ID"
```

If the API returns 404, warn the user that sub-issues may not be enabled
for this repo and skip this batch.

### Batch 3: Label assignments

```bash
gh issue edit {n} --add-label "priority:high,area:ci,effort:small,semver:minor"
```

### Batch 4: Milestone assignments

Create new milestones if needed:

```bash
gh api repos/{owner}/{repo}/milestones -f title="0.4"
```

Assign milestones:

```bash
gh issue edit {n} --milestone "0.3"
```

### Batch 5: Summary

Print a summary of all changes made:
- New parent issues created (with numbers)
- Sub-issue links added
- Labels applied
- Milestones assigned
- Issues left unchanged (and why)

## Error Handling

- **404 on sub-issue endpoints**: Warn user that sub-issues may not be enabled. Skip sub-issue batches, continue with labels and milestones.
- **Label creation failure** (duplicate): Skip gracefully, the label already exists.
- **Milestone creation failure**: Report error, continue with other milestones.
- **Never retry destructive operations**: Report the failure and let the user decide.

## Important Notes

- **Never mutate without approval.** Every change is presented first and requires explicit confirmation.
- Milestones follow SemVer (e.g. `0.3`, `0.4`, `1.0`) matching the project release cycle.
- Existing sub-issue relationships discovered in Phase 1 should be preserved -- only add new links, never remove existing ones.
- If an issue already has a milestone, show it in the matrix but don't suggest changing it unless the user asks.
