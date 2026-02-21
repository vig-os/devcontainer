---
type: issue
state: open
created: 2026-02-20T09:25:33Z
updated: 2026-02-20T23:22:49Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/99
comments: 3
labels: feature
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-21T04:11:19.638Z
---

# [Issue 99]: [[FEATURE] Add unit and container integration tests for scripts/gh_issues.py](https://github.com/vig-os/devcontainer/issues/99)

### Description

Add unit tests and container integration tests for `scripts/gh_issues.py`, which currently has ~540 lines, ~15 functions, and zero test coverage. The script is deployed to downstream workspaces via the sync manifest and needs verification at both the logic and deployment layers.

### Problem Statement

`scripts/gh_issues.py` was originally skipped for TDD with the rationale "no unit-testable logic beyond subprocess calls and rich rendering" (see #84). The script has since grown to include multiple pure-logic functions that are fully testable without mocking `gh` CLI calls or Rich rendering. Additionally, there is no verification that the deployed copy works inside the container or that runtime dependencies are available.

### Proposed Solution

**Two test layers:**

#### 1. Unit tests (`tests/test_gh_issues.py`)

Test all pure-logic functions — no subprocess mocking, no Rich rendering tests:

| Function | What it does |
|---|---|
| `_styled(value, style)` | Wraps text in Rich markup |
| `_extract_label(labels, prefix)` | Finds label by prefix, applies style |
| `_extract_type(labels)` | Finds type label, applies style |
| `_extract_scope(labels)` | Collects `area:*` labels |
| `_clean_title(title)` | Strips `[FEATURE]` etc. prefix |
| `_format_assignees(assignees)` | Formats assignee list |
| `_infer_review(pr)` | Derives review state from PR dict |
| `_extract_reviewers(pr)` | Builds reviewer string from PR dict |
| `_build_cross_refs(branches, prs)` | Builds issue↔PR mappings |

#### 2. Container integration tests (in `tests/test_image.py`)

Add to existing test structure:
- Verify `.devcontainer/scripts/gh_issues.py` exists in the image
- Verify `.devcontainer/justfile.gh` exists in the image
- Verify `rich` is importable: `python -c "from rich.table import Table"`
- Verify `gh_issues.py` is importable in the container (catches syntax errors, missing imports)

### Prerequisite

The uncommitted `gh_issues.py` changes from the #67 branch (reviewer/assignee columns, `_infer_review`, `_extract_reviewers`, `_fetch_sub_issue_tree`, `_build_cross_refs` with closing-keyword parsing) should be moved to this issue's branch. These are the functions that need test coverage.

### Alternatives Considered

- **Test Rich rendering output** — fragile, visual, not worth the maintenance cost
- **Mock subprocess/gh CLI calls** — adds complexity without testing real behavior; save for a future refactoring issue that separates I/O from logic
- **Refactor to extract I/O boundaries first** — worthwhile but separate scope; test the current pure functions first

### Additional Context

- Related: #84 (original script creation), #67 (declarative sync manifest)
- The existing `test_manifest_files` in `test_image.py` already partially covers the deployed copy via SHA-256 checksum verification, but doesn't verify importability or runtime deps
- `scripts/gh_issues.py` depends on `rich` (installed via `uv pip install --system` in the Containerfile) and `gh` CLI

### Impact

- Tests-only change — no user-visible impact, no changelog entry needed
- Establishes test coverage for a growing utility script
- Container integration tests catch deployment regressions early

### Changelog Category

No changelog needed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 09:25 AM_

## Design

### Problem

`scripts/gh_issues.py` has ~540 lines, ~15 functions, and zero test coverage. The original TDD-skip rationale ("no unit-testable logic beyond subprocess calls and rich rendering") no longer holds — the script now contains multiple pure-logic functions fully testable without mocking.

The script is deployed via the sync manifest to `.devcontainer/scripts/gh_issues.py`, but there is no verification that the deployed copy works inside the container or that runtime dependencies are available.

### Approach: Two Test Layers

#### Layer 1: Unit tests (`tests/test_gh_issues.py`)

Pure-logic functions tested with plain data in, data out — no mocking needed:

| Function | Signature | Test strategy |
|---|---|---|
| `_styled(value, style)` | `str, str -> str` | Assert Rich markup wrapping |
| `_extract_label(labels, prefix)` | `list[dict], str -> str` | Label dicts with matching/missing prefixes |
| `_extract_type(labels)` | `list[dict] -> str` | Label dicts with/without type labels |
| `_extract_scope(labels)` | `list[dict] -> str` | Single and multiple `area:*` labels |
| `_clean_title(title)` | `str -> str` | Titles with/without `[FEATURE]` etc. prefix |
| `_format_assignees(assignees)` | `list[dict] -> str` | Empty list, single, multiple assignees |
| `_infer_review(pr)` | `dict -> tuple[str, str]` | Various combinations of `reviewDecision`, `latestReviews`, `reviewRequests` |
| `_extract_reviewers(pr)` | `dict -> str` | Approved, changes requested, requested states |
| `_build_cross_refs(branches, prs)` | `dict, list[dict] -> tuple[dict, dict]` | Branch matching, closing keywords, both |

#### Layer 2: Container integration tests (in `tests/test_image.py`)

Added to existing `TestWorkspaceStructure`:

1. **Deployed files exist**: `.devcontainer/scripts/gh_issues.py` and `.devcontainer/justfile.gh` present in image
2. **`rich` importable**: `python -c "from rich.table import Table"` succeeds
3. **Script importable**: `python -c "import sys; sys.path.insert(0, '/root/assets/workspace/.devcontainer/scripts'); import gh_issues"` succeeds

### Prerequisite

Move the uncommitted `gh_issues.py` changes from the #67 branch to this issue's branch. These contain the functions (`_infer_review`, `_extract_reviewers`, enhanced `_build_cross_refs`) that need test coverage.

### Out of scope

- Testing actual `gh` CLI calls (requires GitHub auth)
- Testing Rich table rendering output (visual, fragile)
- Refactoring to extract I/O boundaries (separate issue)

---

# [Comment #2]() by [gerchowl]()

_Posted on February 20, 2026 at 04:15 PM_

## Implementation Plan

Issue: #99
Branch: `feature/99-just-gh-issues-overview-test-coverage`

### Tasks

- [x] Task 1: Add unit tests for all 9 pure-logic functions in `scripts/gh_issues.py` — `tests/test_gh_issues.py` — verify: `uv run pytest tests/test_gh_issues.py -v`
  - `_styled`: 3 tests (markup wrapping, empty value, empty style)
  - `_extract_label`: 7 tests (matching prefix, no match, empty, unknown label, first-match-wins, effort, semver)
  - `_extract_type`: 6 tests (feature/bug/discussion/chore labels, no type, empty)
  - `_extract_scope`: 4 tests (single area, multiple areas, no area, empty)
  - `_clean_title`: 7 tests (all 5 prefixes, no prefix, empty)
  - `_format_assignees`: 3 tests (empty, single, multiple)
  - `_infer_review`: 9 tests (3 known decisions, unknown, fallback to latestReviews, last-wins, fallback to reviewRequests, no info, empty dict)
  - `_extract_reviewers`: 8 tests (no reviews, approved/changes_requested/requested reviewers, mixed, name fallback, empty dict, no-duplicate)
  - `_build_cross_refs`: 10 tests (branch match, closes/fixes/resolves keywords, case-insensitive, both branch+keyword, no matches, empty inputs, None body, multiple PRs)
  - **57 tests total, all passing**
- [x] Task 2: Add container integration tests for `gh_issues.py` runtime deps — `tests/test_image.py` — verify: `just test-image`
  - `test_rich_importable`: verify `from rich.table import Table` succeeds in container
  - `test_gh_issues_importable`: verify `import gh_issues` succeeds (catches syntax errors, missing imports)
  - File existence and checksum already covered by existing `test_manifest_files`

### Dropped

- **`just` recipe for gh-issues tests**: unnecessary — `just test` already runs all test files
- **`justfile.gh` existence test**: file does not exist in the repo or manifest

---

# [Comment #3]() by [gerchowl]()

_Posted on February 20, 2026 at 11:22 PM_

## Implementation Plan (Fix: move `rich` to system-wide install)

Issue: #99
Branch: `feature/99-just-gh-issues-overview-test-coverage`
PR review: https://github.com/vig-os/devcontainer/pull/129#discussion_r2835415754

### Context

@c-vigo correctly notes that `rich` is a devcontainer tool (like `pre-commit`, `ruff`), not a project dependency. Users modify `pyproject.toml` and would unintentionally remove `rich`. It belongs in the Containerfile as a system-wide install.

### Tasks

- [ ] Task 1: Revert `rich>=13.0` from `assets/workspace/pyproject.toml` — restore `dependencies = []` — verify: `git diff assets/workspace/pyproject.toml`
- [ ] Task 2: Add `rich` to system-wide Python tools in `Containerfile` — add to existing `uv pip install --system` line — verify: `grep rich Containerfile`
- [ ] Task 3: Change `justfile.gh` to use `python3` instead of `uv run python` — both `justfile.gh` (source) and `assets/workspace/.devcontainer/justfile.gh` (deployed copy) — verify: `just --list --justfile justfile.gh`
- [ ] Task 4: Update container integration tests to use system `python3` instead of venv Python — `tests/test_image.py` — verify: `uv run pytest tests/test_image.py -k "test_rich or test_gh_issues_importable" --co`
- [ ] Task 5: Run sync manifest to update checksums for `justfile.gh` — verify: `just sync-workspace`

