---
type: issue
state: closed
created: 2026-07-20T14:18:34Z
updated: 2026-07-20T14:28:57Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1219
comments: 0
labels: chore
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:02.589Z
---

# [Issue 1219]: [Clean up CODEOWNERS to reflect single-maintainer reality](https://github.com/vig-os/devkit/issues/1219)

CODEOWNERS currently assigns several paths (`.claude/skills/`, `justfile.worktree`, several `packages/vig-utils` tools) to @gerchowl, but c-vigo is the de-facto sole maintainer. Combined with the main ruleset's `require_code_owner_review`, this hard-blocks release finalization whenever a release diff touches a gerchowl-owned path — as happened with 1.4.0 (`justfile.worktree`, the #1203/#1204 fix): run 29749319623 failed validate and #1186 sits at REVIEW_REQUIRED with no reachable approver.

Reduce CODEOWNERS to the active maintainer: drop the @gerchowl entries entirely (un-owned paths carry no code-owner gate) and keep @c-vigo on the key control surfaces (workflows, actions, release scripts, renovate configs, CODEOWNERS itself, SECURITY.md).
