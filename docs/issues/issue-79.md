---
type: issue
state: open
created: 2026-02-18T13:30:08Z
updated: 2026-02-20T14:39:16Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/79
comments: 3
labels: feature, priority:medium, area:ci, effort:small, semver:patch
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-20T15:25:37.903Z
---

# [Issue 79]: [[FEATURE] Automatic commit message for pull request merge](https://github.com/vig-os/devcontainer/issues/79)

### Description

Merge commit should follow message standards, either via:

- Automatic web interface commit message upon pull request merge
- GH API

### Problem Statement

Merge commits do not follow our commit standard

### Proposed Solution

Example of message following our standards:

```
chore: merge pull request #78 from vig-os/feature/58-default-commit-validation

feat(vigutils): add --require-scope flag and strict-by-default hook config

Passes all CI/CD

Refs: #58
```

### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

_No response_
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 07:29 PM_

## Implementation Plan

Issue: #79
Branch: `feature/79-auto-merge-commit-message`

### Design Decisions (from brainstorm)

- **Repo merge settings** changed via `gh api`:
  - `merge_commit_title`: `MERGE_MESSAGE` → `PR_TITLE` (merge commit subject = PR title)
  - `merge_commit_message`: `PR_TITLE` → `PR_BODY` (merge commit body = PR body)
- PR titles already follow the commit message standard (`type(scope): description`), so the merge commit subject is automatically compliant.
- PR body template updated to include `Refs:` line, ensuring traceability in merge commit body.
- PR title validated by a CI workflow that reuses `validate_commit_msg.py` (existing logic, no duplication).

### Tasks

- [ ] **Task 1**: Add `gh-repo-merge-settings` recipe to `justfile.gh` — sets `merge_commit_title=PR_TITLE` and `merge_commit_message=PR_BODY` via `gh api` — `justfile.gh` — verify: recipe parses (`just --list --justfile justfile.gh`)
- [ ] **Task 2**: Write failing test for PR title validation (test that `validate_commit_message` correctly validates a PR-title-only string with refs exemption) — `packages/vig-utils/tests/` — verify: `uv run pytest` shows test failing
- [ ] **Task 3**: Add CLI support for subject-only validation (all refs optional) to `validate_commit_msg.py` — `packages/vig-utils/src/vig_utils/validate_commit_msg.py` — verify: `uv run pytest` passes
- [ ] **Task 4**: Create `pr-title-check.yml` workflow that validates the PR title using `validate-commit-msg` on `pull_request: opened/edited/synchronize` — `.github/workflows/pr-title-check.yml` — verify: `actionlint` or yamllint passes
- [ ] **Task 5**: Update PR body template to include `Refs: #` at the bottom so merge commit body contains traceability — `.github/pull_request_template.md` — verify: visual inspection
- [ ] **Task 6**: Update `CHANGELOG.md` under `## Unreleased` — `CHANGELOG.md` — verify: follows existing format

**TDD applies to:** Tasks 2–3 (test first, then implementation).
**TDD skipped for:** Tasks 1, 4, 5, 6 (config, workflow YAML, template, docs — not unit-testable).

cc @c-vigo — does this plan look good to you?

---

# [Comment #2]() by [c-vigo]()

_Posted on February 19, 2026 at 04:03 PM_

Looks good to me! COuple of points:

- You might need a placeholder for `pr-title-check.yml` in `main` for this to work right away, not sure.
- After implementing and merging, I would leave the issue open until we verify it and turn on `Auto merge` [here](https://github.com/vig-os/devcontainer/settings). The `gh-repo-merge-settings` recipe should also set this value.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 20, 2026 at 02:16 PM_

## Implementation Plan

Issue: #79
Branch: `feature/79-auto-merge-commit-message`

### Tasks

- [x] Task 1: Create `setup-gh-repo.sh` script that configures repo merge settings (`merge_commit_title=PR_TITLE`, `merge_commit_message=PR_BODY`, `allow_auto_merge=true`) via `gh api` — `assets/workspace/.devcontainer/scripts/setup-gh-repo.sh` — verify: `bash -n assets/workspace/.devcontainer/scripts/setup-gh-repo.sh`
- [x] Task 2: Wire `setup-gh-repo.sh` into `post-create.sh` — call it after git/gh setup — `assets/workspace/.devcontainer/scripts/post-create.sh` — verify: `bash -n assets/workspace/.devcontainer/scripts/post-create.sh`
- [x] Task 3: Write failing test for `--subject-only` mode in `validate_commit_msg.py` (TDD red) — `packages/vig-utils/tests/test_validate_commit_msg.py` — verify: `just test-vig-utils` shows test failing
- [x] Task 4: Implement `--subject-only` flag and `subject_only` parameter in `validate_commit_message()` (TDD green) — `packages/vig-utils/src/vig_utils/validate_commit_msg.py` — verify: `just test-vig-utils` passes
- [x] Task 5: Create `pr-title-check.yml` workflow — validates PR title using `validate-commit-msg --subject-only` on `pull_request: opened/edited/synchronize` — `.github/workflows/pr-title-check.yml` — verify: `yamllint .github/workflows/pr-title-check.yml`
- [x] Task 6: Update PR body template to include `Refs: #` placeholder — `.github/pull_request_template.md` — verify: visual inspection
- [x] Task 7: Update `CHANGELOG.md` under `## Unreleased` — `CHANGELOG.md` — verify: follows existing format

**TDD applies to:** Tasks 3–4 (test first, then implementation).
**TDD skipped for:** Tasks 1, 2, 5, 6, 7 (shell scripts, workflow YAML, template, docs — not unit-testable).

**Post-merge action:** Run `setup-gh-repo.sh` manually against `vig-os/devcontainer` since the container won't be recreated just for this change.

