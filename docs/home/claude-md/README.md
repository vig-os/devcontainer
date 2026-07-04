# CLAUDE.md hierarchy — templates

Claude Code loads every `CLAUDE.md` from the filesystem root down to the
working directory; **the most specific file wins on conflict**. These
templates layer org-wide practice into that cascade. They are **guidelines,
not enforcement** — copy, adapt, delete freely.

## The layout convention that makes this work

The workspace layer only exists if repos live *under* a workspace directory:

```
~/Documents/                  <- workspace root: 00-root.md
  <workspace>/                <- one per org/project: 10-workspace.md
    <repo>/                   <- the repo's own CLAUDE.md (in git)
```

If you keep a flat `~/code/`, skip the workspace layer — the user-global and
repo layers still apply.

| Template | Copy to | Layer |
|---|---|---|
| `20-user-global.md` | `~/.claude/CLAUDE.md` | every session |
| `00-root.md` | `~/<workspace-root>/CLAUDE.md` | all workspaces |
| `10-workspace.md` | `~/<workspace-root>/<workspace>/CLAUDE.md` | one workspace |

Repo-level files are not templated here — each repo owns its own (this
repo's `CLAUDE.md` is a live example).

These files live outside any git repo. Version them in your personal home
flake (e.g. `home.file` entries) or a dotfiles repo — the optional
management option lands with `vigos.claude` (#823).
