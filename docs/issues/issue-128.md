---
type: issue
state: open
created: 2026-02-20T16:18:37Z
updated: 2026-02-20T16:48:23Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/128
comments: 1
labels: chore, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T16:48:51.266Z
---

# [Issue 128]: [[CHORE] Improve agent skills DX: rename colon namespace to underscore and enhance issue_create workflow](https://github.com/vig-os/devcontainer/issues/128)

### Chore Type

Configuration change

### Description

Two DX improvements for agent skills:

**1. Rename skill directory namespace separator from `:` to `_`**
Skill directories under `.cursor/skills/` currently use `:` as the namespace separator (e.g., `issue:create`, `code:tdd`). Colons in directory names don't work cleanly with Cursor's `@` reference mechanism. Switching to `_` (e.g., `issue_create`, `code_tdd`) will make `@`-based skill invocation reliable.

**2. Enhance `issue_create` skill to gather context before drafting**
The `issue_create` skill should run `just gh-issues` (via `scripts/gh_issues.py`) before drafting a new issue to get an overview of all open issues, milestones, and parent/child relationships. This enables the skill to:
- Suggest parent/child issue coordination (avoid duplicates, link related work)
- Reference `.github/ISSUE_TEMPLATE/` templates and `.github/label-taxonomy.toml` for correct labels
- Suggest an appropriate milestone based on the current backlog

### Acceptance Criteria

- [ ] All skill directories under `.cursor/skills/` renamed from `namespace:action` to `namespace_action`
- [ ] All skill directories under `assets/workspace/.cursor/skills/` renamed likewise
- [ ] All internal cross-references between skills updated (e.g., links in SKILL.md files)
- [ ] `CLAUDE.md` command table updated to reflect new naming
- [ ] `.github/label-taxonomy.toml` comments updated
- [ ] Any other files referencing old skill directory names updated
- [ ] `issue_create` SKILL.md updated to include a step that runs `just gh-issues` output before drafting
- [ ] The new step instructs the agent to suggest parent/child issue relationships
- [ ] The new step instructs the agent to suggest a milestone

### Implementation Notes

**Rename scope:**
- `.cursor/skills/*` — ~26 skill directories to rename
- `assets/workspace/.cursor/skills/*` — mirrored skill directories
- `CLAUDE.md` — command table references `/ci:check`, `/issue:create`, etc.
- `.github/label-taxonomy.toml` — comments reference `.cursor/skills/issue:triage/SKILL.md` etc.
- Cross-references inside SKILL.md files (e.g., `../issue:claim/SKILL.md` → `../issue_claim/SKILL.md`)

**issue_create enhancement:**
- `just gh-issues` runs `scripts/gh_issues.py` which fetches open issues with milestones, labels, linked branches, parent/child sub-issue trees, and open PRs
- The skill should read `.github/ISSUE_TEMPLATE/*.yml` for the chosen template and `.github/label-taxonomy.toml` for valid labels
- Use the `just gh-issues` overview to suggest whether the new issue should be a sub-issue of an existing parent, or if it groups with other open issues under a milestone

### Priority

Medium

### Changelog Category

Changed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 04:48 PM_

## Implementation Plan

Issue: #128
Branch: chore/128-rename-skill-namespace-enhance-issue-create

TDD: Skipped — all changes are config/template/docs with no testable behavior.

### Tasks

#### Part 1: Directory Renames

- [ ] Task 1: Rename all 28 colon-style skill directories under `.cursor/skills/` to use `_` separator (e.g. `issue:create` → `issue_create`) — `git mv` each directory — verify: `ls .cursor/skills/ | grep ':'` returns nothing
- [ ] Task 2: Rename all 28 colon-style skill directories under `assets/workspace/.cursor/skills/` likewise — `git mv` each directory — verify: `ls assets/workspace/.cursor/skills/ | grep ':'` returns nothing

#### Part 2: Update Internal References

- [ ] Task 3: Update `name:` frontmatter field in all 28 SKILL.md files under `.cursor/skills/` (e.g. `name: issue:create` → `name: issue_create`) — verify: `grep -r 'name: .*:' .cursor/skills/*/SKILL.md` returns nothing
- [ ] Task 4: Update all cross-reference relative links in SKILL.md files under `.cursor/skills/` (e.g. `../issue:claim/SKILL.md` → `../issue_claim/SKILL.md`) — verify: `grep -r '\.\./[a-z]*:[a-z]' .cursor/skills/` returns nothing
- [ ] Task 5: Update `name:` frontmatter field in all mirrored SKILL.md files under `assets/workspace/.cursor/skills/` — verify: `grep -r 'name: .*:' assets/workspace/.cursor/skills/*/SKILL.md` returns nothing
- [ ] Task 6: Update all cross-reference relative links in SKILL.md files under `assets/workspace/.cursor/skills/` — verify: `grep -r '\.\./[a-z]*:[a-z]' assets/workspace/.cursor/skills/` returns nothing

#### Part 3: Update External References

- [ ] Task 7: Update `CLAUDE.md` command table — change all `/namespace:action` entries to `/namespace_action` (26 entries) — verify: `grep '/[a-z]*:[a-z]' CLAUDE.md` returns nothing
- [ ] Task 8: Update `.github/label-taxonomy.toml` — change 2 skill path references from colon to underscore — verify: `grep 'skills/.*:' .github/label-taxonomy.toml` returns nothing
- [ ] Task 9: Update `assets/workspace/.github/label-taxonomy.toml` — same 2 references — verify: `grep 'skills/.*:' assets/workspace/.github/label-taxonomy.toml` returns nothing
- [ ] Task 10: Update `CHANGELOG.md` — change 1 reference in Unreleased section (`skills/issue:triage/` → `skills/issue_triage/`) — verify: `grep 'skills/.*:' CHANGELOG.md` returns nothing

#### Part 4: Enhance `issue_create` Skill

- [ ] Task 11: Add a new step to `.cursor/skills/issue_create/SKILL.md` (post-rename) that runs `just gh-issues` before drafting to gather open issues overview, and instructs the agent to suggest parent/child issue relationships and an appropriate milestone — `.cursor/skills/issue_create/SKILL.md`, `assets/workspace/.cursor/skills/issue_create/SKILL.md` — verify: read updated SKILL.md contains the new step

#### Part 5: Final Verification

- [ ] Task 12: Global sweep — confirm no remaining colon-style skill directory references outside of historical docs (`docs/issues/`, `docs/pull-requests/`) — verify: `rg 'skills/[a-z]+:[a-z]' --glob '!docs/issues/*' --glob '!docs/pull-requests/*'` returns nothing

### Notes

- `solve-and-pr` directory already uses a hyphen — no rename needed.
- `worktree:*` directories use colons and are included in the rename scope (→ `worktree_*`).
- Historical docs under `docs/issues/` and `docs/pull-requests/` are snapshots and will not be updated.
- The `inception:explore/README.md` file also contains cross-references that need updating (covered by Tasks 4 and 6).

