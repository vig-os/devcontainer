---
type: issue
state: closed
created: 2026-06-30T12:52:10Z
updated: 2026-07-01T11:20:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/780
comments: 1
labels: priority:medium, area:ci, effort:large, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:47.677Z
---

# [Issue 780]: [[SECURITY] Secrets-management pattern: sops-nix/age + OIDC](https://github.com/vig-os/devkit/issues/780)

**Source:** PR #670 roadmap, thread D — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). **Deferred (needs design).**

Ship the secret-management **pattern**: **sops-nix + age** for runtime + downstream-consumer secrets (decrypt with the consumer's own key, no per-repo GH secret dance) and **OIDC** for cloud/registry auth. Honest caveat: on GH-hosted runners SOPS **relocates** the root of trust to one bootstrap key — it doesn't eliminate the GH secret; OIDC is the real "no stored secret" lever. Keep the existing GH App installation-token model. Refs #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

Resolved on `dev` by PR #787 (`docs(security): record sops-nix/age + OIDC secrets-management pattern`). The secrets-management pattern is recorded as an ADR with the OIDC lever documented. Note: the broader repo-standard framing is tracked separately in #786. Refs #625.

