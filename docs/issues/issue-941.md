---
type: issue
state: closed
created: 2026-07-08T15:56:17Z
updated: 2026-07-08T16:12:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/941
comments: 1
labels: security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:20.262Z
---

# [Issue 941]: [Except unfixed curl 8.20.0 CVEs blocking 0.5.0 RC (vulnix gate)](https://github.com/vig-os/devkit/issues/941)

## Problem

A fresh curl advisory batch (disclosed 2026-06-24) added **17 HIGH/CRITICAL CVEs against `curl 8.20.0`** to the NVD/vulnix feed. The nightly `security-scan` first went red on 2026-07-08 07:27 (green 2026-07-07), and the same findings now block the `0.5.0-rc1` publish at the **Vulnix CVE Gate** ([failed run](https://github.com/vig-os/devcontainer/actions/runs/28954286382)).

Findings (all in curl 8.20.0):

| CVE | CVSS |
|-----|------|
| CVE-2026-10536 | 9.8 |
| CVE-2026-11856 | 9.8 |
| CVE-2026-8925 | 9.8 |
| CVE-2026-9079 | 9.8 |
| CVE-2026-11564 | 9.1 |
| CVE-2026-8924 | 9.1 |
| CVE-2026-8926 | 9.1 |
| CVE-2026-8927 | 9.1 |
| CVE-2026-8286 | 8.1 |
| CVE-2026-11352 | 7.5 |
| CVE-2026-11586 | 7.5 |
| CVE-2026-12064 | 7.5 |
| CVE-2026-8932 | 7.5 |
| CVE-2026-9545 | 7.5 |
| CVE-2026-9546 | 7.5 |
| CVE-2026-9547 | 7.4 |
| CVE-2026-9080 | 7.3 |

## No fix available to bump to

curl is `8.20.0` in the pinned rev, latest `nixos-26.05`, **and** `nixpkgs-unstable`; upstream curl has no release newer than 8.20.0 yet. Since vulnix matches by version, only a version bump (none exists) or a register exception clears the gate. The "advance the rev" lever has nowhere to land.

## Decision

Register the 17 CVEs in `.vulnixignore` with a **short expiry (2026-07-22)** and `awaiting-upstream` rationale, per the IEC 62304 exception-register model already used for openssl/glibc/zlib/libssh2. This unblocks the RC and the nightly. Re-evaluate at expiry: when curl ships a fixed release and nixpkgs picks it up, drop the entries and advance the pin.

## Follow-up
- Remove these entries once a patched curl lands (Renovate `nix` manager should surface it).
- Fix targets the release branch `release/0.5.0` (bugfix PR); propagates to main/dev via the release + sync flow.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 04:12 PM_

Resolved. Time-boxed exceptions for the 17 curl 8.20.0 CVEs landed on `release/0.5.0` via #942 (squash-merged 2026-07-08).

- `check-expirations` passes (53 exceptions validated); `vulnix-gate` against synthetic curl-8.20.0 findings goes exit 1 → exit 0 with the block; PR CI **Security Scan** (real vulnix gate) green.
- **Follow-up is self-tracking:** the `Expiration: 2026-07-22` directive makes `check-expirations` fail CI at expiry, forcing a re-review. Drop the block and advance the nixpkgs pin once a patched curl ships (Renovate nix manager should surface it). No separate open issue needed.

Closing as completed.

