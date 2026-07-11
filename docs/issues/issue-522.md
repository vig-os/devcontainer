---
type: issue
state: closed
created: 2026-04-15T06:53:58Z
updated: 2026-07-08T08:14:16Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/522
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:19.248Z
---

# [Issue 522]: [Missing per-repo bootstrap guide for vigOS branching convention on non-Enterprise orgs](https://github.com/vig-os/devkit/issues/522)

## Problem

After `init-workspace.sh` finishes, the scaffold assumes the vigOS dev/main branching convention is already in place (workflows like `sync-issues.yml`, `sync-main-to-dev.yml`, and the release cycle all target `dev` by default, and rely on `COMMIT_APP_*` / `RELEASE_APP_*` secrets plus `COMMIT_APP` being in the `dev` branch-protection bypass list).

On a **non-Enterprise** GitHub org (e.g. a community org or a second org alongside the vig-os Enterprise one), none of that is bootstrapped automatically: there's no `dev` branch, no rulesets, no GitHub App installations, and no secrets. The scaffolded workflows fail daily ("Sync Issues and PRs" → `appId is required` or git checkout of `refs/heads/dev` returning exit 1) until an operator figures out the full manual setup.

Closed issue #38 confirms that this is intentional — protection rules are applied as GitHub Enterprise org-wide rules, not per-repo scripts. That's fine for the Enterprise org, but the rest of us need a paved path.

## What's missing

Everything between `init-workspace.sh` finishing and the release workflows being runnable:

1. **`dev` branch creation** from `main`
2. **Branch rulesets** on both `main` and `dev` with the `COMMIT_APP` + `RELEASE_APP` App IDs in the bypass list
3. **GitHub App installation** on the target repo (`commit-action-bot`, `vig-os-release-app`)
4. **Org/repo secrets** (`COMMIT_APP_ID`, `COMMIT_APP_PRIVATE_KEY`, `RELEASE_APP_ID`, `RELEASE_APP_PRIVATE_KEY`)
5. **Required status check contexts** matched to the scaffold's `ci.yml` job names

## Prior art in this repo

- `docs/RELEASE_CYCLE.md` defines the branch model and protection intent (~L40–90) and describes the two apps' permissions in "GitHub App Configuration" (~L546)
- `docs/DOWNSTREAM_RELEASE.md` "Required App Secrets" lists the four secrets
- `assets/workspace/.devcontainer/scripts/setup-gh-repo.sh` — the closest thing to repo setup automation; only tweaks merge-commit format and detaches security config
- `assets/init-workspace.sh` — substitutes `{{SHORT_NAME}}` / `{{ORG_NAME}}` / `{{GITHUB_REPOSITORY}}` placeholders, runs `just sync`; does not touch branches/rulesets/apps/secrets
- Closed #38 (Enterprise-level enforcement) and closed #170 (manual smoke-test bootstrap)

## Proposal

Either (or both):

**A. `just bootstrap-repo` recipe** in `assets/workspace/justfile.gh` that:
- Reads the current repo from `gh repo view`
- Creates `dev` from `main` via `gh api`
- Applies two rulesets via `gh api repos/{owner}/{repo}/rulesets` with `COMMIT_APP` and `RELEASE_APP` bypass by App ID (reading the IDs from env / `.vig-os` / prompt)
- Prints an interactive checklist for the manual parts that require human judgment (App installation page, secret values)
- Idempotent — safe to re-run

**B. Post–`init-workspace.sh` printable checklist** with the actual `{{GITHUB_REPOSITORY}}` substituted into every URL and command, so an operator can just follow along:
- \`https://github.com/apps/commit-action-bot/installations/new\` → select this repo
- \`https://github.com/apps/vig-os-release-app/installations/new\` → select this repo
- \`https://github.com/organizations/{{ORG_NAME}}/settings/secrets/actions\` → set the four secrets
- \`gh api -X POST repos/{{GITHUB_REPOSITORY}}/git/refs -f ref=refs/heads/dev -f sha=\$(...)\`
- \`gh api repos/{{GITHUB_REPOSITORY}}/rulesets -X POST --input ...\`
- ...etc.

Option B alone would resolve the gap; Option A is nicer but more work and needs careful handling of secret input.

## Impact

Any repo scaffolded onto a non-Enterprise org hits this wall and has to reverse-engineer the convention from the failing workflows and template workflows. A first-time user of the devcontainer on a community org will spend an hour figuring out that `COMMIT_APP_*` isn't a stub, the App needs to be installed, the PEM has to be set by piping to `gh secret set`, and that `dev` doesn't exist yet — none of which is in the README or docs.

## References
- #38 — Enterprise-level enforcement
- #170 — manual smoke-test bootstrap
- \`docs/RELEASE_CYCLE.md\` — branch model + app config
- \`docs/DOWNSTREAM_RELEASE.md\` — required secrets list
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 08:14 AM_

Closing as part of an agreed backlog cleanup (with @gerchowl) — valid but dormant, no work in progress since the Nix migration. Reopen or refile fresh if picked up.

