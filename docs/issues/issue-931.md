---
type: issue
state: closed
created: 2026-07-08T12:36:32Z
updated: 2026-07-09T13:28:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/931
comments: 2
labels: chore
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:22.164Z
---

# [Issue 931]: [chore(security): clear orphaned Debian Trivy alerts + Scorecard token-permissions pass](https://github.com/vig-os/devkit/issues/931)

Post-#642 close-out. #642 removed the Debian `:latest` Trivy scan but left its code-scanning results behind.

## Context

Security-tab audit (2026-07-08) found the only open code-scanning noise is:

- **308 Trivy alerts**, category `container-image-latest`, all scanning `/tmp/image-latest.tar` and reporting **Debian bookworm** packages (e.g. `libglib2.0-0 2.74.6-2+deb12u9`). The workflow that produced them was removed with the Debian path (#642); it no longer exists on `main`. No current scanner uploads Trivy SARIF (`ci.yml` Trivy is `format: table`/`exit-code: 0`; `security-scan.yml` uses vulnix + SBOM artifact). Because code scanning only auto-closes an alert when a newer analysis of the **same category** stops reporting it, and `container-image-latest` will never run again, these 308 are frozen-open. This is the "dismiss stale Trivy categories" item #642 shipped without completing.
- **13 Scorecard `TokenPermissionsID` alerts** (live, ran on `main` 2026-07-08). One is a real smell — `nix-image.yml` top-level `packages: write`. The other 12 are job-scoped writes genuinely required by the release/promote/sync automation.

Dependabot and secret scanning: 0 open.

## Tasks

- [x] Delete the orphaned `container-image-latest` Trivy analysis chain (removes all 308 alerts + the dead category from the Security tab).
- [x] Fix `nix-image.yml`: move top-level `packages: write` to the GHCR-push job, set top-level to `contents: read` (alert #7627 auto-resolves on next Scorecard run).
- [x] Dismiss the remaining 12 Scorecard alerts (`#7615`–`#7626`) as `won't fix` with a note (minimal required scope for release/sync automation).
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 12:42 PM_

Done in this pass:

- ✅ Deleted the orphaned `container-image-latest` Trivy analysis chain (29 analyses) → all **308** stale Debian alerts cleared; open Trivy alerts now **0**.
- ✅ Dismissed the 12 job-level Scorecard `TokenPermissions` alerts (#7615–#7626) as won't-fix (minimal required scope for release/promote/sync automation).
- 🔧 `nix-image.yml` top-level `packages: write` fix → **#932** (alert #7627 auto-resolves on the next Scorecard run of `main` after merge).

Remaining code-scanning noise: **0** once #932 merges. Dependabot / secret scanning: 0.

Note: a handful of June `container-image` (PR-merge-ref) Trivy analyses from closed PRs remain in history — they are not open alerts on `main` and are out of scope; left untouched.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 12:57 PM_

Follow-up: the code-scanning **Tool status** page still lists Trivy (configuration `security-scan.yml`) because ~968 historical Trivy analyses remain (Feb–Jun 2026, all three defunct Debian categories). This is cosmetic — **0 open Trivy alerts**, nothing re-uploads SARIF to it.

Decision: **leave the residual analyses in place** as historical record. Deleting them would fully remove the retired-tool entry but is an irreversible bulk op with no functional benefit. Not doing it.

