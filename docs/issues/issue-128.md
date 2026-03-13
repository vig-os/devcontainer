---
type: issue
state: open
created: 2026-02-20T16:18:37Z
updated: 2026-02-20T23:04:04Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/128
comments: 3
labels: chore, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:18.189Z
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

- [x] Task 1: Rename all 28 colon-style skill directories under `.cursor/skills/` to use `_` separator (e.g. `issue:create` → `issue_create`) — `git mv` each directory — verify: `ls .cursor/skills/ | grep ':'` returns nothing
- [x] Task 2: Rename all 28 colon-style skill directories under `assets/workspace/.cursor/skills/` likewise — `git mv` each directory — verify: `ls assets/workspace/.cursor/skills/ | grep ':'` returns nothing

#### Part 2: Update Internal References

- [x] Task 3: Update `name:` frontmatter field in all 28 SKILL.md files under `.cursor/skills/` (e.g. `name: issue:create` → `name: issue_create`) — verify: `grep -r 'name: .*:' .cursor/skills/*/SKILL.md` returns nothing
- [x] Task 4: Update all cross-reference relative links in SKILL.md files under `.cursor/skills/` (e.g. `../issue:claim/SKILL.md` → `../issue_claim/SKILL.md`) — verify: `grep -r '\.\./[a-z]*:[a-z]' .cursor/skills/` returns nothing
- [x] Task 5: Update `name:` frontmatter field in all mirrored SKILL.md files under `assets/workspace/.cursor/skills/` — verify: `grep -r 'name: .*:' assets/workspace/.cursor/skills/*/SKILL.md` returns nothing
- [x] Task 6: Update all cross-reference relative links in SKILL.md files under `assets/workspace/.cursor/skills/` — verify: `grep -r '\.\./[a-z]*:[a-z]' assets/workspace/.cursor/skills/` returns nothing

#### Part 3: Update External References

- [x] Task 7: Update `CLAUDE.md` command table — change all `/namespace:action` entries to `/namespace_action` (26 entries) — verify: `grep '/[a-z]*:[a-z]' CLAUDE.md` returns nothing
- [x] Task 8: Update `.github/label-taxonomy.toml` — change 2 skill path references from colon to underscore — verify: `grep 'skills/.*:' .github/label-taxonomy.toml` returns nothing
- [x] Task 9: Update `assets/workspace/.github/label-taxonomy.toml` — same 2 references — verify: `grep 'skills/.*:' assets/workspace/.github/label-taxonomy.toml` returns nothing
- [x] Task 10: Update `CHANGELOG.md` — change 1 reference in Unreleased section (`skills/issue:triage/` → `skills/issue_triage/`) — verify: `grep 'skills/.*:' CHANGELOG.md` returns nothing

#### Part 4: Enhance `issue_create` Skill

- [x] Task 11: Add a new step to `.cursor/skills/issue_create/SKILL.md` (post-rename) that runs `just gh-issues` before drafting to gather open issues overview, and instructs the agent to suggest parent/child issue relationships and an appropriate milestone — `.cursor/skills/issue_create/SKILL.md`, `assets/workspace/.cursor/skills/issue_create/SKILL.md` — verify: read updated SKILL.md contains the new step

#### Part 5: Final Verification

- [x] Task 12: Global sweep — confirm no remaining colon-style skill directory references outside of historical docs (`docs/issues/`, `docs/pull-requests/`) — verify: `rg 'skills/[a-z]+:[a-z]' --glob '!docs/issues/*' --glob '!docs/pull-requests/*'` returns nothing

### Notes

- `solve-and-pr` directory already uses a hyphen — no rename needed.
- `worktree:*` directories use colons and are included in the rename scope (→ `worktree_*`).
- Historical docs under `docs/issues/` and `docs/pull-requests/` are snapshots and will not be updated.
- The `inception:explore/README.md` file also contains cross-references that need updating (covered by Tasks 4 and 6).

---

# [Comment #2]() by [gerchowl]()

_Posted on February 20, 2026 at 10:46 PM_

## Design

### Expand `tdd.mdc` into comprehensive testing guide

**Goal:** Make `tdd.mdc` the single reference for TDD process *and* test-scenario guidance, triggered when writing code (not always-on). Skills reference it instead of inlining TDD steps.

### Changes

#### 1. `tdd.mdc` frontmatter

Switch from `alwaysApply: true` to glob-triggered:

```yaml
description: TDD discipline and test scenario guidance when writing code
alwaysApply: false
globs:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.js"
  - "**/*.sh"
  - "**/test_*"
  - "**/*_test.*"
  - "**/tests/**"
```

#### 2. `tdd.mdc` content structure

Three sections in the rule:

**Section 1: RED-GREEN-REFACTOR process** — existing content, kept as-is.

**Section 2: Test scenario checklist** (new — inception_architect blind-spot pattern)

Before writing a test, evaluate which scenarios apply:

