---
type: issue
state: open
created: 2026-02-20T09:25:33Z
updated: 2026-02-20T09:25:49Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/99
comments: 1
labels: feature
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-20T13:17:18.889Z
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

