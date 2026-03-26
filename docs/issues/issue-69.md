---
type: issue
state: closed
created: 2026-02-18T01:02:45Z
updated: 2026-03-03T09:13:28Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/69
comments: 2
labels: chore, priority:low, area:ci, effort:small, semver:patch
assignees: none
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:16:24.872Z
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

---

# [Comment #2]() by [c-vigo]()

_Posted on March 3, 2026 at 09:13 AM_

This has moved to [sync-issues-action/#17](https://github.com/vig-os/sync-issues-action/issues/17)

