---
type: issue
state: open
created: 2026-06-24T10:59:46Z
updated: 2026-06-25T12:12:52Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/677
comments: 1
labels: chore, priority:low, effort:small
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:57.844Z
---

# [Issue 677]: [[CHORE] Post-merge Nix-migration triage hygiene (sub-issue closure, #255/#521/#545)](https://github.com/vig-os/devcontainer/issues/677)

### Chore Type

General task

### Description

Post-merge housekeeping for the Nix migration epic (#625). Most of this runs
*after* the epic PR #670 lands and after the publish-cutover (#639, user-owned)
completes; filed now so it isn't lost.

### Acceptance Criteria

- [ ] After #670 merges, confirm sync-issues auto-closed the delivered
      sub-issues (#626–#642, #664, #666, #671)
- [ ] Reconcile #545 (bake agent-CLI toolkit) — superseded/absorbed by #631;
      close or link as completed
- [ ] Reconcile #521 (nightly HIGH/CRITICAL in Debian `:latest`) — moot once the
      cutover retires the Debian `:latest`; close or retarget to the Nix image
- [ ] Confirm #255 is closed by its consolidated `docs/NIX.md` follow-up

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

