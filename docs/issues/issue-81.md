---
type: issue
state: closed
created: 2026-02-18T13:36:16Z
updated: 2026-02-18T16:30:57Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/81
comments: 3
labels: feature, priority:medium, area:workflow, effort:medium, semver:minor
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T00:08:07.130Z
---

# [Issue 81]: [[FEATURE] Agent skill for issue triage, milestone planning, and sub-issue grouping](https://github.com/vig-os/devcontainer/issues/81)

### Description

A Cursor agent skill (`.cursor/skills/issue-triage/`) that performs a full triage of all open GitHub issues in the current repo. When invoked, it collects all open issues, milestones, labels, and existing sub-issue relationships, then analyzes each issue across multiple dimensions and presents a decision matrix with grouped suggestions. All mutations (milestone assignment, label changes, sub-issue linking, new milestone/parent issue creation) require explicit user approval.

### Problem Statement

Issues accumulate rapidly during development -- from working on other tasks, brainstorming sessions, and ad-hoc discoveries. Currently there is no structured process to:
- Classify issues by area, priority, effort, SemVer impact, or dependencies
- Group related issues into parent/sub-issue hierarchies
- Assign issues to SemVer milestones (e.g. `0.3`, `0.4`)
- Identify gaps (orphaned issues, missing milestones, unlabeled items)

The result is 16 open issues with only 2 assigned to a milestone, no priority labels, and no sub-issue structure. Manual triage is tedious and falls behind.

### Proposed Solution

**Cursor agent skill** at `.cursor/skills/issue-triage/SKILL.md` with a supporting `label-taxonomy.md` reference file. The skill instructs the agent to:

1. **Collect** -- Fetch all open issues, open PRs (for context), milestones, labels, and existing sub-issue relationships via `gh` CLI and `gh api`
2. **Analyze** -- Score each issue across 7 dimensions:
   - Type (feature, bug, question, task, refactor)
   - Area/component (CI/CD, container image, workspace tooling, developer workflow, docs, testing)
   - Priority (blocking, high, medium, low, backlog)
   - Effort (small, medium, large)
   - SemVer impact (MAJOR, MINOR, PATCH)
   - Dependencies/blockers (which issues depend on or block others)
   - Release readiness (needs design, ready to implement, in progress, done)
3. **Present decision matrix** -- A formatted table showing all issues with their suggested classifications
4. **Group** -- Suggest parent/sub-issue relationships using GitHub's native sub-issues API (`gh api repos/{owner}/{repo}/issues/{issue_number}/sub_issues`)
5. **Milestone** -- Suggest milestone assignments (SemVer-based: `0.3`, `0.4`, etc.), including creating new milestones if needed
6. **Apply** -- Execute approved changes one-by-one after user confirmation

**Label taxonomy** predefined in `label-taxonomy.md`:
- `priority:blocking`, `priority:high`, `priority:medium`, `priority:low`, `priority:backlog`
- `area:ci`, `area:image`, `area:workspace`, `area:workflow`, `area:docs`, `area:testing`
- `effort:small`, `effort:medium`, `effort:large`
- `semver:major`, `semver:minor`, `semver:patch`

The skill creates any missing labels on first run (with user approval).

**Sync manifest update**: `scripts/sync_manifest.py` (and the corresponding `requirements.yaml`) will need to be updated to include the new `.cursor/skills/issue-triage/` directory in the workspace sync process, ensuring the skill is propagated to `assets/workspace/` alongside existing commands and rules.

### Alternatives Considered

- **Cursor command (`.cursor/commands/`)** -- Older Cursor pattern, less discoverable. Skills are the modern approach and better suited for complex, multi-step workflows.
- **External script** -- A standalone Python script could do the analysis, but would lose the interactive suggest-and-approve loop that makes agent-driven triage valuable.
- **GitHub Projects board** -- Useful for visualization but doesn't provide the automated analysis and suggestion engine.

### Additional Context

