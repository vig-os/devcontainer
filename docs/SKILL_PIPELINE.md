<!-- Auto-generated from docs/templates/SKILL_PIPELINE.md.j2 - DO NOT EDIT DIRECTLY -->
<!-- Run 'just docs' to regenerate -->

# Agent Skill Pipeline

How the `/command` skills fit together, what each one does, and when to use them.

## Overview

Skills are markdown playbooks that live in `.cursor/skills/`. Each one defines a repeatable workflow the agent follows when invoked via `/skill-name`. They are grouped into phases that form two parallel pipelines: **interactive** (human-in-the-loop) and **autonomous** (worktree, no user prompts).

```
              ┌─────────────────────────────────────────────┐
              │          INCEPTION (bootstrap)              │
              │             inception:explore               │
              │             inception:scope                 │
              │             inception:architect             │
              │             inception:plan                  │
              └──────────────────────┬──────────────────────┘
                                     │
              ┌──────────────────────▼──────────────────────┐
              │             ISSUE MANAGEMENT                │
              │                issue:triage                 │
              │                issue:create                 │
              │                issue:claim                  │
              └──────────────────────┬──────────────────────┘
                                     │
               ┌────────────────────────────────────────────────────────────────────┐
               │                                                                    │
     INTERACTIVE (human-in-the-loop)                                       AUTONOMOUS (worktree)
               │                                                                    │
  ┌────────────▼─────────────┐                              ┌───────────────────────▼─────────────────────┐
  │  design:brainstorm       │                              │  /solve-and-pr <issue>                      │
  │  design:plan             │                              │  └─► just worktree-start                    │
  │  code:tdd / code:execute │                              │       └─► worktree:solve-and-pr             │
  │  code:verify             │                              │            ├─ worktree:brainstorm           │
  │  code:review             │─► handoff via `just wt-..` ─►│            ├─ worktree:plan                 │
  │  git:commit              │                              │            ├─ worktree:execute              │
  │  pr:create               │                              │            ├─ worktree:verify               │
  │  ci:check / ci:fix       │                              │            ├─ worktree:pr                   │
  │                          │                              │            └─ worktree:ci-check / ci-fix    │
  └─────────────▼────────────┘                              │                                             │
                |                                           │  worktree:ask  (escape hatch: post          │
                |                                           │                 question on issue)          │
                |                                           │                                             │
                |                                           └──────────────────────▼──────────────────────┘
                |                                                                  │
                └─────────────────────────────────▼────────────────────────────────┘
                                                  |
                                                  |
                             ┌────────────────────▼──────────────────────┐
                             │            RELEASE MANAGEMENT             │
                             │             pr:create                     │
                             │             pr:post-merge                 │
                             └───────────────────────────────────────────┘


```

## Phase Breakdown

### Inception (Project Bootstrap)

Run when starting a new repo or major initiative. Explores the problem space, scopes boundaries, validates architecture, and decomposes the result into actionable issues.

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `inception:architect` | `/inception-architect` | Architecture evaluation — validate design against established patterns. |
| `inception:explore` | `/inception-explore` | Divergent exploration — understand the problem space before jumping to solutions. |
| `inception:plan` | `/inception-plan` | Decomposition — turn scoped design into actionable GitHub issues. |
| `inception:scope` | `/inception-scope` | Convergent scoping — define what to build and what not to build. |


### Issue Management

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `issue:claim` | `/issue-claim` | Sets up the local environment to begin working on a GitHub issue, and ensures the issue is assigned. |
| `issue:create` | `/issue-create` | Creates a new GitHub issue using the appropriate issue template. |
| `issue:triage` | `/issue-triage` | Triage open GitHub issues by analyzing them across priority, area, effort, SemVer impact, dependencies, and release readiness. Groups related issues into parent/sub-issue clusters, suggests milestone assignments, and applies approved changes via gh CLI. Use when the user asks to triage issues, groom the backlog, plan a milestone, or organize open issues. |


### Design (Interactive)

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `design:brainstorm` | `/design-brainstorm` | Explores requirements and design before writing any code. |
| `design:plan` | `/design-plan` | Breaks an approved design or issue into bite-sized implementation tasks. |


### Code (Interactive)

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `code:debug` | `/code-debug` | Diagnoses bugs, test failures, or unexpected behavior. Root cause first, fix second. |
| `code:execute` | `/code-execute` | Works through an implementation plan in batches with human checkpoints. |
| `code:review` | `/code-review` | Spawns a fresh-context readonly subagent to review changes before PR. |
| `code:tdd` | `/code-tdd` | Implements changes using strict RED-GREEN-REFACTOR discipline. |
| `code:verify` | `/code-verify` | Runs verification and provides evidence before claiming work is done. |


### Git & PR (Interactive)

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `git:commit` | `/git-commit` | Executes the commit workflow following the project's commit message conventions. |
| `pr:create` | `/pr-create` | Prepares and submits a pull request for feature or bugfix work. |
| `pr:post-merge` | `/pr-post-merge` | Performs cleanup and branch switching after a PR merge. |


