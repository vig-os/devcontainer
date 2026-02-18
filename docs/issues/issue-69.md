---
type: issue
state: open
created: 2026-02-18T01:02:45Z
updated: 2026-02-18T12:24:59Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/69
comments: 1
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T12:55:27.757Z
---

# [Issue 69]: [[TASK] Run pre-commit formatting in sync-issues workflow before committing](https://github.com/vig-os/devcontainer/issues/69)

### Description

The `sync-issues` GitHub Actions workflow syncs issue and PR metadata from GitHub into `docs/issues/` and `docs/pull-requests/` markdown files. It commits these files directly without running any formatting hooks, which regularly introduces:

- Missing or extra trailing newlines (`end-of-file-fixer`)
- Trailing whitespace (`trailing-whitespace`)
- Markdown heading level issues (`pymarkdown`)
- Typos (`typos`)

These then cause the **Project Checks** CI job to fail on unrelated PRs because `pre-commit run --all-files` detects the dirty files.

### Acceptance Criteria

- [ ] The `sync-issues` workflow runs `pre-commit run --all-files -- docs/` (or at minimum `end-of-file-fixer`, `trailing-whitespace`, `pymarkdown`) after syncing and before committing
- [ ] Auto-fixed files are included in the commit
- [ ] Project Checks no longer fails due to formatting issues in auto-synced docs

### Implementation Notes

- The workflow is defined in `.github/workflows/sync-issues.yml`
- It uses `uv` and Python, so `pre-commit` should already be available in the runner environment
- Scope the hook run to `docs/` to avoid touching unrelated files
- Alternative: exclude `docs/issues/` and `docs/pull-requests/` from the formatting hooks in `.pre-commit-config.yaml`, but this is less clean since it hides real issues

### Related Issues

- Encountered repeatedly during #63 and #67 CI runs
- Root cause of multiple "fix trailing blank line" commits

### Priority

Medium
---

# [Comment #1]() by [c-vigo]()

_Posted on February 18, 2026 at 12:24 PM_

The fails were happening because the output directory was changed in the workflow, but not excluded in the pre-commit configuration. This has been fixed, and I would keep it excluded since we cannot guarantee that auto-fix will actually fix all issues.

The question remains whether to actually run pre-commit once with auto-fix during the sync-issues workflow, overriding the exclusion rule.

