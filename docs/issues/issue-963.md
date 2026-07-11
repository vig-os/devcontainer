---
type: issue
state: closed
created: 2026-07-10T08:54:23Z
updated: 2026-07-10T09:08:43Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/963
comments: 0
labels: priority:blocking, security, security-scan
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:15.907Z
---

# [Issue 963]: [openssh 10.3p1 client UAF (CVE-2026-60002) fails nightly vulnix gate](https://github.com/vig-os/devkit/issues/963)

## Summary

The nightly **Scheduled Security Scan** ([run 29079456127](https://github.com/vig-os/devcontainer/actions/runs/29079456127), 2026-07-10) went red at the blocking `vulnix-gate` on one unexcepted finding:

- **CVE-2026-60002** (CVSS 7.7 HIGH per MITRE; NVD rates 9.4 CRITICAL) in **openssh 10.3p1**.

## Analysis

- **Nature:** use-after-free in the OpenSSH **client** (`ssh(1)`, not `sshd`), triggered when a malicious/compromised server changes its host key during key re-exchange (CWE-416). Client-side only.
- **Reachability:** `openssh` is in the image closure (dev tool / git-over-ssh). The `ssh` client is genuinely reachable, but the CVE requires the developer to connect *out* to an attacker-controlled SSH server that mutates its host key mid-rekey — bounded by the single-user dev model and typically-known hosts (github.com etc.). Real but narrow.
- **Fix:** OpenSSH **10.4p1**, released 2026-07-06.
- **Advance-the-rev lever has nowhere to land today:** openssh is `10.3p1` across every nixpkgs branch checked (nixos-26.05 = pinned channel, release-26.05, staging-26.05, master, nixpkgs-unstable). The 10.4p1 bump is merged into the **26.05 staging pipeline** ([nixpkgs#539452](https://github.com/NixOS/nixpkgs/pull/539452) → `staging-nixos`, merged 2026-07-09; backport [nixpkgs#539933](https://github.com/NixOS/nixpkgs/pull/539933) → `staging-nixos-26.05`, merged 2026-07-10) but has **not** yet flowed to `nixos-26.05`.

## Affects both `main` and `release/0.5.1`

`release/0.5.1` has a byte-identical `flake.lock` (same nixpkgs rev → same openssh 10.3p1) and identical `.vulnixignore`, so it fails the same gate. Not a release *blocker* (the scan runs on schedule/dispatch only, not on release push/PR), but a live HIGH that will keep firing nightly.

## Plan

Time-boxed `.vulnixignore` exception (awaiting-nixpkgs), matching the curl #941 / libssh2 / podman #905 precedent, with a short expiry to force re-review. **Flip to a nixpkgs rev-advance** once 10.4p1 reaches `nixos-26.05`. Land on `release/0.5.1`; add a `### Security` changelog entry.

