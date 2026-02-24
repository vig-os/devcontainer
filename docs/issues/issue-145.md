---
type: issue
state: open
created: 2026-02-21T21:57:13Z
updated: 2026-02-23T23:48:00Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/145
comments: 4
labels: feature, area:workflow, effort:large, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-24T04:24:10.279Z
---

# [Issue 145]: [[FEATURE] Rewrite gh-issues dashboard — Polars + Typer + responsive layout](https://github.com/vig-os/devcontainer/issues/145)

### Description

Rewrite `scripts/gh_issues.py` from an imperative script into a proper CLI tool backed by Polars DataFrames, Typer CLI, and Rich rendering. The goal is a responsive, filterable project dashboard accessible via `just gh-issues`.

### Problem Statement

The current `just gh-issues` script has accumulated several pain points:

1. **No CI visibility** — PR check status requires opening GitHub (#143)
2. **Column truncation** — too many columns compete for space on normal terminal widths; data gets clipped and unreadable
3. **No activity signal** — can't tell if an issue/PR is fresh or stale without clicking through
4. **No filtering** — can't scope to "my issues", a specific milestone, or PRs needing review
5. **Brittle architecture** — imperative fetch-loop-format code makes every new column or feature a surgical edit

### Proposed Solution

Rewrite as a Typer CLI app with Polars as the data layer:

- **Data layer (Polars):** Fetch JSON from `gh`, load into DataFrames. All grouping, filtering, joining, and aggregation become DataFrame operations.
- **CLI layer (Typer):** Subcommands and options for filtering (`--assignee @me`, `--milestone 0.4`), grouping, output control.
- **Rendering layer (Rich):** Responsive table layout that adapts column set to terminal width. Activity column as a color-coded dot (no text). CI status column with compact rollup.
- **`@me` support:** Resolve current GitHub user via `gh auth status` and substitute `@me` in filters.

### Sub-Issues

Implementation will be broken into sub-issues (to be filled in during planning):

- [ ] #143 — CI status column
- [ ] Polars data layer — fetch + DataFrame construction
- [ ] Typer CLI scaffolding — subcommands, options, help
- [ ] Responsive column layout — adaptive to terminal width
- [ ] Activity indicator — color-coded staleness dot
- [ ] `@me` filter — resolve current user, filter by assignee/author/reviewer
- [ ] Milestone/label filtering
- [ ] Parent/sub-issue tree rendering in DataFrame model

### Alternatives Considered

- **Incremental patches** — keep adding columns to the current script. Pros: small diffs. Cons: the architecture doesn't support filtering, responsive layout, or clean data operations. Each feature is harder than the last.
- **External tool (e.g., gh-dash)** — Pros: already exists. Cons: doesn't match our label taxonomy, milestone grouping, or sub-issue tree rendering. We'd lose the tight integration with `just` recipes and project conventions.

### Impact

- **Beneficiaries:** All developers using `just gh-issues` for project triage.
- **Breaking changes:** The CLI invocation stays the same (`just gh-issues`). Rich table output format may change (not a stable API).
- **New dependencies:** `polars`, `typer`, `rich` (rich already used, just not declared).

### Acceptance Criteria

- [ ] `just gh-issues` renders a responsive table that adapts to terminal width
- [ ] CI status visible per PR with failure detail
- [ ] Activity indicator per issue/PR (color-coded, no text)
- [ ] `--assignee @me` filter works
- [ ] Existing features preserved: milestone grouping, sub-issue trees, PR cross-refs, branch display
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Added

### References

- #143 — CI status column (first sub-issue)
- #104 — Clickable issue numbers (already implemented)
- #105 — PR reviewer column bug
- #121 — Cross-ref bug (Refs: vs Closes)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 09:58 PM_

## Exploration Summary

### Signal
Direct developer experience using `just gh-issues` daily. The dashboard lacks CI visibility, truncates on normal terminals, has no activity/staleness signal, and offers no filtering.

### Pain Points Identified
1. **No CI visibility** — must open GitHub to check PR pipeline status
2. **Column truncation** — 10 columns compete for space, output unreadable on <140 col terminals
3. **No activity signal** — cannot tell fresh from stale at a glance
4. **No filtering** — no `@me`, no milestone filter, no "needs my review"
5. **Brittle architecture** — imperative loops make each new feature harder

### Key Design Decisions (from exploration)
- **Polars DataFrames** as data backbone — all grouping/filtering/joining become declarative
- **Typer CLI** — subcommands and options for filtering (`--assignee @me`, `--milestone 0.4`)
- **Rich rendering** — responsive layout adapting column set to terminal width
- **Activity dot** — color-coded indicator (green/yellow/red/dim), no text, ~1 char wide
- **`@me` support** — resolve current GitHub user via `gh auth status`
- **Rich tables only** — human-facing dashboard, not a data export tool

### Assumptions to Validate
- Polars binary size (~20 MB) is acceptable for a dev-only dependency
- `statusCheckRollup` provides sufficient CI detail without extra API calls
- Composable filters (`--assignee @me --milestone 0.4`) are the right UX

### RFC
See `docs/rfcs/RFC-001-2026-02-21-gh-issues-dashboard-rewrite.md`

### Next Step
Proceed to **inception_scope** to define boundaries, then **inception_plan** to create sub-issues.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 21, 2026 at 10:44 PM_

## Design

> RFC-001: Rewrite gh-issues dashboard with Polars, Typer, and responsive layout
> Status: draft | Date: 2026-02-21 | Author: @gerchowl

### Problem Statement

`just gh-issues` is the primary CLI dashboard for triaging open issues and PRs.
The current implementation (`scripts/gh_issues.py`) is a single imperative script
that fetches JSON from `gh`, loops through results, and renders Rich tables.

Pain points observed during daily use:

1. **No CI visibility.** PR check status (pass/fail/pending) is invisible. You must open GitHub to see whether a PR pipeline is green. (#143)
2. **Column truncation.** Ten columns compete for terminal width. On normal terminals (<140 cols) the output is clipped and unreadable.
3. **No activity signal.** No way to tell at a glance whether an issue or PR is fresh or stale without clicking through to GitHub.
4. **No filtering.** Cannot scope the view to "my issues", a specific milestone, or PRs waiting on review. The only view is "everything."
5. **Brittle architecture.** Every new feature requires surgical edits to imperative loops. No separation of data, logic, and presentation.

**If we do nothing:** each incremental improvement makes the script harder to maintain. Developers context-switch to GitHub for basic triage.

### Proposed Solution

- **Data layer: Polars DataFrames.** Fetch JSON from `gh`, load into DataFrames. Grouping, filtering, joining, and aggregation become declarative operations.
- **CLI layer: Typer.** Options for filtering (`--assignee @me`, `--milestone 0.4`), grouping, and output control.
- **Rendering layer: Rich.** Responsive table layout that adapts its column set to terminal width. Activity as a color-coded dot (no text). CI status as a compact rollup with link to checks page.
- **`@me` support.** Resolve current GitHub user via `gh auth status`.
- **Output: Rich tables only.** Human-facing dashboard, not a data export tool.

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Incremental patches to current script | Small diffs | Architecture doesn't support filtering, responsive layout, or clean data ops | Rejected — each new feature is harder |
| External tool (gh-dash, etc.) | Already exists | Doesn't match label taxonomy, milestone grouping, sub-issue trees, or `just` integration | Rejected — too disconnected |
| argparse/click instead of Typer | Fewer deps | More boilerplate on Python 3.12 | Rejected — Typer gives type-hint driven CLI |

### Phasing

**Phase 1: CI status column (#143)**
- Add `statusCheckRollup` to PR fetch, render CI column
- Can be done on current architecture as a standalone improvement

**Phase 2: Polars + Typer rewrite (sub-issues TBD)**
- Polars data layer (fetch → DataFrame)
- Typer CLI scaffolding (subcommands, options, `--help`)
- Responsive column layout (adaptive to terminal width)
- Activity indicator (color-coded dot, no text)
- `@me` filter
- Milestone/label filtering
- Parent/sub-issue tree rendering in DataFrame model

**Phase 3: Bug fixes rolled in**
- #105 PR reviewer column accuracy
- #121 Cross-ref `Refs:` vs `Closes` parsing

### Risks

- **New dependencies:** `polars` (~20 MB binary wheel), `typer`. Acceptable for dev-only tool.
- **API rate limits:** `statusCheckRollup` and sub-issue parents add API calls. May need batching.
- **Scope creep:** Sub-issues enforce incremental delivery.

### Open Questions

- Should the rewrite live in `scripts/gh_issues.py` (in-place) or move to a package (e.g., `packages/gh-dashboard/`)?
- Should filters compose (`--assignee @me --milestone 0.4`) or be mutually exclusive subcommands?
- How to handle the Polars binary size: dev dependency group only?

### References

- #143 CI status column (first sub-issue)
- #104 Clickable issue numbers (already implemented)
- #105 PR reviewer column bug
- #121 Cross-ref bug (Refs: vs Closes)
- #109 Discussion: CI pipeline optimization
- Full RFC: `docs/rfcs/RFC-001-2026-02-21-gh-issues-dashboard-rewrite.md`

---

# [Comment #3]() by [gerchowl]()

_Posted on February 23, 2026 at 07:24 AM_

### Alternative to explore: GitKraken CLI (`gk`)

Worth checking out [GitKraken CLI](https://github.com/gitkraken/gk-cli) (`gk`) as a potential alternative or inspiration before committing to the full rewrite. It provides:

- `gk issue list` / `gk pr list` — rich terminal dashboard for issues and PRs
- Built-in filtering by assignee, label, milestone
- Launchpad view with CI status, review state, and activity indicators

If it covers enough of our needs out of the box (or with light scripting), it could replace the custom dashboard entirely. If not, its UX patterns (column layout, status indicators) are worth borrowing.

**Action:** Try `gk` against this repo and evaluate coverage vs. our requirements (milestone grouping, sub-issue trees, label taxonomy, `just` integration).

---

# [Comment #4]() by [gerchowl]()

_Posted on February 23, 2026 at 11:48 PM_

### Alternative to explore: Textual TUI (like Toad)

[Toad](https://github.com/batrachianai/toad) — built by Will McGugan (creator of Rich and Textual) — demonstrates that Textual can power a full interactive terminal UI with live shell embedding, concurrent agent sessions, and streaming output. Worth evaluating as an architecture for the dashboard rewrite.

#### What Textual enables beyond static Rich tables

- **Interactive TUI** — sortable/filterable data tables, keyboard navigation, panel layouts, drill-down into issue details
- **Live refresh** — auto-poll GitHub API and re-render in place (via `Worker` async tasks)
- **Embedded shell / tmux viewer** — Toad proves Textual can run a real PTY widget; this could show live worktree agent output
- **Concurrent session overview** — Toad's `Ctrl+S` shows all running agents; analogous to a worktree status panel

#### Testability

Textual ships with a first-class `Pilot` test driver — headless async tests via pytest:
- `pilot.click()`, `pilot.press()` for interaction
- `app.query_one(CSS_selector)` for widget state assertions
- Snapshot regression testing for visual layout
- No real terminal needed — fits TDD workflow

#### Data layer: Python GitHub API instead of `gh` CLI

Replace the current 5+ serial `subprocess.run` calls to `gh` with direct HTTP calls (`httpx` async) to GitHub REST/GraphQL API:
- Fetch issues, PRs, branches, sub-issue parents in 1-2 GraphQL queries (vs. 5+ CLI round trips)
- `asyncio.gather` for parallel fetches
- Clean mockability (mock HTTP client vs. matching subprocess argument lists)
- Native integration with Textual's async `Worker` for live refresh

#### Potential architecture

```
data layer (async GitHub API client via httpx)
  → model layer (dataclasses / Polars DataFrames)
    → UI layer (Textual widgets consuming models)
```

Each layer independently testable.

#### Scope question: dashboard vs. project control center

Toad covers **agents + shell** but not **project management** (issues, PRs, CI, milestones). The gh-issues dashboard covers **project management** but not **agents or live shells**. Two possible paths:

1. **Keep focused** — Textual TUI for the dashboard rewrite only (issues, PRs, CI, filtering). Agents stay in Toad or tmux.
2. **Expand later** — Build the dashboard first, then layer on worktree overview panel and tmux shell viewer as follow-up issues. The async Textual architecture supports adding panels without rework.

Recommend path 1 first (YAGNI), with the architecture designed to support path 2.

#### References

- [Toad](https://github.com/batrachianai/toad) — Textual-based agent TUI by Will McGugan
- [Textual testing docs](https://textual.textualize.io/guide/testing/)
- [Agent Client Protocol](https://agentclientprotocol.com/overview/introduction) — protocol Toad uses for multi-agent support

