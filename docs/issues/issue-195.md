---
type: issue
state: open
created: 2026-02-25T08:23:10Z
updated: 2026-02-25T10:37:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/195
comments: 4
labels: refactor, area:workspace, effort:small
assignees: c-vigo
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-26T04:22:24.891Z
---

# [Issue 195]: [[REFACTOR] Move alias definitions to source justfiles and add permanent Justfile file associations](https://github.com/vig-os/devcontainer/issues/195)

## Description
Refactor alias ownership so aliases are defined in their respective source justfiles (instead of being centralized in the top-level `justfile`), improving modularity and reducing drift between imported files and alias declarations.

Also add permanent editor file associations so `just-lsp` recognizes imported files such as `justfile.base` and other `just.*` files consistently.

## Files / Modules in Scope
- `justfile`
- `justfile.base`
- `justfile.worktree`
- Workspace/editor configuration file for file associations (e.g. `.vscode/settings.json` or equivalent canonical settings location)

## Out of Scope
- Any behavior change to existing recipes
- Adding/removing recipes unrelated to alias ownership
- CI/workflow changes unrelated to Justfile parsing or file associations

## Invariants / Constraints
- No observable behavior changes in recipes
- Existing aliases remain available after refactor
- Imported justfiles remain valid and parseable by `just` and `just-lsp`
- Keep changes minimal and limited to ownership/association concerns

## Acceptance Criteria
- [ ] Aliases currently in top-level `justfile` are moved to their corresponding justfile modules
- [ ] Top-level `justfile` only keeps aliases that truly belong to top-level concerns
- [ ] Permanent file association is configured so `just-lsp` recognizes:
  - `justfile`
  - `Justfile`
  - `just.*` (e.g. `justfile.base`, `justfile.worktree`)
- [ ] Existing tests/checks continue to pass
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Changelog Category
No changelog needed

## Additional Context
Proposed association snippet:

```json
{
  "files.associations": {
    "justfile": "just",
    "Justfile": "just",
    "just.*": "just"
  }
}
```

Related issues: #71, #187, #190
---

# [Comment #1]() by [c-vigo]()

_Posted on February 25, 2026 at 08:56 AM_

To consider: keep `justfiles` in `.devcontainer` purely container-reated:
- Devcontainer version
- GitHub interactions
- Sidecars
- Git
- Remote development
- ...

but move project-specific recipes to root folder, because they will be modified by users:
- Testing
- Linting
- Sync & update

---

# [Comment #2]() by [c-vigo]()

_Posted on February 25, 2026 at 10:23 AM_

## Design

Issue: #195
Branch: `195-refactor-move-alias-definitions-to-source-justfiles-and-add-permanent-justfile-file-associations`

### Problem

All aliases (podman, worktree, github) are centralized in the top-level `justfile` even though they alias recipes defined in imported justfiles. This creates ownership drift and makes each module less self-contained.

Additionally, the editor has no permanent file associations for `just.*` files (e.g. `justfile.base`, `justfile.worktree`), so `just-lsp` does not recognize them.

### Approach

**1. Move aliases to their source justfiles**

`just` 1.45.0 supports aliases in imported files. Each alias will move to the file that defines the recipe it references:

| Alias group | Current location | Target location |
|---|---|---|
| `pdm-*` (10 aliases) | `justfile` | `justfile.podman` |
| `wt-*` (5 aliases) | `justfile` | `justfile.worktree` |
| `gh-i` (1 alias) | `justfile` | `justfile.gh` |

The top-level `justfile` will have its entire alias section removed. No aliases belong to top-level concerns.

**2. Add permanent file associations**

Add a `files.associations` block to `.vscode/settings.json`:

```json
"files.associations": {
  "justfile": "just",
  "Justfile": "just",
  "just.*": "just"
}
```

This ensures `just-lsp` recognizes all justfile variants (`justfile`, `Justfile`, `justfile.base`, `justfile.worktree`, etc.).

### Decisions

- **No changes to `assets/workspace/` templates**: The asset templates (`assets/workspace/.devcontainer/justfile.base`, etc.) don't currently have aliases, so no changes needed there. The `.vscode/settings.json` at root is the canonical settings file for this repo.
- **No behavior changes**: All aliases remain available after the refactor since `just` imports bring aliases into the global namespace.
- **TDD note**: These are pure config/declaration changes (alias moves + JSON config). No testable behavior is introduced, so TDD is skipped for this issue. Verification is done by running `just --list` and confirming all aliases still appear.

### Testing Strategy

- Run `just --list` before and after, diff the output to confirm no recipes or aliases are lost.
- Run `just --evaluate` to confirm all justfiles parse correctly.
- Run `just precommit` to confirm pre-commit hooks pass.

---

# [Comment #3]() by [c-vigo]()

_Posted on February 25, 2026 at 10:24 AM_

## Implementation Plan

Issue: #195
Branch: `195-refactor-move-alias-definitions-to-source-justfiles-and-add-permanent-justfile-file-associations`

### Tasks

- [x] Task 1: Move podman aliases from `justfile` to `justfile.podman` — `justfile`, `justfile.podman` — verify: `just --list | grep pdm-`
- [x] Task 2: Move worktree aliases from `justfile` to `justfile.worktree` — `justfile`, `justfile.worktree` — verify: `just --list | grep wt-`
- [x] Task 3: Move github alias from `justfile` to `justfile.gh` — `justfile`, `justfile.gh` — verify: `just --list | grep gh-i`
- [x] Task 4: Remove the now-empty alias section from `justfile` — `justfile` — verify: `just --evaluate`
- [x] Task 5: Add `files.associations` to `.vscode/settings.json` — `.vscode/settings.json` — verify: `cat .vscode/settings.json | python3 -m json.tool`
- [x] Task 6: Full verification — diff `just --list` output before/after — verify: `diff /tmp/just-list-before.txt <(just --list 2>&1)`

---

# [Comment #4]() by [c-vigo]()

_Posted on February 25, 2026 at 10:37 AM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (6 tasks)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/200
- CI: all checks pass (10/10)

