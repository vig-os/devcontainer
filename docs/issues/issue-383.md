---
type: issue
state: open
created: 2026-03-19T17:08:53Z
updated: 2026-03-19T17:08:53Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/383
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:22.939Z
---

# [Issue 383]: [[BUG] git commit fails when no default editor is available in image](https://github.com/vig-os/devcontainer/issues/383)

## Description
`git commit` fails in the devcontainer when no text editor is installed/configured as the default editor.

## Steps to Reproduce
1. Start a shell in the devcontainer image.
2. Ensure no default editor is available/configured (e.g., no `EDITOR`/`VISUAL` set and no editor binary present).
3. Run `git commit` without `-m`.
4. Observe failure with an editor-related error.

## Expected Behavior
`git commit` should have a usable editor path in the image, or fail with clear guidance on how to configure one.

## Actual Behavior
Commit fails because Git cannot open an editor (`no text editor is available in the image (or no default)`), so the commit cannot proceed without `-m`.

## Environment
- **OS**: linux 6.17.0-19-generic
- **Shell**: bash
- **Workspace**: `/home/carlosvigo/Documents/vigOS/devcontainer`
- **Container Runtime**: unknown
- **Image Version/Tag**: unknown
- **Architecture**: unknown

## Additional Context
This blocks normal interactive commit flow and can surprise contributors expecting default Git behavior.

## Possible Solution
Install/configure a default terminal editor in the image (or set `core.editor`/`EDITOR`), and document the fallback behavior in contributor docs.

## Changelog Category
Fixed

## Acceptance Criteria
- [ ] Reproduction is documented and verified
- [ ] Root cause identified in image/devcontainer configuration
- [ ] Fix ensures `git commit` works without `-m` in a default shell session
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
