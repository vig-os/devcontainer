---
type: issue
state: open
created: 2026-02-20T10:03:02Z
updated: 2026-02-20T10:03:02Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/104
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T13:17:16.911Z
---

# [Issue 104]: [[FEATURE] Make issue numbers in just gh-issues table clickable links](https://github.com/vig-os/devcontainer/issues/104)

### Description

Enhance the `#` column in the `just gh-issues` overview table so that issue numbers are clickable links. Ideally, clicking an issue number should open it directly in VS Code / Cursor (using a `vscode://` URI), with a fallback to the GitHub web URL for terminals that don't support custom URI schemes.

### Problem Statement

Currently the `#` column in the issue and PR tables rendered by `scripts/gh_issues.py` displays plain text numbers (e.g. `42`). Users who want to view an issue must manually copy the number and run `gh issue view` or navigate to GitHub. Adding clickable hyperlinks would eliminate this friction.

### Proposed Solution

Use Rich's built-in hyperlink support (`[link=URL]text[/link]`) to make the `#` column entries clickable in terminals that support OSC 8 hyperlinks (iTerm2, Windows Terminal, most modern terminal emulators, and Cursor's integrated terminal).

**Two link targets to evaluate (in order of preference):**

1. **Cursor/VS Code URI** — `vscode://file/...` or a `cursor://` URI that opens the issue in the editor's GitHub integration (if a reliable scheme exists)
2. **GitHub web URL** — `https://github.com/{owner}/{repo}/issues/{number}` as a reliable fallback that works universally

The `owner_repo` string is already fetched in `main()` and can be threaded to `_build_table` / `_build_pr_table`.

### Alternatives Considered

- **Keep plain numbers, add a separate "open issue" just recipe** — more keystrokes, doesn't leverage terminal hyperlink capabilities
- **Use `gh issue view --web` shortcut hint** — informational but not interactive

### Additional Context

- Related: #99 (parent — test coverage for `gh_issues.py`)
- Rich hyperlinks docs: `[link=https://...]text[/link]` markup
- OSC 8 terminal hyperlink support is widespread in modern terminals
- The PR table `#` column should also get the same treatment

### Impact

- Quality-of-life improvement for all developers using `just gh-issues`
- Backward-compatible — terminals without OSC 8 support simply render plain text
- Minor change (~5-10 lines in `_build_table` and `_build_pr_table`)

### Changelog Category

Changed
