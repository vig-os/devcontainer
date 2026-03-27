---
type: issue
state: closed
created: 2026-03-09T10:00:25Z
updated: 2026-03-09T10:18:15Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/245
comments: 2
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:45.592Z
---

# [Issue 245]: [Regression: install.sh fails with --force due to missing just sync recipe](https://github.com/vig-os/devcontainer/issues/245)

## Summary
`install.sh` fails during workspace initialization when dependency sync runs, because the generated `justfile` does not define a `sync` recipe.

This appears to have been introduced by #244.

## Reproduction
Run:

```bash
~/Documents/vigOS/devcontainer/install.sh ~/Documents/vigOS/devcontainer-smoke-test/ --version dev --skip-pull --force --org vigOS
```

Observed output (tail):

```text
Syncing dependencies...
error: Justfile does not contain recipe `sync`
error: Failed to initialize workspace
```

## Expected behavior
Workspace initialization should complete successfully in `--force` mode, and dependency synchronization should use an existing recipe/command path.

## Notes
- Command used local image with `--skip-pull`
- Failure occurs after file copy + placeholder replacement, at dependency sync stage
---

# [Comment #1]() by [c-vigo]()

_Posted on March 9, 2026 at 10:18 AM_

Root cause confirmed: the  recipe was moved to , but that file was not updated in the affected path, so  was missing at runtime. Closing this issue based on that diagnosis.

---

# [Comment #2]() by [c-vigo]()

_Posted on March 9, 2026 at 10:18 AM_

Root cause confirmed: the `sync` recipe was moved to `justfile.project`, but that file was not updated in the affected path, so `just sync` was missing at runtime.

Closing this issue based on that diagnosis.

