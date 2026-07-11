---
type: issue
state: closed
created: 2026-07-04T15:52:57Z
updated: 2026-07-04T20:01:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/827
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:38.311Z
---

# [Issue 827]: [C3 — templates.personal starter flake + homeConfigurations.demo](https://github.com/vig-os/devkit/issues/827)

templates.personal: ~20-line personal flake importing homeManagerModules.default with pin placeholder per the E2 policy. homeConfigurations.demo: synthetic demo user, full profile. Schema asserts in tests/test_flake_checks.py.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:23 PM_

Landed via PR #838 into `feature/814-home-environment-modules`. `templates.personal` (starter flake + README, pin-placeholder per E2), `homeConfigurations.demo` (full profile, synthetic user). Evidence: demo activationPackage evaluates; schema pytest green; sandbox pre-commit/deadnix/statix checks green (one ruff-format quoting fixup caught by the sandbox check before merge).

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

