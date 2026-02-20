---
type: issue
state: open
created: 2026-02-19T12:32:46Z
updated: 2026-02-20T15:02:18Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/89
comments: 1
labels: refactor, priority:medium, area:workspace, effort:large, semver:minor
assignees: none
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-20T15:25:37.513Z
---

# [Issue 89]: [[REFACTOR] Consolidate sync_manifest.py and utils.py into manifest-as-config architecture](https://github.com/vig-os/devcontainer/issues/89)

### Description

`scripts/sync_manifest.py` and `scripts/utils.py` have overlapping concerns:

- **`sync_manifest.py`** — declarative manifest entries + transform classes (`Sed`, `RemoveLines`) + sync engine + CLI
- **`utils.py`** — `sed_inplace()` for sed-style substitutions, `update_version_line()` for README patching, and a CLI wrapper

Both define text-replacement logic independently. The manifest's `Sed` transform uses `re.sub`, while `utils.py` implements a custom sed-pattern parser with `str.replace`.

### Proposed refactoring

1. **Extract transform classes** from `sync_manifest.py` into `utils.py` (or a new `scripts/transforms.py`) so they are reusable outside the sync context.
2. **Make the manifest data-only** — convert `MANIFEST` from a Python list to a declarative config file (TOML or YAML), parsed by a thin loader. The manifest becomes pure configuration, not code.
3. **Unify sed logic** — `utils.py`'s `sed_inplace` and the manifest's `Sed` transform both do regex/string replacement. Consolidate into one implementation.
4. **Keep `utils.py` CLI** — `utils.py` is called directly by workflows (`version`, `sed` subcommands). Its CLI interface must be preserved.

### Acceptance Criteria

- [ ] No duplicate text-replacement logic between the two files
- [ ] `sync_manifest.py` manifest entries are declarative config (not Python code defining data)
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

