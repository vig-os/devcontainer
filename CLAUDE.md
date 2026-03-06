# Project: eXoma Devcontainer

## Custom Commands

Available slash commands (SSoT: `.cursor/skills/`, mapped via `.claude/commands/`):

| Command | Description |
|---------|-------------|
| `/project:ci_check` | Check CI pipeline status for current branch/PR |
| `/project:ci_fix` | Diagnose and fix failing CI runs |
| `/project:code_debug` | Systematic debugging: root cause first, fix second |
| `/project:code_execute` | Work through implementation plan in batches with checkpoints |
| `/project:code_review` | Structured self-review before submitting a PR |
| `/project:code_tdd` | Strict RED-GREEN-REFACTOR discipline |
| `/project:code_verify` | Run verification and provide evidence before claiming done |
| `/project:design_brainstorm` | Explore requirements and design before writing code |
| `/project:design_plan` | Break approved design into implementation tasks |
| `/project:git_commit` | Commit workflow following project conventions |
| `/project:inception_explore` | Divergent exploration -- understand the problem space |
| `/project:inception_scope` | Convergent scoping -- define what to build and what not to build |
| `/project:inception_architect` | Architecture evaluation -- validate design against established patterns |
| `/project:inception_plan` | Decomposition -- turn scoped design into actionable GitHub issues |
| `/project:issue_claim` | Set up local environment to work on a GitHub issue |
| `/project:issue_create` | Create a new GitHub issue using templates |
| `/project:issue_triage` | Triage and label GitHub issues |
| `/project:pr_create` | Prepare and submit a pull request |
| `/project:pr_post-merge` | Cleanup after PR merge |
| `/project:pr_solve` | Diagnose PR failures, plan fixes, execute them |
| `/project:worktree_ci-check` | Autonomous CI check -- polls until completion, triggers fix on failure |
| `/project:worktree_ci-fix` | Autonomous CI fix -- diagnose, post diagnosis, fix, push, re-check |
| `/project:worktree_brainstorm` | Autonomous design -- reads issue, posts design, never blocks |
| `/project:worktree_plan` | Autonomous planning -- posts implementation plan, never blocks |
| `/project:worktree_execute` | Autonomous TDD implementation -- no user checkpoints |
| `/project:worktree_verify` | Autonomous verification -- evidence only, loops on failure |
| `/project:worktree_pr` | Autonomous PR creation from worktree branch |
| `/project:worktree_ask` | Post question to issue when autonomous agent is stuck |
| `/project:worktree_solve-and-pr` | Full autonomous pipeline: detect state, design, plan, execute, verify, PR |

---

## Always-Apply Rules

Rules SSoT: `.cursor/rules/` (read these files for full detail).

### Coding Principles

See `.cursor/rules/coding-principles.mdc` for full detail.

1. **YAGNI** -- Implement only what the issue or user explicitly requests. No speculative features. Ask before adding anything unasked.
2. **Minimal diff** -- Touch only files and lines required for the task. No drive-by refactors, renames, or reformats. Mention improvements separately; don't silently change them.
3. **DRY** -- Don't duplicate logic. Extract shared code only after the pattern appears twice. Prefer existing abstractions over new ones.
4. **No secrets** -- Never hardcode tokens, passwords, keys, or connection strings. Use env vars. Don't commit .env or credential files. Flag existing secrets to the user.
5. **Traceability** -- Every change must link to a GitHub issue. No out-of-scope fixes. Suggest a new issue instead of bundling unrelated changes.
6. **Single responsibility** -- One function = one job. Prefer new functions over extending existing ones. Split functions exceeding ~50 lines or handling multiple concerns.

**Stop if:** Adding code the issue didn't ask for, editing files outside scope, hardcoding secrets, making untraceable changes, or growing a function beyond one purpose.

### Commit Message Standard

See `.cursor/rules/commit-messages.mdc` and `docs/COMMIT_MESSAGE_STANDARD.md` for full detail.

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
- Never add Co-authored-by trailers. Never set git author/committer to an AI agent identity. Never mention AI agent names in commit messages or PR descriptions. The pre-commit hooks will reject violations.

### Changelog Rules

- Update the `## Unreleased` section of `CHANGELOG.md` for `feat`, `fix`, `refactor`, `build`, `revert`, `style`, `test`, `docs` changes with user-visible impact.
- Skip for purely internal `chore` commits.
- Use [Keep a Changelog](https://keepachangelog.com/) categories: Added, Changed, Deprecated, Removed, Fixed, Security.
- Entry format: `- **Bold title** ([#issue](url))` with sub-bullets for details.
- Never modify entries below `## Unreleased`.

### Branch Naming

See `.cursor/rules/branch-naming.mdc` for full detail.

Format: `<type>/<issue_number>-<short_summary>`

Types: `feature` | `bugfix` | `release`

Use `gh issue develop` to create and link branches. Always confirm branch name with user before creating.

### Single Source of Truth

Every piece of knowledge lives in exactly one place. Reference it everywhere else. Don't copy -- link. Applies to docs, config, infra, rules, and comments.

### TDD

See `.cursor/rules/tdd.mdc` for the scenario checklist and full detail.

1. Write the failing test first. Run it. Confirm it fails.
2. **Commit** the failing test (`test: ...`) following the Commit Message Standard above. Do not proceed before committing.
3. Write minimal code to pass. Run it. Confirm it passes. **Commit** the implementation.
4. Refactor. Run tests. Confirm no regressions. **Commit** if meaningful.

All commits must follow the Commit Message Standard. Never use `--no-verify`.

Each phase gets its own commit. Do not write implementation before its test. Skip TDD only for non-testable changes (config, templates, docs) -- note why.