### CI

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `ci:check` | `/ci-check` | Checks the CI pipeline status for the current branch or PR. |
| `ci:fix` | `/ci-fix` | Diagnoses and fixes a failing CI run using systematic debugging. |


### Autonomous Launcher

Interactive entry point to kick off autonomous work. Launches a worktree where the agent runs design → plan → execute → verify → PR → CI with no further human interaction. All progress is posted as issue comments.

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `solve-and-pr` | `/solve-and-pr` | Launches the autonomous worktree pipeline for an issue via just worktree-start. |


### Autonomous Worktree Pipeline

These are non-blocking counterparts of the interactive skills. They run in a git worktree with no user prompts — designed for `just worktree-start <issue>`. **Do not invoke these directly in your editor session.** They only work inside a worktree environment launched via `just`.

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `worktree:ask` | `/worktree-ask` | Posts a question to the GitHub issue when the autonomous agent is stuck. |
| `worktree:brainstorm` | `/worktree-brainstorm` | Autonomous design — reads full issue, posts design comment, never blocks for feedback. |
| `worktree:ci-check` | `/worktree-ci-check` | Autonomous CI check — polls until CI finishes, invokes worktree:ci-fix on failure. |
| `worktree:ci-fix` | `/worktree-ci-fix` | Autonomous CI fix — diagnoses failure, posts diagnosis, fixes, pushes, re-checks. |
| `worktree:execute` | `/worktree-execute` | Autonomous TDD implementation — commits as it goes, no user checkpoints. |
| `worktree:plan` | `/worktree-plan` | Autonomous planning — reads issue and design, posts implementation plan, never blocks. |
| `worktree:pr` | `/worktree-pr` | Autonomous PR creation from a worktree branch. |
| `worktree:solve-and-pr` | `/worktree-solve-and-pr` | State-aware autonomous pipeline — detect phase from issue, run remaining phases through PR. |
| `worktree:verify` | `/worktree-verify` | Autonomous verification — full test suite + lint + precommit, evidence only, loops on failure. |


## Artifacts & Outputs

Each phase produces concrete artifacts that feed into the next. This is the data flow through the pipeline.

### Inception → Issues

| Step | Output | Where it lives |
|------|--------|---------------|
| `inception:explore` | RFC document (Problem Statement, Impact, References) | `docs/rfcs/RFC-XXX-*.md` |
| `inception:scope` | RFC updated (Proposed Solution, Alternatives, Phasing); status → `proposed` | `docs/rfcs/RFC-XXX-*.md` |
| `inception:architect` | Design document (architecture, components, topology, tech stack) | `docs/designs/DES-XXX-*.md` |
| `inception:plan` | Parent epic + sub-issues + spike issues; milestone assignments; effort labels; RFC/Design updated with issue links | GitHub Issues |

### Issue Management → Branch

| Step | Output | Where it lives |
|------|--------|---------------|
| `issue:triage` | Triage matrix; labels, milestones, parent-issue links applied | `.github_data/triage-matrix.md` + GitHub |
| `issue:create` | New GitHub issue from template | GitHub |
| `issue:claim` | Issue assigned to you; linked branch created and checked out | GitHub + local git |

### Design → Plan (posted on the issue)

| Step | Output | Where it lives |
|------|--------|---------------|
| `design:brainstorm` | `## Design` comment (approved design) | GitHub issue comment |
| `design:plan` | `## Implementation Plan` comment (ordered tasks with acceptance criteria) | GitHub issue comment |

### Code → Commits

| Step | Output | Where it lives |
|------|--------|---------------|
| `code:tdd` | RED commit (`test: …`), GREEN commit (`feat: …`/`fix: …`), optional REFACTOR commit | Local git |
| `code:execute` | Code commits per batch; plan comment updated with checked-off tasks | Local git + GitHub issue comment |
| `code:debug` | Failing-test commit + fix commit | Local git |
| `code:verify` | Pass/fail verification report (tests, lint, precommit) | Terminal output |
| `code:review` | Structured review report (acceptance criteria checklist, issues by severity) | Terminal output (readonly subagent) |

### Git & PR → Pull Request

| Step | Output | Where it lives |
|------|--------|---------------|
| `git:commit` | Single commit following project conventions | Local git |
| `pr:create` | PR draft file + GitHub PR + CHANGELOG update if needed | `.github/pr-draft-*.md` + GitHub PR |
| `pr:post-merge` | Feature branch deleted; switched to base branch; draft file cleaned up | Local git |

### CI → Green Build

| Step | Output | Where it lives |
|------|--------|---------------|
| `ci:check` | CI status report | Terminal output |
| `ci:fix` | Fix commits pushed to remote | Local + remote git |

### Autonomous Pipeline (same artifacts, no human prompts)

> **Important:** `worktree:*` skills are **not** invoked directly in your editor session. They only work inside a worktree launched via `just worktree-start`, which sets up the isolated environment, tmux session, and `cursor-agent` process they depend on.

