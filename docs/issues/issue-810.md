---
type: issue
state: closed
created: 2026-07-04T13:39:27Z
updated: 2026-07-04T16:11:13Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/810
comments: 2
labels: bug, priority:blocking, area:ci, semver:patch
assignees: none
milestone: 0.4
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:43.542Z
---

# [Issue 810]: [[BUG] prepare-release: draft-PR body exceeds GitHub's 65536-char limit on large releases](https://github.com/vig-os/devkit/issues/810)

## Summary

The **Prepare Release** workflow fails at the `Create draft PR to main` step when the frozen release CHANGELOG section is large:

```
pull request create failed: GraphQL: Body is too long (maximum is 65536 characters) (createPullRequest)
```

Failing run: https://github.com/vig-os/devcontainer/actions/runs/28699283187 (0.4.0). The `validate` job passed; the automatic rollback restored `CHANGELOG.md` on `dev`, so no partial release resulted — but the release cannot be prepared until this is fixed.

## Root cause

`.github/workflows/prepare-release.yml` (`Create draft PR to main` step) builds `PR_BODY` from the **entire** frozen CHANGELOG section and passes it verbatim to `gh pr create --body`. GitHub caps PR bodies at **65,536 characters**. The 0.4.0 section alone is **64,211 chars** (1,276 bullet lines — the large Nix-cutover release); with the header it clears the cap.

This is distinct from #620 (which fixed *early* truncation at inline `## [` headings) — here the body is well-formed but simply too long for the API.

## Proposed fix

In the `Create draft PR to main` step, cap the body to a safe budget (< 65,536): if the assembled body would exceed it, truncate the changelog content at a line boundary and append a pointer to the full `CHANGELOG.md` on the release branch. The complete changelog is always available in the diff, so no information is lost.

## Acceptance criteria

- Prepare Release succeeds for a release whose CHANGELOG section exceeds 65,536 chars.
- The draft PR body stays under the limit and links to the full changelog when truncated.
- Small releases are unaffected (full changelog still inlined).
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 03:55 PM_

**Reopening scope: the same uncapped PR-body rebuild exists in `release.yml`** (the #812 fix covered only `prepare-release.yml`).

Two further sites rebuild the PR body from the full changelog section with no cap:

1. **Finalize path** — `Refresh release PR body from finalized changelog` (blocking: `set -euo pipefail`, no `continue-on-error`). With the 0.4.0 section measuring **~66.8k chars > 65,536**, the first `finalize-release 0.4.0` dispatch would have crashed mid-finalize on `GraphQL: Body is too long` and triggered the rollback job.
2. **Rollback path** — `Restore release PR body from pre-finalization CHANGELOG` (`continue-on-error`, so an overflow would only leave the body unrestored).

Fix: port the same cap (65,000-char budget, line-boundary truncation, note pointing to the full `CHANGELOG.md` on the release branch) to both steps, landing on `release/0.4.0` before the RC so the candidate tests the tree that ships. Verified with a standalone harness against the real 0.4.0 section: 66,794-char section → 64,869-char body with the truncation note; sub-threshold input passes through byte-identical.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 04:11 PM_

All three uncapped PR-body writes are now fixed:

- `prepare-release.yml` `Create draft PR to main` — #812, **proven in production**: prepare-release run [28710154495](https://github.com/vig-os/devcontainer/actions/runs/28710154495) succeeded on the ~66.8k-char 0.4.0 changelog, producing the capped 65,125-char body on PR #813.
- `release.yml` finalize-path `Refresh release PR body` and rollback-path `Restore release PR body` — #830 (merged to `release/0.4.0` at `c140fd6f`), same cap, verified against the real 0.4.0 section with a standalone harness (66,794-char section → 64,869-char capped body; sub-threshold passthrough byte-identical).

The fix reaches `dev`/`main` via the 0.4.0 promote merge + sync-back. Follow-up noted in #830: the cap now exists in three inline copies — candidate for extraction into a shared `.github/scripts/` helper next cycle.

