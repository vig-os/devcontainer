---
type: issue
state: closed
created: 2026-06-30T12:52:09Z
updated: 2026-07-03T11:22:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/779
comments: 1
labels: chore, priority:medium, area:ci, effort:large
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:48.094Z
---

# [Issue 779]: [[CHORE] Flake-checks as CI Tier 0 (garnix / nix-fast-build)](https://github.com/vig-os/devkit/issues/779)

**Source:** PR #670 roadmap, thread C — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). **Deferred.**

Move *pure* checks into `checks.<system>.*` (nixfmt, ruff, typos, shellcheck, taplo, deadnix/statix; pure pytest units `test_utils`/`test_vulnix_gate`/`test_claude_ssot`/`check-expirations`; `checks.pre-commit` from thread B). **Keep effectful jobs GH-orchestrated** (image testinfra, network integration, parity test, vulnix CVE-DB, multi-arch, publish/cosign/SBOM/cachix). Drive with **garnix** (hosted app, zero YAML) or **`nix-fast-build`/`om ci`** on existing runners. Tier-1 (Hydra/Buildkite self-host) is a separate, later decision. Refs #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 11:22 AM_

Closed in #791 

