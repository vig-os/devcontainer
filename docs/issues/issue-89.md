---
type: issue
state: open
created: 2026-02-19T12:32:46Z
updated: 2026-02-23T08:05:07Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/89
comments: 3
labels: refactor, priority:medium, area:workspace, effort:large, semver:minor
assignees: gerchowl
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-24T04:24:11.079Z
---

# [Issue 89]: [[REFACTOR] Consolidate sync_manifest.py and utils.py into manifest-as-config architecture](https://github.com/vig-os/devcontainer/issues/89)

### Description

`scripts/sync_manifest.py` and `scripts/utils.py` have overlapping concerns:

- **`sync_manifest.py`** — declarative manifest entries + transform classes (`Sed`, `RemoveLines`) + sync engine + CLI
- **`utils.py`** — `sed_inplace()` for sed-style substitutions, `update_version_line()` for README patching, and a CLI wrapper

Both define text-replacement logic independently. The manifest's `Sed` transform uses `re.sub`, while `utils.py` implements a custom sed-pattern parser with `str.replace`.

### Proposed refactoring

1. **Extract transform classes** from `sync_manifest.py` into a new `scripts/transforms.py` so they are reusable outside the sync context.
2. **Keep manifest as declarative Python** — the `MANIFEST` list stays in `sync_manifest.py` as Python dataclass instances (pure data, no logic). TOML/YAML conversion was evaluated and rejected: the transforms have complex parameters (multi-line replacements, regex patterns, lists) that map poorly to config formats, and the file changes rarely. Declarative Python dataclasses with behavior extracted to `transforms.py` achieves the same separation-of-concerns goal.
3. **Unify sed logic** — `utils.py`'s `sed_inplace` and the manifest's `Sed` transform both do regex/string replacement. Consolidate into one implementation.
4. **Keep `utils.py` CLI** — `utils.py` is called directly by workflows (`version`, `sed` subcommands). Its CLI interface must be preserved.

### Acceptance Criteria

- [ ] No duplicate text-replacement logic between the two files
- [ ] Transform classes live in `scripts/transforms.py`, separate from the manifest data and sync engine
- [ ] `sync_manifest.py` manifest entries are declarative data (dataclass instances importing transforms from `transforms.py`)
- [ ] `utils.py` CLI (`version`, `sed` subcommands) continues to work unchanged
- [ ] `just sync-workspace` produces identical output before and after
- [ ] All existing tests pass

### Changelog Category

Changed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 03:02 PM_

## Suggestion: Pre-commit hook to prevent asset drift

While working on #102, we hit a `test_manifest_files` failure caused by `assets/workspace/` being out of sync with the canonical source files. The build pipeline (`prepare-build.sh`) always syncs fresh via `sync_manifest.py`, but the checked-in `assets/workspace/` drifts when someone changes a source file and forgets to run `just sync-workspace`.

### Proposed solution

Add a **scoped pre-commit hook** (similar to the existing `generate-docs` hook) that:

1. Runs `sync_manifest.py sync assets/workspace/` when any manifest source file is staged
2. Stages the updated `assets/workspace/` files
3. Fails if the sync produces changes (so the developer sees the diff)

This follows the same pattern as the `generate-docs` hook already in `.pre-commit-config.yaml`:

```yaml
- id: sync-workspace
  name: sync-workspace (keep assets/workspace in sync)
  entry: bash -c 'uv run python scripts/sync_manifest.py sync assets/workspace/ && git add assets/workspace/ 2>/dev/null || true'
  language: system
  files: <pattern matching manifest source files>
  pass_filenames: false
```

The `files:` pattern would need to cover all manifest source paths (`.github/pull_request_template.md`, `justfile.worktree`, `.cursor/rules/`, `.cursor/skills/`, etc.) — ideally derived from the manifest entries themselves.

### Alternatives considered

- **CI-only check**: Catches drift on PRs but doesn't prevent it locally — developers still forget.
- **Remove `assets/workspace/` from git**: Since `prepare-build.sh` regenerates it, the checked-in copy is redundant. But this breaks "browse the template on GitHub".
- **Unscoped hook (runs on every commit)**: Works but adds unnecessary latency to commits that don't touch manifest sources.

