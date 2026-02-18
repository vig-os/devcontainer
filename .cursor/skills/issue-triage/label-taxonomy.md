# Label Taxonomy

Predefined labels used by the issue triage skill. On first run the skill
compares these against the repo's actual labels (`gh label list`) and asks
the user to approve creation of any that are missing.

Existing type labels (`bug`, `feature`, `question`, `documentation`, etc.)
are not listed here -- they are already in the repo and serve as the **type**
dimension.

## Priority

| Label | Color | Description |
|-------|-------|-------------|
| `priority:blocking` | `#b60205` | Blocks other work or a release |
| `priority:high` | `#d93f0b` | Should be done in the current milestone |
| `priority:medium` | `#fbca04` | Important but not urgent |
| `priority:low` | `#0e8a16` | Nice to have, do when capacity allows |
| `priority:backlog` | `#c5def5` | Someday/maybe, no timeline |

## Area

| Label | Color | Description |
|-------|-------|-------------|
| `area:ci` | `#1d76db` | CI/CD, GitHub Actions, workflows |
| `area:image` | `#1d76db` | Container image, Dockerfile, build |
| `area:workspace` | `#1d76db` | Workspace tooling, justfile, templates |
| `area:workflow` | `#1d76db` | Developer workflow, commands, rules, skills |
| `area:docs` | `#1d76db` | Documentation, README, guides |
| `area:testing` | `#1d76db` | Test infrastructure, BATS, pytest |

## Effort

| Label | Color | Description |
|-------|-------|-------------|
| `effort:small` | `#c2e0c6` | Less than 1 hour |
| `effort:medium` | `#fef2c0` | 1-4 hours |
| `effort:large` | `#f9d0c4` | More than 4 hours or multi-session |

## SemVer Impact

| Label | Color | Description |
|-------|-------|-------------|
| `semver:major` | `#b60205` | Breaking change |
| `semver:minor` | `#fbca04` | New feature, backward-compatible |
| `semver:patch` | `#0e8a16` | Bug fix, backward-compatible |
