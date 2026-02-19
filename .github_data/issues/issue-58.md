---
type: issue
state: closed
created: 2026-02-17T18:44:24Z
updated: 2026-02-19T14:22:30Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/58
comments: 3
labels: feature, priority:medium, area:workflow, effort:small, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T14:22:48.646Z
---

# [Issue 58]: [validate-commit-msg: enforce types/scopes/refs by default](https://github.com/vig-os/devcontainer/issues/58)

cc @c-vigo

**Suggestion:** `validate-commit-msg` should ship with types, scopes, and refs **enforced by default** (strict-by-default) instead of being opt-in via commented-out CLI args.

**Why:** Users won't discover commented-out config. If enforcement is on by default, they experience the value immediately. The pre-commit error message can link to `.pre-commit-config.yaml` with a "customize or disable" hint — easy opt-out beats invisible opt-in.

**TL;DR:** Default strict → show config path in error → users discover greatness, can relax if needed.

Ref: `.pre-commit-config.yaml` lines 120–126.
---

# [Comment #1]() by [c-vigo]()

_Posted on February 18, 2026 at 10:00 AM_

I agree on enforced types, but not so much on scopes since they can be very project-dependent, and there is even a question to be made whether they are useful or not.

Currently we use:

```ini
  # Commit message validation (commit-msg stage)
  - repo: local
    hooks:
      - id: validate-commit-msg
        name: validate commit message
        entry: uv run validate-commit-msg
        language: system
        stages: [commit-msg]
        args: [
          "--types", "feat,fix,docs,chore,refactor,test,ci,build,revert,style",
          "--scopes", "setup,image,vigutils",
          "--refs-optional-types", "chore",
        ]
```

---

# [Comment #2]() by [gerchowl]()

_Posted on February 18, 2026 at 10:21 AM_

I'd say so, i.e. for changelog generation/grouping and, yes, scopes one could do some generic (or even have them auto populated based on codebase/project analysis / AST .. :-D)

---

# [Comment #3]() by [c-vigo]()

_Posted on February 19, 2026 at 02:22 PM_

Solved in [e27722c](https://github.com/vig-os/devcontainer/commit/e27722c216d1a9a55b74c3a98639ab4615dbde82)

