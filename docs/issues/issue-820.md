---
type: issue
state: closed
created: 2026-07-04T15:52:26Z
updated: 2026-07-04T20:01:38Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/820
comments: 2
labels: feature, area:ci
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:40.895Z
---

# [Issue 820]: [A3 — aarch64-darwin + aarch64-linux home-matrix CI workflow with Cachix push](https://github.com/vig-os/devkit/issues/820)

Separate non-required workflow (fail-soft by status, not continue-on-error): macos-latest (arm64) and ubuntu-24.04-arm jobs building hm-minimal/hm-full for their system and pushing closures to the vig-os Cachix. Must be green before first colleague onboarding; promotion to required check is a follow-up decision.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:32 PM_

Landed via PR #836 into `feature/814-home-environment-modules`. First live runs of the *Home Matrix* workflow on draft PR #833 **succeeded** on both jobs (macos-latest arm64 + ubuntu-24.04-arm), hm-minimal/hm-full built and closures pushed to the `vig-os` Cachix — the darwin-cache-before-onboarding gate is satisfied. Non-required (fail-soft) by design; promotion to required is a morning decision.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

