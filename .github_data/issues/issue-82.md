---
type: issue
state: closed
created: 2026-02-18T15:53:14Z
updated: 2026-02-18T18:44:46Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/82
comments: 2
labels: discussion
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-18T18:45:03.211Z
---

# [Issue 82]: [[DISCUSSION] Backlog triage: proposed clustering, milestones, and label assignments](https://github.com/vig-os/devcontainer/issues/82)

cc @c-vigo

## Description

Full triage of all 19 open issues, proposing clustering into parent/sub-issue groups, milestone assignments (0.3, 0.4, backlog), and label classifications across priority, area, effort, and SemVer impact.

## TL;DR

- **19 open issues** analyzed across 7 dimensions (type, area, priority, effort, SemVer, readiness, dependencies)
- **6 clusters** identified — grouped by theme, with parent/sub-issue relationships proposed
- **18 new triage labels** created (priority, area, effort, semver) per the taxonomy in `.cursor/skills/issue-triage/label-taxonomy.md`
- **Milestone 0.4** to be created for medium-term work
- **Key decisions made:**
  - #67 moves to **0.4** (parent tracks the full initiative; closes when all sub-issues are done)
  - #63 moves to **0.3** (agent workflow commands needed sooner)
  - #80 (label reconciliation) is a blocker — assigned 0.3 with high priority
  - #27 (Nix/devenv) moved to **backlog** — exploratory, needs design
  - #70 (remote devcontainer) deferred to backlog (depends on #71 which is 0.4)
  - Discussions (#59, #17, #40) remain in backlog with no milestone

### Milestone breakdown

| Milestone | Count | Issues |
|-----------|-------|--------|
| **0.3** | 9 | #18, #80, #81, #61, #63, #69, #79, #57, #58 |
| **0.4** | 5 | #67, #64, #71, #73, #66 |
| **backlog** | 5 | #27, #70, #59, #17, #40 |

## Context / Motivation

We have 19 open issues with only 2 assigned to a milestone, no priority/area/effort labels, and no sub-issue structure. Manual triage keeps falling behind. This was generated using the new agent triage skill (#81) to bring structure to the backlog before the 0.3 release.

## Full Decision Matrix

### Cluster 1: "Agent-Driven Development Workflows" (existing parent: #67)

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| P #67 | Consolidate sync-manifest and sync-workspace into declarative Python manifest | feature | workspace | high | large | minor | in progress | 0.4 | — |
| └ #61 | Add agent-friendly issue templates, changelog rule, PR template enhancements | feature | workflow | medium | medium | minor | ready | 0.3 | — |
| └ #63 | Add Cursor commands and rules for agent-driven development workflows | feature | workflow | medium | large | minor | ready | 0.3 | #61 |
| └ #80 | Reconcile issue template labels with repository labels | feature | workflow | high | small | patch | ready | 0.3 | — |
| └ #81 | Agent skill for issue triage, milestone planning, sub-issue grouping | feature | workflow | medium | medium | minor | in progress | 0.3 | #80 |
| └ #64 | Add Cursor worktree support for parallel agent development | feature | workflow | low | medium | minor | needs design | 0.4 | #63 |

New sub-issue links: #80, #81, #64 → parent #67

### Cluster 2: "Workspace Tooling & Justfile" (suggested parent: #71)

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| P #71 | Expand justfile.base with devcontainer, quality, security, docs, info, and git recipes | feature | workspace | medium | large | minor | ready | 0.4 | — |
| └ #73 | Wire up version-check notification and add host-side devcontainer-upgrade recipe | feature | workspace | medium | medium | minor | ready | 0.4 | #71 |
| └ #66 | Improve workspace init: global just command and better non-empty error output | feature | workspace | low | medium | minor | ready | 0.4 | #71 |

New sub-issue links: #73, #66 → parent #71

### Cluster 3: "Remote Development"

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #70 | Remote devcontainer orchestration via just recipe | feature | workspace | low | large | minor | needs design | backlog | #71 |

### Cluster 4: "CI & Build Pipeline"

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #69 | Run pre-commit formatting in sync-issues workflow before committing | chore | ci | high | small | patch | ready | 0.3 | — |
| #79 | Automatic commit message for pull request merge | feature | ci | medium | small | patch | ready | 0.3 | — |
| #59 | Local build vs. CI build: intended parity? | discussion | ci | low | — | — | needs design | backlog | — |

### Cluster 5: "Container Image & Build"

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #27 | Adopt Nix/devenv for reproducible, auditable dependency management | feature | image | low | large | minor | needs design | backlog | — |
| #17 | Python base image vs uv-managed Python | discussion | image | low | — | — | needs design | backlog | — |
| #57 | Inconsistent version tag convention (v prefix) | bug | ci | medium | small | patch | ready | 0.3 | — |

### Cluster 6: "Testing Infrastructure"

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #18 | Auto-cleanup test containers on failure with --keep-containers flag | feature | testing | medium | medium | minor | ready | 0.3 | — |

### Ungrouped

| # | Title | Type | Area | Priority | Effort | SemVer | Readiness | Milestone | Deps |
|---|-------|------|------|----------|--------|--------|-----------|-----------|------|
| #58 | validate-commit-msg: enforce types/scopes/refs by default | feature | workflow | medium | small | minor | ready | 0.3 | — |
| #40 | [DISCUSSION] Migration to prek | discussion | workflow | backlog | — | — | needs design | backlog | — |

## Open Questions

- Is 0.3 too loaded (9 issues) vs 0.4 (5 issues)?
- Should we create parent issues for Clusters 4 and 5, or leave them flat?
- Any priority overrides? (e.g. #69 sync-issues formatting is marked high — it causes CI failures on unrelated PRs)

## Related Issues

All 19 open issues: #17, #18, #27, #40, #57, #58, #59, #61, #63, #64, #66, #67, #69, #70, #71, #73, #79, #80, #81

## Changelog Category

No changelog needed
---

# [Comment #1]() by [c-vigo]()

_Posted on February 18, 2026 at 04:06 PM_

Looks very cool indeed, should such a matrix be tracked locally inside `docs`?

---

# [Comment #2]() by [gerchowl]()

_Posted on February 18, 2026 at 06:44 PM_

Closing this discussion — the proposed triage plan has been reviewed and the decisions captured here have been applied (milestone assignments, label classifications, clustering). Future triage iterations will be tracked via the agent triage skill (#81).

