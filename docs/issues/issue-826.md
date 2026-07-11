---
type: issue
state: closed
created: 2026-07-04T15:52:56Z
updated: 2026-07-04T20:01:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/826
comments: 2
labels: docs
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:38.680Z
---

# [Issue 826]: [C2 — Override cookbook, rollback, Intel tier, credential hygiene docs](https://github.com/vig-os/devkit/issues/826)

Override cookbook (mkDefault/mkForce/extraConfig, disabling a module, keeping your own tmux.conf). Rollback one-pager (HM generations / nixos-rebuild --rollback / image-tag pin). Spelled-out operational meaning of best-effort x86_64-darwin (eval-only, fallback = amd64 devcontainer image, EOL at nixpkgs 26.05 EOL 2026-12-31). Credential-hygiene one-pager: fine-grained expiring PATs, per-userxhost SSH keys (auth + signing, never copied — signatures identify the machine), rotation/offboarding runbook, secretsEnv interface.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:25 PM_

Landed via PR #839 into `feature/814-home-environment-modules` — docs/home/{BOOTSTRAP,COOKBOOK,ROLLBACK,CREDENTIALS}.md. pymarkdown/typos hooks green. The zero-live-help onboarding acceptance test runs when the arm-Mac colleague first follows BOOTSTRAP.md.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

