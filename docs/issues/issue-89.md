---
type: issue
state: open
created: 2026-02-19T12:32:46Z
updated: 2026-02-19T12:32:46Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/89
comments: 0
labels: refactor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-19T15:36:55.133Z
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
