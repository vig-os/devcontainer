---
type: issue
state: closed
created: 2026-07-07T12:22:39Z
updated: 2026-07-08T07:41:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/897
comments: 1
labels: chore, area:image
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:28.294Z
---

# [Issue 897]: [chore(image): remove the pre-commit compat shim (one-cycle deprecation ends)](https://github.com/vig-os/devkit/issues/897)

### Chore Type

Scheduled removal

### Description

#881 shipped a `pre-commit` -> `prek` compat shim in the image (`writeShellScriptBin` in `imageTools`, flake.nix, marked `DEPRECATED — remove in 0.5`) to cover consumers whose preserved files still call the retired binary. The deprecation window is one release cycle: remove the shim in 0.5.

### Acceptance Criteria

- [ ] Shim removed from `imageTools` in flake.nix
- [ ] `tests/test_image.py`: drop `test_pre_commit_compat_shim`; re-add the absence assertion (`pre-commit` NOT on PATH) that the shim displaced (see #881 PR notes)
- [ ] MIGRATION.md: shim references updated (rename guidance stays)
- [ ] Changelog: Removed entry

Refs: #881
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #899 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

