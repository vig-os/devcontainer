---
type: issue
state: closed
created: 2026-06-30T12:52:05Z
updated: 2026-07-01T11:20:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/776
comments: 1
labels: chore, priority:medium, area:ci, effort:medium
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:49.208Z
---

# [Issue 776]: [[CHORE] Make the image-closure Cachix push first-class and blocking](https://github.com/vig-os/devkit/issues/776)

**Source:** PR #670 roadmap, thread A — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). **Deferred.**

Cachix today is opportunistic: `continue-on-error`, paths-filtered, and pushes only the dev-shell **runtime** closure — not the image. Consumers may rebuild the whole closure from source. Make the **image-closure** push first-class and **blocking** so published images are cache-backed. Refs #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

Resolved on `dev` by PR #789 (`ci(cachix): make image-closure Cachix push first-class and blocking`). The image-closure Cachix push is now a first-class, blocking CI step. Refs #625.