- **Depends on #80** -- The label taxonomy defined here relies on the repo labels being reconciled first. Issue #80 (Reconcile issue template labels with repository labels) must be resolved so the triage skill can use a consistent, complete set of labels for grouping and classification.
- Sub-issues use the GitHub REST API (`POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`). The `gh` CLI does not yet have native sub-issue flags (cli/cli#10298), so the skill uses `gh api` directly.
- Milestones follow SemVer (e.g. `0.3`, `0.4`, `1.0`) matching the project's release cycle documented in `docs/RELEASE_CYCLE.md`.
- The skill should be invoked explicitly (not auto-triggered).
- Interaction model: suggest everything, user approves each action.

### Impact

- All project contributors benefit from structured backlog management
- No breaking changes -- purely additive (new skill + new labels)
- Backward compatible with existing issues and milestones

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 02:56 PM_

## Design: Issue Triage Agent Skill

### Overview & Architecture

A Cursor agent skill at `.cursor/skills/issue-triage/SKILL.md` that, when explicitly invoked, performs a full triage of all open GitHub issues. It:

1. **Collects** all open issues, PRs (for context), milestones, labels, and existing sub-issue relationships via `gh` CLI
2. **Analyzes** each issue across 7 dimensions (decision matrix)
3. **Presents** a triage report with issues grouped into parent/sub-issue clusters
4. **Applies** approved changes one-by-one (milestones, labels, sub-issue links, new parent issues, new milestones)

**Trigger:** Only when user explicitly asks (e.g. "triage issues", "backlog grooming").

**Interaction model:** Suggest everything, user approves each action. No mutations without confirmation.

**Files:**

```
.cursor/skills/issue-triage/
├── SKILL.md              # Main skill instructions (~300-400 lines)
└── label-taxonomy.md     # Label definitions (reference file read on demand)
```

Additionally, `scripts/sync_manifest.py` / `requirements.yaml` updated to sync `.cursor/skills/` to `assets/workspace/.cursor/skills/`.

---

### Label Taxonomy

Predefined in `label-taxonomy.md`. The skill checks for missing labels on first run and asks user to approve creation.

| Category | Labels | Color | Description |
|----------|--------|-------|-------------|
| **Priority** | `priority:blocking` | `#b60205` (red) | Blocks other work or a release |
| | `priority:high` | `#d93f0b` (orange) | Should be done in the current milestone |
| | `priority:medium` | `#fbca04` (yellow) | Important but not urgent |
| | `priority:low` | `#0e8a16` (green) | Nice to have, do when capacity allows |
| | `priority:backlog` | `#c5def5` (light blue) | Someday/maybe, no timeline |
| **Area** | `area:ci` | `#1d76db` | CI/CD, GitHub Actions, workflows |
| | `area:image` | `#1d76db` | Container image, Dockerfile, build |
| | `area:workspace` | `#1d76db` | Workspace tooling, justfile, templates |
| | `area:workflow` | `#1d76db` | Developer workflow, commands, rules, skills |
| | `area:docs` | `#1d76db` | Documentation, README, guides |
| | `area:testing` | `#1d76db` | Test infrastructure, BATS, pytest |
| **Effort** | `effort:small` | `#c2e0c6` | < 1 hour |
| | `effort:medium` | `#fef2c0` | 1-4 hours |
| | `effort:large` | `#f9d0c4` | > 4 hours or multi-session |
| **SemVer** | `semver:major` | `#b60205` | Breaking change |
| | `semver:minor` | `#fbca04` | New feature, backward-compatible |
| | `semver:patch` | `#0e8a16` | Bug fix, backward-compatible |

Existing labels (`bug`, `feature`, `question`, `documentation`, etc.) remain as-is and serve as the **type** dimension.

---

### Decision Matrix & Hierarchy

#### Grouping logic

1. Agent reads all open issues and identifies **clusters** — issues that are thematically related (same area, overlapping scope, or one is a prerequisite for another).
2. For each cluster, it either:
   - Identifies an **existing issue** that naturally serves as the parent (epic-level scope), or
   - Suggests **creating a new parent issue** to represent the cluster
3. Standalone issues that don't belong to any cluster are listed in an "Ungrouped" section.

#### Matrix format

Grouped tables, one per cluster, with ungrouped section at the end:

```
### Cluster: "Developer Workflow Tooling" (suggested parent: NEW)
| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| P | [NEW parent issue title] | feature | workflow | high | large | minor | — | 0.3 | — |
| └ 63 | Add Cursor commands... | feature | workflow | medium | medium | minor | ready | 0.3 | — |
| └ 64 | Add Cursor worktree... | feature | workflow | medium | medium | minor | needs design | 0.3 | #63 |

### Cluster: "Release & CI" (suggested parent: #57)
| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| P #57 | Inconsistent version tag... | bug | ci | high | small | patch | ready | 0.3 | — |
| └ 69 | Run pre-commit in sync... | task | ci | low | small | patch | ready | 0.3 | — |

### Ungrouped
| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| 17 | Python base image vs uv | question | image | low | — | — | needs design | backlog | — |
```

#### Column definitions

| Column | Values | Source |
|--------|--------|--------|
| **#** | Issue number, `P` for parent, `└` for sub-issue | Hierarchy analysis |
| **Type** | Existing labels: `feature`, `bug`, `question`, `task`, etc. | Current labels |
| **Area** | `ci`, `image`, `workspace`, `workflow`, `docs`, `testing` | Agent analysis |
| **Priority** | `blocking`, `high`, `medium`, `low`, `backlog` | Agent analysis |
| **Effort** | `small`, `medium`, `large` | Agent analysis |
| **SemVer** | `major`, `minor`, `patch` | Agent analysis |
| **Readiness** | `needs design`, `ready`, `in progress`, `done` | Linked PRs/branches/design docs |
| **Milestone** | e.g. `0.3`, `0.4`, `backlog` | Agent suggestion |
| **Deps** | Issue numbers this issue depends on | Cross-references in bodies |

#### User review actions

1. **Approve clusters** — agent creates parent issues (if new) and links sub-issues via `gh api`
2. **Reassign rows** — move an issue to a different cluster or ungrouped
3. **Override any cell** — change suggested priority, milestone, effort, etc.
4. **Approve labels** — agent applies label changes
5. **Approve milestones** — agent assigns milestones (creating new ones if needed)

Each action type presented as a batch: "Approve all / pick individually?"

---

### Workflow Steps

#### Phase 1: Collect

1. `gh issue list --state open --limit 200 --json number,title,labels,milestone,assignees,body`
2. `gh pr list --state open --json number,title,headRefName,labels,milestone`
3. `gh api repos/{owner}/{repo}/milestones --jq '.[] | {number,title,state,open_issues,closed_issues}'`
4. `gh label list --json name,description,color`
5. For each issue: `gh api repos/{owner}/{repo}/issues/{n}/sub_issues` and `gh api repos/{owner}/{repo}/issues/{n}/parent` (batch, skip 404s)
6. Read `.github_data/issues/` for local context

#### Phase 2: Check label taxonomy

1. Compare repo labels against `label-taxonomy.md`
2. Present missing labels: "These labels need to be created. Approve all / pick / skip?"
3. Create approved labels: `gh label create "priority:high" --color "d93f0b" --description "..."`

#### Phase 3: Analyze & build decision matrix

1. Analyze each issue (title + body + labels) to suggest values for all 7 dimensions
2. Identify clusters by shared area, cross-references, thematic similarity
3. Determine parent for each cluster (existing issue or suggest new)
4. Build grouped decision matrix

#### Phase 4: Present & approve

1. Show full decision matrix
2. User can override any cell, reassign clusters, reject suggestions
3. Proceed to apply after user is satisfied

#### Phase 5: Apply (batched by action type)

**Batch 1 — New parent issues:** `gh issue create --title "..." --label "..." --body "..."`
**Batch 2 — Sub-issue links:** `gh api repos/{owner}/{repo}/issues/{parent}/sub_issues -f sub_issue_id={child_node_id}`
**Batch 3 — Label assignments:** `gh issue edit {n} --add-label "priority:high,area:ci,..."`
**Batch 4 — Milestone assignments:** Create new milestones if needed (`gh api repos/{owner}/{repo}/milestones -f title="0.4"`), then `gh issue edit {n} --milestone "0.3"`
**Batch 5 — Summary:** Print all changes made, note unchanged issues

#### Error handling

- 404 on sub-issue endpoints → warn user, skip batch
- Label creation failure (duplicate) → skip gracefully
- Milestone creation failure → report, continue with others
- Never retry destructive operations — report failure, let user decide

---

### Testing strategy

This is a skill (markdown instructions), not code. Validation is manual: invoke the skill on the actual repo and verify the triage output is sensible. The label taxonomy file can be validated by checking that all labels are parseable (name, color, description).

---

# [Comment #2]() by [gerchowl]()

_Posted on February 18, 2026 at 03:01 PM_

## Implementation Plan

- [x] Task 1: Create `label-taxonomy.md` reference file with all predefined labels
- [x] Task 2: Create `SKILL.md` with the full triage skill instructions
- [x] Task 3: Add `.cursor/skills/` entry to the sync manifest in `scripts/sync_manifest.py`
- [x] Task 4: Run `just sync-workspace` and verify the skill is propagated to `assets/workspace/`
- [x] Task 5: Update `CHANGELOG.md` Unreleased section

---

# [Comment #3]() by [gerchowl]()

_Posted on February 18, 2026 at 03:40 PM_

Implemented in PR #68 on branch `feature/67-declarative-sync-manifest`.

Commits:
- `feat: add issue triage agent skill with label taxonomy`
- `chore: add .cursor/skills/ to sync manifest`
- `chore: sync issue-triage skill to workspace template`
- `docs: add issue triage skill to CHANGELOG`
- `refactor: migrate cursor commands to skills and fix stale links`

