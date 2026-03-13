---
type: issue
state: open
created: 2026-02-25T09:51:14Z
updated: 2026-02-25T10:42:02Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/197
comments: 3
labels: bug, area:workspace, effort:small, semver:patch
assignees: c-vigo
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-26T04:22:24.265Z
---

# [Issue 197]: [[BUG] install.sh is not idempotent and creates nested src/tmp/template_project on second run](https://github.com/vig-os/devcontainer/issues/197)

## Description
Running `install.sh` a second time in the same target directory creates an unexpected nested folder (`src/tmp/template_project/`) instead of keeping the workspace clean/idempotent.

## Steps to Reproduce
1. Run:
   `~/Documents/vigOS/devcontainer/install.sh ./ --version dev --skip-pull --force --org vigOS`
2. Confirm working tree is clean:
   `git status` -> `nothing to commit, working tree clean`
3. Run the same install command again in the same directory.
4. Check status:
   `git status` -> shows untracked files under `src/tmp/template_project/`

## Expected Behavior
Re-running `install.sh` on the same directory should be idempotent and should not create additional nested template folders or untracked artifacts.

## Actual Behavior
Second execution creates `src/tmp/template_project/` as untracked content.

## Environment
- **OS**: Linux 6.17.0-14-generic
- **Container Runtime**: N/A (not involved in reproduction)
- **Image Version/Tag**: `dev` (`--version dev`)
- **Architecture**: x86_64

## Additional Context
Reproduction commands/output provided by reporter:

```bash
~/Documents/vigOS/devcontainer/install.sh ./ --version dev --skip-pull --force --org vigOS
git status  # clean
~/Documents/vigOS/devcontainer/install.sh ./ --version dev --skip-pull --force --org vigOS
git status  # shows src/tmp/template_project/
```

## Possible Solution
Ensure `install.sh` handles repeat execution safely by:
- normalizing target path handling for template copy/sync operations
- preventing recursive copy into `src/` when target is already initialized
- adding guard clauses for existing destination structure

## Changelog Category
Fixed

## Acceptance Criteria
- [ ] Re-running `install.sh` with the same arguments does not create new untracked files/folders
- [ ] `src/tmp/template_project/` is not created on second run
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
---

# [Comment #1]() by [c-vigo]()

_Posted on February 25, 2026 at 10:29 AM_

## Design

### Root Cause

In \`assets/init-workspace.sh\`, the rename logic at lines 256-259:

\`\`\`bash
if [[ -d "$WORKSPACE_DIR/src/template_project" ]]; then
    mv "$WORKSPACE_DIR/src/template_project" "$WORKSPACE_DIR/src/${SHORT_NAME}"
fi
\`\`\`

On **first run**: rsync copies \`src/template_project/\` from the template, then \`mv\` renames it to \`src/${SHORT_NAME}/\`. Correct.

On **second run** (with \`--force\`): rsync re-copies \`src/template_project/\` because it no longer exists in the workspace (it was renamed). Then \`mv\` attempts to rename it to \`src/${SHORT_NAME}\`, but that directory already exists. The \`mv\` command moves \`template_project\` **inside** the existing directory, creating \`src/${SHORT_NAME}/template_project/\`.

### Fix

In the rename block, check whether \`src/${SHORT_NAME}\` already exists. If so, remove the redundant \`src/template_project\` instead of renaming it. This handles the idempotency case cleanly:

\`\`\`bash
if [[ -d "$WORKSPACE_DIR/src/template_project" ]]; then
    if [[ -d "$WORKSPACE_DIR/src/${SHORT_NAME}" ]] && [[ "$SHORT_NAME" != "template_project" ]]; then
        echo "Removing duplicate src/template_project (src/${SHORT_NAME} already exists)..."
        rm -rf "$WORKSPACE_DIR/src/template_project"
    else
        echo "Renaming src/template_project to src/${SHORT_NAME}..."
        mv "$WORKSPACE_DIR/src/template_project" "$WORKSPACE_DIR/src/${SHORT_NAME}"
    fi
fi
\`\`\`

### Testing Strategy

Add a BATS test to \`tests/bats/init-workspace.bats\` that verifies the guard clause exists in the script. This matches the existing test pattern (structure/grep tests) since functional testing of init-workspace.sh requires a container environment.

### Scope

- **Files changed**: \`assets/init-workspace.sh\` (fix), \`tests/bats/init-workspace.bats\` (test), \`CHANGELOG.md\` (entry)
- **No changes** to \`install.sh\` — the bug is entirely in the container-side script.

---

# [Comment #2]() by [c-vigo]()

_Posted on February 25, 2026 at 10:29 AM_

## Implementation Plan

Issue: #197
Branch: bugfix/197-install-sh-idempotent

### Tasks

- [x] Task 1: Add BATS test for idempotent rename guard — `tests/bats/init-workspace.bats` — verify: `just test-bats`
- [x] Task 2: Fix rename logic in init-workspace.sh to handle existing destination — `assets/init-workspace.sh` — verify: `just test-bats`
- [x] Task 3: Add CHANGELOG entry — `CHANGELOG.md` — verify: `grep 'idempotent' CHANGELOG.md`

---

# [Comment #3]() by [c-vigo]()

_Posted on February 25, 2026 at 10:42 AM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (3 tasks)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/201
- CI: all checks pass (10/10)

