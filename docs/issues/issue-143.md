---
type: issue
state: open
created: 2026-02-21T21:23:24Z
updated: 2026-02-21T21:58:59Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/143
comments: 1
labels: feature, area:workflow, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-22T04:23:20.233Z
---

# [Issue 143]: [[FEATURE] Show CI status and failure details in just gh-issues PR table](https://github.com/vig-os/devcontainer/issues/143)

### Description

Enhance the `just gh-issues` PR table to show CI pipeline status for each open PR. When checks fail, show which check(s) failed. Include a clickable link to the CI run overview on GitHub.

### Problem Statement

When reviewing open PRs via `just gh-issues`, there's no visibility into CI status. You have to open each PR on GitHub to see if checks are passing, failing, or still running. This slows down triage and review prioritization.

### Proposed Solution

Add a **CI** column to the PR table in `scripts/gh_issues.py`:

- Fetch `statusCheckRollup` from the `gh pr list` JSON output (already available, zero extra API calls).
- Display a compact summary per PR:
  - All passed: `✓ 6/6` (green)
  - In progress: `⏳ 3/6` (yellow)
  - Failures: `✗ 5/6` (red) with failed check names shown (e.g., `Project Checks`)
- Make the CI cell a clickable link to the PR's checks tab (`https://github.com/{owner}/{repo}/pull/{num}/checks`).

### Alternatives Considered

- A separate `just gh-ci` command — adds fragmentation, CI status is most useful in the PR context.
- Showing full check details — too noisy for a summary table; failed check names are sufficient.

### Impact

- Developer workflow improvement — faster triage of PRs.
- No breaking change; additive column in existing table.

### Acceptance Criteria

- [ ] PR table shows CI column with pass/fail/pending summary
- [ ] Failed check names are visible
- [ ] CI cell links to the GitHub checks page
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 09:58 PM_

## Design

### 1. Data Acquisition

Add `statusCheckRollup` to the existing `_fetch_prs()` JSON field list. Zero extra API calls — `gh pr list --json` already supports this field.

The `statusCheckRollup` payload is an array of objects:

```json
{
  "__typename": "CheckRun",
  "name": "Project Checks",
  "status": "COMPLETED",
  "conclusion": "SUCCESS"
}
```

Relevant fields: `status` (COMPLETED, IN_PROGRESS, QUEUED) and `conclusion` (SUCCESS, FAILURE, NEUTRAL, SKIPPED, CANCELLED).

### 2. New Pure Functions

**`_summarize_ci(checks: list[dict]) -> tuple[str, str, int, int]`**

Returns `(symbol, style, passed_count, total_count)`.

- Empty/None checks → `("—", "dim", 0, 0)`
- Count `total` = len(checks)
- Count `passed` = checks where `status == "COMPLETED"` and `conclusion` in `{SUCCESS, NEUTRAL, SKIPPED}`
- Count `failed` = checks where `status == "COMPLETED"` and `conclusion` not in that set
- If `failed > 0` → `("✗", "red", passed, total)`
- If `passed == total` → `("✓", "green", passed, total)`
- Otherwise (in-progress/queued) → `("⏳", "yellow", passed, total)`

**`_failed_check_names(checks: list[dict]) -> list[str]`**

Returns sorted list of `name` values for checks that completed with a non-success conclusion.

### 3. Cell Rendering (inside `_build_pr_table`)

```python
symbol, style, passed, total = _summarize_ci(pr.get("statusCheckRollup") or [])
if total == 0:
    ci_cell = _styled("—", "dim")
else:
    summary = f"{symbol} {passed}/{total}"
    failed = _failed_check_names(pr.get("statusCheckRollup") or [])
    if failed:
        summary += f" {', '.join(failed)}"
    ci_url = f"https://github.com/{owner_repo}/pull/{pr['number']}/checks"
    ci_cell = f"[link={ci_url}][{style}]{summary}[/][/link]"
```

### 4. Column Definition

New column inserted **before Review** (column order: #, Title, Author, Assignee, Issues, Branch, **CI**, Review, Reviewer, Delta):

```python
table.add_column("CI", no_wrap=True, justify="center", max_width=30)
```

### 5. Error Handling

- `statusCheckRollup` missing or `None` → treated as empty list → dash
- Check entries missing `status`/`conclusion`/`name` → default to empty strings via `.get()`, won't count as passed or failed (treated as in-progress)
- No new exceptions; follows existing defensive `.get()` pattern

### 6. Testing Strategy

Pure unit tests (no mocking), matching existing test style:

| Function | Scenarios |
|---|---|
| `_summarize_ci` | all passed, all failed, mixed pass/fail, in-progress, empty list, neutral/skipped count as passed |
| `_failed_check_names` | no failures, single failure, multiple sorted, empty input, missing name field |

### 7. Files Changed

| File | Change |
|---|---|
| `scripts/gh_issues.py` | Add `statusCheckRollup` to `_fetch_prs`, add `_summarize_ci`, `_failed_check_names`, add CI column + cell in `_build_pr_table` |
| `tests/test_gh_issues.py` | Add `TestSummarizeCi` and `TestFailedCheckNames` test classes |

