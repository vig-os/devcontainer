---
type: issue
state: closed
created: 2026-06-24T10:59:46Z
updated: 2026-07-07T09:41:12Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/677
comments: 4
labels: chore, priority:low, effort:small
assignees: none
milestone: 0.4.1
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:07.128Z
---

# [Issue 677]: [[CHORE] Post-merge Nix-migration triage hygiene (sub-issue closure, #255/#521/#545)](https://github.com/vig-os/devkit/issues/677)

### Chore Type

General task

### Description

Post-merge housekeeping for the Nix migration epic (#625). Most of this runs
*after* the epic PR #670 lands and after the publish-cutover (#639, user-owned)
completes; filed now so it isn't lost.

### Acceptance Criteria

- [x] After #670 merges, confirm sync-issues auto-closed the delivered
      sub-issues (#626–#642, #664, #666, #671)
- [x] Reconcile #545 (bake agent-CLI toolkit) — superseded/absorbed by #631;
      close or link as completed
- [x] Reconcile #521 (nightly HIGH/CRITICAL in Debian `:latest`) — moot once the
      cutover retires the Debian `:latest`; close or retarget to the Nix image
- [x] Confirm #255 is closed by its consolidated `docs/NIX.md` follow-up

### Implementation Notes

Largely a `gh` housekeeping pass; no code. Blocked on #670 merge and the
user-driven cutover for the #521/#545 reconciliation.

### Related Issues

Part of #625. Touches #521, #545, #255, #670.

### Priority

Low

### Changelog Category

No changelog needed


---

# [Comment #1]() by [c-vigo]()

_Posted on June 25, 2026 at 12:12 PM_

## Issue-tracker reconciliation against the #670 merge (state-of-repo review)

PR #670 only carries one auto-close keyword — `Closes #625`. The sub-issues below were **fixed via sub-PRs that merged into the `feature/625-nix-claude-migration` branch (not `main`)**, so GitHub will **not** auto-close them on the #670 merge. They are referenced only in #670 prose ("delivered #626–#642", "Supersedes …"), which does not trigger closure.

**Concretely done (merged sub-PR → issue):**

| Issue | Done by | Issue | Done by |
|------|---------|------|---------|
| #255 | #681 | #687 | #690 |
| #673 | #678 | #688 | #689 |
| #674 | #680 | #691 | #693 |
| #675 | #679 | #692 | #694 |
| #676 | #682 | #695 | #696 |
| #683 | #684 | #697 | #699 |
| #685 | #686 | #698 | #700 |
| | | #701 | #702 |

**Recommended action:** add explicit `Closes #255 #673 #674 #675 #676 #683 #685 #687 #688 #691 #692 #695 #697 #698 #701` to the **#670 body** so they close on merge (or close them manually after merge). *(An automated edit to #670's body was intentionally not made — left for a maintainer.)*

**Still genuinely open / needs human decision** (claimed delivered in #670 prose but verify before closing): #639 (cutover — note the image still carries WIP tag `nix-wt634`, see #705), #642, #641, #640, #671, #637, #638, #636, #666, #664. Confirm each is truly complete vs. pending the gated cutover.

**New issues from the review (Track A pre-merge cleanups):** #705 (WIP tag guard), #706 (downstream venv path), #707 (dup pre-commit hook), #708 (ruff py314), #709 (TESTING.md 3.12→3.14), #710 (cosmetic).

---

# [Comment #2]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

## Backlog-hygiene pass (2026-07-01)

Closed the delivered-on-`dev`-but-still-open issues, each with a comment citing the landing PR. These were open only because the epic merged to `dev` (not `main`) and the T/C-track issues carried `Tracking: #625` without being linked as GitHub sub-issues, so sync-issues auto-close never fired.

**T-track (via #670 + follow-ups):** #631 #632 #633 #634 #635 #636 (#659) #637 (#660) #638 #666 (#667)
**C-track (via #670):** #626 #627 #628 #629 #630
**Wave-A follow-ups:** #775 (#788) #776 (#789) #777 (#790) #780 (#787)
**Release-blocker bugs (fixed on `dev`):** #705 (#713) #706 (#716) #703 (#704) #687 (#690) #664 (#665)
**Recent test/docs:** #792 (#793) #794 (#796)

**Left open deliberately:**
- **#639** — the real remaining release gate (deliberate, human-gated publish-cutover of `:latest`).
- **#640 #641 #642** — T4 downstream/decommission track, sequenced behind the cutover. ⚠️ Note a possible inconsistency: #642's landed commit already removed the root Debian `Containerfile` from `dev`, while #639's plan says to *retain* Debian as a one-cycle fallback — worth reconciling before cutover.
- **#737** — only partially addressed (in-repo pins ranged; image still ships CPython 3.14.4). Needs a decision.
- **#778 / #779** — will auto-close when PR #791 merges to `dev`.
- **#255 / #521 / #545** — still pending the user-driven cutover reconciliation this umbrella also tracks.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 7, 2026 at 09:39 AM_

## Post-cutover verification pass (2026-07-07)

0.4.0 is promoted (main @ f20bf6b, Nix-only image live). Verified every item in the acceptance list with `gh`; all four boxes are now ticked in the body. Nothing needed re-closing — the 2026-07-01/02 hygiene pass had already landed the closures with rationale; this pass confirmed them against the post-promote state.

**Sub-issues #626–#642, #664, #666, #671** — all CLOSED except **#642** (T4.4 decommission), which is deliberately open in milestone **0.4.1** and actively being worked; left untouched.

**#545** — CLOSED 2026-07-02 with rationale: toolkit absorbed into flake `devTools` via #631/#634 (delivered through #670). Noted follow-up gaps in that thread (`fzf` not carried over; no image test for the toolkit / `IS_SANDBOX`).

**#521** — CLOSED 2026-07-02 as superseded. Premise re-verified today: `security-scan.yml` on main is vulnix-primary + Trivy SBOM (no Debian `scan-latest` job, no SARIF upload); the nightly Debian `:latest` Trivy scan that generated the issue no longer exists.

**#602 / #604** — both already CLOSED (2026-06-22). #604 closed via PR #605 with a full outcome comment. #602 had no closing note, so a traceability comment was added citing the same Debian-scan-retirement rationale as #521.

**#255** — CLOSED 2026-06-30, resolved by #681 (via #670); `docs/NIX.md` exists on main (23.5 KB).

**Residue for maintainer judgment — orphaned code-scanning alerts:** 308 open Trivy alerts remain under category `container-image-latest`. The producer is retired: the last upload in that category was 2026-07-06 from pre-promote main (0.3.9, `security-scan.yml:scan-latest`); the 2026-07-07 scheduled run on 0.4.0 produced none. These are Debian-scan-era artifacts and can be bulk-dismissed ("won't fix — scanner retired, image replaced"), but that is left as a deliberate maintainer action (same pattern as the #604 Track A/B dismissals). Also 13 open Scorecard `supply-chain/local` alerts, out of scope here.

Leaving this issue open for final review/closure.


---

# [Comment #4]() by [c-vigo]()

_Posted on July 7, 2026 at 09:41 AM_

Verification pass complete: all #625 sub-issues confirmed closed with landing-PR citations (#642 excepted — active in 0.4.1), #545 absorbed by #631, #521/#602 superseded by the vulnix-only scan, #604 resolved via #605, #255 resolved by #681. Acceptance criteria all satisfied; see summary comment above. Remaining maintainer option (not part of this issue): bulk-dismiss the 308 stale Trivy alerts in the retired container-image-latest category.

