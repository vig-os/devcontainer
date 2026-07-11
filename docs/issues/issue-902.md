---
type: issue
state: closed
created: 2026-07-07T13:25:16Z
updated: 2026-07-07T14:04:12Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/902
comments: 1
labels: feature, priority:medium, area:ci, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:27.875Z
---

# [Issue 902]: [feat(ci): gate RC dispatch on CI only — move approval + ready-for-review to the final release](https://github.com/vig-os/devkit/issues/902)

## Description

Move the release approval gate off the **release-candidate (RC)** dispatch and
onto the **final** dispatch. Today `release.yml`'s `validate` job runs the same
"Find and verify PR" gate for *both* `release-kind=candidate` and
`release-kind=final`: it requires the release PR to be **non-draft**,
**approved** (`reviewDecision=APPROVED`), and **CI-green** before it will cut
anything (release.yml:308–393, with no `if:` on `release-kind`).

That forces a human to approve the release PR *before* any RC image exists —
i.e. before the artifact they would functionally verify has been built. RCs
should instead be the disposable tool used *during* verification, with the
single human approval landing once, on the settled final diff.

## Problem Statement

The current gate conflates two distinct activities into one blocking check:

- **Code review** — a human reading the diff/CHANGELOG and approving.
- **Functional verification** — pulling the built image and confirming it works.

The RC *is* the artifact needed for functional verification, yet approval is
required *before* the RC can be produced → the reviewer approves blind. It also
means approval sits on an *intermediate* diff: fixes can land on the release
branch after approval, so (absent stale-approval dismissal) we can ship
something a human never actually approved.

RC blast radius is already low: an RC burns a fresh auto-incrementing
`X.Y.Z-rcN` tag + `:X.Y.Z-rcN` GHCR images (+cosign/SBOM) and dispatches the
smoke-test. It does **not** touch `:latest`, does **not** create a GitHub
Release on this repo, does **not** merge anything, and is pruned at promote.
Gating that behind full PR approval is over-restrictive for what it costs.

## Proposed Solution

Make the draft + approval portion of the PR gate conditional on
`release-kind == final`; keep the CI-status checks for **both** kinds.

- **RC dispatch** (`publish-candidate`): gated on **CI-green only**. Drop the
  `isDraft` and `reviewDecision` checks (release.yml:342–364); keep the CI
  status checks (release.yml:367–391). The release PR *stays draft* through the
  whole RC phase.
- **Final dispatch** (`finalize-release`): the real gate — `gh pr ready` +
  **approval** + CI-green. Justified because final burns the **immutable**
  `X.Y.Z` tag (a mistaken final can only be forward-fixed to `X.Y.Z+1`).
- **Promote**: unchanged. Its `merge` job already re-verifies not-draft +
  approved + CI before merging to `main`, so `main`/`:latest` stay protected
  regardless.

Scope of change:
- `release.yml` `validate` job: wrap the draft + `reviewDecision` checks in an
  `if [ "$RELEASE_KIND" = "final" ]` guard; leave CI checks applying to both.
- `justfile` / release docs: the RC phase no longer instructs `gh pr ready`
  first; that moves to just before `finalize-release`.
- `prepare-release.yml`, `promote-release.yml`: no changes.

## Alternatives Considered

- **Fully ungate RC** (skip the PR-verify step entirely for candidate).
  Rejected: loses the cheap "no RC on a red branch" floor and lets anyone with
  dispatch perms mint org-signed `rcN` images with no gate. `build-and-test` +
  `vulnix-gate` run inside the RC anyway, so keeping the PR CI check is nearly
  free insurance.
- **Approval at promote only** (final becomes ready+CI, no approval). Rejected:
  final burns the immutable `X.Y.Z` tag, so it deserves human sign-off before
  that irreversible step, not only at promote.

## Impact

- Beneficiaries: release maintainers. RCs become freely dispatchable for
  verification; the one approval lands on the exact diff that ships.
- Backward compatible: no change to the shipped image, tags, or consumer-facing
  artifacts. Only the maintainer release procedure changes.
- Accepted residuals: higher RC volume → more downstream smoke-test/RC
  pre-release churn (pruned at promote); approval may be dismissed if a fix
  lands after approval (this is the *correct* friction — re-approving a changed
  diff); RCs queue under `concurrency: publish-image`.

## Changelog Category

Changed

---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 02:04 PM_

Implemented in #907 (merged to `dev`, commit d6188076). `release.yml` now gates candidate dispatch on CI only; the draft + approval gate applies to the final release, and `promote-release.yml` re-enforces approval before merging to `main`. Docs/justfile/CONTRIBUTE reordered accordingly. Live for the next release branch cut from `dev`.

