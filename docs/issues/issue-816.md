---
type: issue
state: closed
created: 2026-07-04T15:51:21Z
updated: 2026-07-04T20:01:31Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/816
comments: 2
labels: docs
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:42.395Z
---

# [Issue 816]: [E2 — Module release/versioning/changelog policy + scaffold vigos.url alignment](https://github.com/vig-os/devkit/issues/816)

Document in docs/NIX.md: modules ride the existing release train; consumers pin `github:vig-os/devcontainer/<tag>`; option renames get a mkRenamedOptionModule shim for one release + changelog entry; dogfood-canary exception (maintainer tracks dev until first module-bearing tag). Add the *Modules* subcategory convention to CHANGELOG.md. Align the workspace scaffold's untagged `vigos.url` with the policy (pin, or explicitly documented float).

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 03:58 PM_

Landed via PR #831 (commit 3cb7e314) into `feature/814-home-environment-modules`.

- `docs/NIX.md`: new *Home-manager modules — versioning & release policy* section (release train, pin recipe, deprecation shims, canary exception, `#### Modules` changelog convention).
- Scaffold `assets/workspace/flake.nix`: deliberate-float comment + pin recipe above `vigos.url`.
- Verification: downstream-stub `nix flake check ./assets/workspace --override-input vigos path:$PWD` exit 0; pre-commit hooks green.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

