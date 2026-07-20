---
type: issue
state: closed
created: 2026-07-20T11:24:46Z
updated: 2026-07-20T11:44:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1216
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:03.323Z
---

# [Issue 1216]: [Detect host Nix probe captures ambient NIX_CONFIG parse error instead of version](https://github.com/vig-os/devkit/issues/1216)

## Problem

The `Detect host Nix` step in `setup-devkit-toolchain` (#1192) captures `nix --version 2>&1` (#1198). On a self-hosted runner whose service environment carries a malformed ambient `NIX_CONFIG` (observed on exo-fleet's meatgrinder during 1.4.0-rc5 validation, exo-pet/exo-fleet#230 run 29738048251, job 88338000749), nix 2.34 rejects the config before printing the version, so the detect log shows:

```
Host Nix present: /nix/var/nix/profiles/default/bin/nix (error: syntax error in configuration line 'experimental-features' in "NIX_CONFIG"
```

Non-fatal — the subsequent "Configure host Nix" step rewrites a clean `NIX_CONFIG` via `GITHUB_ENV` and the toolchain works — but the diagnostic value #1198 aimed for (a real version string in the log) is lost on exactly the hosts where diagnostics matter.

## Suggested fix

Run the detect probe with the ambient config scrubbed, e.g. `NIX_CONFIG= nix --version 2>&1` (or `env -u NIX_CONFIG`), so the captured string is the version even when the runner's environment is broken. Keep the `2>&1` fold as a fallback for other failure shapes.

## Scope

Dev-targeted polish (post-1.4.0), not a release blocker. Found during rc5 consumer-lane validation.

Refs: #1198, #1192
---

# [Comment #1]() by [c-vigo]()

_Posted on July 20, 2026 at 11:44 AM_

Fixed via PR #1217, merged into release/1.4.0 @0633f0c3. TDD: red test reproduces the meatgrinder symptom (stub nix erroring on malformed ambient NIX_CONFIG before --version); probe now runs `env -u NIX_CONFIG nix --version 2>&1`. Live proof lands with the exo-fleet lane re-bump on the next rc.

