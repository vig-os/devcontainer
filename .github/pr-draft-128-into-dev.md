## Description

Improve agent skills DX with two changes: rename all skill directory namespace separators from colon (`:`) to underscore (`_`) for reliable Cursor `@`-reference, and enhance the `issue_create` and `tdd.mdc` workflows.

Closes #128

## Type of Change

- [x] `chore` -- Maintenance task (deps, config, etc.)
- [x] `docs` -- Documentation only

## Changes Made

### Skill namespace rename (colon → underscore)

- Renamed all 28 skill directories under `.cursor/skills/` and `assets/workspace/.cursor/skills/` (e.g. `issue:create` → `issue_create`)
- Updated all internal cross-references between skills (relative links in SKILL.md files)
- Updated `name:` frontmatter fields in all SKILL.md files
- Updated `CLAUDE.md` command table, `.github/label-taxonomy.toml`, and `CHANGELOG.md`
- Updated docs generator and templates for underscore namespace

### `issue_create` skill enhancement

- Added step to run `just gh-issues` before drafting to gather open issues overview
- Skill now suggests parent/child issue relationships and appropriate milestones
- Added TDD acceptance criterion for testable issue types

### `tdd.mdc` expansion

- Switched from `alwaysApply: true` to `alwaysApply: false` with globs on source/test files (`**/*.py`, `**/*.ts`, `**/*.js`, `**/*.sh`, `**/test_*`, `**/*_test.*`, `**/tests/**`)
- Added test scenario checklist (happy path, edge cases, error paths, input validation, state/side effects, regression, smoke)
- Added test type guidance (unit, integration, smoke, E2E) with narrowest-type-first principle
- Updated `code_tdd`, `code_execute`, and `worktree_execute` skills to reference `tdd.mdc` explicitly
- Updated `CLAUDE.md` TDD summary to reflect changes

### Workspace sync

- Propagated all changes to `assets/workspace/` via `just sync-workspace`

## Changelog Entry

### Changed

- **Rename skill namespace separator from colon to underscore** ([#128](https://github.com/vig-os/devcontainer/issues/128))
  - All skill directories renamed (e.g. `issue:create` → `issue_create`)
  - All internal cross-references, frontmatter, prose, CLAUDE.md, and label taxonomy updated
  - `issue_create` skill enhanced with context gathering and TDD acceptance criteria
  - `tdd.mdc` expanded with scenario checklist and test type guidance; switched to glob-triggered
  - `code_tdd`, `code_execute`, and `worktree_execute` skills now reference `tdd.mdc` explicitly

## Testing

- [x] Manual testing performed (describe below)

### Manual Testing Details

- Verified no remaining colon-style skill directory names: `ls .cursor/skills/ | grep ':'` returns nothing
- Verified no remaining colon-style cross-references (excluding historical docs): `rg 'skills/[a-z]+:[a-z]' --glob '!docs/issues/*' --glob '!docs/pull-requests/*'` returns nothing
- Verified `tdd.mdc` has `alwaysApply: false`, globs, scenario checklist, and test types sections
- Verified all three skills reference `tdd.mdc` via grep
- Verified `just sync-workspace` propagates cleanly with no diff on `tdd.mdc`

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have updated the documentation accordingly
- [x] I have updated `CHANGELOG.md` in the `[Unreleased]` section (and pasted the entry above)
- [x] My changes generate no new warnings or errors
- [x] Any dependent changes have been merged and published

## Additional Notes

All changes are config/templates/docs — no testable behavior, TDD skipped per project rules.

Refs: #128