| Step | Output | Where it lives |
|------|--------|---------------|
| `worktree:brainstorm` | `## Design` comment | GitHub issue comment |
| `worktree:plan` | `## Implementation Plan` comment | GitHub issue comment |
| `worktree:execute` | Code commits; plan tasks checked off | Local git + GitHub issue comment |
| `worktree:verify` | Verification report; fix commits if needed | Terminal + local git |
| `worktree:pr` | GitHub PR + CHANGELOG update | GitHub PR |
| `worktree:ci-check` | CI polling result | Terminal output |
| `worktree:ci-fix` | `## CI Diagnosis` comment + fix commits pushed | GitHub issue comment + remote git |
| `worktree:ask` | `## Question` comment (escape hatch) | GitHub issue comment |
| `worktree:solve-and-pr` | `## Autonomous Run Complete` summary + all of the above | GitHub issue comment |

## State Detection (Autonomous Pipeline)

`worktree:solve-and-pr` determines where to resume by scanning issue comments:

| Comment heading found | Phase considered done | Next phase |
|---|---|---|
| *(none)* | — | `worktree:brainstorm` |
| `## Design` | Design | `worktree:plan` |
| `## Implementation Plan` | Planning | `worktree:execute` |

This makes the autonomous pipeline **idempotent** — re-running it picks up where it left off.

## Subagent Delegation

Skills can delegate mechanical sub-steps (CLI calls, template filling, comment posting) to lightweight subagents via the Task tool, keeping the primary model focused on reasoning. Delegation tiers are defined in `.cursor/rules/subagent-delegation.mdc`:

- **Lightweight** — CLI commands, file reading, template filling, comment posting
- **Standard** — code review, log analysis, structured verification
- **Main agent** — design, code generation, debugging, TDD loops

## Worktree Infrastructure (`justfile.worktree`)

The autonomous pipeline doesn't run inside your current editor session. It runs in an isolated **git worktree** managed by `just` recipes, with a `cursor-agent` process inside a `tmux` session. This is the runtime layer that makes `worktree:*` skills work.

### Lifecycle Recipes

| Recipe | What it does |
|--------|-------------|
| `just worktree-start <issue> "<prompt>"` | Creates a worktree, resolves (or creates) the linked branch, sets up the environment (`uv sync`, `pre-commit install`, `.env` copy), trusts the directory for `cursor-agent`, then launches a `tmux` session running `agent chat --yolo` with the given prompt. If the worktree already exists, it reuses it. |
| `just worktree-attach <issue>` | Attaches to the running `tmux` session so you can watch or intervene. |
| `just worktree-list` | Lists all worktrees with their branch, issue number, and tmux status (`[RUNNING]` / `[STOPPED]`). |
| `just worktree-stop <issue>` | Kills the tmux session, removes the worktree directory, and deletes the local branch. |
| `just worktree-clean` | Stops and removes all worktrees at once. Prunes stale git worktree refs. |

### What `worktree-start` Does Under the Hood

1. **Prerequisites** — checks for `tmux` and `cursor-agent` CLI.
2. **Authentication** — tries existing browser login, falls back to `CURSOR_API_KEY`, or prompts `agent login`.
3. **Branch resolution** — calls `gh issue develop --list` to find the linked branch. If none exists, it:
   - Fetches issue metadata, infers branch type from labels (`bugfix` vs `feature`).
   - Uses a lightweight agent call to derive a kebab-case summary from the issue title.
   - Determines the base branch (parent issue's branch, or `dev`).
   - Creates and links the branch via `gh issue develop`.
   - Assigns the issue to `@me`.
4. **Worktree setup** — `git worktree add`, then inside the worktree: `uv sync`, `pre-commit install`, copies `.env` from the main worktree.
5. **Trust** — adds the worktree path to `~/.cursor/cli-config.json` `trustedDirectories`.
6. **Launch** — starts `tmux new-session` running `agent chat --model <autonomous-model> --yolo "<prompt>"`.

The `--yolo` flag means the agent auto-approves all shell commands — appropriate because there's no human at this terminal.

### Model Selection

Agent models are read from `.cursor/agent-models.toml`. The worktree recipes use:
- **`autonomous` tier** for the main `agent chat` session (design, code, reasoning).
- **`lightweight` tier** for the one-shot branch-naming call.

## Typical Interactive Workflow

```
/issue-claim 42
/design-brainstorm          ← explore + propose + approve
/design-plan                ← break into tasks
/code-tdd                   ← implement (repeat per task)
/code-verify                ← run full verification
/code-review                ← pre-PR review
/git-commit                 ← commit (as needed throughout)
/pr-create                  ← open PR
/ci-check                   ← confirm CI passes
/pr-post-merge              ← cleanup after merge
```

## Typical Autonomous Workflow

### Option 1: From your editor

```
/solve-and-pr 42            ← launches worktree, returns immediately
# Agent runs in background: brainstorm → plan → execute → verify → pr → ci-check
# Progress posted as issue comments. You're the reviewer.
```

### Option 2: From the command line

```bash
just worktree-start 42 "/worktree-solve-and-pr"
# Same as above, but launched via just directly
# All progress posted as issue comments. No human interaction needed.

just worktree-attach 42     # watch or intervene
just worktree-stop 42       # tear down when done
```
