# vigOS org practices (managed fragment)

<!-- Managed by vigos.claude: org updates overwrite this file (a .bak of
     local edits is kept). Put personal rules in ~/.claude/CLAUDE.md. -->

- Never name an AI in git history: no AI Co-Authored-By trailers, never an
  AI as author or committer. Repos enforce this with hooks.
- Conventional Commits with a final `Refs: #<issue>` line (`chore` may omit
  when no issue applies). Pre-commit hooks are mandatory; never `--no-verify`.
- Traceability: issue → branch → PR; minimal diffs; no out-of-scope drive-bys.
- Run the repo's full local hook suite green before any push.
- Autonomous / skip-permissions agent runs happen inside the devcontainer,
  not on hosts (org working agreement).