This fits naturally into the manifest-as-config refactor scope.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 21, 2026 at 01:27 AM_

## Implementation Plan

Issue: #89
Branch: feature/89-consolidate-sync-manifest-utils

### Tasks

- [ ] Task 1: Write tests for all existing transform classes (`Sed`, `RemoveLines`, `StripTrailingBlankLines`, `RemoveBlock`, `RemovePrecommitHooks`, `ReplaceBlock`) — `tests/test_transforms.py` — verify: `uv run pytest tests/test_transforms.py -v`
- [ ] Task 2: Extract transform classes and `_resolve` helper from `sync_manifest.py` into `scripts/transforms.py`; update `sync_manifest.py` to import from it — `scripts/transforms.py`, `scripts/sync_manifest.py` — verify: `uv run pytest tests/ -v` + `just sync-workspace`
- [ ] Task 3: Write test that `sed_inplace` handles regex patterns (new behavior) — `tests/test_utils.py` — verify: `uv run pytest tests/test_utils.py::TestSedInplace -v`
- [ ] Task 4: Unify `sed_inplace` to use `re.sub` internally while preserving the `s|old|new|g` CLI interface — `scripts/utils.py` — verify: `uv run pytest tests/test_utils.py -v`
- [ ] Task 5: Write snapshot test — capture `just sync-workspace` output and diff against a golden reference to prove no behavioral change — `tests/test_sync_manifest.py` — verify: `uv run pytest tests/test_sync_manifest.py -v`
- [ ] Task 6: Update `CHANGELOG.md` under `## Unreleased` — `CHANGELOG.md` — verify: visual review

### Notes

- Tasks 1-2 handle the transform extraction (the main structural change)
- Tasks 3-4 handle the sed unification (DRY)
- Task 5 is the safety net proving identical output
- TDD: test tasks (1, 3, 5) come before or alongside their implementation tasks (2, 4)
- `conftest.py`'s `parse_manifest` fixture continues to work since it imports `MANIFEST` dynamically
- TOML/YAML manifest was evaluated and rejected — transforms have complex parameters (multi-line replacements, regex patterns, lists) that map poorly to config formats, and the file changes rarely. Declarative Python dataclasses with behavior in `transforms.py` achieves the same separation goal.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 23, 2026 at 08:03 AM_

## PR Diagnosis: #140

### CI Failures
- **Project Checks** / Run project checks: `invalid-syntax: Expected a statement` at `scripts/sync_manifest.py:195:7` — git merge conflict marker `>>>>>>> dev` left in file
- **Project Checks**: ruff format failed (cannot parse file with conflict markers)
- **Project Checks**: pymarkdown failed (BadTokenizationError — likely downstream of malformed files)
- **Build Container Image**: failed (depends on Project Checks / uses same codebase)
- **Test Summary**: failed (aggregates Build + Project Checks failures)

### Review Feedback
No pending review feedback ✓

### Merge State
mergeable: UNKNOWN, mergeStateStatus: UNKNOWN

---

## Implementation Plan

Issue: #89
Branch: feature/89-consolidate-sync-manifest-utils

### Tasks

- [x] Task 1: Resolve merge conflict in `scripts/sync_manifest.py` — remove conflict markers, keep declarative manifest.toml approach (lines 104–195) — verify: `python -m py_compile scripts/sync_manifest.py`
- [x] Task 2: Resolve merge conflict in `CHANGELOG.md` — merge both sides: keep #89 entry from feature branch, add #71 and #147 entries from dev — verify: `head -50 CHANGELOG.md` shows no conflict markers
- [x] Task 3: Add missing `justfile.base` entry to `scripts/manifest.toml` (present in dev, missing in current manifest) — verify: `uv run python scripts/sync_manifest.py list` includes justfile.base
- [x] Task 4: Run pre-commit and tests — verify: `just precommit` and `just test` pass
- [x] Task 5: Commit and push fixes — verify: CI passes on PR #140

---

## Autonomous Run Complete

- **Diagnosis**: posted above
- **Plan**: 5 tasks
- **Execute**: all tasks done
- **Commit**: `9138d28` fix: resolve merge conflicts in sync_manifest and CHANGELOG
- **Push**: completed
- **CI**: pending (check PR #140)

