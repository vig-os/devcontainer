# Global preferences (template: ~/.claude/CLAUDE.md)

## Commits

- **Never name an AI in git history.** No Co-Authored-By trailers naming an
  AI, never an AI as author or committer. This is the single source of truth
  for the rule; repos may enforce it with hooks but should not restate it.

## Working style

- Prefer minimal diffs; ask before out-of-scope changes.
- Run the full local hook suite green before any push.
