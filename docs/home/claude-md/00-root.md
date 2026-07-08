# CLAUDE.md — workspace root (template)

<!-- Copy to ~/<workspace-root>/CLAUDE.md and adapt. -->

This directory holds independent project workspaces, each a collection of
git repos cloned side by side. Do real work inside a repo, never at a
workspace root.

## Workspace map

| Dir | What it is | Confidentiality |
|-----|------------|-----------------|
| `<workspace-a>` | <description> | <public/private — default-deny external sharing> |

## Cross-cutting rules

- Confidentiality is default-deny: nothing leaves this machine (pastes,
  uploads, third-party APIs) without explicit authorization in the request.
- Git identity is managed by `~/.gitconfig` includeIf mappings — never
  hand-set an author or email.
- Engineering conventions (commit format, TDD, traceability) live in each
  org's meta/standards repo; the repo-level CLAUDE.md links them.
