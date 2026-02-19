# Project: eXoma Devcontainer

## Custom Commands

Available slash commands (symlinked from `.cursor/skills/`):

| Command | Description |
|---------|-------------|
| `/ci-check` | Check CI pipeline status for current branch/PR |
| `/ci-fix` | Diagnose and fix failing CI runs |
| `/code-debug` | Systematic debugging: root cause first, fix second |
| `/code-execute` | Work through implementation plan in batches with checkpoints |
| `/code-review` | Structured self-review before submitting a PR |
| `/code-tdd` | Strict RED-GREEN-REFACTOR discipline |
| `/code-verify` | Run verification and provide evidence before claiming done |
| `/design-brainstorm` | Explore requirements and design before writing code |
| `/design-plan` | Break approved design into implementation tasks |
| `/git-commit` | Commit workflow following project conventions |
| `/issue-claim` | Set up local environment to work on a GitHub issue |
| `/issue-create` | Create a new GitHub issue using templates |
| `/issue-triage` | Triage and label GitHub issues |
| `/pr-create` | Prepare and submit a pull request |
| `/pr-post-merge` | Cleanup after PR merge |
| `/worktree-ci-check` | Autonomous CI check — polls until completion, triggers fix on failure |
| `/worktree-ci-fix` | Autonomous CI fix — diagnose, post diagnosis, fix, push, re-check |
| `/worktree-brainstorm` | Autonomous design — reads issue, posts design, never blocks |
| `/worktree-plan` | Autonomous planning — posts implementation plan, never blocks |
| `/worktree-execute` | Autonomous TDD implementation — no user checkpoints |
| `/worktree-verify` | Autonomous verification — evidence only, loops on failure |
| `/worktree-pr` | Autonomous PR creation from worktree branch |
| `/worktree-ask` | Post question to issue when autonomous agent is stuck |
| `/worktree-solve-and-pr` | Full autonomous pipeline: detect state → design → plan → execute → verify → PR |

---

## Always-Apply Rules

### Coding Principles

1. **YAGNI** -- Implement only what the issue or user explicitly requests. No speculative features. Ask before adding anything unasked.
2. **Minimal diff** -- Touch only files and lines required for the task. No drive-by refactors, renames, or reformats. Mention improvements separately; don't silently change them.
3. **DRY** -- Don't duplicate logic. Extract shared code only after the pattern appears twice. Prefer existing abstractions over new ones.
4. **No secrets** -- Never hardcode tokens, passwords, keys, or connection strings. Use env vars. Don't commit .env or credential files. Flag existing secrets to the user.
5. **Traceability** -- Every change must link to a GitHub issue. No out-of-scope fixes. Suggest a new issue instead of bundling unrelated changes.
6. **Single responsibility** -- One function = one job. Prefer new functions over extending existing ones. Split functions exceeding ~50 lines or handling multiple concerns.

**Stop if:** Adding code the issue didn't ask for, editing files outside scope, hardcoding secrets, making untraceable changes, or growing a function beyond one purpose.

### Commit Message Standard

Format:

```
type(scope)!: short description

Refs: #<issue>
```

- **Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `revert`, `style`
- Scope optional; `!` only for breaking changes
- Imperative mood, no period
- **Refs line mandatory** (at least one GitHub issue, e.g. `Refs: #36`). Exception: `chore` commits may omit `Refs:` when no issue is related.
- Exactly one `Refs:` line, always last line
- No emojis, no semantic-release style, no types outside the list

### Changelog Rules

- Update the `## Unreleased` section of `CHANGELOG.md` for `feat`, `fix`, `refactor`, `build`, `revert`, `style`, `test`, `docs` changes with user-visible impact.
- Skip for purely internal `chore` commits.
- Use [Keep a Changelog](https://keepachangelog.com/) categories: Added, Changed, Deprecated, Removed, Fixed, Security.
- Entry format: `- **Bold title** ([#issue](url))` with sub-bullets for details.
- Never modify entries below `## Unreleased`.

### Branch Naming

Format: `<type>/<issue_number>-<short_summary>`

Types: `feature` | `bugfix` | `release`

Use `gh issue develop` to create and link branches. Always confirm branch name with user before creating.

### Single Source of Truth

Every piece of knowledge lives in exactly one place. Reference it everywhere else. Don't copy -- link. Applies to docs, config, infra, rules, and comments.

### TDD

1. Write the failing test first. Run it. Confirm it fails. **Commit** (`test: ...`).
2. Write minimal code to pass. Run it. Confirm it passes. **Commit** the implementation.
3. Refactor. Run tests. Confirm no regressions. **Commit** if meaningful.

Each phase gets its own commit. Do not write implementation before its test. Skip TDD only for non-testable changes (config, templates, docs) -- note why.
