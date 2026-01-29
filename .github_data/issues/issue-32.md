---
type: issue
state: open
created: 2026-01-28T20:41:51Z
updated: 2026-01-29T07:59:33Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/32
comments: 1
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-29T08:09:50.644Z
---

# [Issue 32]: [Question: Was the dev branch intentionally removed?](https://github.com/vig-os/devcontainer/issues/32)

## Question

@c-vigo Was there a particular reason the `dev` branch was removed from the repository?

I noticed when trying to pull that the `origin/dev` branch no longer exists on the remote. Several other branches were also cleaned up:
- `origin/dev`
- `origin/c-vigo/issue1`
- `origin/gerchowl/issue8`
- `origin/revert-6-dev`
- `origin/revert-fix`

Just want to confirm if this was intentional and what branches working on for dev / pre-release?
---

# [Comment #1]() by [c-vigo]()

_Posted on January 29, 2026 at 07:59 AM_

I wanted to bring `dev`  up to date with `main` but forgot to re-create it. For the other branches, I did some clean-up, yeah.

We should establish clear rules on these branches and put them into workflows. I have also become more appreciative of the "release" branches where one can fully test before merging. To be discussed when you are back. For now, we keep `dev` as the main development branch with topic branches if necessary.

