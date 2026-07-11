---
type: issue
state: closed
created: 2026-07-06T14:48:56Z
updated: 2026-07-06T15:43:16Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/874
comments: 1
labels: bug, priority:high, area:ci, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:32.948Z
---

# [Issue 874]: [fix(ci): Renovate changelog artifact drops the workspace mirror; metadata.env breaks on parenthesized branches](https://github.com/vig-os/devkit/issues/874)

### Description

Re-enabling the Renovate changelog automation after #863/#864 surfaced two residual defects in `renovate-changelog-build.yml`, verified on the live PR queue (#861, #862, #865, #866):

1. **Workspace mirror dropped from the artifact.** The build step copies `assets/workspace/.devcontainer/CHANGELOG.md` into `changelog-artifact/`, but `actions/upload-artifact` excludes hidden directories by default (`include-hidden-files: false` since v4.4). `.devcontainer` is a hidden directory, so the artifact only ever contains the root `CHANGELOG.md` + `metadata.env`. The commit workflow lists both paths in `FILE_PATHS`, but only the root changelog exists to commit — the PR branch ends up with root ≠ mirror and the `sync-manifest` pre-commit gate fails Project Checks (observed on #861/#862 after runs 28799680160 → commit 6a94ceed, artifact verified to lack the mirror).

2. **`metadata.env` breaks on Renovate group branches.** The metadata is written unquoted (`echo "HEAD_REF=${HEAD_REF}"`) and `source`d by the commit workflow. Grouped Renovate branches contain parentheses (`renovate/python-(minor-and-patch)`), producing `metadata.env: line 3: syntax error near unexpected token '('` — the commit stage crashes before pushing anything (runs 28799792964, 28799804936 for #865/#866).

### Steps to Reproduce

1. Open a Renovate PR (any branch for defect 1; a grouped branch with parentheses for defect 2).
2. Let `Renovate changelog build` run and `Renovate changelog commit` fire via `workflow_run`.

### Expected Behavior

One bot commit per PR updating **both** `CHANGELOG.md` and `assets/workspace/.devcontainer/CHANGELOG.md`; commit stage succeeds regardless of branch-name characters.

### Actual Behavior

- Paren-free branches: bot commit contains only the root changelog → `sync-manifest` fails → red CI.
- Parenthesized branches: commit stage crashes sourcing `metadata.env` → no changelog entry at all (PR can go green while silently missing its entry).

### Environment

`dev` @ 694c9797 (post-#873 sync, workflow re-enabled 2026-07-06).

### Additional Context

Second half of #863 resurfacing: #864 fixed the copy *into* the artifact staging dir but the upload silently dropped it. Remediation for the four open Renovate PRs after this lands: re-tick their rebase checkboxes so Renovate rewrites the branches and the fixed automation re-adds entries.

### Possible Solution

In `.github/workflows/renovate-changelog-build.yml` (sync-manifest propagates to the shipped workspace copy):
- Add `include-hidden-files: true` to the `Upload changelog artifact` step.
- Write `metadata.env` with `printf '%s=%q\n'` so sourced values survive shell metacharacters.

TDD note: workflow-YAML-only change — TDD exception applies (non-testable config).

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 6, 2026 at 03:43 PM_

Fix verified in production after #875 merged to dev:

- **#865** (`renovate/python-(minor-and-patch)` — parenthesized branch): changelog build + commit succeeded, bot commit 4fe42a1c touches both `CHANGELOG.md` and `assets/workspace/.devcontainer/CHANGELOG.md`, all checks green. Both defects exercised and gone.
- **#862**: rebased, two-file bot commit 8f72ebdc, checks green.
- **#861**: two-file bot commit landed; remaining CI failures are the PR's own content (python 3.14.6 pin has no matching interpreter in the flake), unrelated.
- Loop guard intact: follow-up builds on bot pushes correctly skipped.

Remaining flake on #866 was a Renovate double-force-push race (build succeeded on f8b3fe0b, superseded by c7d1617f before the commit stage), resolved by re-ticking the rebase box — not a workflow defect.

