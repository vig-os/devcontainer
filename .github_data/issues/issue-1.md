---
type: issue
state: open
created: 2025-11-24T15:26:22Z
updated: 2026-01-08T15:32:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/1
comments: 4
labels: none
assignees: gerchowl, c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-01-09T16:17:39.105Z
---

# [Issue 1]: [Implement "just"](https://github.com/vig-os/devcontainer/issues/1)

## In this repo

Use it to manage project configuration and image building, testing & pushing, i.e. to replace the Makefile
Migrate as many bash lines to python functions

## In the image

- Add to Containerfile
- Use it for self-deployment
- Use it as a landing script
- Use it to self-update?
---

# [Comment #1]() by [gerchowl]()

_Posted on January 6, 2026 at 02:22 PM_

Implemented across multiple releases:

**In this repo (build/test/push):**
- `just` replaces `make` for all build automation
- Layered justfile architecture: `justfile.base` (managed), `justfile.project` (team-shared), `justfile.local` (personal)
- Recipes: build, test, push, clean, docs, lint, format, etc.

**In the image:**
- `just` installed in Containerfile
- Available in devcontainer for project automation

**Self-update / version check:**
- `version-check.sh` script for automatic update notifications
- Checks for new releases and notifies users

See CHANGELOG.md 'Unreleased' section for full details.

---

# [Comment #2]() by [c-vigo]()

_Posted on January 7, 2026 at 09:40 AM_

@gerchowl I think `just` is not installed in the image, maybe in some other branch?

- [ ] Add to `Containerfile`
- [ ] Add test

---

# [Comment #3]() by [c-vigo]()

_Posted on January 7, 2026 at 09:49 AM_

Related:

In `just`, the default recipe must be defined in the main `justfile`, not in imported files. Move default from the base file to the main` justfile`.

---

# [Comment #4]() by [gerchowl]()

_Posted on January 8, 2026 at 03:32 PM_

super weird. i went through exactly that. that after first draft, neither the installation was present nor the tests, so I went to implement/fix that, but also none of the other branches have that..  could only imagine that it happened in the 'just playground' too and I am mixing up things ...

