---
type: issue
state: closed
created: 2026-07-04T15:51:22Z
updated: 2026-07-08T07:54:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/817
comments: 6
labels: chore, area:ci
assignees: none
milestone: 0.4.1
projects: none
parent: 814
children: none
synced: 2026-07-11T13:33:42.019Z
---

# [Issue 817]: [E3 — Scheduled nixpkgs-unstable lock bump workflow](https://github.com/vig-os/devkit/issues/817)

Weekly scheduled workflow + workflow_dispatch: `nix flake update nixpkgs-unstable` → chore branch → PR to dev, full CI as merge gate. Keeps the fastMovers overlay (uv, gh, claude-code) fresh; per the ADR, no third-party claude-code flake.

Part of the home-environment epic. Design authority: docs/rfcs/ADR-home-environment-modules.md.

Refs: #814
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:00 PM_

Landed via PR #832 into `feature/814-home-environment-modules`.

- `.github/workflows/update-nixpkgs-unstable.yml`: weekly cron + workflow_dispatch; app-token commit identity; SHA-pinned actions; opens/reuses a `chore/update-nixpkgs-unstable` PR to dev only when the lock changed.
- Verification: yamllint + check-action-pins hooks green at commit. NOTE: schedule only fires from the default branch — after this reaches dev, run one `workflow_dispatch` as the live test (morning task).

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:01 PM_

Merged to dev via the epic PRs (#833, #846). Evidence in the issue thread; epic tracking continues in #814.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 4, 2026 at 08:03 PM_

Reopening note: the first `workflow_dispatch` live test failed on the repo's **verified-signature rule** (git-CLI push from the runner is unsigned). Fix in PR #851: branch ref via API + `vig-os/commit-action` verified commit (the renovate mechanism). Will re-dispatch after #851 merges — expect a `chore/update-nixpkgs-unstable` PR bumping claude-code 2.1.177 → current.

---

# [Comment #4]() by [c-vigo]()

_Posted on July 4, 2026 at 08:39 PM_

Second live test (run 28718889651): the verified-commit fix from #851 **works** — the `chore/update-nixpkgs-unstable` branch was created and the lock-bump commit landed via `vig-os/commit-action` with a verified signature. The run now fails one step later: `gh pr create` → *"Resource not accessible by integration (createPullRequest)"* — **the commit GitHub App has no Pull requests permission.**

**Needed (owner action, one click):** in the GitHub App settings for the commit app (`COMMIT_APP_CLIENT_ID`), grant **Pull requests: Read and write**, then re-run the workflow (`gh workflow run update-nixpkgs-unstable.yml --ref dev`). No code change required — commit + branch steps already succeed.

Deliberately NOT worked around with `GITHUB_TOKEN`: PRs created by the Actions token don't trigger CI, which would leave every chore PR unmergeable against the required checks.

Current state: the chore branch holds the pending bump (nixpkgs-unstable 16 days stale → claude-code 2.1.177 → current); the next successful run force-resets and reuses it.

---

# [Comment #5]() by [c-vigo]()

_Posted on July 7, 2026 at 09:32 AM_

Verification before closing turned up a residual: the workflow landed (PR #851) and the lock bump works, but every run so far is red — the "Open PR if none exists" step fails with `GraphQL: Resource not accessible by integration (createPullRequest)` (run 28742838159 and both dispatches on 2026-07-04). The plain `GITHUB_TOKEN` can't create PRs here; it needs the Commit/Release-app token pattern the other privileged workflows use. Keeping open and pulling into 0.4.1.

---

# [Comment #6]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

