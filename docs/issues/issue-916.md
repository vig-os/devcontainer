---
type: issue
state: closed
created: 2026-07-07T15:32:27Z
updated: 2026-07-08T07:54:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/916
comments: 1
labels: bug, priority:medium, area:workspace, effort:medium, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:24.572Z
---

# [Issue 916]: [fix(workspace): init-workspace upgrade hardening — git-diff preview, workflow scan scope, GITHUB_REPOSITORY ordering, pin stamp](https://github.com/vig-os/devkit/issues/916)

Bundle of init-workspace.sh follow-ups found during 0.4.1-rc1 consumer-upgrade testing. All localized to `assets/init-workspace.sh` (+ its BATS tests).

1. **#878 diff-preview box prints empty.** The image has no `diff`/`cmp`, so the preserved-vs-template report the #878 fix added is blank (`line 582: diff: command not found`). The image **does** ship `git 2.54.0` → use `git diff --no-index` (and drop the `diff -q` gate for `git diff --no-index --quiet`). Reproduced in all five test upgrades. Refs: #878

2. **#881 pre-commit reference scan misses `.github/workflows/`.** The scan only covers `justfile.project` and `.githooks/`. mat has a real `uv run pre-commit run --all-files` in `.github/workflows/ci-container.yml:119` that went unflagged. Extend the scan scope to preserved consumer workflows. Refs: #881

3. **`--no-prompts` half-applies before validating `GITHUB_REPOSITORY`.** The origin-resolution check runs *after* the rsync copy but *before* placeholder substitution, so when the origin can't be derived it aborts (exit 1) leaving a half-scaffolded tree (files copied, `{{GITHUB_REPOSITORY}}` unsubstituted). Move the resolution/validation *before* any filesystem mutation so it fails clean.

4. **`.vig-os` pin not advanced on upgrade.** The baked template `.vig-os` pins `DEVCONTAINER_VERSION=0.4.0`; `init-workspace.sh` only rewrites the pin when `VIG_OS_VERSION` is set (forwarded by `install.sh`, absent on a bare `docker run … init-workspace.sh`). A direct-run upgrade silently leaves the consumer on the old pin. Stamp the pin from the image's own version at scaffold time.

Lower-priority, include if clean:
5. **`--force` clobbers a customized `.gitignore` with no warning** (talys lost data-ignore patterns). Add a non-fatal diff/warning like #878, or preserve.
6. **Template source stubs littered** (`src/<short_name>/__init__.py`, `tests/test_example.py`) when upgrading an existing project whose package dir differs from SHORT_NAME. Skip source-stub scaffolding on `--force` upgrade of a populated workspace.

Refs: #877
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