| Category | Consider |
|---|---|
| Happy path | Does the expected input produce the expected output? |
| Edge cases | Empty input, single element, max values, boundary values |
| Error paths | Invalid input, missing dependencies, network/IO failures |
| Input validation | Null, undefined, wrong type, malformed data |
| State & side effects | Does it modify state correctly? Idempotent? Cleanup? |
| Regression | If fixing a bug, does the test prove the bug is fixed? |
| Smoke | After integration, does the system start and key flows work? |

Not every category applies to every change. Skip with a note.

**Section 3: Test types** (new — when to use what)

- **Unit** — isolated function behavior, fast, no external deps
- **Integration** — components working together, may need fixtures/containers
- **Smoke** — system starts, critical paths respond (post-deploy or post-build)
- **E2E** — full user flow through the system

Use the narrowest type that covers the behavior. Prefer unit tests. Escalate to integration/smoke only when the behavior crosses boundaries.

#### 3. Skill cross-references

Add explicit `tdd.mdc` links to these skills:

| Skill | Change |
|---|---|
| `code_tdd/SKILL.md` | Add link: "Follow [tdd.mdc](../../rules/tdd.mdc) for process and scenario checklist" |
| `code_execute/SKILL.md` | Add link: "(following [tdd.mdc](../../rules/tdd.mdc))" |
| `worktree_execute/SKILL.md` | Add link: "following [tdd.mdc](../../rules/tdd.mdc)" |
| `code_debug/SKILL.md` | No change (transitive via code_tdd) |
| `issue_create/SKILL.md` | No change (already references tdd.mdc) |

#### 4. `CLAUDE.md`

Update TDD summary to mention scenario checklist and the activation change.

#### 5. Mirror to `assets/workspace/`

Handled by `just sync-workspace` (via `scripts/sync_manifest.py`). No manual mirroring needed — the manifest already syncs `.cursor/rules/` and `.cursor/skills/` as directories.

### Files touched (source only)

| File | Change |
|---|---|
| `.cursor/rules/tdd.mdc` | Expand content, flip `alwaysApply`, add `globs` |
| `.cursor/skills/code_tdd/SKILL.md` | Add `tdd.mdc` reference |
| `.cursor/skills/code_execute/SKILL.md` | Add `tdd.mdc` reference |
| `.cursor/skills/worktree_execute/SKILL.md` | Add `tdd.mdc` reference |
| `CLAUDE.md` | Update TDD summary |

Then: `just sync-workspace` to propagate.

### What stays the same

- `code_tdd/SKILL.md` keeps its detailed procedural workflow (verify baseline, RED, commit, GREEN, commit, REFACTOR, commit)
- Commit discipline (separate commits per TDD phase) unchanged
- "Skip TDD for non-testable changes" escape clause unchanged

### TDD applicability

Skipped — all changes are config/templates/docs with no testable behavior.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 20, 2026 at 10:54 PM_

## Implementation Plan

Issue: #128
Branch: chore/128-rename-skill-namespace-enhance-issue-create

TDD: Skipped — all changes are config/templates/docs with no testable behavior.

### Tasks

- [x] Task 1: Expand `.cursor/rules/tdd.mdc` — change frontmatter to `alwaysApply: false` with code-generation globs, add "Test scenario checklist" section (table with 7 categories), add "Test types" section (unit/integration/smoke/E2E guidance) — `.cursor/rules/tdd.mdc` — verify: read file, confirm `alwaysApply: false`, globs present, both new sections exist
- [x] Task 2: Add `tdd.mdc` reference to `code_tdd/SKILL.md` — in "Understand what to test" step (step 1), add a line referencing `tdd.mdc` for scenario checklist — `.cursor/skills/code_tdd/SKILL.md` — verify: `grep 'tdd.mdc' .cursor/skills/code_tdd/SKILL.md` returns a match
- [x] Task 3: Add `tdd.mdc` reference to `code_execute/SKILL.md` — in step 2 where it says "following ... and TDD", add explicit link to `tdd.mdc` — `.cursor/skills/code_execute/SKILL.md` — verify: `grep 'tdd.mdc' .cursor/skills/code_execute/SKILL.md` returns a match
- [x] Task 4: Add `tdd.mdc` reference to `worktree_execute/SKILL.md` — in step 2 where it says "and TDD:", add explicit link to `tdd.mdc` — `.cursor/skills/worktree_execute/SKILL.md` — verify: `grep 'tdd.mdc' .cursor/skills/worktree_execute/SKILL.md` returns a match
- [x] Task 5: Update `CLAUDE.md` TDD summary — update the TDD subsection under "Always-Apply Rules" to reflect that the rule is now glob-triggered (not always-on) and mention the scenario checklist — `CLAUDE.md` — verify: read file, confirm TDD section mentions glob-triggered and scenario checklist
- [x] Task 6: Run `just sync-workspace` to propagate all changes to `assets/workspace/` — verify: `diff .cursor/rules/tdd.mdc assets/workspace/.cursor/rules/tdd.mdc` shows no diff (or expected transform diffs only)

