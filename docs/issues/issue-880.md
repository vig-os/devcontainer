---
type: issue
state: closed
created: 2026-07-06T16:24:57Z
updated: 2026-07-08T07:54:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/880
comments: 2
labels: chore, priority:medium, area:ci, effort:small
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:31.409Z
---

# [Issue 880]: [[CHORE] Post-promote RC cleanup deleted rc5 images while consumers still pinned them (hyrr, talys)](https://github.com/vig-os/devkit/issues/880)

### Chore Type

Process gap

### Description

The 0.4.0 promote's RC-cleanup job (run 28797093506, `Cleanup RC artifacts: success`) deleted all `0.4.0-rc*` git tags and GHCR image versions while two field-validation consumers (EXOMA/hyrr, EXOMA/talys) were still pinned to `DEVCONTAINER_VERSION=0.4.0-rc5` — leaving them unable to pull their devcontainer image until bumped (done as part of the Phase-B rollout).

### Acceptance Criteria

- [ ] Release docs (RELEASE_CYCLE.md Phase 5/6) note that RC-pinned consumers must be migrated to the final tag before (or immediately after) promote — add it to the promote checklist
- [ ] Optionally: cleanup job (or promote preflight) greps known consumer repos' `.vig-os` for `-rc` pins and warns

### Changelog Category

No changelog needed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 09:38 AM_

PR #887 addresses the first acceptance criterion: docs/RELEASE_CYCLE.md now has a promote-checklist step (Phase 5, step 2) requiring RC-pinned consumers to bump `DEVCONTAINER_VERSION` in their `.vig-os` file to the final tag before promote runs, plus a cross-reference in Release Phases step 6 naming the `cleanup` job ("Cleanup RC artifacts") in `promote-release.yml` as the job that deletes the RC artifacts.

The second (optional) criterion — the cleanup job grepping known consumer repos' `.vig-os` for `-rc` pins — is deliberately left out of this PR (YAGNI): it would require a cross-org token with read access to private EXOMA repos and a maintained consumer-repo list, i.e. new infrastructure rather than a small addition to the existing job. Happy to file it as a follow-up issue if wanted.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Resolved in the 0.4.1 cycle via #887 — the release process now requires migrating RC-pinned consumers before RC image/tag cleanup. Closing as completed.

