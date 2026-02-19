---
type: issue
state: open
created: 2026-02-19T15:10:21Z
updated: 2026-02-19T15:14:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/93
comments: 0
labels: chore, priority:blocking
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T15:14:45.139Z
---

# [Issue 93]: [fix: update expected gh version in test_gh_version to 2.87.x](https://github.com/vig-os/devcontainer/issues/93)

## Description

CI is failing on \`test_gh_version\` because the installed \`gh\` CLI version bumped from 2.86.x to 2.87.0 (released 2026-02-18), but the test still asserts \`2.86.\`.

## Failing test

```
tests/test_image.py::TestSystemTools::test_gh_version
```

**Error:**
```
AssertionError: Expected gh 2.86., got: gh version 2.87.0 (2026-02-18)
assert '2.86.' in 'gh version 2.87.0 (2026-02-18)\n...'
```

## Fix

Update the expected version string in \`tests/test_image.py\` (around line 124) from \`2.86.\` to \`2.87.\`.

Also consider whether the Containerfile pins \`gh\` to a specific version — if so, bump it to 2.87.0 to match the image build.

## References

- Upstream release: https://github.com/cli/cli/releases/tag/v2.87.0
