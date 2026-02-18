---
type: issue
state: open
created: 2026-02-18T13:36:16Z
updated: 2026-02-18T13:36:16Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/81
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T13:36:37.325Z
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
