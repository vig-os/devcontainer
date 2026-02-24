---
type: issue
state: open
created: 2026-02-23T22:59:55Z
updated: 2026-02-23T23:04:31Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/163
comments: 1
labels: bug, area:workflow, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-24T04:24:07.489Z
---

# [Issue 163]: [[BUG] Wrong identity tags in commits & PR messages](https://github.com/vig-os/devcontainer/issues/163)

### Description

AI agents (Cursor, Codex, etc.) inject their own identity into commits and PR messages in multiple ways:
- Adding `Co-authored-by: Cursor <cursoragent@cursor.com>` trailers to commit messages
- Setting themselves as git author/committer
- Mentioning agent names in PR descriptions

The current `git_commit` skill has a "NEVER add Co-authored-by" note, but agents still do it. There is no enforcement mechanism — the `validate-commit-msg` commit-msg hook does not check for agent fingerprints.

### Steps to Reproduce

1. Ask a Cursor agent or Codex worktree agent to commit staged changes
2. Inspect the commit with `git log --format=full` or `git log --format='%b'`
3. Observe `Co-authored-by: Cursor <cursoragent@cursor.com>` trailer, or agent set as author/committer

### Expected Behavior

Commits and PR messages contain zero traces of AI agent identity. A pre-commit or commit-msg hook actively **rejects** commits containing known agent fingerprints (e.g. `cursor`, `claude`, `codex`, `chatgpt`, `copilot`, `cursoragent`).

### Actual Behavior

Agent identity leaks into commit trailers, author fields, and PR descriptions despite skill-level rules telling agents not to do it.

### Environment

- All agent-driven commit flows: interactive `/git_commit`, autonomous `worktree_execute`, `worktree_ci-fix`, `worktree_pr`

### Possible Solution

1. Extend `validate-commit-msg` (or add a new pre-commit hook) to scan the full commit message for a blocklist of agent-related keywords/patterns: `Co-authored-by`, `cursor`, `claude`, `codex`, `chatgpt`, `copilot`, `cursoragent@cursor.com`, etc. Reject the commit if any match is found.
2. Strengthen rules in `CLAUDE.md`, `git_commit` SKILL, and all worktree skills.
3. Consider a `prepare-commit-msg` hook that strips `Co-authored-by` trailers automatically.

### Changelog Category

Fixed

- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 23, 2026 at 11:04 PM_

## Design

### Overview

Three enforcement layers to strip all AI agent identity from commits and PRs:

1. **`prepare-commit-msg` hook** — auto-strips `Co-authored-by` trailers before the commit is finalized
2. **`commit-msg` hook** (extend `validate-commit-msg`) — rejects commits whose message body contains blocklisted agent patterns
3. **Pre-commit hook** — rejects commits where git author/committer name or email matches blocklisted agent patterns
4. **CI workflow** (extend `pr-title-check`) — scans PR title and body for agent fingerprints
5. **Skill rules** — strengthen existing "NEVER add Co-authored-by" notes across all skills

### Canonical blocklist: `.github/agent-blocklist.toml`

Single source of truth for all agent patterns, referenced by all hooks and CI.

```toml
# Canonical blocklist for AI agent identity fingerprints.
# Referenced by: validate-commit-msg, pre-commit hooks, pr-title-check CI.

[patterns]
# Trailer patterns (regex, matched against full lines)
trailers = [
  "^Co-authored-by:.*$",
  "^Signed-off-by:.*cursor.*$",
]

# Agent names/identifiers (substring match, case-insensitive)
names = [
  "cursor",
  "claude",
  "codex",
  "chatgpt",
  "copilot",
  "openai",
  "anthropic",
  "devin",
]

# Agent email patterns (substring match, case-insensitive)
emails = [
  "cursoragent@cursor.com",
  "noreply@cursor.com",
  "github-actions[bot]",
]
```

### Component 1: `prepare-commit-msg` hook (auto-strip trailers)

A local pre-commit hook (stage: `prepare-commit-msg`) that:
- Reads `COMMIT_EDITMSG`
- Removes any line matching `trailer` patterns from the blocklist
- Writes back the cleaned message

Runs **before** `commit-msg` validation, so trailers injected by the editor/agent are silently stripped.

### Component 2: Extend `validate-commit-msg` (reject remaining fingerprints)

Add a new validation step to the existing `validate_commit_message()` function:
- New optional parameter: `blocked_patterns_file: Path | None`
- If provided, load the TOML blocklist and scan the full message (body lines, not subject) for:
  - Remaining trailer patterns (regex match per line)
  - Agent name substrings (case-insensitive)
  - Agent email substrings (case-insensitive)
- Return `(False, "Commit message contains blocked AI agent fingerprint: '<match>'")` on first match
- New CLI arg: `--blocked-patterns <path>` forwarded from pre-commit config

The `.pre-commit-config.yaml` commit-msg hook gains the new arg:

```yaml
- id: validate-commit-msg
  args: [
    "--types", "feat,fix,...",
    "--blocked-patterns", ".github/agent-blocklist.toml",
  ]
```

### Component 3: Pre-commit hook for author/committer identity

A new local pre-commit hook (stage: `pre-commit`) implemented as a small Python script:
- Reads `.github/agent-blocklist.toml`
- Checks `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, `GIT_COMMITTER_EMAIL` (from env) and `git config user.name`/`git config user.email`
- If any match a `names` or `emails` pattern (case-insensitive substring), reject with a clear error

Added as a `local` hook in `.pre-commit-config.yaml`.

### Component 4: Extend `pr-title-check.yml` CI workflow

Add a second step to the existing `pr-title-check.yml`:
- Fetch PR body via `${{ github.event.pull_request.body }}`
- Load `.github/agent-blocklist.toml`
- Scan title + body for `names` and `emails` patterns
- Fail the check if any match

Can reuse a shared helper function extracted from `validate-commit-msg`.

### Component 5: Strengthen skill rules

Update the "NEVER add Co-authored-by" notes in:
- `git_commit/SKILL.md`
- `worktree_execute/SKILL.md`
- `worktree_pr/SKILL.md`
- `CLAUDE.md`

Replace with: "Never add Co-authored-by trailers. Never set git author/committer to an AI agent identity. Never mention AI agent names in commit messages or PR descriptions. The pre-commit hooks will reject violations."

### What this does NOT cover

- Rewriting existing commit history (out of scope)
- Blocking agent names in code comments or file content (not requested)
- GitHub Actions bot commits (e.g. Dependabot) — the author check hook excludes CI environments via env var check

### Sync to workspace template

Both `.pre-commit-config.yaml` and `.github/agent-blocklist.toml` are synced to `assets/workspace/` per the project's sync manifest pattern.

