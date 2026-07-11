---
type: issue
state: closed
created: 2026-07-07T13:32:27Z
updated: 2026-07-07T14:01:31Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/905
comments: 1
labels: bug, priority:high, area:image, semver:patch, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:26.978Z
---

# [Issue 905]: [fix(security): accept podman CVE-2026-57231 in vulnix register pending the 26.05 backport](https://github.com/vig-os/devkit/issues/905)

## Summary

The `release/0.4.1` RC dispatch ([run 28869306823](https://github.com/vig-os/devcontainer/actions/runs/28869306823)) failed the **Vulnix CVE Gate** on a single unexcepted HIGH finding:

```
1 unexcepted HIGH/CRITICAL or unscored vulnix finding(s):
  - CVE-2026-57231 (CVSS 7.5) in podman 5.8.2
```

The failure triggered the automated rollback of the release branch.

## The CVE

**[CVE-2026-57231](https://cve.threatint.eu/CVE/CVE-2026-57231)** (CVSS 7.5, HIGH): a malicious container image whose manifest carries malformed `Env` entries (a key with no value, exploitable via the `*` glob) causes podman to leak matching **host** environment variables into the container — a supply-chain risk when running untrusted images. Affects podman 5.8.1–5.8.3; fixed upstream in **5.8.4** (2026-06-26) and **6.0.0**.

## Why it is a real match (not a closure/CPE false positive)

`podman` is a **direct** devTool (`nix/devtools.nix`) and the binary backing the docker→podman shim (`flake.nix`). The image ships `podman-5.8.2` (confirmed in the run log). Reachability is bounded by the single-user dev model — podman is a rootless CLI running developer/CI-chosen images, not untrusted workloads.

## Why "advance the pinned rev" cannot fix it today

The pinned `nixpkgs` channel `release-26.05` (and `staging-26.05`) still ships podman **5.8.2**. The fix (5.8.4) is only on `master`/`staging`/`nixpkgs-unstable`. The 26.05 backport [NixOS/nixpkgs#536367](https://github.com/NixOS/nixpkgs/pull/536367) is **open (draft)**.

## Proposed fix

Add a short-dated `.vulnixignore` exception for `CVE-2026-57231` (expiry 2026-08-06, "re-check weekly"), matching the register's established convention, plus a `### Security` CHANGELOG note in `[0.4.1]`. The exception flips to a nixpkgs rev-advance once #536367 lands in `release-26.05`. This unblocks the 0.4.1 release gate.

## Acceptance

- [ ] `.vulnixignore` exception added with provenance + expiry; `check-expirations` passes
- [ ] `CHANGELOG.md` `[0.4.1]` `### Security` entry
- [ ] Lands on `release/0.4.1` via PR

---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 02:01 PM_

Resolved by #906 (merged into release/0.4.1, merge commit c3770915c). Not auto-closed because the merge target is a release branch, not the default branch.

